from pathlib import Path
import re
import sys


text = Path("README.md").read_text(encoding="utf-8")
if "dollars" in text.lower() or re.search(r"(?i)\breturns?\b[^\n.]*\bcents?\b", text) is None:
  print("README correction is missing", file=sys.stderr)
  raise SystemExit(1)

unexpected = [
  path
  for path in Path(".").rglob("*")
  if path.is_file()
  and not str(path).startswith(".agents/")
  and path.name != "README.md"
]
if unexpected:
  print(f"documentation only task created files: {unexpected}", file=sys.stderr)
  raise SystemExit(1)
