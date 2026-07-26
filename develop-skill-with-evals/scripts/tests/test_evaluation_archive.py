import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


SKILL_ROOT = Path(__file__).parents[2]
SCRIPTS = SKILL_ROOT / "scripts"
RUNNER = SCRIPTS / "run_skill_evals.py"
RENDERER = SCRIPTS / "render_eval_report.py"
COMPARATOR = SCRIPTS / "compare_model_reports.py"
ARCHIVE_MANAGER = SCRIPTS / "manage_evaluation_archive.py"
if str(SCRIPTS) not in sys.path:
  sys.path.insert(0, str(SCRIPTS))


class EvaluationArchiveTest(unittest.TestCase):
  def setUp(self):
    self.temp = tempfile.TemporaryDirectory()
    self.root = Path(self.temp.name)
    self.skill = self._behavioral_skill("sample-skill")
    self.pricing = self.root / "pricing.json"
    self.pricing.write_text(json.dumps({
      "version": 1,
      "effective_date": "2026-07-26",
      "source": "https://example.test/pricing",
      "currency": "USD",
      "unit": "per_million_tokens",
      "models": {
        "fixture-model": {
          "input": 1.0,
          "cached_input": 0.5,
          "output": 2.0,
        }
      },
      "limitations": ["Fixture reference only."],
    }), encoding="utf-8")
    self.fake_codex = self._fake_codex("codex")

  def tearDown(self):
    self.temp.cleanup()

  def test_all_executed_commands_accept_no_report_and_reject_conflicts(self):
    for operation in (
      "run",
      "verify-change",
      "stability",
      "probe-change",
      "validate-change",
    ):
      with self.subTest(operation=operation):
        completed = subprocess.run(
          ["python3", str(RUNNER), operation, "--help"],
          text=True,
          capture_output=True,
          check=False,
        )
        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertIn("--no-report", completed.stdout)
    completed = subprocess.run(
      [
        "python3",
        str(RUNNER),
        "run",
        "--skill",
        str(self.skill),
        "--case",
        "write-result",
        "--no-report",
        "--report-dir",
        str(self.root / "reports"),
      ],
      text=True,
      capture_output=True,
      check=False,
    )
    self.assertEqual(2, completed.returncode)
    self.assertIn("--no-report is incompatible", completed.stderr)

  def test_automatic_archive_uses_configured_pricing_for_codex(self):
    runner, archive = self._configured_runner()
    completed = self._run(runner, self.fake_codex)
    self.assertEqual(0, completed.returncode, completed.stderr)
    stdout = json.loads(completed.stdout)
    report_path = Path(stdout["evidence_report"])
    self.assertEqual(
      archive / "sample-skill" / "operations",
      report_path.parent.parent,
    )
    report = json.loads(report_path.read_text(encoding="utf-8"))
    self.assertTrue(report["pricing"]["applied"])
    self.assertEqual("2026-07-26", report["pricing"]["snapshot"]["effective_date"])
    self.assertFalse(report["api_reference_estimate"]["actual_charge"])

  def test_fake_zero_session_no_report_and_no_report_override(self):
    runner, archive = self._configured_runner()
    fake = self._fake_codex("fake-codex")
    completed = self._run(runner, fake)
    self.assertEqual(0, completed.returncode, completed.stderr)
    self.assertNotIn("evidence_report", json.loads(completed.stdout))
    self.assertEqual([], list(archive.glob("*/operations/*/report.json")))

    deterministic = self._deterministic_skill()
    completed = self._run(
      runner,
      self.fake_codex,
      skill=deterministic,
      case="deterministic-check",
    )
    self.assertEqual(0, completed.returncode, completed.stderr)
    self.assertNotIn("evidence_report", json.loads(completed.stdout))

    completed = self._run(runner, self.fake_codex, extra=["--no-report"])
    self.assertEqual(0, completed.returncode, completed.stderr)
    self.assertNotIn("evidence_report", json.loads(completed.stdout))
    self.assertEqual([], list(archive.glob("*/operations/*/report.json")))

  def test_explicit_destination_precedes_automatic_and_works_without_config(self):
    runner, archive = self._configured_runner()
    explicit = self.root / "explicit"
    completed = self._run(
      runner,
      self.fake_codex,
      extra=[
        "--report-dir",
        str(explicit),
        "--pricing-file",
        str(self.pricing),
      ],
    )
    self.assertEqual(0, completed.returncode, completed.stderr)
    report_path = Path(json.loads(completed.stdout)["evidence_report"])
    self.assertEqual(explicit, report_path.parent.parent)
    self.assertEqual([], list(archive.glob("*/operations/*/report.json")))

    plain_repo = self.root / "plain-repo"
    plain_runner = self._copy_runner(plain_repo)
    completed = self._run(plain_runner, self.fake_codex)
    self.assertEqual(0, completed.returncode, completed.stderr)
    self.assertNotIn("evidence_report", json.loads(completed.stdout))

  def test_persistence_failure_after_session_blocks_and_retains_artifacts(self):
    runner, archive = self._configured_runner()
    (archive / "sample-skill").write_text("blocks directory creation", encoding="utf-8")
    completed = self._run(runner, self.fake_codex)
    self.assertEqual(1, completed.returncode)
    report = json.loads(completed.stdout)
    self.assertEqual("ERROR", report["status"])
    self.assertEqual("infrastructure", report["failure_category"])
    self.assertEqual(1, report["model_sessions"]["total"])
    self.assertTrue(Path(report["artifacts"]).is_dir())
    self.assertIn("report_persistence_error", report)

  def test_renderer_rejects_tampered_digest_and_replays_identical_bytes(self):
    runner, _ = self._configured_runner()
    completed = self._run(runner, self.fake_codex)
    self.assertEqual(0, completed.returncode, completed.stderr)
    report_path = Path(json.loads(completed.stdout)["evidence_report"])
    replay = self.root / "replay.md"
    rendered = subprocess.run(
      [
        "python3",
        str(RENDERER),
        "--input",
        str(report_path),
        "--output",
        str(replay),
      ],
      text=True,
      capture_output=True,
      check=False,
    )
    self.assertEqual(0, rendered.returncode, rendered.stderr)
    self.assertEqual(report_path.with_name("report.md").read_bytes(), replay.read_bytes())
    normalized = json.loads(report_path.read_text(encoding="utf-8"))
    normalized["observations"][0]["executor"]["response"]["diagnosis"] = ""
    normalized["observations"][0]["evidence"]["diff"] = (
      "+line with spaces  \n+next line\n"
    )
    from eval_report import report_digest
    normalized["report_digest"]["value"] = report_digest(normalized)
    report_path.write_text(
      json.dumps(normalized, indent=2, ensure_ascii=False) + "\n",
      encoding="utf-8",
    )
    rendered = subprocess.run(
      [
        "python3",
        str(RENDERER),
        "--input",
        str(report_path),
        "--output",
        str(replay),
      ],
      text=True,
      capture_output=True,
      check=False,
    )
    self.assertEqual(0, rendered.returncode, rendered.stderr)
    self.assertTrue(all(
      line == line.rstrip()
      for line in replay.read_text(encoding="utf-8").splitlines()
    ))

    tampered = normalized
    tampered["duration_ms"] += 1
    report_path.write_text(json.dumps(tampered), encoding="utf-8")
    rendered = subprocess.run(
      [
        "python3",
        str(RENDERER),
        "--input",
        str(report_path),
        "--output",
        str(replay),
      ],
      text=True,
      capture_output=True,
      check=False,
    )
    self.assertNotEqual(0, rendered.returncode)
    self.assertIn("digest mismatch", rendered.stderr)

  def test_comparator_rejects_duplicate_ids_and_mixed_skills(self):
    runner, _ = self._configured_runner()
    completed = self._run(runner, self.fake_codex)
    self.assertEqual(0, completed.returncode, completed.stderr)
    source = Path(json.loads(completed.stdout)["evidence_report"])
    reports = self.root / "comparison-input"
    first = reports / "one" / "report.json"
    second = reports / "two" / "report.json"
    first.parent.mkdir(parents=True)
    second.parent.mkdir(parents=True)
    shutil.copy2(source, first)
    shutil.copy2(source, second)
    compared = self._compare(reports)
    self.assertNotEqual(0, compared.returncode)
    self.assertIn("Duplicate operation id", compared.stderr)

    from eval_report import report_digest

    changed = json.loads(second.read_text(encoding="utf-8"))
    changed["operation"]["id"] += "-other"
    changed["skill"]["name"] = "other-skill"
    changed["report_digest"]["value"] = report_digest(changed)
    second.write_text(
      json.dumps(changed, indent=2, ensure_ascii=False) + "\n",
      encoding="utf-8",
    )
    compared = self._compare(reports)
    self.assertNotEqual(0, compared.returncode)
    self.assertIn("different skills", compared.stderr)

  def test_archive_rebuild_and_validation_are_deterministic(self):
    runner, archive = self._configured_runner()
    completed = self._run(runner, self.fake_codex)
    self.assertEqual(0, completed.returncode, completed.stderr)
    rebuilt = subprocess.run(
      [
        "python3",
        str(ARCHIVE_MANAGER),
        "rebuild",
        "--archive",
        str(archive),
      ],
      text=True,
      capture_output=True,
      check=False,
    )
    self.assertEqual(0, rebuilt.returncode, rebuilt.stderr)
    first_manifest = (archive / "manifest.json").read_bytes()
    validated = subprocess.run(
      [
        "python3",
        str(ARCHIVE_MANAGER),
        "validate",
        "--archive",
        str(archive),
      ],
      text=True,
      capture_output=True,
      check=False,
    )
    self.assertEqual(0, validated.returncode, validated.stderr)
    rebuilt = subprocess.run(
      [
        "python3",
        str(ARCHIVE_MANAGER),
        "rebuild",
        "--archive",
        str(archive),
      ],
      text=True,
      capture_output=True,
      check=False,
    )
    self.assertEqual(0, rebuilt.returncode, rebuilt.stderr)
    self.assertEqual(first_manifest, (archive / "manifest.json").read_bytes())
    report_md = next(archive.glob("*/operations/*/report.md"))
    report_md.write_text("tampered\n", encoding="utf-8")
    validated = subprocess.run(
      [
        "python3",
        str(ARCHIVE_MANAGER),
        "validate",
        "--archive",
        str(archive),
      ],
      text=True,
      capture_output=True,
      check=False,
    )
    self.assertNotEqual(0, validated.returncode)
    self.assertIn("Markdown replay mismatch", validated.stderr)

  def _configured_runner(self):
    repo = self.root / "configured-repo"
    runner = self._copy_runner(repo)
    archive = repo / "evaluation-reports"
    (archive / "pricing").mkdir(parents=True)
    shutil.copy2(self.pricing, archive / "pricing" / "2026-07-26.json")
    (archive / "archive-config.json").write_text(json.dumps({
      "version": 1,
      "pricing_file": "pricing/2026-07-26.json",
      "comparisons": [],
    }), encoding="utf-8")
    return runner, archive

  def _copy_runner(self, repo):
    scripts = repo / "develop-skill-with-evals" / "scripts"
    shutil.copytree(
      SCRIPTS,
      scripts,
      ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "tests"),
    )
    return scripts / "run_skill_evals.py"

  def _run(self, runner, codex, skill=None, case="write-result", extra=None):
    return subprocess.run(
      [
        "python3",
        str(runner),
        "run",
        "--skill",
        str(skill or self.skill),
        "--case",
        case,
        "--source",
        "working-tree",
        "--model",
        "fixture-model",
        "--reasoning-effort",
        "medium",
        "--codex-command",
        str(codex),
        "--artifacts-dir",
        str(self.root / "artifacts"),
        *(extra or []),
      ],
      text=True,
      capture_output=True,
      check=False,
    )

  def _compare(self, reports):
    return subprocess.run(
      [
        "python3",
        str(COMPARATOR),
        "--reports",
        str(reports),
        "--output-dir",
        str(self.root / "comparison-output"),
      ],
      text=True,
      capture_output=True,
      check=False,
    )

  def _behavioral_skill(self, name):
    skill = self.root / name
    case = skill / "evals" / "cases" / "write-result"
    case.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
      f"---\nname: {name}\ndescription: Archive fixture.\n---\n",
      encoding="utf-8",
    )
    (skill / "evals" / "suite.json").write_text(
      json.dumps({"version": 1, "cases": ["write-result"]}),
      encoding="utf-8",
    )
    (case / "prompt.md").write_text("Create result.txt.", encoding="utf-8")
    (case / "case.json").write_text(json.dumps({
      "id": "write-result",
      "kind": "behavioral",
      "prompt_file": "prompt.md",
      "mechanical": {
        "expected_exit_code": 0,
        "required_paths": ["result.txt"],
      },
      "judge": {"enabled": False, "criteria": []},
    }), encoding="utf-8")
    return skill

  def _deterministic_skill(self):
    skill = self.root / "deterministic-skill"
    case = skill / "evals" / "cases" / "deterministic-check"
    fixture = case / "fixture"
    fixture.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
      "---\nname: deterministic-skill\ndescription: Deterministic fixture.\n---\n",
      encoding="utf-8",
    )
    (skill / "evals" / "suite.json").write_text(
      json.dumps({"version": 1, "cases": ["deterministic-check"]}),
      encoding="utf-8",
    )
    (fixture / "check.py").write_text("raise SystemExit(0)\n", encoding="utf-8")
    (case / "case.json").write_text(json.dumps({
      "id": "deterministic-check",
      "kind": "deterministic",
      "mechanical": {
        "commands": [{"argv": ["python3", "check.py"], "exit_code": 0}],
      },
      "judge": {"enabled": False, "criteria": []},
    }), encoding="utf-8")
    return skill

  def _fake_codex(self, name):
    fake = self.root / name
    fake.write_text(
      "#!/usr/bin/env python3\n"
      "import json\n"
      "from pathlib import Path\n"
      "import sys\n"
      "if '--version' in sys.argv:\n"
      "  print('codex fixture')\n"
      "  raise SystemExit(0)\n"
      "if sys.argv[1:3] == ['login', 'status']:\n"
      "  print('Logged in with ChatGPT')\n"
      "  raise SystemExit(0)\n"
      "workspace = Path(sys.argv[sys.argv.index('-C') + 1])\n"
      "output = Path(sys.argv[sys.argv.index('-o') + 1])\n"
      "(workspace / 'result.txt').write_text('ok', encoding='utf-8')\n"
      "output.write_text(json.dumps({\n"
      "  'summary': 'Created result.',\n"
      "  'classification': 'implementation',\n"
      "  'evidence': ['result.txt'],\n"
      "  'files_changed': ['result.txt'],\n"
      "  'diagnosis': 'The result was absent.',\n"
      "  'approach': ['Create it.'],\n"
      "  'decisions': [],\n"
      "  'rejected_alternatives': [],\n"
      "  'key_changes': ['Added result.txt.'],\n"
      "  'validation': ['Checked result.txt.'],\n"
      "}), encoding='utf-8')\n"
      "print(json.dumps({'type': 'turn.completed', 'usage': {\n"
      "  'input_tokens': 100,\n"
      "  'cached_input_tokens': 20,\n"
      "  'output_tokens': 10,\n"
      "  'reasoning_output_tokens': 4,\n"
      "}}))\n",
      encoding="utf-8",
    )
    fake.chmod(0o755)
    return fake


if __name__ == "__main__":
  unittest.main()
