#!/usr/bin/env python3

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import json
import os
from pathlib import Path
import sys
import tempfile


class WorkflowError(Exception):
  pass


SPECIALISTS = {
  "implementer": ("gpt-5.6-sol", "xhigh"),
  "committer": ("gpt-5.6-terra", "xhigh"),
  "validator": ("gpt-5.6-luna", "xhigh"),
  "habit-curator": ("gpt-5.6-sol", "xhigh"),
  "structural-reviewer": ("gpt-5.6-sol", "xhigh"),
}
LEASE_OWNERS = ("coordinator", *SPECIALISTS)
TRANSITIONS = {
  "initialized": {"implementing"},
  "implementing": {"implemented"},
  "implemented": {"committed"},
  "committed": {"initial-validating"},
  "initial-validating": {"coordinator-review", "implementing"},
  "coordinator-review": {"habit-curation", "implementing"},
  "habit-curation": {"structural-review", "implementing"},
  "structural-review": {"final-validating", "implementing"},
  "final-validating": {
    "habit-frozen",
    "implementing",
    "habit-curation",
    "structural-review",
  },
  "habit-frozen": {"baseline-committed"},
  "baseline-committed": {"pr-open"},
  "pr-open": {"ci-monitoring"},
  "ci-monitoring": {"ready-for-merge", "implementing"},
  "ready-for-merge": {"merged"},
  "merged": set(),
}
COMMIT_KINDS = (
  "implementation",
  "correction",
  "habit-refactor",
  "structural-refactor",
  "baseline",
)
GATE_NAMES = ("initial", "public-checkpoint", "sonar", "final")
GATE_STATUSES = ("passed", "failed", "not-applicable")
HABIT_STATUSES = ("active", "curated", "frozen", "not-applicable")
CI_STATUSES = (
  "queued",
  "running",
  "passed",
  "code-failed",
  "environment-failed",
  "transient-failed",
  "retrying",
)
LEDGER_FIELDS = {
  "slug": str,
  "plan_path": str,
  "repository": str,
  "branch": str,
  "base": str,
  "phase": str,
  "chats": dict,
  "commits": list,
  "gates": dict,
  "history": list,
  "created_at": str,
  "updated_at": str,
}


def fields_match(record, schema):
  return isinstance(record, dict) and all(
    name in record and isinstance(record[name], expected_types)
    for name, expected_types in schema.items()
  )


def nested_records_are_valid(ledger):
  chats_valid = all(
    role in SPECIALISTS
    and fields_match(chat, {"thread_id": str, "model": str, "effort": str})
    and (chat["model"], chat["effort"]) == SPECIALISTS[role]
    for role, chat in ledger["chats"].items()
  )
  commits_valid = all(
    fields_match(
      commit,
      {"sha": str, "kind": str, "subject": str, "recorded_at": str},
    )
    and commit["kind"] in COMMIT_KINDS
    for commit in ledger["commits"]
  )
  gates_valid = all(
    name in GATE_NAMES
    and isinstance(attempts, list)
    and all(
      fields_match(
        attempt,
        {
          "status": str,
          "details": str,
          "url": (str, type(None)),
          "recorded_at": str,
        },
      )
      and attempt["status"] in GATE_STATUSES
      for attempt in attempts
    )
    for name, attempts in ledger["gates"].items()
  )
  history_valid = bool(ledger["history"]) and all(
    fields_match(event, {"at": str, "from": (str, type(None)), "to": str})
    and event["from"] in (None, *TRANSITIONS)
    and event["to"] in TRANSITIONS
    and ("note" not in event or isinstance(event["note"], str))
    for event in ledger["history"]
  )
  lease = ledger["checkout_lease"]
  lease_valid = lease is None or (
    fields_match(lease, {"owner": str, "acquired_at": str})
    and lease["owner"] in LEASE_OWNERS
  )
  habit = ledger["habit"]
  habit_valid = habit is None or (
    fields_match(
      habit,
      {
        "status": str,
        "details": str,
        "finding_count": int,
        "classified_count": int,
        "snoozed_until_changed": bool,
        "pruned": bool,
        "recorded_at": str,
      },
    )
    and habit["status"] in HABIT_STATUSES
    and ("history" not in habit or isinstance(habit["history"], list))
  )
  pull_request = ledger["pull_request"]
  pull_request_valid = pull_request is None or (
    fields_match(
      pull_request,
      {
        "repository": str,
        "number": int,
        "url": str,
        "status": str,
        "issue_reference": (str, type(None)),
        "labels": list,
        "recorded_at": str,
      },
    )
    and pull_request["status"] in ("OPEN", "CLOSED", "MERGED")
    and pull_request["issue_reference"] in (None, "see", "closes")
    and all(isinstance(label, str) for label in pull_request["labels"])
  )
  ci = ledger["ci"]
  ci_valid = ci is None or (
    fields_match(ci, {"events": list, "transient_retries": int, "status": str})
    and ci["status"] in CI_STATUSES
    and ci["transient_retries"] in (0, 1)
    and all(
      fields_match(
        event,
        {
          "status": str,
          "run_id": str,
          "url": str,
          "details": str,
          "recorded_at": str,
        },
      )
      and event["status"] in CI_STATUSES
      for event in ci["events"]
    )
  )
  return all(
    (
      chats_valid,
      commits_valid,
      gates_valid,
      history_valid,
      lease_valid,
      habit_valid,
      pull_request_valid,
      ci_valid,
    )
  )


