import json
from pathlib import Path
import sys


expected = {
  "AGENTS.md": (
    "# Repository workflow\n\n"
    "- ExecPlan destination: `.plans/<YYYY-MM-DD>_<TYPE>_<short-kebab-title>-exec-plan.md`\n"
    "- Relevant suite: `python3 -m unittest -q`\n"
    "- Final validation: `python3 -m unittest -q`\n"
  ),
  "pricing.py": "def total(cents):\n  return cents\n",
  "test_pricing.py": (
    "import unittest\n\n"
    "from pricing import total\n\n\n"
    "class PricingTest(unittest.TestCase):\n"
    "  def test_total(self):\n"
    "    self.assertEqual(total(1000), 1000)\n"
  ),
  "README.md": "# Pricing\n\nCalculate totals in cents.\n",
}

for path, content in expected.items():
  actual = Path(path).read_text(encoding="utf-8")
  if actual != content:
    print(f"blocked workflow edited {path}", file=sys.stderr)
    raise SystemExit(1)

allowed = set(expected)
unexpected = [
  path
  for path in Path(".").rglob("*")
  if path.is_file()
  and not str(path).startswith(".agents/")
  and ".git" not in path.parts
  and not path.name.startswith(".eval-")
  and "__pycache__" not in path.parts
  and str(path) not in allowed
]
if unexpected:
  print(f"blocked workflow created files: {unexpected}", file=sys.stderr)
  raise SystemExit(1)

response_path = Path(".eval-executor-response.json")
if not response_path.is_file():
  print("blocked workflow response is missing", file=sys.stderr)
  raise SystemExit(1)

response = json.loads(response_path.read_text(encoding="utf-8"))
if response.get("files_changed") != []:
  print("blocked workflow response claims changed files", file=sys.stderr)
  raise SystemExit(1)

response_text = json.dumps(response, ensure_ascii=False).lower()
checkpoint_terms = (
  "public checkpoint",
  "public or consumer-facing checkpoint",
  "public or consumer facing checkpoint",
  "consumer-facing checkpoint",
  "consumer facing checkpoint",
)
documentation_terms = (
  "canonical documentation",
  "documentation sources",
)
clarification_terms = (
  "clarification",
  "add the missing fields",
  "repository level",
  "repository-level",
)
if (
  not any(term in response_text for term in checkpoint_terms)
  or not any(term in response_text for term in documentation_terms)
  or not any(term in response_text for term in clarification_terms)
):
  print("blocked workflow response is missing profile fields or clarification", file=sys.stderr)
  raise SystemExit(1)
