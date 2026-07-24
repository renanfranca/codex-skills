#!/usr/bin/env python3
import json
from pathlib import Path


plan = json.loads(Path("evaluation-plan.json").read_text(encoding="utf-8"))
assert Path("plan-exit-code.txt").read_text(encoding="utf-8").strip() == "0"
assert Path("plan-stderr.log").read_text(encoding="utf-8") == ""
assert plan["operation"] == "plan"
assert plan["impact"] == "deterministic"
assert plan["selected_cases"] == ["runner-output"]
assert plan["regression_cases"] == []
assert plan["sessions"]["executor"] == 0
assert plan["sessions"]["judge"] == 0
assert plan["sessions"]["total"] == 0
assert plan["approval_required"] is False
assert plan["execution_blockers"] == []
