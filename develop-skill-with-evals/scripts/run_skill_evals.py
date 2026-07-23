#!/usr/bin/env python3
"""Run isolated, structured forward evaluations for Codex skills."""

import argparse
import fnmatch
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile
from typing import Any


PASS = "PASS"
BLOCKING = {"FAIL", "ERROR", "INCONCLUSIVE", "INVALID_RED", "UNSTABLE"}


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

  args = parser.parse_args(argv)
  if hasattr(args, "runs") and args.runs < 2:
    parser.error("--runs must be at least 2")
  return args


def add_skill_argument(parser: argparse.ArgumentParser) -> None:
  parser.add_argument("--skill", type=Path, required=True)


def add_runtime_arguments(parser: argparse.ArgumentParser) -> None:
  parser.add_argument("--model")
  parser.add_argument("--codex-command", default="codex")
  parser.add_argument("--artifacts-dir", type=Path, default=Path("/tmp/skill-eval-artifacts"))
  progress = parser.add_mutually_exclusive_group()
  progress.add_argument("--progress", action="store_true", help="Show progress on stderr even without a TTY")
  progress.add_argument("--quiet", action="store_true", help="Suppress progress on stderr")


def progress_enabled(args: argparse.Namespace, stream: Any | None = None) -> bool:
  if args.quiet:
    return False
  if args.progress:
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


def run_process(command: list[str], cwd: Path, prompt: str | None = None) -> subprocess.CompletedProcess[str]:
  return subprocess.run(command, cwd=cwd, input=prompt, text=True, capture_output=True, check=False)


def run_judge(
  args: argparse.Namespace,
  workspace: Path,
  case: dict[str, Any],
  response: dict[str, Any] | None,
  mechanical: dict[str, Any],
) -> dict[str, Any]:
  judge = case.get("judge", {})
  if not judge.get("enabled", False):
    return {"enabled": False, "verdict": PASS, "rationale": "Semantic judge disabled for this case.", "evidence": []}

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
  command = codex_command(args, workspace, schema, output)
  completed = run_process(command, workspace, json.dumps(payload))
  if completed.returncode != 0 or not output.exists():
    return {
      "enabled": True,
      "verdict": "INCONCLUSIVE",
      "rationale": f"Judge process failed with exit code {completed.returncode}.",
      "evidence": [completed.stderr[-1000:]],
    }
  try:
    result = read_json(output)
  except (OSError, ValueError, json.JSONDecodeError) as error:
    return {"enabled": True, "verdict": "INCONCLUSIVE", "rationale": str(error), "evidence": []}
  verdict = result.get("verdict")
  if verdict not in {PASS, "FAIL", "INCONCLUSIVE"}:
    verdict = "INCONCLUSIVE"
  return {"enabled": True, "verdict": verdict, "rationale": result.get("rationale", ""), "evidence": result.get("evidence", [])}


def codex_command(args: argparse.Namespace, workspace: Path, schema: Path, output: Path) -> list[str]:
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
  if args.model:
    command[2:2] = ["--model", args.model]
  return command


def evaluate_case(
  args: argparse.Namespace,
  installed_source: Path,
  case_source_skill: Path,
  case_id: str,
  operation_root: Path,
  progress: ProgressReporter,
  context: str | None = None,
) -> dict[str, Any]:
  label = f"Case {case_id}" + (f" [{context}]" if context else "")
  progress.emit(f"{label}: preparing workspace")
  case_dir = case_source_skill / "evals" / "cases" / case_id
  case = read_json(case_dir / "case.json")
  if case.get("id") != case_id:
    raise ValueError(f"Case id mismatch in {case_dir / 'case.json'}")
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
  completed = run_process(codex_command(args, workspace, schema, output), workspace, prompt)
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
  progress.emit(f"{label}: running judge")
  judge = run_judge(args, workspace, case, response, mechanical)
  if judge["verdict"] == "INCONCLUSIVE":
    status = "INCONCLUSIVE"
  elif mechanical["passed"] and judge["verdict"] == PASS:
    status = PASS
  else:
    status = "FAIL"
  result = {
    "case_id": case_id,
    "status": status,
    "kind": case.get("kind", "behavioral"),
    "executor": {
      "exit_code": completed.returncode,
      "response": response,
      "stderr": completed.stderr[-4000:],
    },
    "mechanical": mechanical,
    "judge": judge,
    "changed_paths": changed,
    "workspace": str(workspace),
  }
  (workspace / ".eval-result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
  progress.emit(f"{label}: {status}")
  return result


def suite_cases(skill: Path) -> list[str]:
  suite = read_json(skill / "evals" / "suite.json")
  if suite.get("version") != 1 or not isinstance(suite.get("cases"), list):
    raise ValueError("suite.json must declare version 1 and a cases array")
  return suite["cases"]


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


def resolve_model(args: argparse.Namespace) -> str:
  return args.model or os.environ.get("CODEX_MODEL") or "configured-default"


def execute(args: argparse.Namespace, progress: ProgressReporter | None = None) -> dict[str, Any]:
  progress = progress or ProgressReporter(False)
  progress.emit(f"Preparing {args.operation}")
  skill = args.skill.resolve()
  operation_root = make_operation_root(args)
  source_root = operation_root / "source"
  source_root.mkdir()
  model = resolve_model(args)

  if args.operation == "run":
    installed_source = materialize_skill_source(skill, args.source, source_root)
    case_ids = suite_cases(skill) if args.all else [args.case]
    results = [
      evaluate_case(args, installed_source, skill, case_id, operation_root, progress)
      for case_id in case_ids
    ]
    status = aggregate_status(results)
  elif args.operation == "verify-change":
    baseline_spec = args.baseline or "git:HEAD"
    if baseline_spec.startswith("git:"):
      baseline = materialize_skill_source(skill, baseline_spec, source_root / "baseline")
    else:
      baseline = Path(baseline_spec).resolve()
    candidate = skill
    baseline_result = evaluate_case(
      args, baseline, skill, args.case, operation_root, progress, "baseline"
    )
    baseline_result["role"] = "baseline"
    candidate_result = evaluate_case(
      args, candidate, skill, args.case, operation_root, progress, "candidate"
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
    results = [
      evaluate_case(
        args,
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
    "model": model,
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
      "results": [{"status": "ERROR", "error": str(error)}],
      "artifacts": None,
    }
  progress.emit(f"Final result: {report['status']}")
  print(json.dumps(report, indent=2))
  return 0 if report["status"] == PASS else 1


if __name__ == "__main__":
  sys.exit(main())