def now():
  return datetime.now(timezone.utc).isoformat()


@contextmanager
def exclusive_ledger_transaction(path):
  lock_path = path.with_name(f".{path.name}.lock")
  descriptor = None
  try:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(lock_path, os.O_CREAT | os.O_RDWR, 0o600)
    fcntl.flock(descriptor, fcntl.LOCK_EX)
  except OSError as error:
    if descriptor is not None:
      os.close(descriptor)
    raise WorkflowError(f"Unable to lock ledger at {path}: {error}") from error
  try:
    yield
  finally:
    os.close(descriptor)


def write_atomic(path, value):
  descriptor = None
  temporary_path = None
  try:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
      dir=path.parent,
      prefix=f".{path.name}.",
      suffix=".tmp",
    )
    temporary_path = Path(temporary_name)
    stream = os.fdopen(descriptor, "w", encoding="utf-8")
    descriptor = None
    with stream:
      json.dump(value, stream, indent=2, sort_keys=True)
      stream.write("\n")
      stream.flush()
      os.fsync(stream.fileno())
    os.replace(temporary_path, path)
  except OSError as error:
    raise WorkflowError(f"Unable to write ledger at {path}: {error}") from error
  finally:
    if descriptor is not None:
      os.close(descriptor)
    if temporary_path is not None:
      temporary_path.unlink(missing_ok=True)


def load_ledger(path):
  try:
    with path.open(encoding="utf-8") as stream:
      ledger = json.load(stream)
  except (OSError, json.JSONDecodeError) as error:
    raise WorkflowError(f"Corrupt ledger at {path}: {error}") from error
  if not isinstance(ledger, dict) or ledger.get("schema_version") != 1:
    raise WorkflowError(f"Corrupt ledger at {path}: unsupported structure")
  invalid_fields = [
    name
    for name, expected_type in LEDGER_FIELDS.items()
    if not isinstance(ledger.get(name), expected_type)
  ]
  nullable_objects = ("habit", "pull_request", "ci", "checkout_lease")
  invalid_fields.extend(
    name
    for name in nullable_objects
    if name not in ledger or (ledger[name] is not None and not isinstance(ledger[name], dict))
  )
  if invalid_fields or ledger["phase"] not in TRANSITIONS:
    fields = ", ".join(sorted(set(invalid_fields))) or "phase"
    raise WorkflowError(f"Corrupt ledger at {path}: invalid fields: {fields}")
  if not nested_records_are_valid(ledger):
    raise WorkflowError(f"Corrupt ledger at {path}: invalid nested records")
  return ledger


def persist(args, ledger):
  ledger["updated_at"] = now()
  write_atomic(args.state, ledger)


def command_init(args):
  plan_path = Path(args.plan).resolve()
  repository = Path(args.repo).resolve()
  if args.state.exists():
    existing = load_ledger(args.state)
    identity = {
      "slug": args.slug,
      "plan_path": str(plan_path),
      "repository": str(repository),
      "branch": args.branch,
      "base": args.base,
    }
    if all(existing.get(key) == value for key, value in identity.items()):
      print(json.dumps(existing, sort_keys=True))
      return
    raise WorkflowError("State path already belongs to a different plan identity")
  timestamp = now()
  ledger = {
    "schema_version": 1,
    "slug": args.slug,
    "plan_path": str(plan_path),
    "repository": str(repository),
    "branch": args.branch,
    "base": args.base,
    "phase": "initialized",
    "chats": {},
    "commits": [],
    "gates": {},
    "habit": None,
    "pull_request": None,
    "ci": None,
    "checkout_lease": None,
    "history": [
      {
        "at": timestamp,
        "from": None,
        "to": "initialized",
      }
    ],
    "created_at": timestamp,
    "updated_at": timestamp,
  }
  write_atomic(args.state, ledger)
  print(json.dumps(ledger, sort_keys=True))


