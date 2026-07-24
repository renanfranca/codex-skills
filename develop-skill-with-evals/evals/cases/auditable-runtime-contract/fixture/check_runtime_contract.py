#!/usr/bin/env python3
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile


evaluated_skill = Path(os.environ["SKILL_EVAL_SKILL_DIR"]).resolve()
runner = evaluated_skill / "scripts" / "run_skill_evals.py"
fixture = Path(__file__).resolve().parent

with tempfile.TemporaryDirectory() as temporary:
  root = Path(temporary)
  skill = root / "sample-skill"
  case_dir = skill / "evals" / "cases" / "write-result"
  case_dir.mkdir(parents=True)
  (skill / "SKILL.md").write_text(
    "---\nname: sample-skill\ndescription: Test fixture.\n---\n",
    encoding="utf-8",
  )
  (skill / "evals" / "suite.json").write_text(
    json.dumps({"version": 1, "cases": ["write-result"]}),
    encoding="utf-8",
  )
  (case_dir / "prompt.md").write_text("Create result.txt.", encoding="utf-8")
  (case_dir / "case.json").write_text(
    json.dumps({
      "id": "write-result",
      "kind": "behavioral",
      "prompt_file": "prompt.md",
      "mechanical": {"expected_exit_code": 0, "required_paths": ["result.txt"]},
      "judge": {"enabled": True, "criteria": ["The result exists."]},
    }),
    encoding="utf-8",
  )
  baseline = root / "baseline"
  subprocess.run(["cp", "-a", str(skill), str(baseline)], check=True)
  log = root / "codex-argv.jsonl"
  env = {**os.environ, "AUDIT_RUNTIME_LOG": str(log)}

  plan_command = [
    sys.executable,
    str(runner),
    "plan",
    "--skill",
    str(skill),
    "--baseline",
    str(baseline),
    "--impact",
    "scoped",
    "--case",
    "write-result",
    "--model",
    "gpt-5.6-sol",
    "--reasoning-effort",
    "medium",
    "--judge-model",
    "gpt-5.6-terra",
    "--judge-reasoning-effort",
    "high",
  ]
  planned = subprocess.run(plan_command, text=True, capture_output=True, env=env, check=False)
  assert planned.returncode == 0, planned.stderr
  plan = json.loads(planned.stdout)
  assert plan["runtime"]["complete"] is True
  assert plan["runtime"]["audit_quality"] == "promotion"
  assert plan["runtime"]["executor"]["model_source"] == "cli"
  assert plan["runtime"]["judge"]["model"] == "gpt-5.6-terra"
  assert len(plan["runtime_fingerprint"]) == 64
  assert plan["execution_blockers"] == []
  assert not log.exists()

  blocked_artifacts = root / "blocked-artifacts"
  blocked = subprocess.run(
    [
      sys.executable,
      str(runner),
      "validate-change",
      "--skill",
      str(skill),
      "--baseline",
      str(baseline),
      "--impact",
      "scoped",
      "--case",
      "write-result",
      "--approved-model-sessions",
      "0",
      "--codex-command",
      str(fixture / "fake-codex"),
      "--artifacts-dir",
      str(blocked_artifacts),
      "--progress",
    ],
    text=True,
    capture_output=True,
    env=env,
    check=False,
  )
  blocked_plan = json.loads(blocked.stdout)
  assert blocked.returncode == 2
  assert [item["code"] for item in blocked_plan["execution_blockers"]] == [
    "executor-runtime-explicit-required",
    "judge-runtime-unresolved",
    "insufficient-model-session-budget",
  ]
  assert blocked.stderr
  assert not blocked_artifacts.exists()
  assert not log.exists()

  run = subprocess.run(
    [
      sys.executable,
      str(runner),
      "run",
      "--skill",
      str(skill),
      "--case",
      "write-result",
      "--source",
      "working-tree",
      "--model",
      "gpt-5.6-sol",
      "--reasoning-effort",
      "medium",
      "--judge-model",
      "gpt-5.6-terra",
      "--judge-reasoning-effort",
      "high",
      "--codex-command",
      str(fixture / "fake-codex"),
      "--artifacts-dir",
      str(root / "run-artifacts"),
    ],
    text=True,
    capture_output=True,
    env=env,
    check=False,
  )
  report = json.loads(run.stdout)
  assert run.returncode == 0, run.stderr
  assert report["runtime"]["executor"]["model"] == "gpt-5.6-sol"
  assert report["runtime"]["judge"]["model"] == "gpt-5.6-terra"
  assert report["model_sessions"] == {"executor": 1, "judge": 1, "total": 2}
  arguments = [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()]
  assert ["--model", "gpt-5.6-sol"] == arguments[0][1:3]
  assert 'model_reasoning_effort="medium"' in arguments[0]
  assert ["--model", "gpt-5.6-terra"] == arguments[1][1:3]
  assert 'model_reasoning_effort="high"' in arguments[1]

  log.unlink()
  failed = subprocess.run(
    [
      sys.executable,
      str(runner),
      "run",
      "--skill",
      str(skill),
      "--case",
      "write-result",
      "--source",
      "working-tree",
      "--model",
      "gpt-5.6-sol",
      "--reasoning-effort",
      "medium",
      "--judge-model",
      "gpt-5.6-terra",
      "--judge-reasoning-effort",
      "high",
      "--codex-command",
      str(fixture / "fake-codex"),
      "--artifacts-dir",
      str(root / "failed-artifacts"),
    ],
    text=True,
    capture_output=True,
    env={**env, "AUDIT_RUNTIME_MECHANICAL_FAILURE": "1"},
    check=False,
  )
  failed_report = json.loads(failed.stdout)
  assert failed.returncode == 1
  result = failed_report["results"][0]
  assert result["judge"]["executed"] is False
  assert result["judge"]["verdict"] == "SKIPPED"
  assert failed_report["model_sessions"] == {"executor": 1, "judge": 0, "total": 1}
  assert len(log.read_text(encoding="utf-8").splitlines()) == 1
