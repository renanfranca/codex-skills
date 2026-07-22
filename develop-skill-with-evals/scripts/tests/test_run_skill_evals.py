import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


SCRIPT = Path(__file__).parents[1] / "run_skill_evals.py"


def load_runner():
  spec = importlib.util.spec_from_file_location("run_skill_evals", SCRIPT)
  module = importlib.util.module_from_spec(spec)
  spec.loader.exec_module(module)
  return module


class SkillEvalRunnerTest(unittest.TestCase):
  def setUp(self):
    self.temp = tempfile.TemporaryDirectory()
    self.root = Path(self.temp.name)
    self.skill = self.root / "sample-skill"
    (self.skill / "evals" / "cases" / "write-result" / "fixture").mkdir(parents=True)
    (self.skill / "SKILL.md").write_text("---\nname: sample-skill\ndescription: Test.\n---\n", encoding="utf-8")
    (self.skill / "evals" / "suite.json").write_text(
      json.dumps({"version": 1, "cases": ["write-result"]}), encoding="utf-8"
    )
    case = {
      "id": "write-result",
      "kind": "behavioral",
      "prompt_file": "prompt.md",
      "mechanical": {
        "expected_exit_code": 0,
        "required_paths": ["result.txt"],
        "forbidden_changed_paths": [".agents/skills/**"],
        "commands": [{"argv": ["python3", "-c", "from pathlib import Path; assert Path('result.txt').read_text() == 'ok'"]}],
      },
      "judge": {"enabled": False, "criteria": []},
    }
    case_dir = self.skill / "evals" / "cases" / "write-result"
    (case_dir / "case.json").write_text(json.dumps(case), encoding="utf-8")
    (case_dir / "prompt.md").write_text("Create result.txt", encoding="utf-8")
    self.fake = self.root / "fake-codex"
    self.fake.write_text(
      "#!/usr/bin/env python3\n"
      "import json, os, pathlib, sys\n"
      "out = pathlib.Path(sys.argv[sys.argv.index('-o') + 1])\n"
      "cwd = pathlib.Path(sys.argv[sys.argv.index('-C') + 1])\n"
      "mode = os.environ.get('FAKE_CODEX_MODE', 'pass')\n"
      "if mode == 'pass': (cwd / 'result.txt').write_text('ok')\n"
      "if mode == 'mutate-skill': (cwd / '.agents/skills/sample-skill/SKILL.md').write_text('changed')\n"
      "response = {'summary': mode, 'classification': 'Design risk', 'evidence': ['fixture'], 'files_changed': ['result.txt']}\n"
      "out.write_text(json.dumps(response))\n",
      encoding="utf-8",
    )
    self.fake.chmod(0o755)

  def tearDown(self):
    self.temp.cleanup()

  def invoke(self, *args, env=None):
    command = ["python3", str(SCRIPT), *args, "--codex-command", str(self.fake), "--artifacts-dir", str(self.root / "artifacts")]
    return subprocess.run(command, text=True, capture_output=True, env={**os.environ, **(env or {})}, check=False)

  def test_parser_requires_exactly_case_or_all(self):
    runner = load_runner()

    with self.assertRaises(SystemExit):
      runner.parse_args(["run", "--skill", str(self.skill), "--source", "working-tree"])

  def test_run_uses_isolated_workspace_and_passes_mechanical_checks(self):
    completed = self.invoke("run", "--skill", str(self.skill), "--case", "write-result", "--source", "working-tree")

    report = json.loads(completed.stdout)
    self.assertEqual(0, completed.returncode, completed.stderr)
    self.assertEqual("PASS", report["status"])
    self.assertEqual("configured-default", report["model"])
    self.assertEqual(["write-result"], [result["case_id"] for result in report["results"]])
    self.assertFalse((self.root / "result.txt").exists())
    self.assertIsNone(report["artifacts"])

  def test_run_all_aggregates_blocking_results_and_keeps_artifacts(self):
    second = self.skill / "evals" / "cases" / "missing"
    second.mkdir()
    (second / "prompt.md").write_text("Do nothing", encoding="utf-8")
    manifest = json.loads((self.skill / "evals" / "cases" / "write-result" / "case.json").read_text())
    manifest["id"] = "missing"
    manifest["mechanical"]["required_paths"] = ["missing.txt"]
    (second / "case.json").write_text(json.dumps(manifest), encoding="utf-8")
    (self.skill / "evals" / "suite.json").write_text(json.dumps({"version": 1, "cases": ["write-result", "missing"]}), encoding="utf-8")

    completed = self.invoke("run", "--skill", str(self.skill), "--all", "--source", "working-tree")

    report = json.loads(completed.stdout)
    self.assertEqual(1, completed.returncode)
    self.assertEqual("FAIL", report["status"])
    self.assertEqual(["PASS", "FAIL"], [result["status"] for result in report["results"]])
    self.assertTrue(Path(report["artifacts"]).exists())

  def test_mechanical_check_detects_skill_self_modification(self):
    completed = self.invoke(
      "run", "--skill", str(self.skill), "--case", "write-result", "--source", "working-tree", env={"FAKE_CODEX_MODE": "mutate-skill"}
    )

    report = json.loads(completed.stdout)
    self.assertEqual(1, completed.returncode)
    self.assertEqual("FAIL", report["status"])
    checks = report["results"][0]["mechanical"]["checks"]
    self.assertIn("evaluated skill remained unchanged", [check["name"] for check in checks if not check["passed"]])

  def test_verify_change_rejects_a_case_that_passes_on_baseline(self):
    baseline = self.root / "baseline"
    subprocess.run(["cp", "-a", str(self.skill), str(baseline)], check=True)

    completed = self.invoke("verify-change", "--skill", str(self.skill), "--case", "write-result", "--baseline", str(baseline))

    report = json.loads(completed.stdout)
    self.assertEqual(1, completed.returncode)
    self.assertEqual("INVALID_RED", report["status"])
    self.assertEqual(["baseline", "candidate"], [result["role"] for result in report["results"]])

  def test_git_source_materializes_the_requested_baseline(self):
    repository = self.root / "repository"
    repository.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=repository, check=True)
    subprocess.run(["git", "config", "user.email", "eval@example.invalid"], cwd=repository, check=True)
    subprocess.run(["git", "config", "user.name", "Eval"], cwd=repository, check=True)
    tracked_skill = repository / "sample-skill"
    subprocess.run(["cp", "-a", str(self.skill), str(tracked_skill)], check=True)
    subprocess.run(["git", "add", "."], cwd=repository, check=True)
    subprocess.run(["git", "commit", "-qm", "baseline"], cwd=repository, check=True)
    (tracked_skill / "marker.txt").write_text("working tree only", encoding="utf-8")
    runner = load_runner()

    materialized = runner.materialize_skill_source(tracked_skill, "git:HEAD", self.root / "materialized")

    self.assertTrue((materialized / "SKILL.md").exists())
    self.assertFalse((materialized / "marker.txt").exists())

  def test_stability_blocks_when_normalized_results_diverge(self):
    counter = self.root / "counter"
    self.fake.write_text(
      self.fake.read_text(encoding="utf-8").replace(
        "mode = os.environ.get('FAKE_CODEX_MODE', 'pass')",
        f"counter = pathlib.Path({str(counter)!r}); n = int(counter.read_text()) if counter.exists() else 0; counter.write_text(str(n + 1)); mode = 'pass' if n % 2 == 0 else 'fail'",
      ),
      encoding="utf-8",
    )

    completed = self.invoke("stability", "--skill", str(self.skill), "--case", "write-result", "--runs", "3")

    report = json.loads(completed.stdout)
    self.assertEqual(1, completed.returncode)
    self.assertEqual("UNSTABLE", report["status"])
    self.assertEqual(3, len(report["results"]))

  def test_stability_signature_ignores_only_harness_and_python_cache_artifacts(self):
    runner = load_runner()
    result = {
      "status": "PASS",
      "mechanical": {"checks": [{"name": "suite", "passed": True}]},
      "judge": {"verdict": "PASS"},
      "changed_paths": [
        ".eval-executor-schema.json",
        "__pycache__/module.cpython-310.pyc",
        "src/__pycache__/nested.cpython-310.pyc",
        "report_builder.py",
      ],
    }

    signature = json.loads(runner.verdict_signature(result))

    self.assertEqual(["report_builder.py"], signature["changed_paths"])


if __name__ == "__main__":
  unittest.main()
