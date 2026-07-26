import os
from pathlib import Path
import subprocess
import sys


skill = Path(os.environ["SKILL_EVAL_SKILL_DIR"])
test_file = skill / "scripts" / "tests" / "test_evaluation_archive.py"
if not test_file.is_file():
  raise SystemExit("missing deterministic archive contract tests")

completed = subprocess.run(
  [
    sys.executable,
    "-m",
    "unittest",
    "discover",
    "-s",
    str(test_file.parent),
    "-p",
    test_file.name,
    "-v",
  ],
  text=True,
  capture_output=True,
  check=False,
)
if completed.returncode != 0:
  sys.stdout.write(completed.stdout)
  sys.stderr.write(completed.stderr)
  raise SystemExit(completed.returncode)
