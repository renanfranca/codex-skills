import os
from pathlib import Path


skill_under_test = Path(os.environ["SKILL_EVAL_SKILL_DIR"])
instructions = (skill_under_test / "SKILL.md").read_text(encoding="utf-8")

required_contracts = {
  "preflight command": "codex doctor --json",
  "matching permission boundary": "at the same permission boundary",
  "healthy preflight": "overallStatus: ok",
  "tui subprocess boundary": (
    "--ask-for-approval on-request` does not automatically elevate "
    "its noninteractive subprocesses"
  ),
  "blocked Codex state": "CODEX_HOME` is read only",
  "blocked network": "network access is unavailable",
  "complete outer approval": (
    "request external approval for the complete runner command"
  ),
  "internal sandbox": "internal `workspace-write` sandbox",
  "no broad sandbox": "Do not use `danger-full-access`",
  "no copied authentication": "copy authentication state into `/tmp`",
  "separate cost authorization": (
    "Obtain model session cost authorization separately from shell approval"
  ),
  "independent approvals": "Neither authorization implies the other",
}

missing = [
  name
  for name, expected in required_contracts.items()
  if expected not in instructions
]
if missing:
  raise AssertionError(
    "SKILL.md is missing nested Codex outer sandbox contracts: "
    + ", ".join(missing)
  )
