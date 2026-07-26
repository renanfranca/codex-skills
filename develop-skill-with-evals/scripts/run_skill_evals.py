#!/usr/bin/env python3
"""Run isolated, structured forward evaluations for Codex skills."""

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import fcntl
import fnmatch
import hashlib
import json
import os
from pathlib import Path
import shlex
import shutil
import stat
import subprocess
import sys
import tarfile
import tempfile
import time
from typing import Any
import uuid

SCRIPT_DIRECTORY = Path(__file__).resolve().parent
if str(SCRIPT_DIRECTORY) not in sys.path:
  sys.path.insert(0, str(SCRIPT_DIRECTORY))

from eval_report import (
  api_reference_estimate,
  atomic_write_text,
  build_file_evidence,
  canonical_json,
  capture_evidence_snapshot,
  codex_environment,
  load_pricing,
  report_digest,
  sanitize_fact,
)
from render_eval_report import render_report


PASS = "PASS"
BLOCKING = {"FAIL", "ERROR", "INCONCLUSIVE", "INVALID_RED", "UNSTABLE"}
IMPACTS = ("static", "deterministic", "scoped", "cross-cutting")
WORKFLOWS = ("diagnostic", "promotion")
DEFAULT_APPROVED_MODEL_SESSIONS = 8


def utc_now() -> str:
  return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True)
class RoleRuntime:
  required: bool
  model: str | None
  model_source: str
  reasoning_effort: str | None
  reasoning_effort_source: str

  def as_dict(self) -> dict[str, Any]:
    return {
      "required": self.required,
      "model": self.model,
      "model_source": self.model_source,
      "reasoning_effort": self.reasoning_effort,
      "reasoning_effort_source": self.reasoning_effort_source,
    }


@dataclass(frozen=True)
class EvaluationRuntime:
  required: bool
  complete: bool
  audit_quality: str
  executor: RoleRuntime
  judge: RoleRuntime

  def as_dict(self) -> dict[str, Any]:
    return {
      "required": self.required,
      "complete": self.complete,
      "audit_quality": self.audit_quality,
      "executor": self.executor.as_dict(),
      "judge": self.judge.as_dict(),
    }


class ProgressReporter:
  def __init__(self, enabled: bool):
    self.enabled = enabled

  def emit(self, message: str) -> None:
    if self.enabled:
      print(message, file=sys.stderr, flush=True)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
  parser = argparse.ArgumentParser(description=__doc__)
  subparsers = parser.add_subparsers(dest="operation", required=True)

  run_parser = subparsers.add_parser("run", help="Run one case or a complete suite")
  add_skill_argument(run_parser)
  selection = run_parser.add_mutually_exclusive_group(required=True)
  selection.add_argument("--case")
  selection.add_argument("--all", action="store_true")
  run_parser.add_argument("--source", default="working-tree")
  add_runtime_arguments(run_parser)

  verify_parser = subparsers.add_parser("verify-change", help="Require baseline RED and candidate GREEN")
  add_skill_argument(verify_parser)
  verify_parser.add_argument("--case", required=True)
  verify_parser.add_argument("--baseline")
  add_runtime_arguments(verify_parser)

  stability_parser = subparsers.add_parser("stability", help="Repeat a case and reject divergent verdicts")
  add_skill_argument(stability_parser)
  stability_parser.add_argument("--case", required=True)
  stability_parser.add_argument("--runs", type=int, default=3)
  stability_parser.add_argument("--source", default="working-tree")
  add_runtime_arguments(stability_parser)

  plan_parser = subparsers.add_parser("plan", help="Plan proportional evaluation gates without running them")
  add_skill_argument(plan_parser)
  plan_parser.add_argument("--baseline", type=Path, required=True)
  plan_parser.add_argument("--impact", choices=IMPACTS, required=True)
  plan_parser.add_argument("--case", action="append", default=[])
  plan_parser.add_argument("--workflow", choices=WORKFLOWS, default="promotion")
  add_runtime_selection_arguments(plan_parser)
  add_campaign_arguments(plan_parser)

  probe_parser = subparsers.add_parser(
    "probe-change",
    help="Observe RED, candidate, and regression contracts once without promotion eligibility",
  )
  add_skill_argument(probe_parser)
  probe_parser.add_argument("--baseline", type=Path, required=True)
  probe_parser.add_argument(
    "--impact", choices=("deterministic", "scoped", "cross-cutting"), required=True
  )
  probe_parser.add_argument("--case", action="append", default=[])
  probe_parser.add_argument(
    "--approved-model-sessions", type=int, default=DEFAULT_APPROVED_MODEL_SESSIONS
  )
  probe_parser.set_defaults(workflow="diagnostic")
  add_runtime_arguments(probe_parser)
  add_campaign_arguments(probe_parser)

  validate_parser = subparsers.add_parser(
    "validate-change", help="Run RED, GREEN, stability, and proportional regression gates"
  )
  add_skill_argument(validate_parser)
  validate_parser.add_argument("--baseline", type=Path, required=True)
  validate_parser.add_argument(
    "--impact", choices=("deterministic", "scoped", "cross-cutting"), required=True
  )
  validate_parser.add_argument("--case", action="append", default=[])
  validate_parser.add_argument(
    "--approved-model-sessions", type=int, default=DEFAULT_APPROVED_MODEL_SESSIONS
  )
  validate_parser.set_defaults(workflow="promotion")
  add_runtime_arguments(validate_parser)
  add_campaign_arguments(validate_parser)

  args = parser.parse_args(argv)
  if hasattr(args, "runs") and args.runs < 2:
    parser.error("--runs must be at least 2")
  if hasattr(args, "approved_model_sessions") and args.approved_model_sessions < 0:
    parser.error("--approved-model-sessions must be non-negative")
  if (
    getattr(args, "approved_cumulative_model_sessions", None) is not None
    and args.approved_cumulative_model_sessions < 0
  ):
    parser.error("--approved-cumulative-model-sessions must be non-negative")
  campaign_values = (
    getattr(args, "campaign_ledger", None),
    getattr(args, "approved_cumulative_model_sessions", None),
  )
  if (campaign_values[0] is None) != (campaign_values[1] is None):
    parser.error(
      "--campaign-ledger and --approved-cumulative-model-sessions must be supplied together"
    )
  if (
    getattr(args, "pricing_file", None) is not None
    and getattr(args, "report_dir", None) is None
  ):
    parser.error("--pricing-file requires --report-dir")
  return args


def add_skill_argument(parser: argparse.ArgumentParser) -> None:
  parser.add_argument("--skill", type=Path, required=True)


def add_runtime_selection_arguments(parser: argparse.ArgumentParser) -> None:
  parser.add_argument("--model")
  parser.add_argument("--reasoning-effort")
  parser.add_argument("--judge-model")
  parser.add_argument("--judge-reasoning-effort")


def add_runtime_arguments(parser: argparse.ArgumentParser) -> None:
  add_runtime_selection_arguments(parser)
  parser.add_argument("--codex-command", default="codex")
  parser.add_argument("--artifacts-dir", type=Path, default=Path("/tmp/skill-eval-artifacts"))
  parser.add_argument("--report-dir", type=Path)
  parser.add_argument("--pricing-file", type=Path)
  progress = parser.add_mutually_exclusive_group()
  progress.add_argument("--progress", action="store_true", help="Show progress on stderr even without a TTY")
  progress.add_argument("--quiet", action="store_true", help="Suppress progress on stderr")


def add_campaign_arguments(parser: argparse.ArgumentParser) -> None:
  parser.add_argument("--campaign-ledger", type=Path)
  parser.add_argument("--approved-cumulative-model-sessions", type=int)


def progress_enabled(args: argparse.Namespace, stream: Any | None = None) -> bool:
  if getattr(args, "quiet", False):
    return False
  if getattr(args, "progress", False):
    return True
  output = sys.stderr if stream is None else stream
  return output.isatty()


def read_json(path: Path) -> dict[str, Any]:
  with path.open(encoding="utf-8") as stream:
    value = json.load(stream)
  if not isinstance(value, dict):
    raise ValueError(f"Expected a JSON object in {path}")
  return value


def copy_skill_without_evals(source: Path, destination: Path) -> None:
  shutil.copytree(source, destination, ignore=shutil.ignore_patterns("evals", "__pycache__", "*.pyc"))


