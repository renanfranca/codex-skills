from pathlib import Path
import re
import sys


def section(text, heading):
  match = re.search(
    rf"(?ms)^##\s+{re.escape(heading)}\s*$.*?(?=^##\s+|\Z)",
    text,
  )
  if match is None:
    print(f"missing section {heading}", file=sys.stderr)
    raise SystemExit(1)
  return match.group(0).lower()


public = Path("plans/public-change.md").read_text(encoding="utf-8")
internal = Path("plans/internal-change.md").read_text(encoding="utf-8")

for name, text in (("public", public), ("internal", internal)):
  for heading in (
    "Purpose / Big Picture",
    "Milestones",
    "Progress",
    "Decisions",
    "Risks and Mitigations",
    "Validation Strategy",
    "Documentation Impact",
    "Lessons Learned",
  ):
    section(text, heading)

public_docs = section(public, "Documentation Impact")
for term in ("readme.md", "config.json", "timeout_seconds"):
  if term not in public_docs:
    print(f"public plan documentation impact missing {term}", file=sys.stderr)
    raise SystemExit(1)

if "readme.md" not in section(public, "Milestones") or "config.json" not in section(public, "Milestones"):
  print("public plan milestones omit canonical documentation edits", file=sys.stderr)
  raise SystemExit(1)

public_validation = section(public, "Validation Strategy")
names_both_sources = (
  "readme.md" in public_validation
  and "config.json" in public_validation
)
cross_references_canonical_documentation = (
  "config.json" in public_validation
  and "documentation" in public_validation
  and any(
    term in public_validation
    for term in ("inspect", "validate", "reconcile", "compare")
  )
)
if not names_both_sources and not cross_references_canonical_documentation:
  print("public plan final validation omits documentation reconciliation", file=sys.stderr)
  raise SystemExit(1)

internal_docs = section(internal, "Documentation Impact")
if "readme.md" not in internal_docs or "config.json" not in internal_docs:
  print("internal plan does not name canonical documentation", file=sys.stderr)
  raise SystemExit(1)
if not any(
  phrase in internal_docs
  for phrase in (
    "no change",
    "no documentation change",
    "remain accurate",
    "remains accurate",
    "does not require",
    "unchanged",
    "without edits",
  )
):
  print("internal plan lacks an explicit no change justification", file=sys.stderr)
  raise SystemExit(1)