def command_show(args):
  print(json.dumps(load_ledger(args.state), indent=2, sort_keys=True))


def command_register_chat(args):
  ledger = load_ledger(args.state)
  required_model, required_effort = SPECIALISTS[args.role]
  if (args.model, args.effort) != (required_model, required_effort):
    raise WorkflowError(
      f"{args.role} requires {required_model} at {required_effort}; fallback is forbidden"
    )
  chat = {
    "thread_id": args.thread_id,
    "model": args.model,
    "effort": args.effort,
  }
  existing = ledger["chats"].get(args.role)
  if existing is not None and existing != chat:
    raise WorkflowError(f"{args.role} already has a different registered chat")
  if existing is None:
    ledger["chats"][args.role] = chat
    persist(args, ledger)
  print(json.dumps(chat, sort_keys=True))


def command_acquire(args):
  with exclusive_ledger_transaction(args.state):
    ledger = load_ledger(args.state)
    lease = ledger["checkout_lease"]
    if lease is not None and lease["owner"] != args.owner:
      raise WorkflowError(f"Checkout lease is held by {lease['owner']}")
    if lease is None:
      lease = {"owner": args.owner, "acquired_at": now()}
      ledger["checkout_lease"] = lease
      persist(args, ledger)
  print(json.dumps(lease, sort_keys=True))


def command_release(args):
  ledger = load_ledger(args.state)
  lease = ledger["checkout_lease"]
  if lease is not None and lease["owner"] != args.owner:
    raise WorkflowError(f"Checkout lease is held by {lease['owner']}")
  if lease is not None:
    ledger["checkout_lease"] = None
    persist(args, ledger)
  print(json.dumps({"released": args.owner}, sort_keys=True))


def command_transition(args):
  ledger = load_ledger(args.state)
  current = ledger["phase"]
  if args.to == current:
    previous = ledger["history"][-1]
    if previous.get("note") != args.note:
      raise WorkflowError(f"Transition to {args.to} already recorded with different details")
    print(json.dumps(previous, sort_keys=True))
    return
  if args.to not in TRANSITIONS.get(current, set()):
    raise WorkflowError(f"Invalid transition from {current} to {args.to}")
  if args.to == "structural-review":
    checkpoints = ledger["gates"].get("public-checkpoint", [])
    if not checkpoints or checkpoints[-1]["status"] != "passed":
      raise WorkflowError("Structural review requires a passed public-checkpoint gate")
  timestamp = now()
  ledger["phase"] = args.to
  event = {"at": timestamp, "from": current, "to": args.to}
  if args.note:
    event["note"] = args.note
  ledger["history"].append(event)
  persist(args, ledger)
  print(json.dumps(event, sort_keys=True))


def require_lease(ledger, owner):
  lease = ledger["checkout_lease"]
  if lease is None or lease["owner"] != owner:
    held_by = "nobody" if lease is None else lease["owner"]
    raise WorkflowError(f"Operation requires checkout lease for {owner}; held by {held_by}")


def command_record_commit(args):
  ledger = load_ledger(args.state)
  require_lease(ledger, "committer")
  commit = {
    "sha": args.sha,
    "kind": args.kind,
    "subject": args.subject,
  }
  existing = next((item for item in ledger["commits"] if item["sha"] == args.sha), None)
  if existing is not None:
    comparable = {key: existing[key] for key in commit}
    if comparable != commit:
      raise WorkflowError(f"Commit {args.sha} already recorded with different details")
    print(json.dumps(existing, sort_keys=True))
    return
  commit["recorded_at"] = now()
  ledger["commits"].append(commit)
  persist(args, ledger)
  print(json.dumps(commit, sort_keys=True))


def command_record_gate(args):
  ledger = load_ledger(args.state)
  require_lease(ledger, "validator")
  gate = {
    "status": args.status,
    "details": args.details,
    "url": args.url,
  }
  attempts = ledger["gates"].setdefault(args.name, [])
  if attempts:
    comparable = {key: attempts[-1].get(key) for key in gate}
    if comparable == gate:
      print(json.dumps(attempts[-1], sort_keys=True))
      return
  gate["recorded_at"] = now()
  attempts.append(gate)
  persist(args, ledger)
  print(json.dumps(gate, sort_keys=True))