def materialize_skill_source(skill: Path, source: str, destination: Path) -> Path:
  skill = skill.resolve()
  destination.mkdir(parents=True, exist_ok=True)
  if source == "working-tree":
    target = destination / skill.name
    shutil.copytree(skill, target, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    return target
  if not source.startswith("git:"):
    raise ValueError("--source must be working-tree or git:<revision>")

  revision = source.removeprefix("git:")
  repository = Path(
    subprocess.run(
      ["git", "-C", str(skill), "rev-parse", "--show-toplevel"],
      text=True,
      capture_output=True,
      check=True,
    ).stdout.strip()
  )
  relative_skill = skill.relative_to(repository)
  archive = destination / "source.tar"
  with archive.open("wb") as stream:
    subprocess.run(
      ["git", "-C", str(repository), "archive", revision, str(relative_skill)],
      stdout=stream,
      check=True,
    )
  extracted = destination / "git-source"
  extracted.mkdir()
  with tarfile.open(archive) as tar:
    tar.extractall(extracted, filter="data")
  return extracted / relative_skill


def file_hash(path: Path) -> str:
  digest = hashlib.sha256()
  with path.open("rb") as stream:
    for block in iter(lambda: stream.read(65536), b""):
      digest.update(block)
  return digest.hexdigest()


def snapshot(root: Path) -> dict[str, str]:
  result = {}
  for path in sorted(root.rglob("*")):
    relative = path.relative_to(root)
    if (
      path.is_file()
      and ".git" not in relative.parts
      and "__pycache__" not in relative.parts
      and path.suffix != ".pyc"
    ):
      result[path.relative_to(root).as_posix()] = file_hash(path)
  return result


def fingerprint_files(root: Path) -> dict[str, dict[str, Any]]:
  result = {}
  if not root.exists():
    return result
  for path in sorted(root.rglob("*")):
    relative = path.relative_to(root)
    if ".git" in relative.parts or "__pycache__" in relative.parts or path.suffix == ".pyc":
      continue
    if path.is_file():
      result[relative.as_posix()] = {
        "mode": path.stat().st_mode & 0o7777,
        "sha256": file_hash(path),
      }
  return result


def fingerprint_payload(value: Any) -> str:
  encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
  return hashlib.sha256(encoded).hexdigest()


def tree_fingerprint(root: Path) -> str:
  return fingerprint_payload(fingerprint_files(root))


def changed_paths(before: dict[str, str], after: dict[str, str]) -> list[str]:
  return sorted(path for path in before.keys() | after.keys() if before.get(path) != after.get(path))


def check(name: str, passed: bool, detail: str) -> dict[str, Any]:
  return {"name": name, "passed": passed, "detail": detail}


def empty_usage() -> dict[str, Any]:
  return {
    "input_tokens": None,
    "cached_input_tokens": None,
    "output_tokens": None,
    "reasoning_output_tokens": None,
    "total_tokens": None,
    "complete": False,
    "reasoning_output_tokens_complete": False,
    "events": [],
    "event_count": 0,
    "events_complete": False,
  }


def usage_from_jsonl(output: str) -> dict[str, Any]:
  observations = []
  for line in output.splitlines():
    try:
      event = json.loads(line)
    except json.JSONDecodeError:
      continue
    usage = event.get("usage") if isinstance(event, dict) else None
    if not isinstance(usage, dict):
      continue
    values = {
      key: usage.get(key)
      for key in ("input_tokens", "cached_input_tokens", "output_tokens")
    }
    complete = all(
      isinstance(value, int) and value >= 0
      for value in values.values()
    )
    reasoning = usage.get("reasoning_output_tokens")
    reasoning_value = (
      reasoning
      if isinstance(reasoning, int) and reasoning >= 0
      else None
    )
    event_type = event.get("type")
    values.update({
      "sequence": len(observations) + 1,
      "source_event_type": (
        event_type if isinstance(event_type, str) else "unknown"
      ),
      "scope": "turn" if event_type == "turn.completed" else "unknown",
      "reasoning_output_tokens": reasoning_value,
      "total_tokens": (
        values["input_tokens"] + values["output_tokens"]
        if complete
        else None
      ),
      "complete": complete,
      "reasoning_output_tokens_complete": reasoning_value is not None,
    })
    observations.append(values)
  if not observations:
    return empty_usage()
  events_complete = all(value["complete"] for value in observations)
  if not events_complete:
    return {
      **empty_usage(),
      "events": observations,
      "event_count": len(observations),
      "events_complete": False,
    }
  input_tokens = sum(value["input_tokens"] for value in observations)
  cached_input_tokens = sum(value["cached_input_tokens"] for value in observations)
  output_tokens = sum(value["output_tokens"] for value in observations)
  reasoning_complete = all(
    value["reasoning_output_tokens"] is not None
    for value in observations
  )
  return {
    "input_tokens": input_tokens,
    "cached_input_tokens": cached_input_tokens,
    "output_tokens": output_tokens,
    "reasoning_output_tokens": (
      sum(value["reasoning_output_tokens"] for value in observations)
      if reasoning_complete
      else None
    ),
    "total_tokens": input_tokens + output_tokens,
    "complete": True,
    "reasoning_output_tokens_complete": reasoning_complete,
    "events": observations,
    "event_count": len(observations),
    "events_complete": True,
  }


def aggregate_usage(values: list[dict[str, Any]]) -> dict[str, Any]:
  events = []
  for value in values:
    for event in value.get("events", []):
      normalized = dict(event)
      normalized["sequence"] = len(events) + 1
      events.append(normalized)
  if not values or not all(value.get("complete", False) for value in values):
    return {
      **empty_usage(),
      "events": events,
      "event_count": len(events),
      "events_complete": bool(events) and all(
        event.get("complete", False) for event in events
      ),
    }
  reasoning_complete = all(
    value.get("reasoning_output_tokens_complete", False)
    for value in values
  )
  return {
    "input_tokens": sum(value["input_tokens"] for value in values),
    "cached_input_tokens": sum(value["cached_input_tokens"] for value in values),
    "output_tokens": sum(value["output_tokens"] for value in values),
    "reasoning_output_tokens": (
      sum(value["reasoning_output_tokens"] for value in values)
      if reasoning_complete
      else None
    ),
    "total_tokens": sum(value["total_tokens"] for value in values),
    "complete": True,
    "reasoning_output_tokens_complete": reasoning_complete,
    "events": events,
    "event_count": len(events),
    "events_complete": bool(events) and all(
      event.get("complete", False) for event in events
    ),
  }


def write_executor_schema(path: Path) -> None:
  schema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "required": [
      "summary",
      "classification",
      "evidence",
      "files_changed",
      "diagnosis",
      "approach",
      "decisions",
      "rejected_alternatives",
      "key_changes",
      "validation",
    ],
    "properties": {
      "summary": {"type": "string"},
      "classification": {"type": "string"},
      "evidence": {"type": "array", "items": {"type": "string"}},
      "files_changed": {"type": "array", "items": {"type": "string"}},
      "diagnosis": {"type": "string"},
      "approach": {"type": "array", "items": {"type": "string"}},
      "decisions": {"type": "array", "items": {"type": "string"}},
      "rejected_alternatives": {"type": "array", "items": {"type": "string"}},
      "key_changes": {"type": "array", "items": {"type": "string"}},
      "validation": {"type": "array", "items": {"type": "string"}},
    },
    "additionalProperties": False,
  }
  path.write_text(json.dumps(schema), encoding="utf-8")


def write_judge_schema(path: Path) -> None:
  schema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "required": ["verdict", "rationale", "evidence"],
    "properties": {
      "verdict": {"enum": ["PASS", "FAIL", "INCONCLUSIVE"]},
      "rationale": {"type": "string"},
      "evidence": {"type": "array", "items": {"type": "string"}},
    },
    "additionalProperties": False,
  }
  path.write_text(json.dumps(schema), encoding="utf-8")


def valid_executor_response(response: Any) -> bool:
  return (
    isinstance(response, dict)
    and isinstance(response.get("summary"), str)
    and isinstance(response.get("classification"), str)
    and isinstance(response.get("evidence"), list)
    and all(isinstance(item, str) for item in response["evidence"])
    and isinstance(response.get("files_changed"), list)
    and all(isinstance(item, str) for item in response["files_changed"])
  )


