#!/usr/bin/env python3
"""Run isolated, structured forward evaluations for Codex skills."""

import argparse
from dataclasses import dataclass
import fnmatch
import hashlib
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tarfile
import tempfile
from typing import Any


PASS = "PASS"
BLOCKING = {"FAIL", "ERROR", "INCONCLUSIVE", "INVALID_RED", "UNSTABLE"}
IMPACTS = ("static", "deterministic", "scoped", "cross-cutting")
DEFAULT_APPROVED_MODEL_SESSIONS = 8


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
  add_runtime_selection_arguments(plan_parser)

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
  add_runtime_arguments(validate_parser)

  args = parser.parse_args(argv)
  if hasattr(args, "runs") and args.runs < 2:
    parser.error("--runs must be at least 2")
  if hasattr(args, "approved_model_sessions") and args.approved_model_sessions < 0:
    parser.error("--approved-model-sessions must be non-negative")
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
  progress = parser.add_mutually_exclusive_group()
  progress.add_argument("--progress", action="store_true", help="Show progress on stderr even without a TTY")
  progress.add_argument("--quiet", action="store_true", help="Suppress progress on stderr")


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
    if path.is_file() and ".git" not in path.relative_to(root).parts:
      result[path.relative_to(root).as_posix()] = file_hash(path)
  return result


def changed_paths(before: dict[str, str], after: dict[str, str]) -> list[str]:
  return sorted(path for path in before.keys() | after.keys() if before.get(path) != after.get(path))


def check(name: str, passed: bool, detail: str) -> dict[str, Any]:
  return {"name": name, "passed": passed, "detail": detail}


def write_executor_schema(path: Path) -> None:
  schema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "required": ["summary", "classification", "evidence", "files_changed"],
    "properties": {
      "summary": {"type": "string"},
      "classification": {"type": "string"},
      "evidence": {"type": "array", "items": {"type": "string"}},
      "files_changed": {"type": "array", "items": {"type": "string"}},
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
  }


