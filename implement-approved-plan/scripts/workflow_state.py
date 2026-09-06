#!/usr/bin/env python3

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import json
import os
from pathlib import Path
import re
import sys
import tempfile


class WorkflowError(Exception):
  pass


SPECIALISTS_BY_SCHEMA = {
  1: {
    "implementer": ("gpt-5.6-sol", "xhigh"),
    "committer": ("gpt-5.6-terra", "xhigh"),
    "validator": ("gpt-5.6-luna", "xhigh"),
    "habit-curator": ("gpt-5.6-sol", "xhigh"),
    "structural-reviewer": ("gpt-5.6-sol", "xhigh"),
  },
  2: {
    "implementer": ("gpt-5.6-sol", "xhigh"),
    "committer": ("gpt-5.6-terra", "xhigh"),
    "validator": ("gpt-5.6-luna", "xhigh"),
    "habit-curator": ("gpt-5.6-luna", "xhigh"),
    "structural-reviewer": ("gpt-5.6-sol", "xhigh"),
  },
  3: {
    "implementer": ("gpt-5.6-sol", "xhigh"),
    "committer": ("gpt-5.6-terra", "xhigh"),
    "validator": ("gpt-5.6-luna", "xhigh"),
    "habit-curator": ("gpt-5.6-luna", "xhigh"),
    "mutation-analyst": ("gpt-5.6-luna", "xhigh"),
    "structural-reviewer": ("gpt-5.6-sol", "xhigh"),
  },
}
SPECIALIST_ROLES = tuple(
  sorted({role for specialists in SPECIALISTS_BY_SCHEMA.values() for role in specialists})
)
LEASE_OWNERS = ("coordinator", *SPECIALIST_ROLES)
V1_TRANSITIONS = {
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
V2_TRANSITIONS = {
  "initialized": {"implementing"},
  "implementing": {"implemented"},
  "implemented": {"habit-checking"},
  "habit-checking": {"checkpoint-committing", "implementing"},
  "checkpoint-committing": {"initial-validating", "implementing"},
  "initial-validating": {"structural-review", "implementing"},
  "structural-review": {"habit-rechecking", "implementing"},
  "habit-rechecking": {
    "final-committing",
    "final-validating",
    "implementing",
    "structural-review",
  },
  "final-committing": {"final-validating", "implementing"},
  "final-validating": {
    "delivery-ready",
    "implementing",
    "habit-rechecking",
    "structural-review",
  },
  "delivery-ready": {"pr-open"},
  "pr-open": {"ci-monitoring"},
  "ci-monitoring": {"ready-for-merge", "implementing"},
  "ready-for-merge": {"merged"},
  "merged": set(),
}
V3_TRANSITIONS = {
  "initialized": {"implementing"},
  "implementing": {"implemented"},
  "implemented": {"habit-checking"},
  "habit-checking": {"checkpoint-committing", "implementing"},
  "checkpoint-committing": {"initial-validating", "implementing"},
  "initial-validating": {"mutation-testing", "implementing"},
  "mutation-testing": {"structural-review", "implementing"},
  "structural-review": {"habit-rechecking", "implementing"},
  "habit-rechecking": {
    "final-committing",
    "final-validating",
    "implementing",
  },
  "final-committing": {"final-validating", "implementing"},
  "final-validating": {
    "mutation-rechecking",
    "implementing",
  },
  "mutation-rechecking": {"delivery-ready", "implementing"},
  "delivery-ready": {"pr-open"},
  "pr-open": {"ci-monitoring"},
  "ci-monitoring": {"ready-for-merge", "implementing"},
  "ready-for-merge": {"merged"},
  "merged": set(),
}
V2_CORRECTIVE_TRANSITIONS = {
  ("habit-checking", "implementing"),
  ("checkpoint-committing", "implementing"),
  ("initial-validating", "implementing"),
  ("structural-review", "implementing"),
  ("habit-rechecking", "implementing"),
  ("habit-rechecking", "structural-review"),
  ("final-committing", "implementing"),
  ("final-validating", "implementing"),
  ("final-validating", "habit-rechecking"),
  ("final-validating", "structural-review"),
  ("ci-monitoring", "implementing"),
}
V3_CORRECTIVE_TRANSITIONS = {
  ("habit-checking", "implementing"),
  ("checkpoint-committing", "implementing"),
  ("initial-validating", "implementing"),
  ("mutation-testing", "implementing"),
  ("structural-review", "implementing"),
  ("habit-rechecking", "implementing"),
  ("final-committing", "implementing"),
  ("final-validating", "implementing"),
  ("mutation-rechecking", "implementing"),
  ("ci-monitoring", "implementing"),
}
CORRECTIVE_TRANSITIONS_BY_SCHEMA = {
  2: V2_CORRECTIVE_TRANSITIONS,
  3: V3_CORRECTIVE_TRANSITIONS,
}
TRANSITIONS_BY_SCHEMA = {1: V1_TRANSITIONS, 2: V2_TRANSITIONS, 3: V3_TRANSITIONS}
ALL_PHASES = tuple(
  sorted(V1_TRANSITIONS.keys() | V2_TRANSITIONS.keys() | V3_TRANSITIONS.keys())
)
COMMIT_KINDS = (
  "implementation",
  "correction",
  "habit-refactor",
  "structural-refactor",
  "baseline",
)
V1_GATE_NAMES = ("initial", "public-checkpoint", "sonar", "final")
V2_GATE_NAMES = (
  "initial-verify",
  "initial-sonar",
  "final-verify",
  "final-sonar",
)
GATE_NAMES_BY_SCHEMA = {1: V1_GATE_NAMES, 2: V2_GATE_NAMES, 3: V2_GATE_NAMES}
ALL_GATE_NAMES = tuple(sorted(set(V1_GATE_NAMES + V2_GATE_NAMES)))
GATE_STATUSES = ("passed", "failed", "not-applicable")
V1_HABIT_STATUSES = ("active", "curated", "frozen", "not-applicable")
V2_HABIT_STATUSES = ("clean", "ratcheted", "snoozed", "not-applicable")
ALL_HABIT_STATUSES = tuple(sorted(set(V1_HABIT_STATUSES + V2_HABIT_STATUSES)))
HABIT_OBSERVATION_KINDS = ("no-configured-files",)
MUTATION_RESULTS = ("passed", "failed", "not-applicable", "reused")
MUTATION_OUTCOMES = ("survived", "no-coverage")
MUTATION_CLASSIFICATIONS = (
  "behavior-gap",
  "dead-code",
  "redundant-code",
  "equivalent",
)
ACTIONABLE_MUTATION_CLASSIFICATIONS = (
  "behavior-gap",
  "dead-code",
  "redundant-code",
)
MUTATION_NOT_APPLICABLE_REASONS = (
  "runner-unavailable",
  "no-production-changes",
)
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
  specialists = SPECIALISTS_BY_SCHEMA[ledger["schema_version"]]
  transitions = TRANSITIONS_BY_SCHEMA[ledger["schema_version"]]
  chats_valid = all(
    role in specialists
    and fields_match(chat, {"thread_id": str, "model": str, "effort": str})
    and (chat["model"], chat["effort"]) == specialists[role]
    for role, chat in ledger["chats"].items()
  )
  commits_valid = all(
    fields_match(
      commit,
      {"sha": str, "kind": str, "subject": str, "recorded_at": str},
    )
    and commit["kind"] in COMMIT_KINDS
    and (
      ledger["schema_version"] == 1
      or (
        fields_match(commit, {"phase": str})
        and commit["phase"] in ("checkpoint-committing", "final-committing")
      )
    )
    for commit in ledger["commits"]
  )
  gates_valid = all(
    name in GATE_NAMES_BY_SCHEMA[ledger["schema_version"]]
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
      and (
        ledger["schema_version"] == 1
        or (
          fields_match(attempt, {"phase": str})
          and attempt["phase"]
          in ("initial-validating", "final-validating")
        )
      )
      for attempt in attempts
    )
    for name, attempts in ledger["gates"].items()
  )
  history = ledger["history"]
  history_valid = (
    bool(history)
    and all(
      fields_match(event, {"at": str, "from": (str, type(None)), "to": str})
      and event["from"] in (None, *transitions)
      and event["to"] in transitions
      and ("note" not in event or isinstance(event["note"], str))
      for event in history
    )
    and history[0]["from"] is None
    and history[0]["to"] == "initialized"
    and all(
      current["from"] == previous["to"]
      and current["to"] in transitions[current["from"]]
      for previous, current in zip(history, history[1:])
    )
    and ledger["phase"] == history[-1]["to"]
  )
  lease = ledger["checkout_lease"]
  lease_valid = lease is None or (
    fields_match(lease, {"owner": str, "acquired_at": str})
    and lease["owner"]
    in ("coordinator", *SPECIALISTS_BY_SCHEMA[ledger["schema_version"]])
  )
  habit = ledger["habit"]
  if ledger["schema_version"] == 1:
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
      and habit["status"] in V1_HABIT_STATUSES
      and ("history" not in habit or isinstance(habit["history"], list))
    )
  else:
    habit_valid = habit is None or (
      fields_match(
        habit,
        {
          "status": str,
          "details": str,
          "finding_count": int,
          "stage": str,
          "recorded_at": str,
        },
      )
      and habit["status"] in V2_HABIT_STATUSES
      and habit["stage"] in ("quick", "final")
      and habit["finding_count"] >= 0
      and (
        habit["status"] != "clean" or habit["finding_count"] == 0
      )
      and (
        habit["status"] != "ratcheted"
        or (
          fields_match(
            habit,
            {
              "active_finding_count": int,
              "baseline_authorized": bool,
              "baseline_unchanged": bool,
            },
          )
          and habit["active_finding_count"] == 0
          and habit["baseline_authorized"]
          and habit["baseline_unchanged"]
        )
      )
      and (
        habit["status"] != "snoozed"
        or (
          fields_match(habit, {"user_authorized_snooze": bool})
          and habit["user_authorized_snooze"]
        )
      )
      and (
        habit["status"] != "not-applicable"
        or (
          fields_match(habit, {"tool_unavailable": bool})
          and habit["tool_unavailable"]
        )
      )
      and ("history" not in habit or isinstance(habit["history"], list))
    )
  habit_observations = ledger.get("habit_observations", [])
  habit_observations_valid = ledger["schema_version"] == 1 or (
    isinstance(habit_observations, list)
    and all(
      fields_match(
        observation,
        {
          "kind": str,
          "details": str,
          "stage": str,
          "reclassified_habit": (dict, type(None)),
          "recorded_at": str,
        },
      )
      and observation["kind"] in HABIT_OBSERVATION_KINDS
      and observation["stage"] == "quick"
      for observation in habit_observations
    )
  )
  mutation_attempts = ledger.get("mutation_attempts", [])
  mutation_attempts_valid = ledger["schema_version"] in (1, 2) or (
    mutation_attempts_are_valid(mutation_attempts)
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
      habit_observations_valid,
      mutation_attempts_valid,
      pull_request_valid,
      ci_valid,
    )
  )


