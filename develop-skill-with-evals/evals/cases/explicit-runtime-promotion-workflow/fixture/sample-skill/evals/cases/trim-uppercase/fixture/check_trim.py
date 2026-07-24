#!/usr/bin/env python3
import os
from pathlib import Path
import subprocess
import sys


skill = Path(os.environ["SKILL_EVAL_SKILL_DIR"])
completed = subprocess.run(
  [sys.executable, str(skill / "scripts" / "render.py"), "  hello  "],
  text=True,
  capture_output=True,
  check=False,
)
assert completed.returncode == 0
assert completed.stdout == "HELLO\n"
