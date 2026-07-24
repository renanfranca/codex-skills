#!/usr/bin/env python3
import json
from pathlib import Path
import subprocess
import sys

from jsonschema import Draft202012Validator


root = Path.cwd()
plan = json.loads((root / "plan.json").read_text(encoding="utf-8"))
report = json.loads((root / "validation.json").read_text(encoding="utf-8"))
skill_under_test = root / "sample-skill"
baseline = root / "sample-baseline"
runner_skill = root / ".agents" / "skills" / "develop-skill-with-evals"
plan_schema = json.loads(
  (runner_skill / "references" / "eval-plan.schema.json").read_text(encoding="utf-8")
)
result_schema = json.loads(
  (runner_skill / "references" / "eval-result.schema.json").read_text(encoding="utf-8")
)
Draft202012Validator(plan_schema).validate(plan)
Draft202012Validator(result_schema).validate(report)

assert plan["operation"] == "plan"
assert plan["impact"] == "deterministic"
assert plan["selected_cases"] == ["trim-uppercase"]
assert plan["sessions"]["total"] == 0
assert plan["execution_blockers"] == []
assert report["operation"] == "validate-change"
assert report["status"] == "PASS"
assert report["model_sessions"]["total"] == 0
assert report["plan"]["runtime_fingerprint"] == plan["runtime_fingerprint"]

for document in (plan, report):
  runtime = document["runtime"] if document is plan else document["plan"]["runtime"]
  assert runtime["executor"]["model"] == "gpt-5.6-sol"
  assert runtime["executor"]["model_source"] == "cli"
  assert runtime["executor"]["reasoning_effort"] == "medium"
  assert runtime["judge"]["model"] == "gpt-5.6-terra"
  assert runtime["judge"]["model_source"] == "cli"
  assert runtime["judge"]["reasoning_effort"] == "medium"

invocations = [
  json.loads(line)
  for line in (root / "runner-invocations.jsonl").read_text(encoding="utf-8").splitlines()
]
assert [arguments[0] for arguments in invocations] == ["plan", "validate-change"]
for arguments in invocations:
  joined = " ".join(arguments)
  assert "--model gpt-5.6-sol" in joined
  assert "--reasoning-effort medium" in joined
  assert "--judge-model gpt-5.6-terra" in joined
  assert "--judge-reasoning-effort medium" in joined
  assert not {"run", "verify-change", "stability"} & set(arguments)
  assert "--all" not in arguments
assert "--approved-model-sessions" in invocations[1]
assert invocations[1][invocations[1].index("--approved-model-sessions") + 1] == "0"
assert not (root / "unexpected-nested-model-session").exists()

candidate_result = subprocess.run(
  [sys.executable, str(skill_under_test / "scripts" / "render.py"), "  hello  "],
  text=True,
  capture_output=True,
  check=False,
)
baseline_result = subprocess.run(
  [sys.executable, str(baseline / "scripts" / "render.py"), "  hello  "],
  text=True,
  capture_output=True,
  check=False,
)
assert candidate_result.returncode == 0
assert candidate_result.stdout == "HELLO\n"
assert baseline_result.stdout == "  HELLO  \n"

print(json.dumps({
  "workflow": [arguments[0] for arguments in invocations],
  "impact": plan["impact"],
  "selected_cases": plan["selected_cases"],
  "executor_runtime": {
    "model": plan["runtime"]["executor"]["model"],
    "reasoning_effort": plan["runtime"]["executor"]["reasoning_effort"],
    "source": plan["runtime"]["executor"]["model_source"],
  },
  "judge_runtime": {
    "model": plan["runtime"]["judge"]["model"],
    "reasoning_effort": plan["runtime"]["judge"]["reasoning_effort"],
    "source": plan["runtime"]["judge"]["model_source"],
  },
  "validation_status": report["status"],
  "planned_model_sessions": plan["sessions"]["total"],
  "actual_model_sessions": report["model_sessions"]["total"],
  "disallowed_gates_absent": True,
  "nested_fake_codex_invoked": False,
}, sort_keys=True))