def mutation_attempt_is_valid(attempt):
  if not fields_match(
    attempt,
    {
      "stage": str,
      "result": str,
      "runner": str,
      "analyzed_sha": str,
      "fingerprint": str,
      "target_classes": list,
      "metrics": dict,
      "classifications": list,
      "actionable_findings": int,
      "classification_path": (str, type(None)),
      "log_path": str,
      "report_paths": list,
      "details": str,
      "not_applicable_reason": (str, type(None)),
      "failure_kind": (str, type(None)),
      "reused_from_sha": (str, type(None)),
      "reused_from_fingerprint": (str, type(None)),
      "recorded_at": str,
    },
  ):
    return False
  metrics = attempt["metrics"]
  required_metrics = (
    "generated",
    "killed",
    "survived",
    "no_coverage",
    "execution_errors",
  )
  classifications = attempt["classifications"]
  classifications_valid = all(
    mutation_classification_is_valid(item) for item in classifications
  )
  outcome_counts = {
    outcome: sum(item.get("outcome") == outcome for item in classifications)
    for outcome in MUTATION_OUTCOMES
  }
  actionable_findings = sum(
    item.get("classification") in ACTIONABLE_MUTATION_CLASSIFICATIONS
    for item in classifications
  )
  return all(
    (
      attempt["stage"] in ("initial", "final"),
      attempt["result"] in MUTATION_RESULTS,
      bool(attempt["runner"].strip()),
      re.fullmatch(r"[0-9a-f]{40}", attempt["analyzed_sha"]) is not None,
      re.fullmatch(r"[0-9a-f]{64}", attempt["fingerprint"]) is not None,
      all(isinstance(target, str) and target for target in attempt["target_classes"]),
      all(
        name in metrics
        and isinstance(metrics[name], int)
        and not isinstance(metrics[name], bool)
        and metrics[name] >= 0
        for name in required_metrics
      ),
      classifications_valid,
      attempt["result"] == "failed"
      or outcome_counts["survived"] == metrics.get("survived"),
      attempt["result"] == "failed"
      or outcome_counts["no-coverage"] == metrics.get("no_coverage"),
      attempt["actionable_findings"] == actionable_findings,
      all(isinstance(path, str) and path for path in attempt["report_paths"]),
      attempt["result"] != "passed"
      or (
        attempt["actionable_findings"] == 0
        and metrics.get("execution_errors") == 0
        and metrics.get("generated")
        == sum(
          metrics.get(name, 0) for name in ("killed", "survived", "no_coverage")
        )
        and bool(attempt["target_classes"])
        and bool(attempt["report_paths"])
      ),
      attempt["result"] != "not-applicable"
      or attempt["not_applicable_reason"] in MUTATION_NOT_APPLICABLE_REASONS,
      attempt["result"] != "failed" or attempt["failure_kind"] == "environmental",
      attempt["result"] != "reused"
      or (
        attempt["stage"] == "final"
        and attempt["reused_from_sha"] is not None
        and attempt["reused_from_fingerprint"] is not None
      ),
    )
  )


