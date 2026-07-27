import json
from pathlib import Path


economical = json.loads(Path("plan-economical.json").read_text(encoding="utf-8"))
user_sol = json.loads(Path("plan-user-sol.json").read_text(encoding="utf-8"))

for plan in (economical, user_sol):
  assert plan["operation"] == "plan"
  assert plan["impact"] == "scoped"
  assert plan["selected_cases"] == ["eligible"]
  assert plan["regression_cases"] == []
  assert plan["sessions"] == {
    "baseline": {"executor": 1, "judge": 0, "total": 1},
    "candidate": {"executor": 3, "judge": 0, "total": 3},
    "executor": 4,
    "judge": 0,
    "total": 4,
  }
  assert plan["economic_runtime"]["policy_version"] == 1
  assert plan["economic_runtime"]["mode"] == "scoped-complete-oracle"
  assert plan["economic_runtime"]["executor"]["recommended_model"] == "gpt-5.6-luna"
  assert plan["economic_runtime"]["executor"]["recommended_reasoning_effort"] == "medium"
  assert plan["economic_runtime"]["judge"]["recommended_model"] is None
  assert plan["execution_blockers"] == []
  assert plan["campaign"]["ledger"] is None

assert economical["runtime"]["executor"]["model"] == "gpt-5.6-luna"
assert economical["runtime"]["executor"]["reasoning_effort"] == "medium"
assert economical["economic_runtime"]["executor"]["matches_explicit_runtime"] is True
assert not any(
  "differs from the economic runtime recommendation" in warning
  for warning in economical["warnings"]
)

assert user_sol["runtime"]["executor"]["model"] == "gpt-5.6-sol"
assert user_sol["runtime"]["executor"]["reasoning_effort"] == "medium"
assert user_sol["economic_runtime"]["executor"]["matches_explicit_runtime"] is False
assert any(
  "Explicit executor runtime differs from the economic runtime recommendation"
  in warning
  for warning in user_sol["warnings"]
)
assert "--model gpt-5.6-sol" in user_sol["commands"][0]

allowed = {
  ".eval-executor-response.json",
  ".eval-executor-schema.json",
  ".eval-result.json",
  ".git",
  "plan-economical.json",
  "plan-user-sol.json",
}
unexpected = [
  path.as_posix()
  for path in Path(".").iterdir()
  if path.name not in allowed
  and path.name not in {
    ".agents",
    "candidate-skill",
    "baseline-skill",
  }
]
assert unexpected == [], unexpected
