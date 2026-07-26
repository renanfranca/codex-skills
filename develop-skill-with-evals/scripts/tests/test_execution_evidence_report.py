import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


SKILL_ROOT = Path(__file__).parents[2]
RUNNER = SKILL_ROOT / "scripts" / "run_skill_evals.py"
RENDERER = SKILL_ROOT / "scripts" / "render_eval_report.py"
COMPARATOR = SKILL_ROOT / "scripts" / "compare_model_reports.py"


class ExecutionEvidenceReportTest(unittest.TestCase):
  def setUp(self):
    self.temp = tempfile.TemporaryDirectory()
    self.root = Path(self.temp.name)
    self.skill = self.root / "sample-skill"
    case_dir = self.skill / "evals" / "cases" / "write-result"
    case_dir.mkdir(parents=True)
    (self.skill / "SKILL.md").write_text(
      "---\nname: sample-skill\ndescription: Test evidence reports.\n---\n",
      encoding="utf-8",
    )
    (self.skill / "marker.txt").write_text("candidate", encoding="utf-8")
    (self.skill / "evals" / "suite.json").write_text(
      json.dumps({"version": 1, "cases": ["write-result"]}),
      encoding="utf-8",
    )
    (case_dir / "prompt.md").write_text(
      "Create result.txt with the word ok.",
      encoding="utf-8",
    )
    (case_dir / "case.json").write_text(
      json.dumps({
        "id": "write-result",
        "kind": "behavioral",
        "prompt_file": "prompt.md",
        "mechanical": {
          "expected_exit_code": 0,
          "required_paths": ["result.txt"],
          "forbidden_changed_paths": [".agents/skills/**"],
        },
        "judge": {"enabled": False, "criteria": []},
      }),
      encoding="utf-8",
    )
    self.fake = self.root / "fake-codex"
    self.fake.write_text(
      "#!/usr/bin/env python3\n"
      "import json\n"
      "import os\n"
      "from pathlib import Path\n"
      "import sys\n"
      "if '--version' in sys.argv or sys.argv[1:3] == ['login', 'status']:\n"
      "  raise SystemExit(9)\n"
      "workspace = Path(sys.argv[sys.argv.index('-C') + 1])\n"
      "output = Path(sys.argv[sys.argv.index('-o') + 1])\n"
      "(workspace / 'result.txt').write_text('ok', encoding='utf-8')\n"
      "(workspace / 'large.txt').write_text('x' * 50000, encoding='utf-8')\n"
      "(workspace / 'credentials.txt').write_text('OPENAI_API_KEY=sk-test-secret-value', encoding='utf-8')\n"
      "(workspace / '.eval-secret').write_text('secret', encoding='utf-8')\n"
      "(workspace / '__pycache__').mkdir(exist_ok=True)\n"
      "(workspace / '__pycache__' / 'secret.pyc').write_bytes(b'secret')\n"
      "response = {\n"
      "  'summary': 'Created the required result.',\n"
      "  'classification': 'implementation',\n"
      "  'evidence': ['result.txt contains ok'],\n"
      "  'files_changed': ['result.txt', 'large.txt'],\n"
      "  'diagnosis': 'The requested output file was absent.',\n"
      "  'approach': ['Create the requested text file.'],\n"
      "  'decisions': ['Use UTF-8 text.'],\n"
      "  'rejected_alternatives': [],\n"
      "  'key_changes': ['Added result.txt.'],\n"
      "  'validation': ['Verified the exact file contents.'],\n"
      "}\n"
      "output.write_text(json.dumps(response), encoding='utf-8')\n"
      "print(json.dumps({'type': 'turn.completed', 'usage': {\n"
      "  'input_tokens': int(os.environ.get('FAKE_INPUT_TOKENS', '100')),\n"
      "  'cached_input_tokens': 20,\n"
      "  'output_tokens': 10,\n"
      "  'reasoning_output_tokens': 4,\n"
      "}}))\n",
      encoding="utf-8",
    )
    self.fake.chmod(0o755)
    self.pricing = self.root / "pricing.json"
    self.pricing.write_text(
      json.dumps({
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
            "long_context": {
              "input_token_threshold": 272000,
              "input_multiplier": 2.0,
              "output_multiplier": 1.5,
              "applies_per": "request",
            },
          }
        },
        "limitations": ["Fixture prices are not a charge."],
      }),
      encoding="utf-8",
    )

  def tearDown(self):
    self.temp.cleanup()

  def command(self, report_dir=None):
    command = [
      "python3",
      str(RUNNER),
      "run",
      "--skill",
      str(self.skill),
      "--case",
      "write-result",
      "--source",
      "working-tree",
      "--model",
      "fixture-model",
      "--reasoning-effort",
      "medium",
      "--codex-command",
      str(self.fake),
      "--artifacts-dir",
      str(self.root / "artifacts"),
    ]
    if report_dir is not None:
      command.extend([
        "--report-dir",
        str(report_dir),
        "--pricing-file",
        str(self.pricing),
      ])
    return command

  def run_with_report(self, name):
    report_dir = self.root / name
    completed = subprocess.run(
      self.command(report_dir),
      text=True,
      capture_output=True,
      check=False,
    )
    self.assertEqual(0, completed.returncode, completed.stderr)
    stdout_report = json.loads(completed.stdout)
    reports = list(report_dir.glob("*/report.json"))
    self.assertEqual(1, len(reports))
    return stdout_report, reports[0], json.loads(reports[0].read_text(encoding="utf-8"))

  def test_executed_commands_accept_report_and_pricing_options(self):
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
        self.assertIn("--report-dir", completed.stdout)
        self.assertIn("--pricing-file", completed.stdout)

  def test_report_persists_pass_evidence_before_workspace_cleanup(self):
    stdout_report, report_path, evidence = self.run_with_report("reports")

    self.assertEqual("PASS", stdout_report["status"])
    self.assertIsNone(stdout_report["artifacts"])
    self.assertTrue(report_path.exists())
    self.assertTrue(report_path.with_name("report.md").exists())
    self.assertEqual("run", evidence["operation"]["type"])
    self.assertEqual("PASS", evidence["operation"]["status"])
    self.assertEqual("executed", evidence["provenance"])
    self.assertEqual("fixture-model", evidence["runtime"]["executor"]["model"])
    self.assertGreaterEqual(evidence["duration_ms"], 0)
    self.assertIsNone(evidence["environment"]["codex_cli"]["version"])
    self.assertEqual("unavailable", evidence["environment"]["codex_cli"]["status"])
    self.assertEqual("unknown", evidence["environment"]["authentication"]["mode"])
    self.assertEqual(
      hashlib.sha256(RUNNER.read_bytes()).hexdigest(),
      evidence["environment"]["runner"]["sha256"],
    )
    self.assertEqual(1, len(evidence["observations"]))
    observation = evidence["observations"][0]
    self.assertGreaterEqual(observation["duration_ms"], 0)
    self.assertGreaterEqual(observation["executor"]["duration_ms"], 0)
    self.assertEqual(4, observation["usage"]["reasoning_output_tokens"])
    self.assertTrue(observation["usage"]["reasoning_output_tokens_complete"])
    self.assertEqual(1, observation["usage"]["event_count"])
    self.assertTrue(observation["usage"]["events_complete"])
    self.assertEqual(
      {
        "sequence": 1,
        "source_event_type": "turn.completed",
        "scope": "turn",
        "input_tokens": 100,
        "cached_input_tokens": 20,
        "output_tokens": 10,
        "reasoning_output_tokens": 4,
        "total_tokens": 110,
        "complete": True,
        "reasoning_output_tokens_complete": True,
      },
      observation["usage"]["events"][0],
    )
    self.assertEqual(
      "The requested output file was absent.",
      observation["executor"]["response"]["diagnosis"],
    )
    self.assertEqual("Create result.txt with the word ok.", observation["prompt"])
    self.assertEqual(
      ["credentials.txt", "large.txt", "result.txt"],
      observation["evidence"]["changed_files"],
    )
    self.assertNotIn(".eval-secret", observation["evidence"]["diff"])
    self.assertNotIn("__pycache__", observation["evidence"]["diff"])
    self.assertNotIn(".agents/skills", observation["evidence"]["diff"])
    serialized = json.dumps(evidence)
    self.assertNotIn("sk-test-secret-value", serialized)
    self.assertIn("[REDACTED]", serialized)
    self.assertTrue(observation["evidence"]["truncated"])
    self.assertTrue(observation["evidence"]["truncations"])
    self.assertFalse(Path(observation["workspace"]["original_path"]).exists())
    self.assertEqual("removed", observation["workspace"]["retention"])
    self.assertEqual("chatgpt-plan-or-unknown", evidence["billing"]["mode"])
    self.assertFalse(evidence["api_reference_estimate"]["actual_charge"])
    self.assertEqual("complete", evidence["api_reference_estimate"]["status"])
    self.assertAlmostEqual(0.00011, evidence["api_reference_estimate"]["amount"])
    self.assertAlmostEqual(
      0.00011,
      evidence["api_reference_estimate"]["base_rate_amount"],
    )
    self.assertEqual(
      evidence["report_digest"]["value"],
      self._report_digest(evidence),
    )

  def test_markdown_rendering_is_deterministic_from_json(self):
    _, report_path, _ = self.run_with_report("render-source")
    first = self.root / "first.md"
    second = self.root / "second.md"

    for output in (first, second):
      completed = subprocess.run(
        [
          "python3",
          str(RENDERER),
          "--input",
          str(report_path),
          "--output",
          str(output),
        ],
        text=True,
        capture_output=True,
        check=False,
      )
      self.assertEqual(0, completed.returncode, completed.stderr)

    self.assertEqual(first.read_bytes(), second.read_bytes())
    self.assertEqual(report_path.with_name("report.md").read_bytes(), first.read_bytes())
    markdown = first.read_text(encoding="utf-8")
    self.assertIn("API reference estimate", markdown)
    self.assertIn("not an actual charge", markdown)
    self.assertIn("Normalized usage events: `1`", markdown)
    self.assertIn("scopes `turn`", markdown)
    self.assertNotIn("secret", markdown)

  def test_turn_aggregate_above_request_threshold_is_not_exactly_priced(self):
    report_dir = self.root / "long-context-reports"
    environment = dict(os.environ)
    environment["FAKE_INPUT_TOKENS"] = "300000"
    completed = subprocess.run(
      self.command(report_dir),
      text=True,
      capture_output=True,
      check=False,
      env=environment,
    )

    self.assertEqual(0, completed.returncode, completed.stderr)
    report_path = next(report_dir.glob("*/report.json"))
    evidence = json.loads(report_path.read_text(encoding="utf-8"))
    usage = evidence["usage"]
    self.assertEqual(1, usage["event_count"])
    self.assertEqual("turn", usage["events"][0]["scope"])
    estimate = evidence["api_reference_estimate"]
    self.assertFalse(estimate["available"])
    self.assertEqual("indeterminate-long-context", estimate["status"])
    self.assertIsNone(estimate["amount"])
    self.assertAlmostEqual(0.30001, estimate["base_rate_amount"])
    self.assertEqual(
      {
        "input_token_threshold": 272000,
        "applies_per": "request",
        "triggering_event_sequences": [1],
        "observed_event_scopes": ["turn"],
      },
      estimate["long_context_assessment"],
    )
    self.assertTrue(any(
      "request-scoped threshold" in limitation
      for limitation in estimate["limitations"]
    ))
    markdown = report_path.with_name("report.md").read_text(encoding="utf-8")
    self.assertIn("Base-rate amount", markdown)
    self.assertIn("indeterminate-long-context", markdown)

    comparison_dir = self.root / "long-context-comparison"
    compared = subprocess.run(
      [
        "python3",
        str(COMPARATOR),
        "--reports",
        str(report_dir),
        "--output-dir",
        str(comparison_dir),
      ],
      text=True,
      capture_output=True,
      check=False,
    )
    self.assertEqual(0, compared.returncode, compared.stderr)
    comparison = json.loads(
      (comparison_dir / "comparison.json").read_text(encoding="utf-8")
    )
    cost = comparison["models"][0]["api_reference_cost"]
    self.assertFalse(cost["complete"])
    self.assertIsNone(cost["total"])
    self.assertAlmostEqual(0.30001, cost["base_rate_total"])
    self.assertAlmostEqual(0.30001, cost["base_rate_per_stable_gate"])
    self.assertEqual(1, cost["indeterminate_long_context_count"])

  def test_comparator_summarizes_three_stable_executed_reports(self):
    reports_root = self.root / "model-reports"
    for repetition in range(1, 4):
      self.run_with_report(str(reports_root / f"run-{repetition}"))
    output_dir = self.root / "comparison"

    completed = subprocess.run(
      [
        "python3",
        str(COMPARATOR),
        "--reports",
        str(reports_root),
        "--output-dir",
        str(output_dir),
      ],
      text=True,
      capture_output=True,
      check=False,
    )

    self.assertEqual(0, completed.returncode, completed.stderr)
    comparison = json.loads(
      (output_dir / "comparison.json").read_text(encoding="utf-8")
    )
    self.assertEqual(3, comparison["observation_count"])
    self.assertEqual(3, comparison["executed_observation_count"])
    model = comparison["models"][0]
    self.assertEqual("fixture-model", model["model"])
    self.assertEqual(3, model["pass_count"])
    self.assertTrue(model["cases"][0]["stable"])
    self.assertTrue(model["qualifies"])
    self.assertEqual(300, model["tokens"]["input"]["total"])
    self.assertEqual(0.2, model["cache_ratio"])
    self.assertAlmostEqual(0.00033, model["api_reference_cost"]["total"])
    self.assertEqual(1.0, model["explanation"]["complete_ratio"])
    self.assertEqual(1.0, model["explanation"]["coherent_ratio"])
    self.assertTrue((output_dir / "comparison.md").exists())

  def test_compatibility_without_report_dir_creates_no_evidence_report(self):
    completed = subprocess.run(
      self.command(),
      text=True,
      capture_output=True,
      check=False,
    )

    self.assertEqual(0, completed.returncode, completed.stderr)
    report = json.loads(completed.stdout)
    self.assertEqual("PASS", report["status"])
    self.assertNotIn("evidence_report", report)
    self.assertEqual([], list(self.root.glob("**/report.json")))

  def _report_digest(self, report):
    payload = dict(report)
    payload.pop("report_digest")
    encoded = json.dumps(
      payload,
      sort_keys=True,
      separators=(",", ":"),
      ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


if __name__ == "__main__":
  unittest.main()
