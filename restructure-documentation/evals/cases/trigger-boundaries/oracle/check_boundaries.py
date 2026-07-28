from pathlib import Path
import re
import sys


text = Path("trigger-assessment.md").read_text(encoding="utf-8")
expected = {
  "SYS-1": "APPLY",
  "TYPO-2": "EXCLUDE",
  "ZERO-3": "EXCLUDE",
  "AGENT-4": "APPLY",
  "AUDIT-5": "APPLY_NO_ACTION",
}

for request_id, status in expected.items():
  section = re.search(
    rf"(?ms)^#+\s+{re.escape(request_id)}(?:\s+[—:-]\s*"
    rf"(?:APPLY_NO_ACTION|APPLY|EXCLUDE))?\s*$"
    rf".*?(?=^#+\s+|\Z)",
    text,
  )
  if section is None:
    print(f"missing section for {request_id}", file=sys.stderr)
    raise SystemExit(1)
  statuses = re.findall(
    r"\b(?:APPLY_NO_ACTION|APPLY|EXCLUDE)\b",
    section.group(0),
  )
  if statuses != [status]:
    print(
      f"{request_id} expected exactly {status}, got {statuses}",
      file=sys.stderr,
    )
    raise SystemExit(1)