def disabled_judge(reason: str) -> dict[str, Any]:
  return {
    "enabled": False,
    "executed": False,
    "verdict": PASS,
    "rationale": reason,
    "evidence": [],
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
  progress.emit(f"{label}: preparing workspace")
  workspace = Path(tempfile.mkdtemp(prefix=f"{case_id}-", dir=operation_root))
  fixture = case_dir / "fixture"
  if fixture.exists():
    shutil.copytree(fixture, workspace, dirs_exist_ok=True)
  subprocess.run(["git", "init", "-q"], cwd=workspace, check=True)
  before = snapshot(workspace)
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
  status = PASS if mechanical["passed"] else "FAIL"
  result = {
    "case_id": case_id,
    "status": status,
    "kind": "deterministic",
    "executor": disabled_executor(),
    "mechanical": mechanical,
    "judge": disabled_judge("Deterministic cases do not use a semantic judge."),
    "changed_paths": changed,
    "workspace": str(workspace),
    "model_sessions": {"executor": 0, "judge": 0, "total": 0},
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
  completed = run_process(command, workspace, json.dumps(payload))
  if completed.returncode != 0 or not output.exists():
    return {
      "enabled": True,
      "executed": True,
      "verdict": "INCONCLUSIVE",
      "rationale": f"Judge process failed with exit code {completed.returncode}.",
      "evidence": [completed.stderr[-1000:]],
    }
  try:
    result = read_json(output)
  except (OSError, ValueError, json.JSONDecodeError) as error:
    return {"enabled": True, "executed": True, "verdict": "INCONCLUSIVE", "rationale": str(error), "evidence": []}
  verdict = result.get("verdict")
  if verdict not in {PASS, "FAIL", "INCONCLUSIVE"}:
    verdict = "INCONCLUSIVE"
  return {
    "enabled": True,
    "executed": True,
    "verdict": verdict,
    "rationale": result.get("rationale", ""),
    "evidence": result.get("evidence", []),
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
  skill_before = snapshot(scoped_skill)

  schema = workspace / ".eval-executor-schema.json"
  output = workspace / ".eval-executor-response.json"
  write_executor_schema(schema)
  raw_prompt = (case_dir / case.get("prompt_file", "prompt.md")).read_text(encoding="utf-8")
  if case.get("implicit_skill", False):
    prompt = raw_prompt
  else:
    prompt = f"Use ${installed_source.name} from the repository-scoped skill installation to complete this task.\n\n{raw_prompt}"
  progress.emit(f"{label}: running executor")
  completed = run_process(
    codex_command(args, runtime.executor, workspace, schema, output),
    workspace,
    prompt,
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
  judge_enabled = case.get("judge", {}).get("enabled", False)
  if mechanical["passed"]:
    progress.emit(f"{label}: running judge")
    judge = run_judge(args, runtime.judge, workspace, case, response, mechanical)
  elif judge_enabled:
    judge = {
      "enabled": True,
      "executed": False,
      "verdict": "SKIPPED",
      "rationale": "Semantic judge skipped because mechanical checks failed.",
      "evidence": [],
    }
  else:
    judge = disabled_judge("Semantic judge disabled for this case.")
  if not mechanical["passed"]:
    status = "FAIL"
  elif judge["verdict"] == "INCONCLUSIVE":
    status = "INCONCLUSIVE"
  elif judge["verdict"] == PASS:
    status = PASS
  else:
    status = "FAIL"
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
    },
    "mechanical": mechanical,
    "judge": judge,
    "changed_paths": changed,
    "workspace": str(workspace),
    "model_sessions": {
      "executor": 1,
      "judge": 1 if judge.get("executed", False) else 0,
      "total": 1 + (1 if judge.get("executed", False) else 0),
    },
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
    "validate-change",
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
  commands.insert(
    0,
    shlex.join(validate_argv),
  )
  return commands


def manifest_fingerprint(manifests: dict[str, dict[str, Any]]) -> str:
  encoded = json.dumps(manifests, sort_keys=True, separators=(",", ":")).encode()
  return hashlib.sha256(encoded).hexdigest()


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
  baseline_executor = baseline_judge = 0
  candidate_executor = candidate_judge = 0
  for case_id in selected:
    executor, judge = case_session_cost(manifests[case_id])
    baseline_executor += executor
    baseline_judge += judge
    candidate_executor += executor * 3
    candidate_judge += judge * 3
  for case_id in remaining:
    executor, judge = case_session_cost(manifests[case_id])
    candidate_executor += executor
    candidate_judge += judge
  executor_sessions = baseline_executor + candidate_executor
  judge_sessions = baseline_judge + candidate_judge
  total_sessions = executor_sessions + judge_sessions
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
    "skill": str(skill),
    "baseline": str(baseline),
    "impact": impact,
    "selected_cases": selected,
    "regression_cases": remaining,
    "steps": (
      ["structural-validation"]
      if impact == "static"
      else ["baseline-red", "candidate-green-stability"]
      + (["remaining-suite-regression"] if remaining else [])
      + ["structural-validation"]
    ),
    "commands": plan_commands(
      skill,
      baseline,
      impact,
      selected,
      runtime,
      approved_model_sessions,
    ),
    "executions": {
      "baseline": {"affected": len(selected), "total": len(selected)},
      "candidate": {
        "affected": len(selected) * 3,
        "regression": len(remaining),
        "total": len(selected) * 3 + len(remaining),
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
    "runtime": runtime.as_dict(),
    "runtime_fingerprint": runtime_fingerprint(
      manifest_fingerprint(manifests),
      runtime,
    ),
    "execution_blockers": execution_blockers(
      runtime,
      total_sessions,
      approved_model_sessions,
    ),
  }
  validate_eval_plan(plan)
  return plan


def validate_eval_plan(plan: dict[str, Any]) -> None:
  required = {
    "operation",
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
    "runtime",
    "runtime_fingerprint",
    "execution_blockers",
  }
  missing = sorted(required - plan.keys())
  if missing:
    raise ValueError(f"Evaluation plan is missing fields: {', '.join(missing)}")
  if plan["operation"] != "plan" or plan["impact"] not in IMPACTS:
    raise ValueError("Invalid evaluation plan operation or impact")
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


def resolved_model_label(runtime: EvaluationRuntime) -> str:
  return runtime.executor.model or "configured-default"


def aggregate_model_sessions(results: list[dict[str, Any]]) -> dict[str, int]:
  executor = sum(result["model_sessions"]["executor"] for result in results)
  judge = sum(result["model_sessions"]["judge"] for result in results)
  return {"executor": executor, "judge": judge, "total": executor + judge}


def validate_change(
  args: argparse.Namespace,
  plan: dict[str, Any],
  progress: ProgressReporter,
) -> dict[str, Any]:
  skill = args.skill.resolve()
  baseline = args.baseline.resolve()
  runtime = resolve_runtime(
    args,
    executor_required=plan["sessions"]["executor"] > 0,
    judge_required=plan["sessions"]["judge"] > 0,
  )
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
    "selected_cases",
    "regression_cases",
    "executions",
    "sessions",
    "approval_required",
    "manifest_fingerprint",
    "runtime_fingerprint",
  )
  if any(snapshot_plan[field] != plan[field] for field in stable_plan_fields):
    shutil.rmtree(operation_root)
    raise ValueError("Candidate evaluation manifests changed after cost planning")
  results = []
  status = PASS

  for case_id in plan["selected_cases"]:
    result = evaluate_case(
      args,
      runtime,
      baseline_snapshot,
      candidate_snapshot,
      case_id,
      operation_root,
      progress,
      "baseline",
    )
    result["role"] = "baseline"
    results.append(result)
    if result["status"] == PASS:
      status = "INVALID_RED"
      break
    if result["status"] != "FAIL":
      status = result["status"]
      break

  if status == PASS:
    for case_id in plan["selected_cases"]:
      repetitions = []
      for run_number in range(1, 4):
        result = evaluate_case(
          args,
          runtime,
          candidate_snapshot,
          candidate_snapshot,
          case_id,
          operation_root,
          progress,
          f"candidate repetition {run_number}/3",
        )
        result["role"] = "candidate"
        result["repetition"] = run_number
        results.append(result)
        repetitions.append(result)
        if result["status"] != PASS:
          status = result["status"]
          break
      if status != PASS:
        break
      if len({verdict_signature(result) for result in repetitions}) != 1:
        status = "UNSTABLE"
        break

  if status == PASS:
    for case_id in plan["regression_cases"]:
      result = evaluate_case(
        args,
        runtime,
        candidate_snapshot,
        candidate_snapshot,
        case_id,
        operation_root,
        progress,
        "regression",
      )
      result["role"] = "regression"
      results.append(result)
      if result["status"] != PASS:
        status = result["status"]
        break

  report = {
    "operation": "validate-change",
    "status": status,
    "skill": str(skill),
    "model": resolved_model_label(runtime),
    "runtime": runtime.as_dict(),
    "model_sessions": aggregate_model_sessions(results),
    "plan": plan,
    "results": results,
    "artifacts": str(operation_root) if status in BLOCKING else None,
  }
  if status == PASS:
    shutil.rmtree(operation_root)
    for result in results:
      result["workspace"] = None
  return report


def execute(args: argparse.Namespace, progress: ProgressReporter | None = None) -> dict[str, Any]:
  progress = progress or ProgressReporter(False)
  progress.emit(f"Preparing {args.operation}")
  skill = args.skill.resolve()
  if args.operation == "plan":
    return build_eval_plan(skill, args.baseline, args.impact, args.case, args)
  if args.operation == "validate-change":
    plan = build_eval_plan(
      skill,
      args.baseline,
      args.impact,
      args.case,
      args,
      args.approved_model_sessions,
    )
    if plan["execution_blockers"]:
      plan["requested_operation"] = "validate-change"
      plan["_exit_code"] = 2
      return plan
    return validate_change(args, plan, progress)

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
    signatures = {verdict_signature(result) for result in results}
    status = aggregate_status(results) if len(signatures) == 1 else "UNSTABLE"

  report = {
    "operation": args.operation,
    "status": status,
    "skill": str(skill),
    "model": resolved_model_label(runtime),
    "runtime": runtime.as_dict(),
    "model_sessions": aggregate_model_sessions(results),
    "results": results,
    "artifacts": str(operation_root) if status in BLOCKING else None,
  }
  if status == PASS:
    shutil.rmtree(operation_root)
    for result in results:
      result["workspace"] = None
  return report


def main(argv: list[str] | None = None) -> int:
  progress = ProgressReporter(False)
  try:
    args = parse_args(argv)
    progress = ProgressReporter(progress_enabled(args))
    report = execute(args, progress)
  except (OSError, ValueError, subprocess.SubprocessError) as error:
    operation = argv[0] if argv else "run"
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
      "results": [{"status": "ERROR", "error": str(error)}],
      "artifacts": None,
    }
  exit_code = report.pop("_exit_code", None)
  final_label = report.get("status", "APPROVAL_REQUIRED" if report.get("approval_required") else "READY")
  progress.emit(f"Final result: {final_label}")
  print(json.dumps(report, indent=2))
  if exit_code is not None:
    return exit_code
  if report["operation"] == "plan":
    return 0
  return 0 if report["status"] == PASS else 1


if __name__ == "__main__":
  sys.exit(main())
