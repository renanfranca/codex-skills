import json
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
  and ".git" not in path.parts
  and not path.name.startswith(".eval-")
  and "__pycache__" not in path.parts
  and path.name != "README.md"
]
if unexpected:
  print(f"documentation only task created files: {unexpected}", file=sys.stderr)
  raise SystemExit(1)

response_path = Path(".eval-executor-response.json")
if not response_path.is_file():
  print("documentation only response is missing", file=sys.stderr)
  raise SystemExit(1)

response = json.loads(response_path.read_text(encoding="utf-8"))
if response.get("files_changed") != ["README.md"]:
  print("documentation only response does not identify only README.md", file=sys.stderr)
  raise SystemExit(1)

response_text = json.dumps(response, ensure_ascii=False).lower()
if "execplan-tdd" in response_text and not any(
  term in response_text
  for term in (
    "outside execplan-tdd",
    "does not use execplan-tdd",
    "execplan-tdd does not apply",
    "not governed by execplan-tdd",
  )
):
  print("documentation only response claims execplan-tdd governs the task", file=sys.stderr)
  raise SystemExit(1)