def mutation_attempts_are_valid(attempts):
  if not isinstance(attempts, list):
    return False
  latest_accepted_initial = None
  reused_fields = (
    "runner",
    "fingerprint",
    "target_classes",
    "metrics",
    "classifications",
    "actionable_findings",
    "classification_path",
    "report_paths",
    "not_applicable_reason",
  )
  for attempt in attempts:
    if not mutation_attempt_is_valid(attempt):
      return False
    if attempt["stage"] == "initial" and attempt["result"] in (
      "passed",
      "not-applicable",
    ):
      latest_accepted_initial = attempt
    if attempt["result"] == "reused":
      if latest_accepted_initial is None:
        return False
      if (
        attempt["reused_from_sha"] != latest_accepted_initial["analyzed_sha"]
        or attempt["reused_from_fingerprint"]
        != latest_accepted_initial["fingerprint"]
        or any(
          attempt[field] != latest_accepted_initial[field]
          for field in reused_fields
        )
      ):
        return False
  return True


def mutation_classification_is_valid(classification):
  return (
    fields_match(
      classification,
      {
        "mutant_id": str,
        "outcome": str,
        "classification": str,
        "justification": str,
      },
    )
    and bool(classification["mutant_id"].strip())
    and classification["outcome"] in MUTATION_OUTCOMES
    and classification["classification"] in MUTATION_CLASSIFICATIONS
    and bool(classification["justification"].strip())
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
  if not isinstance(ledger, dict) or ledger.get("schema_version") not in (1, 2, 3):
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
  transitions = TRANSITIONS_BY_SCHEMA[ledger["schema_version"]]
  if ledger["schema_version"] == 3:
    if (
      not isinstance(ledger.get("base_sha"), str)
      or re.fullmatch(r"[0-9a-f]{40}", ledger["base_sha"]) is None
    ):
      invalid_fields.append("base_sha")
    if not isinstance(ledger.get("mutation_attempts"), list):
      invalid_fields.append("mutation_attempts")
  if invalid_fields or ledger["phase"] not in transitions:
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
  if not re.fullmatch(r"[0-9a-fA-F]{40}", args.base_sha):
    raise WorkflowError("Schema v3 requires a full 40-character hexadecimal base SHA")
  base_sha = args.base_sha.lower()
  if args.state.exists():
    existing = load_ledger(args.state)
    identity = {
      "slug": args.slug,
      "plan_path": str(plan_path),
      "repository": str(repository),
      "branch": args.branch,
      "base": args.base,
      "base_sha": base_sha,
    }
    if all(existing.get(key) == value for key, value in identity.items()):
      print(json.dumps(existing, sort_keys=True))
      return
    raise WorkflowError("State path already belongs to a different plan identity")
  timestamp = now()
  ledger = {
    "schema_version": 3,
    "slug": args.slug,
    "plan_path": str(plan_path),
    "repository": str(repository),
    "branch": args.branch,
    "base": args.base,
    "base_sha": base_sha,
    "phase": "initialized",
    "chats": {},
    "commits": [],
    "gates": {},
    "habit": None,
    "habit_observations": [],
    "mutation_attempts": [],
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
  if args.role not in SPECIALISTS_BY_SCHEMA[ledger["schema_version"]]:
    raise WorkflowError(
      f"Role {args.role} is not supported by schema v{ledger['schema_version']}"
    )
  required_model, required_effort = SPECIALISTS_BY_SCHEMA[ledger["schema_version"]][
    args.role
  ]
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
    if args.owner not in (
      "coordinator",
      *SPECIALISTS_BY_SCHEMA[ledger["schema_version"]],
    ):
      raise WorkflowError(
        f"Lease owner {args.owner} is not supported by schema "
        f"v{ledger['schema_version']}"
      )
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
  if args.owner not in (
    "coordinator",
    *SPECIALISTS_BY_SCHEMA[ledger["schema_version"]],
  ):
    raise WorkflowError(
      f"Lease owner {args.owner} is not supported by schema v{ledger['schema_version']}"
    )
  lease = ledger["checkout_lease"]
  if lease is not None and lease["owner"] != args.owner:
    raise WorkflowError(f"Checkout lease is held by {lease['owner']}")
  if lease is not None:
    ledger["checkout_lease"] = None
    persist(args, ledger)
  print(json.dumps({"released": args.owner}, sort_keys=True))


def command_transition(args):
  ledger = load_ledger(args.state)
  transitions = TRANSITIONS_BY_SCHEMA[ledger["schema_version"]]
  current = ledger["phase"]
  if args.to == current:
    previous = ledger["history"][-1]
    if previous.get("note") != args.note:
      raise WorkflowError(f"Transition to {args.to} already recorded with different details")
    print(json.dumps(previous, sort_keys=True))
    return
  if args.to not in transitions.get(current, set()):
    raise WorkflowError(f"Invalid transition from {current} to {args.to}")
  if (
    ledger["schema_version"] in (2, 3)
    and (current, args.to)
    in CORRECTIVE_TRANSITIONS_BY_SCHEMA[ledger["schema_version"]]
    and (args.note is None or not args.note.strip())
  ):
    raise WorkflowError(
      "Corrective transition requires a Coordinator authorization note"
    )
  if ledger["schema_version"] in (2, 3) and args.to == "implementing":
    require_registered_specialists(ledger)
  if (
    ledger["schema_version"] in (2, 3)
    and current == "habit-checking"
    and args.to == "checkpoint-committing"
  ):
    require_current_quick_habit_evidence(ledger)
  if (
    ledger["schema_version"] in (2, 3)
    and current == "checkpoint-committing"
    and args.to == "initial-validating"
  ):
    require_current_commit(ledger, "checkpoint-committing", "checkpoint")
  if (
    ledger["schema_version"] in (2, 3)
    and current == "habit-rechecking"
    and args.to in ("final-committing", "final-validating")
  ):
    require_current_habit_evidence(ledger, "final")
  if (
    ledger["schema_version"] in (2, 3)
    and current == "final-committing"
    and args.to == "final-validating"
  ):
    require_current_commit(ledger, "final-committing", "final delta")
  if ledger["schema_version"] == 1 and args.to == "structural-review":
    checkpoints = ledger["gates"].get("public-checkpoint", [])
    if not checkpoints or checkpoints[-1]["status"] != "passed":
      raise WorkflowError("Structural review requires a passed public-checkpoint gate")
  if (
    ledger["schema_version"] == 2
    and current == "initial-validating"
    and args.to == "structural-review"
  ):
    require_current_gates(
      ledger,
      ("initial-verify", "initial-sonar"),
      "initial-validating",
    )
  if (
    ledger["schema_version"] == 3
    and current == "initial-validating"
    and args.to == "mutation-testing"
  ):
    require_current_gates(
      ledger,
      ("initial-verify", "initial-sonar"),
      "initial-validating",
    )
  if (
    ledger["schema_version"] == 3
    and current == "mutation-testing"
    and args.to == "structural-review"
  ):
    require_current_mutation_evidence(ledger, "initial")
  if (
    ledger["schema_version"] == 2
    and current == "final-validating"
    and args.to == "delivery-ready"
  ):
    require_current_gates(
      ledger,
      ("final-verify", "final-sonar"),
      "final-validating",
    )
  if (
    ledger["schema_version"] == 3
    and current == "final-validating"
    and args.to == "mutation-rechecking"
  ):
    require_current_gates(
      ledger,
      ("final-verify", "final-sonar"),
      "final-validating",
    )
  if (
    ledger["schema_version"] == 3
    and current == "mutation-rechecking"
    and args.to == "delivery-ready"
  ):
    require_current_mutation_evidence(ledger, "final")
  if (
    ledger["schema_version"] in (2, 3)
    and current == "ci-monitoring"
    and args.to == "ready-for-merge"
  ):
    require_current_passed_ci(ledger)
  timestamp = now()
  ledger["phase"] = args.to
  event = {"at": timestamp, "from": current, "to": args.to}
  if args.note:
    event["note"] = args.note
  ledger["history"].append(event)
  persist(args, ledger)
  print(json.dumps(event, sort_keys=True))


def require_registered_specialists(ledger):
  invalid_roles = [
    role
    for role in SPECIALISTS_BY_SCHEMA[ledger["schema_version"]]
    if role not in ledger["chats"] or not ledger["chats"][role]["thread_id"].strip()
  ]
  if invalid_roles:
    roles = ", ".join(invalid_roles)
    raise WorkflowError(
      "Implementation requires registered specialist chats with non-empty "
      f"thread IDs: {roles}"
    )


def require_current_habit_evidence(ledger, stage):
  habit = ledger["habit"]
  if (
    habit is None
    or habit["stage"] != stage
    or habit["recorded_at"] < ledger["history"][-1]["at"]
  ):
    raise WorkflowError(f"Transition requires current {stage} Habit evidence")


def require_current_quick_habit_evidence(ledger):
  habit = ledger["habit"]
  phase_started_at = ledger["history"][-1]["at"]
  terminal_evidence = (
    habit is not None
    and habit["stage"] == "quick"
    and habit["recorded_at"] >= phase_started_at
  )
  observations = ledger.get("habit_observations", [])
  scoped_observation = bool(observations) and (
    observations[-1]["stage"] == "quick"
    and observations[-1]["recorded_at"] >= phase_started_at
  )
  if not terminal_evidence and not scoped_observation:
    raise WorkflowError("Transition requires current quick Habit evidence")


def require_current_commit(ledger, phase, label):
  phase_started_at = ledger["history"][-1]["at"]
  if not any(
    commit.get("phase") == phase and commit["recorded_at"] >= phase_started_at
    for commit in ledger["commits"]
  ):
    raise WorkflowError(f"Transition requires a current {label} commit")


def require_current_gates(ledger, names, phase):
  phase_started_at = next(
    event["at"] for event in reversed(ledger["history"]) if event["to"] == phase
  )
  missing = []
  for name in names:
    attempts = ledger["gates"].get(name, [])
    if (
      not attempts
      or attempts[-1].get("phase") != phase
      or attempts[-1]["status"] != "passed"
      or attempts[-1]["recorded_at"] < phase_started_at
    ):
      missing.append(name)
  if missing:
    raise WorkflowError(f"Transition requires passed current gates: {', '.join(missing)}")


def require_current_passed_ci(ledger):
  ci = ledger["ci"]
  phase_started_at = ledger["history"][-1]["at"]
  if (
    ci is None
    or ci["status"] != "passed"
    or not ci["events"]
    or ci["events"][-1]["recorded_at"] < phase_started_at
  ):
    raise WorkflowError("Transition requires current passed CI evidence")


def require_current_mutation_evidence(ledger, stage):
  attempts = ledger["mutation_attempts"]
  phase = "mutation-testing" if stage == "initial" else "mutation-rechecking"
  phase_started_at = next(
    event["at"] for event in reversed(ledger["history"]) if event["to"] == phase
  )
  if (
    not attempts
    or attempts[-1]["stage"] != stage
    or attempts[-1]["result"] not in ("passed", "reused", "not-applicable")
    or attempts[-1]["recorded_at"] < phase_started_at
  ):
    raise WorkflowError(
      f"Transition requires accepted current {stage} mutation evidence"
    )


def require_lease(ledger, owner):
  lease = ledger["checkout_lease"]
  if lease is None or lease["owner"] != owner:
    held_by = "nobody" if lease is None else lease["owner"]
    raise WorkflowError(f"Operation requires checkout lease for {owner}; held by {held_by}")


def command_record_commit(args):
  ledger = load_ledger(args.state)
  require_lease(ledger, "committer")
  if ledger["schema_version"] in (2, 3):
    allowed_kinds_by_phase = {
      "checkpoint-committing": ("implementation", "correction"),
      "final-committing": (
        "correction",
        "habit-refactor",
        "structural-refactor",
      ),
    }
    if args.kind not in allowed_kinds_by_phase.get(ledger["phase"], ()):
      raise WorkflowError(
        f"Commit kind {args.kind} is not allowed during {ledger['phase']}"
      )
  commit = {
    "sha": args.sha,
    "kind": args.kind,
    "subject": args.subject,
  }
  if ledger["schema_version"] in (2, 3):
    commit["phase"] = ledger["phase"]
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
  if args.name not in GATE_NAMES_BY_SCHEMA[ledger["schema_version"]]:
    raise WorkflowError(
      f"Gate {args.name} is not supported by schema v{ledger['schema_version']}"
    )
  if ledger["schema_version"] in (2, 3):
    required_phase = (
      "initial-validating" if args.name.startswith("initial-") else "final-validating"
    )
    if ledger["phase"] != required_phase:
      raise WorkflowError(f"Gate {args.name} requires phase {required_phase}")
  gate = {
    "status": args.status,
    "details": args.details,
    "url": args.url,
  }
  if ledger["schema_version"] in (2, 3):
    gate["phase"] = ledger["phase"]
  attempts = ledger["gates"].setdefault(args.name, [])
  if attempts:
    comparable = {key: attempts[-1].get(key) for key in gate}
    current_phase_evidence = (
      ledger["schema_version"] == 1
      or attempts[-1]["recorded_at"] >= ledger["history"][-1]["at"]
    )
    if comparable == gate and current_phase_evidence:
      print(json.dumps(attempts[-1], sort_keys=True))
      return
  gate["recorded_at"] = now()
  attempts.append(gate)
  persist(args, ledger)
  print(json.dumps(gate, sort_keys=True))


def command_record_habit(args):
  ledger = load_ledger(args.state)
  require_lease(ledger, "habit-curator")
  allowed_statuses = (
    V1_HABIT_STATUSES if ledger["schema_version"] == 1 else V2_HABIT_STATUSES
  )
  if args.status not in allowed_statuses:
    raise WorkflowError(
      f"Habit status {args.status} is not supported by schema v{ledger['schema_version']}"
    )
  if ledger["schema_version"] in (2, 3):
    if args.snoozed_until_changed or args.pruned:
      raise WorkflowError("Schema v2 rejects legacy Habit freeze controls")
    if args.finding_count < 0 or args.active_finding_count < 0:
      raise WorkflowError("Habit v2 requires non-negative finding counts")
    stage_by_phase = {"habit-checking": "quick", "habit-rechecking": "final"}
    if ledger["phase"] not in stage_by_phase:
      raise WorkflowError("Habit v2 evidence requires a Habit checking phase")
    if args.status == "clean" and args.finding_count != 0:
      raise WorkflowError("Clean Habit evidence requires zero raw findings")
    if args.status == "ratcheted" and (
      args.active_finding_count != 0
      or not args.baseline_authorized
      or not args.baseline_unchanged
    ):
      raise WorkflowError(
        "Ratcheted Habit evidence requires an authorized unchanged baseline "
        "and zero active findings"
      )
    if args.status == "snoozed" and not args.user_authorized_snooze:
      raise WorkflowError(
        "Snoozed Habit evidence requires explicit user authorization"
      )
    if args.status == "not-applicable" and not args.tool_unavailable:
      raise WorkflowError(
        "Not-applicable Habit status requires tool-unavailable evidence"
      )
    record = {
      "status": args.status,
      "details": args.details,
      "finding_count": args.finding_count,
      "stage": stage_by_phase[ledger["phase"]],
    }
    if args.status == "ratcheted":
      record.update(
        {
          "active_finding_count": args.active_finding_count,
          "baseline_authorized": args.baseline_authorized,
          "baseline_unchanged": args.baseline_unchanged,
        }
      )
    if args.status == "snoozed":
      record["user_authorized_snooze"] = args.user_authorized_snooze
    if args.status == "not-applicable":
      record["tool_unavailable"] = args.tool_unavailable
  else:
    record = legacy_habit_record(args)
  current = ledger["habit"]
  if current is not None:
    comparable = {key: current.get(key) for key in record}
    current_phase_evidence = (
      ledger["schema_version"] == 1
      or current["recorded_at"] >= ledger["history"][-1]["at"]
    )
    if comparable == record and current_phase_evidence:
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


def legacy_habit_record(args):
  if args.status == "frozen":
    if args.finding_count != args.classified_count:
      raise WorkflowError("Habit freeze requires every finding to be classified")
    if not args.snoozed_until_changed or not args.pruned:
      raise WorkflowError("Habit freeze requires until-changed snooze and prune evidence")
  return {
    "status": args.status,
    "details": args.details,
    "finding_count": args.finding_count,
    "classified_count": args.classified_count,
    "snoozed_until_changed": args.snoozed_until_changed,
    "pruned": args.pruned,
  }


def command_record_habit_observation(args):
  ledger = load_ledger(args.state)
  if ledger["schema_version"] not in (2, 3):
    raise WorkflowError("Habit observations require schema v2 or v3")
  require_lease(ledger, "coordinator")
  if ledger["phase"] != "habit-checking":
    raise WorkflowError("Habit observations require the habit-checking phase")
  observations = ledger.setdefault("habit_observations", [])
  candidate = {
    "kind": args.kind,
    "details": args.details,
    "stage": "quick",
  }
  if observations:
    comparable = {key: observations[-1].get(key) for key in candidate}
    current_observation = (
      observations[-1]["recorded_at"] >= ledger["history"][-1]["at"]
    )
    reclassification_matches = (
      not args.reclassify_current
      or observations[-1]["reclassified_habit"] is not None
    )
    if comparable == candidate and current_observation and reclassification_matches:
      print(json.dumps(observations[-1], sort_keys=True))
      return
  reclassified_habit = None
  if args.reclassify_current:
    habit = ledger["habit"]
    if (
      habit is None
      or habit["stage"] != "quick"
      or habit["status"] != "not-applicable"
    ):
      raise WorkflowError(
        "Reclassification requires current quick not-applicable Habit evidence"
      )
    reclassified_habit = habit
  elif ledger["habit"] is not None:
    raise WorkflowError(
      "Habit observation conflicts with active terminal Habit evidence"
    )
  observation = {
    **candidate,
    "reclassified_habit": reclassified_habit,
    "recorded_at": now(),
  }
  observations.append(observation)
  ledger["habit"] = None
  persist(args, ledger)
  print(json.dumps(observation, sort_keys=True))


def mutation_artifact_path(ledger, raw_path, label):
  repository = Path(ledger["repository"]).resolve()
  artifact_root = (repository / ".agent" / "tmp").resolve()
  path = Path(raw_path)
  if not path.is_absolute():
    path = repository / path
  resolved = path.resolve()
  try:
    resolved.relative_to(artifact_root)
    relative = resolved.relative_to(repository)
  except ValueError as error:
    raise WorkflowError(f"Mutation {label} must be stored under .agent/tmp") from error
  if not resolved.exists():
    raise WorkflowError(f"Mutation {label} does not exist: {resolved}")
  if label in ("log", "classification file") and not resolved.is_file():
    raise WorkflowError(f"Mutation {label} must be a file: {resolved}")
  return relative.as_posix(), resolved


def load_mutation_classifications(ledger, raw_path):
  if raw_path is None:
    return None, []
  relative, resolved = mutation_artifact_path(
    ledger,
    raw_path,
    "classification file",
  )
  try:
    with resolved.open(encoding="utf-8") as stream:
      classifications = json.load(stream)
  except (OSError, json.JSONDecodeError) as error:
    raise WorkflowError(f"Invalid mutation classification file: {error}") from error
  if not isinstance(classifications, list):
    raise WorkflowError("Mutation classification file must contain a JSON list")
  if not all(mutation_classification_is_valid(item) for item in classifications):
    raise WorkflowError("Every mutation classification must be complete and supported")
  mutant_ids = [item["mutant_id"] for item in classifications]
  if len(mutant_ids) != len(set(mutant_ids)):
    raise WorkflowError("Mutation classifications require unique mutant IDs")
  return relative, classifications


def validate_completed_mutation_attempt(attempt):
  metrics = attempt["metrics"]
  if any(
    not isinstance(value, int) or isinstance(value, bool) or value < 0
    for value in metrics.values()
  ):
    raise WorkflowError("Mutation metrics require non-negative integer counts")
  if metrics["generated"] < sum(
    metrics[name] for name in ("killed", "survived", "no_coverage")
  ):
    raise WorkflowError("Mutation metrics cannot classify more mutants than generated")
  classifications = attempt["classifications"]
  outcome_counts = {
    outcome: sum(item["outcome"] == outcome for item in classifications)
    for outcome in MUTATION_OUTCOMES
  }
  if attempt["result"] != "failed" and (
    outcome_counts["survived"] != metrics["survived"]
    or outcome_counts["no-coverage"] != metrics["no_coverage"]
  ):
    raise WorkflowError(
      "Every survived and no-coverage mutant must be classified exactly once"
    )
  actionable = sum(
    item["classification"] in ACTIONABLE_MUTATION_CLASSIFICATIONS
    for item in classifications
  )
  if attempt["result"] == "passed":
    if not attempt["target_classes"]:
      raise WorkflowError("Passed mutation evidence requires production target classes")
    if actionable:
      raise WorkflowError("Passed mutation evidence requires zero actionable findings")
    if metrics["execution_errors"] != 0:
      raise WorkflowError("Passed mutation evidence requires zero execution errors")
    if metrics["generated"] != sum(
      metrics[name] for name in ("killed", "survived", "no_coverage")
    ):
      raise WorkflowError(
        "Passed mutation evidence must account for every generated mutant"
      )
    if not attempt["report_paths"]:
      raise WorkflowError("Passed mutation evidence requires at least one report path")
  return actionable


def command_record_mutation(args):
  ledger = load_ledger(args.state)
  if ledger["schema_version"] != 3:
    raise WorkflowError("Mutation evidence requires schema v3")
  require_lease(ledger, "mutation-analyst")
  stage_by_phase = {
    "mutation-testing": "initial",
    "mutation-rechecking": "final",
  }
  if ledger["phase"] not in stage_by_phase:
    raise WorkflowError("Mutation evidence requires a mutation testing phase")
  if not re.fullmatch(r"[0-9a-fA-F]{40}", args.analyzed_sha):
    raise WorkflowError("Mutation evidence requires a full analyzed commit SHA")
  if not re.fullmatch(r"[0-9a-fA-F]{64}", args.fingerprint):
    raise WorkflowError("Mutation evidence requires a SHA-256 input fingerprint")
  if not args.details.strip():
    raise WorkflowError("Mutation evidence requires non-empty details")
  stage = stage_by_phase[ledger["phase"]]
  if stage == "initial" and args.result == "reused":
    raise WorkflowError("Initial mutation evidence cannot be reused")
  log_path, _ = mutation_artifact_path(ledger, args.log, "log")

  if args.result == "reused":
    source = next(
      (
        attempt
        for attempt in reversed(ledger["mutation_attempts"])
        if attempt["stage"] == "initial"
        and attempt["result"] in ("passed", "not-applicable")
      ),
      None,
    )
    if source is None:
      raise WorkflowError("Reused mutation evidence requires an accepted initial attempt")
    if (
      args.reused_from_sha != source["analyzed_sha"]
      or args.reused_from_fingerprint != source["fingerprint"]
      or args.fingerprint.lower() != source["fingerprint"]
      or sorted(set(args.target_class)) != source["target_classes"]
      or args.runner != source["runner"]
    ):
      raise WorkflowError(
        "Mutation evidence can be reused only with unchanged inputs and target classes"
      )
    attempt = {
      "stage": stage,
      "result": "reused",
      "runner": source["runner"],
      "analyzed_sha": args.analyzed_sha.lower(),
      "fingerprint": source["fingerprint"],
      "target_classes": source["target_classes"],
      "metrics": source["metrics"],
      "classifications": source["classifications"],
      "actionable_findings": source["actionable_findings"],
      "classification_path": source["classification_path"],
      "log_path": log_path,
      "report_paths": source["report_paths"],
      "details": args.details,
      "not_applicable_reason": source["not_applicable_reason"],
      "failure_kind": None,
      "reused_from_sha": source["analyzed_sha"],
      "reused_from_fingerprint": source["fingerprint"],
    }
  else:
    classification_path, classifications = load_mutation_classifications(
      ledger,
      args.classification_file,
    )
    report_paths = [
      mutation_artifact_path(ledger, path, "report")[0] for path in args.report
    ]
    target_classes = sorted(set(args.target_class))
    if args.runner.lower() == "pit" and any(
      not target.endswith("*") for target in target_classes
    ):
      raise WorkflowError("PIT target classes must end in * to include inner classes")
    attempt = {
      "stage": stage,
      "result": args.result,
      "runner": args.runner,
      "analyzed_sha": args.analyzed_sha.lower(),
      "fingerprint": args.fingerprint.lower(),
      "target_classes": target_classes,
      "metrics": {
        "generated": args.generated,
        "killed": args.killed,
        "survived": args.survived,
        "no_coverage": args.no_coverage,
        "execution_errors": args.execution_errors,
      },
      "classifications": classifications,
      "actionable_findings": 0,
      "classification_path": classification_path,
      "log_path": log_path,
      "report_paths": report_paths,
      "details": args.details,
      "not_applicable_reason": args.not_applicable_reason,
      "failure_kind": args.failure_kind,
      "reused_from_sha": None,
      "reused_from_fingerprint": None,
    }
    attempt["actionable_findings"] = validate_completed_mutation_attempt(attempt)
    if args.result == "not-applicable":
      if args.not_applicable_reason not in MUTATION_NOT_APPLICABLE_REASONS:
        raise WorkflowError("Not-applicable mutation evidence requires an explicit reason")
      if any(attempt["metrics"].values()) or classifications or report_paths:
        raise WorkflowError("Not-applicable mutation evidence cannot report a runner execution")
      if args.not_applicable_reason == "no-production-changes" and target_classes:
        raise WorkflowError("No-production-changes evidence cannot include target classes")
    elif args.not_applicable_reason is not None:
      raise WorkflowError("Only not-applicable mutation evidence accepts that reason")
    if args.result == "failed":
      if args.failure_kind != "environmental":
        raise WorkflowError("Failed mutation evidence requires environmental diagnosis")
      if attempt["metrics"]["execution_errors"] == 0:
        raise WorkflowError("Failed mutation evidence requires an execution error count")
    elif args.failure_kind is not None:
      raise WorkflowError("Only failed mutation evidence accepts a failure kind")

  attempts = ledger["mutation_attempts"]
  if attempts:
    comparable = {key: attempts[-1].get(key) for key in attempt}
    current_phase_evidence = attempts[-1]["recorded_at"] >= ledger["history"][-1]["at"]
    if comparable == attempt and current_phase_evidence:
      print(json.dumps(attempts[-1], sort_keys=True))
      return
  attempt["recorded_at"] = now()
  attempts.append(attempt)
  persist(args, ledger)
  print(json.dumps(attempt, sort_keys=True))


def command_record_pr(args):
  ledger = load_ledger(args.state)
  if ledger["schema_version"] == 1:
    require_v1_pull_request_evidence(ledger)
  else:
    require_v2_pull_request_evidence(ledger)
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


def require_v1_pull_request_evidence(ledger):
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


def require_v2_pull_request_evidence(ledger):
  if ledger["phase"] != "delivery-ready":
    raise WorkflowError("Pull request creation requires the delivery-ready phase")
  require_current_gates(
    ledger,
    ("final-verify", "final-sonar"),
    "final-validating",
  )
  habit = ledger["habit"]
  if habit is None or habit["stage"] != "final":
    raise WorkflowError("Pull request creation requires final Habit evidence")
  if ledger["schema_version"] == 3:
    require_current_mutation_evidence(ledger, "final")


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
  initialize.add_argument("--base-sha", required=True)
  initialize.set_defaults(handler=command_init)

  show = subparsers.add_parser("show")
  show.set_defaults(handler=command_show)

  register_chat = subparsers.add_parser("register-chat")
  register_chat.add_argument("--role", required=True, choices=sorted(SPECIALIST_ROLES))
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
  transition.add_argument("--to", required=True, choices=ALL_PHASES)
  transition.add_argument("--note")
  transition.set_defaults(handler=command_transition)

  record_commit = subparsers.add_parser("record-commit")
  record_commit.add_argument("--sha", required=True)
  record_commit.add_argument("--kind", required=True, choices=COMMIT_KINDS)
  record_commit.add_argument("--subject", required=True)
  record_commit.set_defaults(handler=command_record_commit)

  record_gate = subparsers.add_parser("record-gate")
  record_gate.add_argument("--name", required=True, choices=ALL_GATE_NAMES)
  record_gate.add_argument("--status", required=True, choices=GATE_STATUSES)
  record_gate.add_argument("--details", required=True)
  record_gate.add_argument("--url")
  record_gate.set_defaults(handler=command_record_gate)

  record_habit = subparsers.add_parser("record-habit")
  record_habit.add_argument("--status", required=True, choices=ALL_HABIT_STATUSES)
  record_habit.add_argument("--details", required=True)
  record_habit.add_argument("--finding-count", type=int, default=0)
  record_habit.add_argument("--classified-count", type=int, default=0)
  record_habit.add_argument("--active-finding-count", type=int, default=0)
  record_habit.add_argument("--baseline-authorized", action="store_true")
  record_habit.add_argument("--baseline-unchanged", action="store_true")
  record_habit.add_argument("--user-authorized-snooze", action="store_true")
  record_habit.add_argument("--tool-unavailable", action="store_true")
  record_habit.add_argument("--snoozed-until-changed", action="store_true")
  record_habit.add_argument("--pruned", action="store_true")
  record_habit.set_defaults(handler=command_record_habit)

  record_habit_observation = subparsers.add_parser("record-habit-observation")
  record_habit_observation.add_argument(
    "--kind",
    required=True,
    choices=HABIT_OBSERVATION_KINDS,
  )
  record_habit_observation.add_argument("--details", required=True)
  record_habit_observation.add_argument("--reclassify-current", action="store_true")
  record_habit_observation.set_defaults(handler=command_record_habit_observation)

  record_mutation = subparsers.add_parser("record-mutation")
  record_mutation.add_argument("--runner", required=True)
  record_mutation.add_argument("--result", required=True, choices=MUTATION_RESULTS)
  record_mutation.add_argument("--analyzed-sha", required=True)
  record_mutation.add_argument("--fingerprint", required=True)
  record_mutation.add_argument("--target-class", action="append", default=[])
  record_mutation.add_argument("--generated", type=int, default=0)
  record_mutation.add_argument("--killed", type=int, default=0)
  record_mutation.add_argument("--survived", type=int, default=0)
  record_mutation.add_argument("--no-coverage", type=int, default=0)
  record_mutation.add_argument("--execution-errors", type=int, default=0)
  record_mutation.add_argument("--classification-file")
  record_mutation.add_argument("--log", required=True)
  record_mutation.add_argument("--report", action="append", default=[])
  record_mutation.add_argument("--details", required=True)
  record_mutation.add_argument(
    "--not-applicable-reason",
    choices=MUTATION_NOT_APPLICABLE_REASONS,
  )
  record_mutation.add_argument("--failure-kind", choices=("environmental",))
  record_mutation.add_argument("--reused-from-sha")
  record_mutation.add_argument("--reused-from-fingerprint")
  record_mutation.set_defaults(handler=command_record_mutation)

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
