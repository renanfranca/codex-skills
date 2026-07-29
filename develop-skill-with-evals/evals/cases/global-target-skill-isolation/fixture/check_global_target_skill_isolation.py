import os
from pathlib import Path
import subprocess
import sys


skill = Path(os.environ["SKILL_EVAL_SKILL_DIR"])
test_name = (
  "scripts.tests.test_run_skill_evals.SkillEvalRunnerTest."
  "test_semantic_executor_disables_the_global_target_skill"
)
completed = subprocess.run(
  ["python3", "-m", "unittest", test_name, "-v"],
  cwd=skill,
  text=True,
  capture_output=True,
  check=False,
)
sys.stdout.write(completed.stdout)
sys.stderr.write(completed.stderr)

if completed.returncode != 0 or "Ran 1 test" not in completed.stderr:
  raise SystemExit(1)
