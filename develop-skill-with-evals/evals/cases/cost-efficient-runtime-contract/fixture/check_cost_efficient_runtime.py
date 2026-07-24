import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile


skill_under_test = Path(os.environ["SKILL_EVAL_SKILL_DIR"])
runner = skill_under_test / "scripts" / "run_skill_evals.py"
fixture_root = Path.cwd()
fake_codex = fixture_root / "fake-codex"
fake_codex.chmod(0o755)

with tempfile.TemporaryDirectory(dir=fixture_root) as temporary:
  root = Path(temporary)
  candidate = root / "sample-skill"
  case_dir = candidate / "evals" / "cases" / "affected"
  case_dir.mkdir(parents=True)
  (candidate / "SKILL.md").write_text(
    "---\nname: sample-skill\ndescription: Test.\n---\n",
    encoding="utf-8",
  )
  (candidate / "marker.txt").write_text("candidate", encoding="utf-8")
  (candidate / "evals" / "suite.json").write_text(
    json.dumps({"version": 1, "cases": ["affected"]}),
    encoding="utf-8",
  )
  (case_dir / "prompt.md").write_text("Create result.txt.", encoding="utf-8")
  (case_dir / "case.json").write_text(
    json.dumps({
      "id": "affected",
      "kind": "behavioral",
      "prompt_file": "prompt.md",
      "mechanical": {
        "expected_exit_code": 0,
        "required_paths": ["result.txt"]
      },
      "judge": {"enabled": False, "criteria": []}
    }),
    encoding="utf-8",
  )
  baseline = root / "baseline"
  shutil.copytree(candidate, baseline)
  (baseline / "marker.txt").write_text("baseline", encoding="utf-8")
  ledger = root / "campaign.json"
  common = [
    "--skill", str(candidate),
    "--baseline", str(baseline),
    "--impact", "scoped",
    "--case", "affected",
    "--model", "fixture-model",
    "--reasoning-effort", "medium",
  ]

  diagnostic = subprocess.run(
    ["python3", str(runner), "plan", *common, "--workflow", "diagnostic"],
    text=True,
    capture_output=True,
    check=False,
  )
  assert diagnostic.returncode == 0, diagnostic.stderr
  diagnostic_plan = json.loads(diagnostic.stdout)
  assert diagnostic_plan["sessions"]["total"] == 2
  assert diagnostic_plan["promotion_eligible"] is False
  assert diagnostic_plan["case_fingerprints"]
  assert diagnostic_plan["evaluation_fingerprint"]
  assert diagnostic_plan["source_fingerprints"]

  probe = subprocess.run(
    [
      "python3", str(runner), "probe-change", *common,
      "--codex-command", str(fake_codex),
      "--artifacts-dir", str(root / "artifacts"),
      "--approved-model-sessions", "2",
      "--campaign-ledger", str(ledger),
      "--approved-cumulative-model-sessions", "2",
    ],
    text=True,
    capture_output=True,
    check=False,
  )
  assert probe.returncode == 0, probe.stderr
  probe_report = json.loads(probe.stdout)
  assert probe_report["promotion_eligible"] is False
  assert probe_report["model_sessions"]["total"] == 2
  assert probe_report["usage"]["complete"] is True
  assert probe_report["campaign"]["consumed_after"] == 2

  promotion = subprocess.run(
    ["python3", str(runner), "plan", *common, "--workflow", "promotion"],
    text=True,
    capture_output=True,
    check=False,
  )
  assert promotion.returncode == 0, promotion.stderr
  promotion_plan = json.loads(promotion.stdout)
  assert promotion_plan["sessions"]["total"] == 4
  assert promotion_plan["promotion_eligible"] is True