def run_process(
  command: list[str],
  cwd: Path,
  prompt: str | None = None,
  env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
  return subprocess.run(
    command,
    cwd=cwd,
    input=prompt,
    text=True,
    capture_output=True,
    check=False,
    env=env,
  )


def timed_process(
  command: list[str],
  cwd: Path,
  prompt: str | None = None,
  env: dict[str, str] | None = None,
) -> tuple[subprocess.CompletedProcess[str], int]:
  started = time.monotonic()
  completed = run_process(command, cwd, prompt, env)
  duration_ms = max(0, round((time.monotonic() - started) * 1000))
  return completed, duration_ms


def model_process_failure(completed: subprocess.CompletedProcess[str], output_exists: bool) -> bool:
  if completed.returncode == 0:
    return False
  diagnostic = f"{completed.stdout}\n{completed.stderr}".lower()
  infrastructure_markers = (
    "authentication",
    "unauthorized",
    "forbidden",
    "quota",
    "rate limit",
    "capacity",
    "connection",
    "timed out",
    "timeout",
    "not found",
  )
  return not output_exists or any(marker in diagnostic for marker in infrastructure_markers)


def load_case_manifest(skill: Path, case_id: str) -> tuple[Path, dict[str, Any]]:
  case_dir = skill / "evals" / "cases" / case_id
  case = read_json(case_dir / "case.json")
  validate_case_manifest(case_dir, case_id, case)
  return case_dir, case


def validate_case_manifest(case_dir: Path, case_id: str, case: dict[str, Any]) -> None:
  if case.get("id") != case_id:
    raise ValueError(f"Case id mismatch in {case_dir / 'case.json'}")
  kind = case.get("kind", "behavioral")
  if kind not in {"behavioral", "non_behavioral", "trigger", "deterministic"}:
    raise ValueError(f"Unsupported case kind {kind!r} in {case_dir / 'case.json'}")
  mechanical = case.get("mechanical", {})
  if not isinstance(mechanical, dict):
    raise ValueError(f"mechanical must be an object in {case_dir / 'case.json'}")
  for field in ("required_paths", "forbidden_changed_paths"):
    values = mechanical.get(field, [])
    if not isinstance(values, list) or not all(isinstance(value, str) for value in values):
      raise ValueError(f"mechanical.{field} must be an array of strings in {case_dir / 'case.json'}")
  commands = mechanical.get("commands", [])
  if not isinstance(commands, list):
    raise ValueError(f"mechanical.commands must be an array in {case_dir / 'case.json'}")
  for command in commands:
    argv = command.get("argv") if isinstance(command, dict) else None
    if not isinstance(argv, list) or not argv or not all(isinstance(item, str) for item in argv):
      raise ValueError(f"Every mechanical command requires a non-empty argv array in {case_dir / 'case.json'}")
  oracle = case.get("oracle", {})
  if not isinstance(oracle, dict):
    raise ValueError(f"oracle must be an object in {case_dir / 'case.json'}")
  oracle_commands = oracle.get("commands", [])
  if not isinstance(oracle_commands, list):
    raise ValueError(f"oracle.commands must be an array in {case_dir / 'case.json'}")
  for command in oracle_commands:
    argv = command.get("argv") if isinstance(command, dict) else None
    if not isinstance(argv, list) or not argv or not all(isinstance(item, str) for item in argv):
      raise ValueError(f"Every oracle command requires a non-empty argv array in {case_dir / 'case.json'}")
  if oracle_commands and not (case_dir / "oracle").is_dir():
    raise ValueError(f"Case {case_id} declares oracle commands but has no oracle directory")
  judge = case.get("judge", {})
  if not isinstance(judge, dict):
    raise ValueError(f"judge must be an object in {case_dir / 'case.json'}")
  if kind == "deterministic":
    observations = (
      mechanical.get("required_paths", [])
      or mechanical.get("forbidden_changed_paths", [])
      or commands
    )
    if not observations:
      raise ValueError(f"Deterministic case {case_id} requires at least one mechanical verification")
    forbidden = {"prompt_file", "implicit_skill", "executor"} & case.keys()
    if forbidden or "expected_exit_code" in mechanical:
      names = sorted(forbidden | ({"mechanical.expected_exit_code"} if "expected_exit_code" in mechanical else set()))
      raise ValueError(f"Deterministic case {case_id} forbids executor configuration: {', '.join(names)}")
    if judge.get("enabled", False):
      raise ValueError(f"Deterministic case {case_id} cannot enable a semantic judge")
  else:
    prompt_file = case.get("prompt_file", "prompt.md")
    if not (case_dir / prompt_file).is_file():
      raise ValueError(f"Missing prompt file for case {case_id}: {prompt_file}")


def disabled_executor() -> dict[str, Any]:
  return {
    "enabled": False,
    "executed": False,
    "exit_code": None,
    "response": None,
    "stderr": "",
    "usage": empty_usage(),
    "duration_ms": 0,
  }


def disabled_judge(reason: str) -> dict[str, Any]:
  return {
    "enabled": False,
    "executed": False,
    "verdict": PASS,
    "rationale": reason,
    "evidence": [],
    "usage": empty_usage(),
    "duration_ms": 0,
    "failure_category": None,
  }


def disabled_oracle() -> dict[str, Any]:
  return {
    "enabled": False,
    "passed": True,
    "commands": [],
  }


def run_oracle(
  case: dict[str, Any],
  case_dir: Path,
  workspace: Path,
) -> dict[str, Any]:
  contracts = case.get("oracle", {}).get("commands", [])
  if not contracts:
    return disabled_oracle()
  oracle_dir = (case_dir / "oracle").resolve()
  results = []
  for contract in contracts:
    argv = [
      item.replace("{oracle_dir}", str(oracle_dir))
      for item in contract["argv"]
    ]
    completed = run_process(
      argv,
      workspace,
      env={**os.environ, "SKILL_EVAL_ORACLE_DIR": str(oracle_dir)},
    )
    expected_exit = contract.get("exit_code", 0)
    results.append({
      "argv": contract["argv"],
      "exit_code": completed.returncode,
      "expected_exit_code": expected_exit,
      "passed": completed.returncode == expected_exit,
      "stdout": completed.stdout[-4000:],
      "stderr": completed.stderr[-4000:],
    })
  return {
    "enabled": True,
    "passed": all(result["passed"] for result in results),
    "commands": results,
  }


def evaluate_deterministic_case(
  installed_source: Path,
  case: dict[str, Any],
  case_dir: Path,
  case_id: str,
  operation_root: Path,
  progress: ProgressReporter,
  label: str,
) -> dict[str, Any]:
  observation_started_at = utc_now()
  observation_started = time.monotonic()
  progress.emit(f"{label}: preparing workspace")
  workspace = Path(tempfile.mkdtemp(prefix=f"{case_id}-", dir=operation_root))
  fixture = case_dir / "fixture"
  if fixture.exists():
    shutil.copytree(fixture, workspace, dirs_exist_ok=True)
  subprocess.run(["git", "init", "-q"], cwd=workspace, check=True)
  before = snapshot(workspace)
  evidence_before = capture_evidence_snapshot(workspace)
  skill_before = snapshot(installed_source)
  progress.emit(f"{label}: running mechanical checks")
  mechanical_contract = case.get("mechanical", {})
  checks = []
  command_results = []
  command_env = {**os.environ, "SKILL_EVAL_SKILL_DIR": str(installed_source.resolve())}
  for command_contract in mechanical_contract.get("commands", []):
    completed = run_process(command_contract["argv"], workspace, env=command_env)
    expected_exit = command_contract.get("exit_code", 0)
    command_results.append(
      {
        "argv": command_contract["argv"],
        "exit_code": completed.returncode,
        "stdout": completed.stdout[-4000:],
        "stderr": completed.stderr[-4000:],
      }
    )
    checks.append(
      check(
        f"command: {' '.join(command_contract['argv'])}",
        completed.returncode == expected_exit,
        f"expected {expected_exit}, got {completed.returncode}",
      )
    )
  for required in mechanical_contract.get("required_paths", []):
    checks.append(check(f"required path: {required}", (workspace / required).exists(), required))
  after = snapshot(workspace)
  file_evidence = build_file_evidence(
    evidence_before,
    capture_evidence_snapshot(workspace),
  )
  changed = changed_paths(before, after)
  for pattern in mechanical_contract.get("forbidden_changed_paths", []):
    matches = [path for path in changed if fnmatch.fnmatch(path, pattern)]
    checks.append(check(f"forbidden changed path: {pattern}", not matches, ", ".join(matches) or "no matches"))
  checks.append(
    check(
      "evaluated skill remained unchanged",
      snapshot(installed_source) == skill_before,
      "evaluated skill hash comparison",
    )
  )
  mechanical = {"passed": all(item["passed"] for item in checks), "checks": checks, "commands": command_results}
  oracle = run_oracle(case, case_dir, workspace)
  status = PASS if mechanical["passed"] and oracle["passed"] else "FAIL"
  observation_finished_at = utc_now()
  result = {
    "case_id": case_id,
    "status": status,
    "kind": "deterministic",
    "executor": disabled_executor(),
    "mechanical": mechanical,
    "oracle": oracle,
    "judge": disabled_judge("Deterministic cases do not use a semantic judge."),
    "changed_paths": changed,
    "workspace": str(workspace),
    "model_sessions": {"executor": 0, "judge": 0, "total": 0},
    "usage": empty_usage(),
    "failure_category": None if status == PASS else "contract",
    "_started_at": observation_started_at,
    "_finished_at": observation_finished_at,
    "_duration_ms": max(0, round((time.monotonic() - observation_started) * 1000)),
    "_prompt": None,
    "_evidence": file_evidence,
  }
  (workspace / ".eval-result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
  progress.emit(f"{label}: {status}")
  return result


def run_judge(
  args: argparse.Namespace,
  runtime: RoleRuntime,
  workspace: Path,
  case: dict[str, Any],
  response: dict[str, Any] | None,
  mechanical: dict[str, Any],
) -> dict[str, Any]:
  judge = case.get("judge", {})
  if not judge.get("enabled", False):
    return disabled_judge("Semantic judge disabled for this case.")

  schema = workspace / ".eval-judge-schema.json"
  output = workspace / ".eval-judge-response.json"
  write_judge_schema(schema)
  payload = {
    "task": "Independently judge an authorized skill evaluation. Use only the supplied evidence.",
    "criteria": judge.get("criteria", []),
    "no_action_acceptable": judge.get("no_action_acceptable", False),
    "executor_response": response,
    "mechanical": mechanical,
  }
  command = codex_command(args, runtime, workspace, schema, output)
  completed, duration_ms = timed_process(
    command,
    workspace,
    json.dumps(payload),
  )
  usage = usage_from_jsonl(completed.stdout)
  if completed.returncode != 0 or not output.exists():
    return {
      "enabled": True,
      "executed": True,
      "verdict": "INCONCLUSIVE",
      "rationale": f"Judge process failed with exit code {completed.returncode}.",
      "evidence": [completed.stderr[-1000:]],
      "usage": usage,
      "duration_ms": duration_ms,
      "failure_category": (
        "infrastructure"
        if model_process_failure(completed, output.exists())
        else "contract"
      ),
    }
  try:
    result = read_json(output)
  except (OSError, ValueError, json.JSONDecodeError) as error:
    return {
      "enabled": True,
      "executed": True,
      "verdict": "INCONCLUSIVE",
      "rationale": str(error),
      "evidence": [],
      "usage": usage,
      "duration_ms": duration_ms,
      "failure_category": "contract",
    }
  verdict = result.get("verdict")
  if verdict not in {PASS, "FAIL", "INCONCLUSIVE"}:
    verdict = "INCONCLUSIVE"
  return {
    "enabled": True,
    "executed": True,
    "verdict": verdict,
    "rationale": result.get("rationale", ""),
    "evidence": result.get("evidence", []),
    "usage": usage,
    "duration_ms": duration_ms,
    "failure_category": None if verdict == PASS else "contract",
  }


def codex_command(
  args: argparse.Namespace,
  runtime: RoleRuntime,
  workspace: Path,
  schema: Path,
  output: Path,
) -> list[str]:
  command = [
    args.codex_command,
    "exec",
    "--ephemeral",
    "--json",
    "--skip-git-repo-check",
    "--sandbox",
    "workspace-write",
    "-C",
    str(workspace),
    "--output-schema",
    str(schema),
    "-o",
    str(output),
    "-",
  ]
  runtime_arguments = []
  if runtime.model:
    runtime_arguments.extend(["--model", runtime.model])
  if runtime.reasoning_effort:
    runtime_arguments.extend([
      "-c",
      f'model_reasoning_effort="{runtime.reasoning_effort}"',
    ])
  command[2:2] = runtime_arguments
  return command


def evaluate_case(
  args: argparse.Namespace,
  runtime: EvaluationRuntime,
  installed_source: Path,
  case_source_skill: Path,
  case_id: str,
  operation_root: Path,
  progress: ProgressReporter,
  context: str | None = None,
) -> dict[str, Any]:
  observation_started_at = utc_now()
  observation_started = time.monotonic()
  label = f"Case {case_id}" + (f" [{context}]" if context else "")
  case_dir, case = load_case_manifest(case_source_skill, case_id)
  if case.get("kind") == "deterministic":
    return evaluate_deterministic_case(
      installed_source,
      case,
      case_dir,
      case_id,
      operation_root,
      progress,
      label,
    )
  progress.emit(f"{label}: preparing workspace")
  workspace = Path(tempfile.mkdtemp(prefix=f"{case_id}-", dir=operation_root))
  fixture = case_dir / "fixture"
  if fixture.exists():
    shutil.copytree(fixture, workspace, dirs_exist_ok=True)
  scoped_skill = workspace / ".agents" / "skills" / installed_source.name
  scoped_skill.parent.mkdir(parents=True, exist_ok=True)
  copy_skill_without_evals(installed_source, scoped_skill)
  subprocess.run(["git", "init", "-q"], cwd=workspace, check=True)
  before = snapshot(workspace)
  evidence_before = capture_evidence_snapshot(workspace)
  skill_before = snapshot(scoped_skill)

  schema = workspace / ".eval-executor-schema.json"
  output = workspace / ".eval-executor-response.json"
  write_executor_schema(schema)
  raw_prompt = (case_dir / case.get("prompt_file", "prompt.md")).read_text(encoding="utf-8")
  if case.get("implicit_skill", False):
    prompt = raw_prompt
  else:
    prompt = f"Use ${installed_source.name} from the repository-scoped skill installation to complete this task.\n\n{raw_prompt}"
  prompt += (
    "\n\nIn the structured response, record only concise decisions actually made. "
    "Do not reveal private reasoning or reconstruct hidden chain of thought."
  )
  progress.emit(f"{label}: running executor")
  completed, executor_duration_ms = timed_process(
    codex_command(args, runtime.executor, workspace, schema, output),
    workspace,
    prompt,
  )
  executor_usage = usage_from_jsonl(completed.stdout)
  executor_infrastructure_failure = model_process_failure(
    completed,
    output.exists(),
  )
  try:
    response = read_json(output) if output.exists() else None
  except (OSError, ValueError, json.JSONDecodeError):
    response = None

  progress.emit(f"{label}: running mechanical checks")
  mechanical_contract = case.get("mechanical", {})
  checks = []
  expected_exit = mechanical_contract.get("expected_exit_code", 0)
  checks.append(check("executor exit code", completed.returncode == expected_exit, f"expected {expected_exit}, got {completed.returncode}"))
  checks.append(check("executor response schema", valid_executor_response(response), "structured response present and valid"))
  for required in mechanical_contract.get("required_paths", []):
    checks.append(check(f"required path: {required}", (workspace / required).exists(), required))

  after = snapshot(workspace)
  file_evidence = build_file_evidence(
    evidence_before,
    capture_evidence_snapshot(workspace),
  )
  changed = changed_paths(before, after)
  forbidden = mechanical_contract.get("forbidden_changed_paths", [])
  for pattern in forbidden:
    matches = [path for path in changed if fnmatch.fnmatch(path, pattern)]
    checks.append(check(f"forbidden changed path: {pattern}", not matches, ", ".join(matches) or "no matches"))
  checks.append(
    check(
      "evaluated skill remained unchanged",
      snapshot(scoped_skill) == skill_before,
      "repository-scoped skill hash comparison",
    )
  )
  command_results = []
  for command_contract in mechanical_contract.get("commands", []):
    command_completed = run_process(command_contract["argv"], workspace)
    expected_command_exit = command_contract.get("exit_code", 0)
    command_results.append(
      {
        "argv": command_contract["argv"],
        "exit_code": command_completed.returncode,
        "stdout": command_completed.stdout[-4000:],
        "stderr": command_completed.stderr[-4000:],
      }
    )
    checks.append(
      check(
        f"command: {' '.join(command_contract['argv'])}",
        command_completed.returncode == expected_command_exit,
        f"expected {expected_command_exit}, got {command_completed.returncode}",
      )
    )

  mechanical = {"passed": all(item["passed"] for item in checks), "checks": checks, "commands": command_results}
  oracle = disabled_oracle() if executor_infrastructure_failure else run_oracle(
    case,
    case_dir,
    workspace,
  )
  judge_enabled = case.get("judge", {}).get("enabled", False)
  if executor_infrastructure_failure:
    judge = {
      "enabled": judge_enabled,
      "executed": False,
      "verdict": "SKIPPED" if judge_enabled else PASS,
      "rationale": "Semantic judge skipped because executor infrastructure failed.",
      "evidence": [],
      "usage": empty_usage(),
      "duration_ms": 0,
      "failure_category": "infrastructure",
    }
  elif mechanical["passed"] and oracle["passed"] and judge_enabled:
    progress.emit(f"{label}: running judge")
    judge = run_judge(args, runtime.judge, workspace, case, response, mechanical)
  elif judge_enabled:
    judge = {
      "enabled": True,
      "executed": False,
      "verdict": "SKIPPED",
      "rationale": "Semantic judge skipped because mechanical checks failed.",
      "evidence": [],
      "usage": empty_usage(),
      "duration_ms": 0,
      "failure_category": None,
    }
  else:
    judge = disabled_judge("Semantic judge disabled for this case.")
  if executor_infrastructure_failure or judge.get("failure_category") == "infrastructure":
    status = "ERROR"
  elif not mechanical["passed"] or not oracle["passed"]:
    status = "FAIL"
  elif judge["verdict"] == "INCONCLUSIVE":
    status = "INCONCLUSIVE"
  elif judge["verdict"] == PASS:
    status = PASS
  else:
    status = "FAIL"
  observation_finished_at = utc_now()
  result = {
    "case_id": case_id,
    "status": status,
    "kind": case.get("kind", "behavioral"),
    "executor": {
      "enabled": True,
      "executed": True,
      "exit_code": completed.returncode,
      "response": response,
      "stderr": completed.stderr[-4000:],
      "usage": executor_usage,
      "duration_ms": executor_duration_ms,
    },
    "mechanical": mechanical,
    "oracle": oracle,
    "judge": judge,
    "changed_paths": changed,
    "workspace": str(workspace),
    "model_sessions": {
      "executor": 1,
      "judge": 1 if judge.get("executed", False) else 0,
      "total": 1 + (1 if judge.get("executed", False) else 0),
    },
    "usage": aggregate_usage([
      executor_usage,
      judge["usage"],
    ] if judge.get("executed", False) else [executor_usage]),
    "failure_category": (
      None
      if status == PASS
      else "infrastructure"
      if status == "ERROR"
      else "contract"
    ),
    "_started_at": observation_started_at,
    "_finished_at": observation_finished_at,
    "_duration_ms": max(0, round((time.monotonic() - observation_started) * 1000)),
    "_prompt": raw_prompt,
    "_evidence": file_evidence,
  }
  (workspace / ".eval-result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
  progress.emit(f"{label}: {status}")
  return result


def suite_cases(skill: Path) -> list[str]:
  suite = read_json(skill / "evals" / "suite.json")
  if suite.get("version") != 1 or not isinstance(suite.get("cases"), list):
    raise ValueError("suite.json must declare version 1 and a cases array")
  cases = suite["cases"]
  if not all(isinstance(case_id, str) for case_id in cases) or len(cases) != len(set(cases)):
    raise ValueError("suite.json case ids must be unique strings")
  return cases


def case_manifests(skill: Path) -> dict[str, dict[str, Any]]:
  return {
    case_id: load_case_manifest(skill, case_id)[1]
    for case_id in suite_cases(skill)
  }


def case_session_cost(case: dict[str, Any]) -> tuple[int, int]:
  if case.get("kind") == "deterministic":
    return 0, 0
  return 1, 1 if case.get("judge", {}).get("enabled", False) else 0


def select_plan_cases(
  impact: str,
  requested: list[str],
  manifests: dict[str, dict[str, Any]],
) -> tuple[list[str], list[str]]:
  unknown = [case_id for case_id in requested if case_id not in manifests]
  if unknown:
    raise ValueError(f"Unknown evaluation case(s): {', '.join(unknown)}")
  if len(requested) != len(set(requested)):
    raise ValueError("--case values must be unique")
  if impact == "static":
    if requested:
      raise ValueError("static impact does not run evaluation cases")
    return [], []
  if impact == "deterministic":
    selected = requested or [
      case_id for case_id, case in manifests.items() if case.get("kind") == "deterministic"
    ]
    non_deterministic = [
      case_id for case_id in selected if manifests[case_id].get("kind") != "deterministic"
    ]
    if non_deterministic:
      raise ValueError(
        "deterministic impact accepts only deterministic cases: "
        + ", ".join(non_deterministic)
      )
    return selected, []
  if not requested:
    raise ValueError(f"{impact} impact requires at least one --case")
  remaining = [
    case_id for case_id in manifests
    if case_id not in requested
  ] if impact == "cross-cutting" else []
  return requested, remaining


def plan_commands(
  skill: Path,
  baseline: Path,
  impact: str,
  selected: list[str],
  runtime: EvaluationRuntime,
  approved_model_sessions: int,
  workflow: str,
  args: argparse.Namespace,
) -> list[str]:
  commands = [
    shlex.join([
      "python3",
      ".system/skill-creator/scripts/quick_validate.py",
      str(skill),
    ]),
  ]
  if impact == "static":
    return commands
  validate_argv = [
    "python3",
    str(Path(__file__).resolve()),
    "probe-change" if workflow == "diagnostic" else "validate-change",
    "--skill",
    str(skill),
    "--baseline",
    str(baseline),
    "--impact",
    impact,
  ]
  for case_id in selected:
    validate_argv.extend(["--case", case_id])
  if runtime.executor.model_source == "cli" and runtime.executor.model:
    validate_argv.extend(["--model", runtime.executor.model])
  if runtime.executor.reasoning_effort:
    validate_argv.extend(["--reasoning-effort", runtime.executor.reasoning_effort])
  if runtime.judge.model_source == "cli" and runtime.judge.model:
    validate_argv.extend(["--judge-model", runtime.judge.model])
  if (
    runtime.judge.reasoning_effort_source == "cli"
    and runtime.judge.reasoning_effort
  ):
    validate_argv.extend([
      "--judge-reasoning-effort",
      runtime.judge.reasoning_effort,
    ])
  validate_argv.extend([
    "--approved-model-sessions",
    str(approved_model_sessions),
  ])
  if getattr(args, "campaign_ledger", None) is not None:
    validate_argv.extend([
      "--campaign-ledger",
      str(args.campaign_ledger),
      "--approved-cumulative-model-sessions",
      str(args.approved_cumulative_model_sessions),
    ])
  commands.insert(
    0,
    shlex.join(validate_argv),
  )
  return commands


def manifest_fingerprint(manifests: dict[str, dict[str, Any]]) -> str:
  return fingerprint_payload(manifests)


def case_fingerprints(skill: Path, manifests: dict[str, dict[str, Any]]) -> dict[str, str]:
  return {
    case_id: tree_fingerprint(skill / "evals" / "cases" / case_id)
    for case_id in manifests
  }


def empty_campaign(
  args: argparse.Namespace,
  planned_maximum: int,
) -> dict[str, Any]:
  ledger_path = getattr(args, "campaign_ledger", None)
  approved = getattr(args, "approved_cumulative_model_sessions", None)
  consumed = 0
  reserved = 0
  if ledger_path is not None and ledger_path.exists():
    ledger = read_campaign_ledger(ledger_path)
    consumed = ledger["consumed_model_sessions"]
    reserved = sum(
      reservation["remaining_model_sessions"]
      for reservation in ledger["active_reservations"]
    )
  return {
    "ledger": str(ledger_path.resolve()) if ledger_path is not None else None,
    "approved_cumulative_model_sessions": approved,
    "consumed_before": consumed,
    "reserved_before": reserved,
    "planned_maximum": planned_maximum,
    "projected_maximum": consumed + reserved + planned_maximum,
  }


def new_campaign_ledger() -> dict[str, Any]:
  return {
    "version": 1,
    "consumed_model_sessions": 0,
    "active_reservations": [],
    "history": [],
  }


def validate_campaign_ledger(ledger: dict[str, Any]) -> None:
  if ledger.get("version") != 1:
    raise ValueError("Campaign ledger must declare version 1")
  consumed = ledger.get("consumed_model_sessions")
  active = ledger.get("active_reservations")
  history = ledger.get("history")
  if not isinstance(consumed, int) or consumed < 0:
    raise ValueError("Campaign ledger consumed_model_sessions must be non-negative")
  if not isinstance(active, list) or not isinstance(history, list):
    raise ValueError("Campaign ledger reservations and history must be arrays")
  for reservation in active:
    if (
      not isinstance(reservation, dict)
      or not isinstance(reservation.get("id"), str)
      or not isinstance(reservation.get("remaining_model_sessions"), int)
      or reservation["remaining_model_sessions"] < 0
    ):
      raise ValueError("Campaign ledger contains an invalid active reservation")


def read_campaign_ledger(path: Path) -> dict[str, Any]:
  ledger = read_json(path)
  validate_campaign_ledger(ledger)
  return ledger


def write_campaign_ledger(path: Path, ledger: dict[str, Any]) -> None:
  validate_campaign_ledger(ledger)
  path.parent.mkdir(parents=True, exist_ok=True)
  temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
  temporary.write_text(json.dumps(ledger, indent=2) + "\n", encoding="utf-8")
  os.replace(temporary, path)


def with_campaign_lock(path: Path, action: Any) -> Any:
  lock_path = path.with_name(f"{path.name}.lock")
  lock_path.parent.mkdir(parents=True, exist_ok=True)
  with lock_path.open("a+", encoding="utf-8") as lock:
    fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
    try:
      return action()
    finally:
      fcntl.flock(lock.fileno(), fcntl.LOCK_UN)


def reserve_campaign(
  args: argparse.Namespace,
  planned_maximum: int,
) -> dict[str, Any] | None:
  path = getattr(args, "campaign_ledger", None)
  if path is None:
    return None
  path = path.resolve()
  approved = args.approved_cumulative_model_sessions
  reservation_id = uuid.uuid4().hex

  def reserve():
    ledger = read_campaign_ledger(path) if path.exists() else new_campaign_ledger()
    reserved = sum(
      item["remaining_model_sessions"]
      for item in ledger["active_reservations"]
    )
    projected = ledger["consumed_model_sessions"] + reserved + planned_maximum
    if projected > approved:
      raise ValueError(
        f"Campaign requires at most {projected} cumulative model sessions, "
        f"but only {approved} are authorized."
      )
    ledger["active_reservations"].append({
      "id": reservation_id,
      "planned_model_sessions": planned_maximum,
      "remaining_model_sessions": planned_maximum,
    })
    write_campaign_ledger(path, ledger)
    return ledger["consumed_model_sessions"]

  consumed_before = with_campaign_lock(path, reserve)
  return {
    "id": reservation_id,
    "path": path,
    "approved": approved,
    "planned": planned_maximum,
    "consumed_before": consumed_before,
    "consumed_operation": 0,
  }


def record_campaign_consumption(reservation: dict[str, Any] | None, count: int) -> None:
  if reservation is None or count == 0:
    return

  def record():
    ledger = read_campaign_ledger(reservation["path"])
    active = next(
      (item for item in ledger["active_reservations"] if item["id"] == reservation["id"]),
      None,
    )
    if active is None or active["remaining_model_sessions"] < count:
      raise ValueError("Campaign reservation is missing or smaller than actual consumption")
    active["remaining_model_sessions"] -= count
    ledger["consumed_model_sessions"] += count
    write_campaign_ledger(reservation["path"], ledger)

  with_campaign_lock(reservation["path"], record)
  reservation["consumed_operation"] += count


def finish_campaign(
  reservation: dict[str, Any] | None,
  status: str,
) -> dict[str, Any] | None:
  if reservation is None:
    return None

  def finish():
    ledger = read_campaign_ledger(reservation["path"])
    ledger["active_reservations"] = [
      item
      for item in ledger["active_reservations"]
      if item["id"] != reservation["id"]
    ]
    ledger["history"].append({
      "id": reservation["id"],
      "planned_model_sessions": reservation["planned"],
      "consumed_model_sessions": reservation["consumed_operation"],
      "status": status,
    })
    write_campaign_ledger(reservation["path"], ledger)
    return ledger["consumed_model_sessions"]

  consumed_after = with_campaign_lock(reservation["path"], finish)
  return {
    "ledger": str(reservation["path"]),
    "approved_cumulative_model_sessions": reservation["approved"],
    "planned_maximum": reservation["planned"],
    "consumed_before": reservation["consumed_before"],
    "consumed_operation": reservation["consumed_operation"],
    "consumed_after": consumed_after,
  }


def resolve_runtime(
  args: argparse.Namespace,
  executor_required: bool,
  judge_required: bool,
) -> EvaluationRuntime:
  cli_model = getattr(args, "model", None)
  environment_model = os.environ.get("CODEX_MODEL")
  executor_model = cli_model or environment_model
  executor_model_source = (
    "cli"
    if cli_model
    else "environment"
    if environment_model
    else "configured-default"
  )
  executor_effort = getattr(args, "reasoning_effort", None)
  executor_effort_source = "cli" if executor_effort else "configured-default"
  executor = RoleRuntime(
    required=executor_required,
    model=executor_model,
    model_source=executor_model_source,
    reasoning_effort=executor_effort,
    reasoning_effort_source=executor_effort_source,
  )

  judge_cli_model = getattr(args, "judge_model", None)
  judge_cli_effort = getattr(args, "judge_reasoning_effort", None)
  judge = RoleRuntime(
    required=judge_required,
    model=judge_cli_model or executor.model,
    model_source="cli" if judge_cli_model else "executor",
    reasoning_effort=judge_cli_effort or executor.reasoning_effort,
    reasoning_effort_source="cli" if judge_cli_effort else "executor",
  )
  executor_complete = (
    not executor.required
    or (
      executor.model is not None
      and executor.model_source == "cli"
      and executor.reasoning_effort is not None
      and executor.reasoning_effort_source == "cli"
    )
  )
  judge_complete = (
    not judge.required
    or (
      judge.model is not None
      and judge.reasoning_effort is not None
      and (
        judge.model_source == "cli"
        or (judge.model_source == "executor" and executor_complete)
      )
      and (
        judge.reasoning_effort_source == "cli"
        or (
          judge.reasoning_effort_source == "executor"
          and executor_complete
        )
      )
    )
  )
  required = executor_required or judge_required
  complete = executor_complete and judge_complete
  audit_quality = (
    "not_applicable"
    if not required
    else "promotion"
    if complete
    else "exploratory"
  )
  return EvaluationRuntime(
    required=required,
    complete=complete,
    audit_quality=audit_quality,
    executor=executor,
    judge=judge,
  )


def runtime_fingerprint(
  manifest_digest: str,
  runtime: EvaluationRuntime,
) -> str:
  payload = {
    "manifest_fingerprint": manifest_digest,
    "executor": runtime.executor.as_dict(),
    "judge": runtime.judge.as_dict(),
  }
  encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
  return hashlib.sha256(encoded).hexdigest()


def execution_blockers(
  runtime: EvaluationRuntime,
  total_sessions: int,
  approved_model_sessions: int,
  campaign: dict[str, Any],
) -> list[dict[str, str]]:
  blockers = []
  if runtime.executor.required and (
    runtime.executor.model_source != "cli"
    or runtime.executor.model is None
    or runtime.executor.reasoning_effort_source != "cli"
    or runtime.executor.reasoning_effort is None
  ):
    blockers.append({
      "code": "executor-runtime-explicit-required",
      "message": "Model-backed promotion requires executor model and reasoning effort from CLI.",
    })
  if runtime.judge.required and (
    runtime.judge.model is None or runtime.judge.reasoning_effort is None
  ):
    blockers.append({
      "code": "judge-runtime-unresolved",
      "message": "The required judge model and reasoning effort could not be resolved.",
    })
  if total_sessions > approved_model_sessions:
    blockers.append({
      "code": "insufficient-model-session-budget",
      "message": (
        f"Plan requires at most {total_sessions} model sessions, "
        f"but only {approved_model_sessions} are authorized."
      ),
    })
  approved_cumulative = campaign["approved_cumulative_model_sessions"]
  if (
    approved_cumulative is not None
    and campaign["projected_maximum"] > approved_cumulative
  ):
    blockers.append({
      "code": "insufficient-cumulative-model-session-budget",
      "message": (
        f"Campaign requires at most {campaign['projected_maximum']} cumulative "
        f"model sessions, but only {approved_cumulative} are authorized."
      ),
    })
  return blockers


def build_eval_plan(
  skill: Path,
  baseline: Path,
  impact: str,
  requested_cases: list[str],
  args: argparse.Namespace,
  approved_model_sessions: int = DEFAULT_APPROVED_MODEL_SESSIONS,
) -> dict[str, Any]:
  skill = skill.resolve()
  baseline = baseline.resolve()
  if not (skill / "SKILL.md").is_file():
    raise ValueError(f"Skill path has no SKILL.md: {skill}")
  if not (baseline / "SKILL.md").is_file():
    raise ValueError(f"Baseline path has no SKILL.md: {baseline}")
  manifests = {} if impact == "static" else case_manifests(skill)
  selected, remaining = select_plan_cases(impact, requested_cases, manifests)
  workflow = getattr(args, "workflow", "promotion")
  baseline_executor = baseline_judge = 0
  candidate_executor = candidate_judge = 0
  candidate_repetitions = 1 if workflow == "diagnostic" else 3
  for case_id in selected:
    executor, judge = case_session_cost(manifests[case_id])
    baseline_executor += executor
    baseline_judge += judge
    candidate_executor += executor * candidate_repetitions
    candidate_judge += judge * candidate_repetitions
  for case_id in remaining:
    executor, judge = case_session_cost(manifests[case_id])
    candidate_executor += executor
    candidate_judge += judge
  executor_sessions = baseline_executor + candidate_executor
  judge_sessions = baseline_judge + candidate_judge
  total_sessions = executor_sessions + judge_sessions
  campaign = empty_campaign(args, total_sessions)
  runtime = resolve_runtime(
    args,
    executor_required=executor_sessions > 0,
    judge_required=judge_sessions > 0,
  )
  reasons = {
    "static": ["Only structural gates are proposed because the change cannot affect skill behavior."],
    "deterministic": ["Selected behavior is fully observable by direct mechanical checks."],
    "scoped": ["RED, GREEN, and stability are limited to the explicitly affected cases."],
    "cross-cutting": [
      "Affected cases receive RED, GREEN, and stability gates.",
      "Every remaining suite case runs once because the change has unbounded reach.",
    ],
  }[impact]
  warnings = [
    "Session counts exclude tokens, duration, and financial cost.",
    "Sandbox or shell approval is not approval for model session consumption.",
  ]
  if impact != "cross-cutting":
    warnings.append("Underclassifying an uncertain change is a workflow error; use cross-cutting when reach is unclear.")
  plan = {
    "operation": "plan",
    "workflow": workflow,
    "promotion_eligible": workflow == "promotion",
    "skill": str(skill),
    "baseline": str(baseline),
    "impact": impact,
    "selected_cases": selected,
    "regression_cases": remaining,
    "steps": (
      ["structural-validation"]
      if impact == "static"
      else (
        ["baseline-red", "candidate-observation"]
        + (["remaining-suite-regression"] if remaining else [])
        + ["structural-validation"]
        if workflow == "diagnostic"
        else ["baseline-red", "candidate-green-1"]
        + (["remaining-suite-regression"] if remaining else [])
        + ["candidate-green-2-and-3", "structural-validation"]
      )
    ),
    "commands": plan_commands(
      skill,
      baseline,
      impact,
      selected,
      runtime,
      approved_model_sessions,
      workflow,
      args,
    ),
    "executions": {
      "baseline": {"affected": len(selected), "total": len(selected)},
      "candidate": {
        "affected": len(selected) * candidate_repetitions,
        "regression": len(remaining),
        "total": len(selected) * candidate_repetitions + len(remaining),
      },
    },
    "sessions": {
      "baseline": {
        "executor": baseline_executor,
        "judge": baseline_judge,
        "total": baseline_executor + baseline_judge,
      },
      "candidate": {
        "executor": candidate_executor,
        "judge": candidate_judge,
        "total": candidate_executor + candidate_judge,
      },
      "executor": executor_sessions,
      "judge": judge_sessions,
      "total": total_sessions,
    },
    "approved_model_sessions": approved_model_sessions,
    "approval_required": total_sessions > approved_model_sessions,
    "reasons": reasons,
    "warnings": warnings,
    "manifest_fingerprint": manifest_fingerprint(manifests),
    "case_fingerprints": case_fingerprints(skill, manifests),
    "source_fingerprints": {
      "baseline": tree_fingerprint(baseline),
      "candidate": tree_fingerprint(skill),
    },
    "runtime": runtime.as_dict(),
    "runtime_fingerprint": runtime_fingerprint(
      manifest_fingerprint(manifests),
      runtime,
    ),
    "campaign": campaign,
    "execution_blockers": execution_blockers(
      runtime,
      total_sessions,
      approved_model_sessions,
      campaign,
    ),
  }
  plan["evaluation_fingerprint"] = fingerprint_payload({
    "workflow": workflow,
    "impact": impact,
    "selected_cases": selected,
    "regression_cases": remaining,
    "case_fingerprints": plan["case_fingerprints"],
    "source_fingerprints": plan["source_fingerprints"],
    "runtime_fingerprint": plan["runtime_fingerprint"],
  })
  validate_eval_plan(plan)
  return plan


def validate_eval_plan(plan: dict[str, Any]) -> None:
  required = {
    "operation",
    "workflow",
    "promotion_eligible",
    "skill",
    "baseline",
    "impact",
    "selected_cases",
    "regression_cases",
    "steps",
    "commands",
    "executions",
    "sessions",
    "approved_model_sessions",
    "approval_required",
    "reasons",
    "warnings",
    "manifest_fingerprint",
    "case_fingerprints",
    "source_fingerprints",
    "evaluation_fingerprint",
    "runtime",
    "runtime_fingerprint",
    "execution_blockers",
    "campaign",
  }
  missing = sorted(required - plan.keys())
  if missing:
    raise ValueError(f"Evaluation plan is missing fields: {', '.join(missing)}")
  if (
    plan["operation"] != "plan"
    or plan["impact"] not in IMPACTS
    or plan["workflow"] not in WORKFLOWS
  ):
    raise ValueError("Invalid evaluation plan operation or impact")
  if plan["promotion_eligible"] != (plan["workflow"] == "promotion"):
    raise ValueError("Evaluation plan promotion eligibility is inconsistent")
  if not isinstance(plan["sessions"].get("total"), int) or plan["sessions"]["total"] < 0:
    raise ValueError("Evaluation plan session total must be a non-negative integer")
  sessions = plan["sessions"]
  if sessions["total"] != sessions["executor"] + sessions["judge"]:
    raise ValueError("Evaluation plan session total does not match executor and judge counts")
  for phase in ("baseline", "candidate"):
    phase_sessions = sessions[phase]
    if phase_sessions["total"] != phase_sessions["executor"] + phase_sessions["judge"]:
      raise ValueError(f"Evaluation plan {phase} session total is inconsistent")
  if sessions["total"] != sessions["baseline"]["total"] + sessions["candidate"]["total"]:
    raise ValueError("Evaluation plan phase session totals are inconsistent")
  expected_approval = sessions["total"] > plan["approved_model_sessions"]
  if plan["approval_required"] != expected_approval:
    raise ValueError("Evaluation plan approval flag is inconsistent with its session limit")
  if not isinstance(plan["execution_blockers"], list):
    raise ValueError("Evaluation plan blockers must be a list")


def aggregate_status(results: list[dict[str, Any]]) -> str:
  for status in ("ERROR", "INCONCLUSIVE", "UNSTABLE", "INVALID_RED", "FAIL"):
    if any(result.get("status") == status for result in results):
      return status
  return PASS


def verdict_signature(result: dict[str, Any]) -> str:
  signature = {
    "status": result["status"],
    "checks": [(item["name"], item["passed"]) for item in result["mechanical"]["checks"]],
    "judge": result["judge"]["verdict"],
    "changed_paths": [path for path in result["changed_paths"] if outcome_path(path)],
  }
  return json.dumps(signature, sort_keys=True)


def outcome_path(path: str) -> bool:
  parts = Path(path).parts
  return not path.startswith(".eval-") and "__pycache__" not in parts and not path.endswith(".pyc")


def make_operation_root(args: argparse.Namespace) -> Path:
  args.artifacts_dir.mkdir(parents=True, exist_ok=True)
  return Path(tempfile.mkdtemp(prefix=f"{args.operation}-", dir=args.artifacts_dir))


def remove_operation_root(operation_root: Path) -> None:
  def make_writable_and_retry(function: Any, path: str, _: Any) -> None:
    target = Path(path)
    if target.exists():
      os.chmod(target, stat.S_IRWXU)
    if target.parent.exists():
      os.chmod(target.parent, stat.S_IRWXU)
    function(path)

  shutil.rmtree(operation_root, onerror=make_writable_and_retry)


def resolved_model_label(runtime: EvaluationRuntime) -> str:
  return runtime.executor.model or "configured-default"


def aggregate_model_sessions(results: list[dict[str, Any]]) -> dict[str, int]:
  executor = sum(result["model_sessions"]["executor"] for result in results)
  judge = sum(result["model_sessions"]["judge"] for result in results)
  return {"executor": executor, "judge": judge, "total": executor + judge}


def aggregate_result_usage(results: list[dict[str, Any]]) -> dict[str, Any]:
  return aggregate_usage([
    result["usage"]
    for result in results
    if result["model_sessions"]["total"] > 0
  ])


def workflow_failure_category(
  status: str,
  results: list[dict[str, Any]],
) -> str | None:
  if status == PASS:
    return None
  if any(result.get("failure_category") == "infrastructure" for result in results):
    return "infrastructure"
  return "contract"


def ensure_operation_context(args: argparse.Namespace) -> None:
  if not hasattr(args, "_operation_started_at"):
    args._operation_started_at = utc_now()
    args._operation_started_monotonic = time.monotonic()
    timestamp = args._operation_started_at.replace("-", "").replace(":", "")
    args._operation_id = f"{timestamp}-{uuid.uuid4().hex[:12]}"


def planned_sessions_for_report(
  stdout_report: dict[str, Any],
  results: list[dict[str, Any]],
) -> dict[str, int]:
  if isinstance(stdout_report.get("plan"), dict):
    sessions = stdout_report["plan"]["sessions"]
    return {
      "executor": sessions["executor"],
      "judge": sessions["judge"],
      "total": sessions["total"],
    }
  executor = sum(
    1 if result.get("executor", {}).get("enabled", False) else 0
    for result in results
  )
  judge = sum(
    1 if result.get("judge", {}).get("enabled", False) else 0
    for result in results
  )
  return {"executor": executor, "judge": judge, "total": executor + judge}


def normalized_executor_response(response: Any) -> dict[str, Any] | None:
  if not isinstance(response, dict):
    return None
  arrays = (
    "approach",
    "decisions",
    "rejected_alternatives",
    "key_changes",
    "validation",
  )
  normalized = {
    "summary": response.get("summary", ""),
    "classification": response.get("classification", ""),
    "evidence": response.get("evidence", []),
    "files_changed": response.get("files_changed", []),
    "diagnosis": response.get("diagnosis", response.get("summary", "")),
  }
  for field in arrays:
    value = response.get(field, [])
    normalized[field] = value if isinstance(value, list) else []
  return sanitize_fact(normalized)


def canonical_observation(
  result: dict[str, Any],
  status: str,
) -> dict[str, Any]:
  workspace_path = result.get("workspace")
  retained = status in BLOCKING
  mechanical = sanitize_fact(result.get("mechanical", {}))
  oracle = sanitize_fact(result.get("oracle", {}))
  judge = sanitize_fact(result.get("judge", {}))
  executor = result.get("executor", {})
  return {
    "case_id": result.get("case_id", "unknown"),
    "status": result.get("status", "ERROR"),
    "kind": result.get("kind"),
    "role": result.get("role", "observation"),
    "repetition": result.get("repetition", 1),
    "provenance": "executed",
    "started_at": result.get("_started_at"),
    "finished_at": result.get("_finished_at"),
    "duration_ms": result.get("_duration_ms"),
    "prompt": result.get("_prompt"),
    "executor": {
      "enabled": executor.get("enabled", False),
      "executed": executor.get("executed", False),
      "exit_code": executor.get("exit_code"),
      "duration_ms": executor.get("duration_ms", 0),
      "response": normalized_executor_response(executor.get("response")),
      "usage": executor.get("usage", empty_usage()),
    },
    "mechanical": mechanical,
    "oracle": oracle,
    "judge": {
      "enabled": judge.get("enabled", False),
      "executed": judge.get("executed", False),
      "verdict": judge.get("verdict", "SKIPPED"),
      "rationale": judge.get("rationale", ""),
      "evidence": judge.get("evidence", []),
      "duration_ms": judge.get("duration_ms", 0),
      "usage": judge.get("usage", empty_usage()),
      "failure_category": judge.get("failure_category"),
    },
    "sessions": result.get(
      "model_sessions",
      {"executor": 0, "judge": 0, "total": 0},
    ),
    "usage": result.get("usage", empty_usage()),
    "evidence": result.get("_evidence", {
      "changed_files": [],
      "diff": "",
      "fragments": [],
      "truncated": False,
      "truncations": [],
      "limits": {},
    }),
    "workspace": {
      "original_path": workspace_path,
      "retention": "retained" if retained else "removed",
    },
  }


def persist_execution_report(
  args: argparse.Namespace,
  stdout_report: dict[str, Any],
  results: list[dict[str, Any]],
  runtime: EvaluationRuntime,
) -> Path | None:
  report_dir = getattr(args, "report_dir", None)
  if report_dir is None:
    return None
  ensure_operation_context(args)
  finished_at = utc_now()
  environment = codex_environment(args.codex_command)
  pricing = load_pricing(getattr(args, "pricing_file", None))
  plan = stdout_report.get("plan")
  skill = args.skill.resolve()
  if isinstance(plan, dict):
    fingerprints = {
      "manifest": plan["manifest_fingerprint"],
      "cases": plan["case_fingerprints"],
      "sources": plan["source_fingerprints"],
      "runtime": plan["runtime_fingerprint"],
      "evaluation": plan["evaluation_fingerprint"],
    }
  else:
    manifests = case_manifests(skill)
    manifest_hash = manifest_fingerprint(manifests)
    runtime_hash = runtime_fingerprint(manifest_hash, runtime)
    source_hashes = {"evaluated": tree_fingerprint(skill)}
    case_hashes = case_fingerprints(skill, manifests)
    fingerprints = {
      "manifest": manifest_hash,
      "cases": case_hashes,
      "sources": source_hashes,
      "runtime": runtime_hash,
      "evaluation": fingerprint_payload({
        "operation": args.operation,
        "cases": [
          result.get("case_id")
          for result in results
        ],
        "case_fingerprints": case_hashes,
        "source_fingerprints": source_hashes,
        "runtime_fingerprint": runtime_hash,
      }),
    }
  estimate = api_reference_estimate(
    pricing,
    stdout_report["usage"],
    runtime.executor.model,
    environment["billing_mode"],
  )
  report = {
    "schema_version": 1,
    "operation": {
      "id": args._operation_id,
      "type": args.operation,
      "status": stdout_report["status"],
      "workflow": getattr(args, "workflow", None),
      "promotion_eligible": stdout_report.get("promotion_eligible", False),
      "failure_category": stdout_report.get("failure_category"),
    },
    "provenance": "executed",
    "started_at": args._operation_started_at,
    "finished_at": finished_at,
    "duration_ms": max(
      0,
      round((time.monotonic() - args._operation_started_monotonic) * 1000),
    ),
    "skill": {
      "path": str(skill),
      "name": skill.name,
    },
    "fingerprints": fingerprints,
    "environment": {
      "codex_cli": environment["codex_cli"],
      "authentication": environment["authentication"],
      "runner": {
        "path": str(Path(__file__).resolve()),
        "sha256": file_hash(Path(__file__).resolve()),
      },
    },
    "billing": {
      "mode": environment["billing_mode"],
      "actual_charge_observed": False,
    },
    "runtime": runtime.as_dict(),
    "sessions": {
      "planned": planned_sessions_for_report(stdout_report, results),
      "executed": stdout_report["model_sessions"],
      "provenance": "executed",
    },
    "usage": stdout_report["usage"],
    "pricing": pricing,
    "api_reference_estimate": estimate,
    "observations": [
      canonical_observation(result, stdout_report["status"])
      for result in results
    ],
    "limitations": [
      "No raw Codex JSONL or complete transcript is persisted.",
      "Structured executor fields record concise declared decisions, not private reasoning.",
      "Diffs and text fragments are sanitized and bounded.",
    ],
  }
  report["report_digest"] = {
    "algorithm": "sha256",
    "value": report_digest(report),
  }
  operation_dir = report_dir.resolve() / args._operation_id
  report_path = operation_dir / "report.json"
  markdown_path = operation_dir / "report.md"
  atomic_write_text(
    report_path,
    json.dumps(report, indent=2, ensure_ascii=False) + "\n",
  )
  atomic_write_text(markdown_path, render_report(report))
  return report_path


def strip_internal_result_fields(results: list[dict[str, Any]]) -> None:
  for result in results:
    for field in tuple(result):
      if field.startswith("_"):
        result.pop(field)


def run_change_workflow(
  args: argparse.Namespace,
  plan: dict[str, Any],
  progress: ProgressReporter,
  reservation: dict[str, Any] | None,
) -> dict[str, Any]:
  skill = args.skill.resolve()
  baseline = args.baseline.resolve()
  runtime = resolve_runtime(
    args,
    executor_required=plan["sessions"]["executor"] > 0,
    judge_required=plan["sessions"]["judge"] > 0,
  )
  operation_root: Path | None = None
  results = []
  status = PASS
  invalid_red = False

  def observe(
    installed_source: Path,
    case_source: Path,
    case_id: str,
    role: str,
    context: str,
    repetition: int | None = None,
  ) -> dict[str, Any]:
    if operation_root is None:
      raise ValueError("Operation workspace is not initialized")
    result = evaluate_case(
      args,
      runtime,
      installed_source,
      case_source,
      case_id,
      operation_root,
      progress,
      context,
    )
    result["role"] = role
    if repetition is not None:
      result["repetition"] = repetition
    results.append(result)
    record_campaign_consumption(reservation, result["model_sessions"]["total"])
    return result

  try:
    operation_root = make_operation_root(args)
    source_root = operation_root / "source"
    source_root.mkdir()
    baseline_snapshot = materialize_skill_source(
      baseline, "working-tree", source_root / "baseline"
    )
    candidate_snapshot = materialize_skill_source(
      skill, "working-tree", source_root / "candidate"
    )
    snapshot_plan = build_eval_plan(
      candidate_snapshot,
      baseline_snapshot,
      args.impact,
      args.case,
      args,
      args.approved_model_sessions,
    )
    stable_plan_fields = (
      "workflow",
      "selected_cases",
      "regression_cases",
      "executions",
      "sessions",
      "approval_required",
      "manifest_fingerprint",
      "case_fingerprints",
      "source_fingerprints",
      "runtime_fingerprint",
      "evaluation_fingerprint",
    )
    if any(snapshot_plan[field] != plan[field] for field in stable_plan_fields):
      raise ValueError("Evaluation inputs changed after cost planning")

    for case_id in plan["selected_cases"]:
      result = observe(
        baseline_snapshot,
        candidate_snapshot,
        case_id,
        "baseline",
        "baseline",
      )
      if result["status"] == PASS:
        invalid_red = True
        if args.workflow == "promotion":
          status = "INVALID_RED"
          break
      elif result["failure_category"] == "infrastructure":
        status = result["status"]
        break
      elif result["status"] != "FAIL" and args.workflow == "promotion":
        status = result["status"]
        break

    signatures: dict[str, list[str]] = {
      case_id: [] for case_id in plan["selected_cases"]
    }
    if status == PASS:
      for case_id in plan["selected_cases"]:
        result = observe(
          candidate_snapshot,
          candidate_snapshot,
          case_id,
          "candidate",
          (
            "candidate observation"
            if args.workflow == "diagnostic"
            else "candidate repetition 1/3"
          ),
          1,
        )
        signatures[case_id].append(verdict_signature(result))
        if result["failure_category"] == "infrastructure":
          status = result["status"]
          break
        if result["status"] != PASS and args.workflow == "promotion":
          status = result["status"]
          break

    if status == PASS:
      for case_id in plan["regression_cases"]:
        result = observe(
          candidate_snapshot,
          candidate_snapshot,
          case_id,
          "regression",
          "regression",
        )
        if result["failure_category"] == "infrastructure":
          status = result["status"]
          break
        if result["status"] != PASS and args.workflow == "promotion":
          status = result["status"]
          break

    if status == PASS and args.workflow == "promotion":
      for run_number in (2, 3):
        for case_id in plan["selected_cases"]:
          result = observe(
            candidate_snapshot,
            candidate_snapshot,
            case_id,
            "candidate",
            f"candidate repetition {run_number}/3",
            run_number,
          )
          signatures[case_id].append(verdict_signature(result))
          if result["status"] != PASS:
            status = result["status"]
            break
        if status != PASS:
          break
      if status == PASS and any(
        len(set(case_signatures)) != 1
        for case_signatures in signatures.values()
      ):
        status = "UNSTABLE"

    if args.workflow == "diagnostic" and status == PASS:
      if invalid_red:
        status = "INVALID_RED"
      else:
        status = aggregate_status([
          result for result in results if result["role"] != "baseline"
        ])
  except Exception:
    finish_campaign(reservation, "ERROR")
    raise

  campaign = finish_campaign(reservation, status)
  actual_sessions = aggregate_model_sessions(results)
  if campaign is None:
    campaign = {
      **plan["campaign"],
      "consumed_operation": actual_sessions["total"],
      "consumed_after": None,
    }
  report = {
    "operation": args.operation,
    "status": status,
    "workflow": args.workflow,
    "promotion_eligible": args.workflow == "promotion" and status == PASS,
    "failure_category": workflow_failure_category(status, results),
    "skill": str(skill),
    "model": resolved_model_label(runtime),
    "runtime": runtime.as_dict(),
    "model_sessions": actual_sessions,
    "usage": aggregate_result_usage(results),
    "campaign": campaign,
    "plan": plan,
    "results": results,
    "artifacts": str(operation_root) if status in BLOCKING else None,
  }
  evidence_path = persist_execution_report(
    args,
    report,
    results,
    runtime,
  )
  if evidence_path is not None:
    report["evidence_report"] = str(evidence_path)
  if status == PASS:
    remove_operation_root(operation_root)
    for result in results:
      result["workspace"] = None
  strip_internal_result_fields(results)
  return report


def execute(args: argparse.Namespace, progress: ProgressReporter | None = None) -> dict[str, Any]:
  progress = progress or ProgressReporter(False)
  progress.emit(f"Preparing {args.operation}")
  ensure_operation_context(args)
  skill = args.skill.resolve()
  if args.operation == "plan":
    return build_eval_plan(skill, args.baseline, args.impact, args.case, args)
  if args.operation in {"probe-change", "validate-change"}:
    plan = build_eval_plan(
      skill,
      args.baseline,
      args.impact,
      args.case,
      args,
      args.approved_model_sessions,
    )
    if plan["execution_blockers"]:
      plan["requested_operation"] = args.operation
      plan["_exit_code"] = 2
      return plan
    reservation = reserve_campaign(args, plan["sessions"]["total"])
    return run_change_workflow(args, plan, progress, reservation)

  operation_root = make_operation_root(args)
  source_root = operation_root / "source"
  source_root.mkdir()
  if args.operation == "run":
    installed_source = materialize_skill_source(skill, args.source, source_root)
    case_ids = suite_cases(skill) if args.all else [args.case]
    manifests = [load_case_manifest(skill, case_id)[1] for case_id in case_ids]
    runtime = resolve_runtime(
      args,
      executor_required=any(case_session_cost(case)[0] for case in manifests),
      judge_required=any(case_session_cost(case)[1] for case in manifests),
    )
    results = [
      evaluate_case(
        args,
        runtime,
        installed_source,
        skill,
        case_id,
        operation_root,
        progress,
      )
      for case_id in case_ids
    ]
    status = aggregate_status(results)
  elif args.operation == "verify-change":
    manifest = load_case_manifest(skill, args.case)[1]
    executor_cost, judge_cost = case_session_cost(manifest)
    runtime = resolve_runtime(
      args,
      executor_required=executor_cost > 0,
      judge_required=judge_cost > 0,
    )
    baseline_spec = args.baseline or "git:HEAD"
    if baseline_spec.startswith("git:"):
      baseline = materialize_skill_source(skill, baseline_spec, source_root / "baseline")
    else:
      baseline = Path(baseline_spec).resolve()
    candidate = skill
    baseline_result = evaluate_case(
      args,
      runtime,
      baseline,
      skill,
      args.case,
      operation_root,
      progress,
      "baseline",
    )
    baseline_result["role"] = "baseline"
    candidate_result = evaluate_case(
      args,
      runtime,
      candidate,
      skill,
      args.case,
      operation_root,
      progress,
      "candidate",
    )
    candidate_result["role"] = "candidate"
    results = [baseline_result, candidate_result]
    if baseline_result["status"] == PASS:
      status = "INVALID_RED"
    elif baseline_result["status"] == "FAIL" and candidate_result["status"] == PASS:
      status = PASS
    else:
      status = aggregate_status(results)
  else:
    installed_source = materialize_skill_source(skill, args.source, source_root)
    manifest = load_case_manifest(skill, args.case)[1]
    executor_cost, judge_cost = case_session_cost(manifest)
    runtime = resolve_runtime(
      args,
      executor_required=executor_cost > 0,
      judge_required=judge_cost > 0,
    )
    results = [
      evaluate_case(
        args,
        runtime,
        installed_source,
        skill,
        args.case,
        operation_root,
        progress,
        f"repetition {run_number}/{args.runs}",
      )
      for run_number in range(1, args.runs + 1)
    ]
    for run_number, result in enumerate(results, start=1):
      result["role"] = "observation"
      result["repetition"] = run_number
    signatures = {verdict_signature(result) for result in results}
    status = aggregate_status(results) if len(signatures) == 1 else "UNSTABLE"

  report = {
    "operation": args.operation,
    "status": status,
    "skill": str(skill),
    "model": resolved_model_label(runtime),
    "runtime": runtime.as_dict(),
    "model_sessions": aggregate_model_sessions(results),
    "usage": aggregate_result_usage(results),
    "promotion_eligible": False,
    "failure_category": workflow_failure_category(status, results),
    "campaign": None,
    "results": results,
    "artifacts": str(operation_root) if status in BLOCKING else None,
  }
  evidence_path = persist_execution_report(
    args,
    report,
    results,
    runtime,
  )
  if evidence_path is not None:
    report["evidence_report"] = str(evidence_path)
  if status == PASS:
    remove_operation_root(operation_root)
    for result in results:
      result["workspace"] = None
  strip_internal_result_fields(results)
  return report


def main(argv: list[str] | None = None) -> int:
  progress = ProgressReporter(False)
  try:
    args = parse_args(argv)
    progress = ProgressReporter(progress_enabled(args))
    report = execute(args, progress)
  except (OSError, ValueError, subprocess.SubprocessError) as error:
    operation = (
      argv[0]
      if argv
      else sys.argv[1]
      if len(sys.argv) > 1
      else "run"
    )
    report = {
      "operation": operation,
      "status": "ERROR",
      "skill": "unknown",
      "model": "unknown",
      "runtime": {
        "required": False,
        "complete": False,
        "audit_quality": "not_applicable",
        "executor": {
          "required": False,
          "model": None,
          "model_source": "configured-default",
          "reasoning_effort": None,
          "reasoning_effort_source": "configured-default",
        },
        "judge": {
          "required": False,
          "model": None,
          "model_source": "executor",
          "reasoning_effort": None,
          "reasoning_effort_source": "executor",
        },
      },
      "model_sessions": {"executor": 0, "judge": 0, "total": 0},
      "usage": empty_usage(),
      "promotion_eligible": False,
      "failure_category": "infrastructure",
      "campaign": None,
      "results": [{"status": "ERROR", "error": str(error)}],
      "artifacts": None,
    }
  exit_code = report.pop("_exit_code", None)
  final_label = report.get("status", "APPROVAL_REQUIRED" if report.get("approval_required") else "READY")
  progress.emit(f"Final result: {final_label}")
  print(json.dumps(report, indent=2))
  if exit_code is not None:
    return exit_code
  if report["operation"] == "plan" and report.get("status") != "ERROR":
    return 0
  return 0 if report["status"] == PASS else 1


if __name__ == "__main__":
  sys.exit(main())