def command_record_habit(args):
  ledger = load_ledger(args.state)
  require_lease(ledger, "habit-curator")
  if args.status == "frozen":
    if args.finding_count != args.classified_count:
      raise WorkflowError("Habit freeze requires every finding to be classified")
    if not args.snoozed_until_changed or not args.pruned:
      raise WorkflowError("Habit freeze requires until-changed snooze and prune evidence")
  record = {
    "status": args.status,
    "details": args.details,
    "finding_count": args.finding_count,
    "classified_count": args.classified_count,
    "snoozed_until_changed": args.snoozed_until_changed,
    "pruned": args.pruned,
  }
  current = ledger["habit"]
  if current is not None:
    comparable = {key: current.get(key) for key in record}
    if comparable == record:
      print(json.dumps(current, sort_keys=True))
      return
    history = current.get("history", []) + [
      {key: value for key, value in current.items() if key != "history"}
    ]
  else:
    history = []
  record["recorded_at"] = now()
  if history:
    record["history"] = history
  ledger["habit"] = record
  persist(args, ledger)
  print(json.dumps(record, sort_keys=True))


def command_record_pr(args):
  ledger = load_ledger(args.state)
  final_gates = ledger["gates"].get("final", [])
  if not final_gates or final_gates[-1]["status"] != "passed":
    raise WorkflowError("Pull request creation requires a passed final gate")
  if ledger["phase"] != "baseline-committed":
    raise WorkflowError("Pull request creation requires the baseline-committed phase")
  habit = ledger["habit"]
  if habit is None or habit["status"] not in ("frozen", "not-applicable"):
    raise WorkflowError(
      "Pull request creation requires Habit evidence marked frozen or not-applicable"
    )
  if not any(commit["kind"] == "baseline" for commit in ledger["commits"]):
    raise WorkflowError("Pull request creation requires a recorded baseline commit")
  require_lease(ledger, "coordinator")
  pull_request = {
    "repository": args.repo,
    "number": args.number,
    "url": args.url,
    "status": args.status,
    "issue_reference": args.issue_reference,
    "labels": sorted(args.label),
  }
  existing = ledger["pull_request"]
  if existing is not None:
    comparable = {key: existing.get(key) for key in pull_request}
    if comparable != pull_request:
      raise WorkflowError("A different pull request is already recorded")
    print(json.dumps(existing, sort_keys=True))
    return
  pull_request["recorded_at"] = now()
  ledger["pull_request"] = pull_request
  persist(args, ledger)
  print(json.dumps(pull_request, sort_keys=True))


def command_record_ci(args):
  ledger = load_ledger(args.state)
  if ledger["pull_request"] is None:
    raise WorkflowError("CI cannot be recorded before a pull request")
  ci = ledger["ci"] or {"events": [], "transient_retries": 0}
  candidate = {
    "status": args.status,
    "run_id": args.run_id,
    "url": args.url,
    "details": args.details,
  }
  existing = next(
    (
      event
      for event in ci["events"]
      if all(event.get(key) == value for key, value in candidate.items())
    ),
    None,
  )
  if existing is not None:
    print(json.dumps(existing, sort_keys=True))
    return
  if args.status == "retrying":
    if ci["transient_retries"] >= 1:
      raise WorkflowError("Only one transient retry is allowed")
    if not ci["events"] or ci["events"][-1]["status"] != "transient-failed":
      raise WorkflowError("A retry requires a recorded transient failure")
    ci["transient_retries"] += 1
  candidate["recorded_at"] = now()
  ci["events"].append(candidate)
  ci["status"] = args.status
  ledger["ci"] = ci
  persist(args, ledger)
  print(json.dumps(candidate, sort_keys=True))


def command_cleanup(args):
  if args.github_status != "MERGED":
    raise WorkflowError("Cleanup requires an unambiguous GitHub MERGED status")
  ledger = load_ledger(args.state)
  pull_request = ledger["pull_request"]
  if pull_request is None:
    raise WorkflowError("Cleanup requires a recorded pull request")
  if args.repo != pull_request["repository"] or args.number != pull_request["number"]:
    raise WorkflowError("GitHub confirmation does not match the recorded pull request")
  state_path = args.state.resolve()
  plan_path = Path(ledger["plan_path"]).resolve()
  expected_plan = state_path.parent / f"{ledger['slug']}.md"
  if plan_path != expected_plan:
    raise WorkflowError("Cleanup refused an unexpected plan path")
  plan_path.unlink(missing_ok=True)
  state_path.unlink()
  print(json.dumps({"cleaned": [str(plan_path), str(state_path)]}, sort_keys=True))


