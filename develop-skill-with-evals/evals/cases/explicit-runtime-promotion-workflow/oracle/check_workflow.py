#!/usr/bin/env python3
import json
from pathlib import Path
import subprocess
import sys

from jsonschema import Draft202012Validator


root = Path.cwd()
diagnostic_plan = json.loads(
  (root / "diagnostic-plan.json").read_text(encoding="utf-8")
)
diagnostic = json.loads((root / "diagnostic.json").read_text(encoding="utf-8"))
promotion_plan = json.loads(
  (root / "promotion-plan.json").read_text(encoding="utf-8")
)
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
for plan in (diagnostic_plan, promotion_plan):
  Draft202012Validator(plan_schema).validate(plan)
for result in (diagnostic, report):
  Draft202012Validator(result_schema).validate(result)

assert diagnostic_plan["workflow"] == "diagnostic"
assert diagnostic_plan["promotion_eligible"] is False
assert promotion_plan["workflow"] == "promotion"
assert promotion_plan["promotion_eligible"] is True
for plan in (diagnostic_plan, promotion_plan):
  assert plan["impact"] == "deterministic"
  assert plan["selected_cases"] == ["trim-uppercase"]
  assert plan["sessions"]["total"] == 0
  assert plan["execution_blockers"] == []
assert diagnostic["operation"] == "probe-change"
assert diagnostic["status"] == "PASS"
assert diagnostic["promotion_eligible"] is False
assert diagnostic["model_sessions"]["total"] == 0
assert report["operation"] == "validate-change"
assert report["status"] == "PASS"
assert report["promotion_eligible"] is True
assert report["model_sessions"]["total"] == 0

for plan in (diagnostic_plan, promotion_plan):
  runtime = plan["runtime"]
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
workflow_invocations = [
  arguments
  for arguments in invocations
  if arguments and arguments[0] in {"plan", "probe-change", "validate-change"}
  and "--help" not in arguments
]
assert [arguments[0] for arguments in workflow_invocations] == [
  "plan",
  "probe-change",
  "plan",
  "validate-change",
]
for arguments in workflow_invocations:
  joined = " ".join(arguments)
  assert "--model gpt-5.6-sol" in joined
  assert "--reasoning-effort medium" in joined
  assert "--judge-model gpt-5.6-terra" in joined
  assert "--judge-reasoning-effort medium" in joined
  assert not {"run", "verify-change", "stability"} & set(arguments)
  assert "--all" not in arguments
for arguments in (workflow_invocations[1], workflow_invocations[3]):
  assert "--approved-model-sessions" in arguments
  assert arguments[arguments.index("--approved-model-sessions") + 1] == "0"
for arguments in invocations:
  assert not {"run", "verify-change", "stability"} & set(arguments)
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
