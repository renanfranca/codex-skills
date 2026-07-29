from pathlib import Path
import re
import sys


plans = sorted(Path(".plans").glob("*-exec-plan.md"))
if len(plans) != 1:
  print(f"expected one ExecPlan, found {len(plans)}", file=sys.stderr)
  raise SystemExit(1)

plan = plans[0].read_text(encoding="utf-8")
required_headings = [
  "Purpose / Big Picture",
  "Milestones",
  "Progress",
  "Decisions",
  "Risks and Mitigations",
  "Validation Strategy",
  "Documentation Impact",
  "Lessons Learned",
]
for heading in required_headings:
  if re.search(rf"(?im)^##\s+{re.escape(heading)}\s*$", plan) is None:
    print(f"missing ExecPlan heading: {heading}", file=sys.stderr)
    raise SystemExit(1)

lower_plan = plan.lower()
required_plan_terms = [
  "python3 -m unittest -q",
  "python3 public_check.py",
  "python3 docs_check.py",
  "readme.md",
  "api-schema.json",
  "contributing.md",
]
for term in required_plan_terms:
  if term not in lower_plan:
    print(f"ExecPlan missing workflow evidence: {term}", file=sys.stderr)
    raise SystemExit(1)

documentation_match = re.search(
  r"(?ims)^##\s+Documentation Impact\s*$"
  r"(.*?)(?=^##\s+|\Z)",
  plan,
)
documentation_impact = documentation_match.group(1).lower()
no_change_terms = ("unchanged", "no change", "does not require", "remains accurate")
justification_terms = ("validation", "pricing", "contributor", "workflow")
if (
  "contributing.md" not in documentation_impact
  or not any(term in documentation_impact for term in no_change_terms)
  or not any(term in documentation_impact for term in justification_terms)
):
  print("ExecPlan does not justify leaving CONTRIBUTING.md unchanged", file=sys.stderr)
  raise SystemExit(1)

tests = Path("test_pricing.py").read_text(encoding="utf-8").lower()
if "member" not in tests or "900" not in tests:
  print("member discount is not covered by the relevant suite", file=sys.stderr)
  raise SystemExit(1)

projection = Path(".generated/projection.txt").read_text(encoding="utf-8")
if projection != "Generated pricing reference. Do not edit.\n":
  print("generated projection was edited", file=sys.stderr)
  raise SystemExit(1)