def build_parser():
  parser = argparse.ArgumentParser(description="Guard an approved-plan workflow ledger.")
  parser.add_argument("--state", required=True, type=Path)
  subparsers = parser.add_subparsers(dest="command", required=True)

  initialize = subparsers.add_parser("init")
  initialize.add_argument("--slug", required=True)
  initialize.add_argument("--plan", required=True)
  initialize.add_argument("--repo", required=True)
  initialize.add_argument("--branch", required=True)
  initialize.add_argument("--base", required=True)
  initialize.set_defaults(handler=command_init)

  show = subparsers.add_parser("show")
  show.set_defaults(handler=command_show)

  register_chat = subparsers.add_parser("register-chat")
  register_chat.add_argument("--role", required=True, choices=sorted(SPECIALISTS))
  register_chat.add_argument("--thread-id", required=True)
  register_chat.add_argument("--model", required=True)
  register_chat.add_argument("--effort", required=True)
  register_chat.set_defaults(handler=command_register_chat)

  acquire = subparsers.add_parser("acquire")
  acquire.add_argument("--owner", required=True, choices=LEASE_OWNERS)
  acquire.set_defaults(handler=command_acquire)

  release = subparsers.add_parser("release")
  release.add_argument("--owner", required=True, choices=LEASE_OWNERS)
  release.set_defaults(handler=command_release)

  transition = subparsers.add_parser("transition")
  transition.add_argument("--to", required=True, choices=sorted(TRANSITIONS))
  transition.add_argument("--note")
  transition.set_defaults(handler=command_transition)

  record_commit = subparsers.add_parser("record-commit")
  record_commit.add_argument("--sha", required=True)
  record_commit.add_argument("--kind", required=True, choices=COMMIT_KINDS)
  record_commit.add_argument("--subject", required=True)
  record_commit.set_defaults(handler=command_record_commit)

  record_gate = subparsers.add_parser("record-gate")
  record_gate.add_argument("--name", required=True, choices=GATE_NAMES)
  record_gate.add_argument("--status", required=True, choices=GATE_STATUSES)
  record_gate.add_argument("--details", required=True)
  record_gate.add_argument("--url")
  record_gate.set_defaults(handler=command_record_gate)

  record_habit = subparsers.add_parser("record-habit")
  record_habit.add_argument("--status", required=True, choices=HABIT_STATUSES)
  record_habit.add_argument("--details", required=True)
  record_habit.add_argument("--finding-count", type=int, default=0)
  record_habit.add_argument("--classified-count", type=int, default=0)
  record_habit.add_argument("--snoozed-until-changed", action="store_true")
  record_habit.add_argument("--pruned", action="store_true")
  record_habit.set_defaults(handler=command_record_habit)

  record_pr = subparsers.add_parser("record-pr")
  record_pr.add_argument("--repo", required=True)
  record_pr.add_argument("--number", required=True, type=int)
  record_pr.add_argument("--url", required=True)
  record_pr.add_argument("--status", required=True, choices=("OPEN", "CLOSED", "MERGED"))
  record_pr.add_argument("--issue-reference", choices=("see", "closes"))
  record_pr.add_argument("--label", action="append", default=[])
  record_pr.set_defaults(handler=command_record_pr)

  record_ci = subparsers.add_parser("record-ci")
  record_ci.add_argument("--status", required=True, choices=CI_STATUSES)
  record_ci.add_argument("--run-id", required=True)
  record_ci.add_argument("--url", required=True)
  record_ci.add_argument("--details", required=True)
  record_ci.set_defaults(handler=command_record_ci)

  cleanup = subparsers.add_parser("cleanup")
  cleanup.add_argument("--github-status", required=True)
  cleanup.add_argument("--repo")
  cleanup.add_argument("--number", type=int)
  cleanup.set_defaults(handler=command_cleanup)
  return parser


def main():
  args = build_parser().parse_args()
  try:
    args.handler(args)
  except WorkflowError as error:
    print(f"error: {error}", file=sys.stderr)
    return 2
  return 0


if __name__ == "__main__":
  sys.exit(main())
