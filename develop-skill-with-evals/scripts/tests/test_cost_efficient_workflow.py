import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


SCRIPT = Path(
  os.environ.get(
    "RUN_SKILL_EVALS_SCRIPT",
    Path(__file__).parents[1] / "run_skill_evals.py",
  )
)


def load_runner():
  spec = importlib.util.spec_from_file_location("cost_efficient_runner", SCRIPT)
  module = importlib.util.module_from_spec(spec)
  spec.loader.exec_module(module)
  return module


class CostEfficientWorkflowTest(unittest.TestCase):
  def setUp(self):
    self.temp = tempfile.TemporaryDirectory()
    self.root = Path(self.temp.name)
    self.skill = self.root / "sample-skill"
    self.skill.mkdir()
    (self.skill / "SKILL.md").write_text(
      "---\nname: sample-skill\ndescription: Test.\n---\n",
      encoding="utf-8",
    )
    (self.skill / "marker.txt").write_text("candidate", encoding="utf-8")
    (self.skill / "evals" / "cases").mkdir(parents=True)
    (self.skill / "evals" / "suite.json").write_text(
      json.dumps({"version": 1, "cases": []}),
      encoding="utf-8",
    )
    self.fake = self.root / "fake-codex"
    self.fake.write_text(
      "#!/usr/bin/env python3\n"
      "import json, os, pathlib, sys\n"
      "out = pathlib.Path(sys.argv[sys.argv.index('-o') + 1])\n"
      "cwd = pathlib.Path(sys.argv[sys.argv.index('-C') + 1])\n"
      "schema = pathlib.Path(sys.argv[sys.argv.index('--output-schema') + 1])\n"
      "mode = os.environ.get('FAKE_CODEX_MODE', 'pass')\n"
      "if mode == 'infrastructure':\n"
      "  print('authentication failed', file=sys.stderr)\n"
      "  sys.exit(1)\n"
      "if 'judge' in schema.name:\n"
      "  response = {'verdict': 'PASS', 'rationale': 'ok', 'evidence': []}\n"
      "else:\n"
      "  marker = next((cwd / '.agents/skills').glob('*/marker.txt'))\n"
      "  if mode == 'pass' and marker.read_text() == 'candidate': (cwd / 'result.txt').write_text('ok')\n"
      "  response = {'summary': mode, 'classification': 'test', 'evidence': [], 'files_changed': ['result.txt']}\n"
      "out.write_text(json.dumps(response))\n"
      "usage = os.environ.get('FAKE_CODEX_USAGE')\n"
      "if '--json' in sys.argv:\n"
      "  event = {'type': 'turn.completed'}\n"
      "  if usage == 'complete': event['usage'] = {'input_tokens': 11, 'cached_input_tokens': 3, 'output_tokens': 5}\n"
      "  print(json.dumps(event))\n",
      encoding="utf-8",
    )
    self.fake.chmod(0o755)

  def tearDown(self):
    self.temp.cleanup()

  def add_case(
    self,
    case_id,
    *,
    judge=False,
    required="result.txt",
    oracle=None,
  ):
    case_dir = self.skill / "evals" / "cases" / case_id
    (case_dir / "fixture").mkdir(parents=True)
    manifest = {
      "id": case_id,
      "kind": "behavioral",
      "prompt_file": "prompt.md",
      "mechanical": {
        "expected_exit_code": 0,
        "required_paths": [required],
      },
      "judge": {
        "enabled": judge,
        "criteria": ["The result is correct."] if judge else [],
      },
    }
    if oracle is not None:
      manifest["oracle"] = {
        "commands": [{"argv": ["python3", "{oracle_dir}/check.py"]}]
      }
      (case_dir / "oracle").mkdir()
      (case_dir / "oracle" / "check.py").write_text(oracle, encoding="utf-8")
    (case_dir / "case.json").write_text(json.dumps(manifest), encoding="utf-8")
    (case_dir / "prompt.md").write_text(f"Complete {case_id}.", encoding="utf-8")
    suite_path = self.skill / "evals" / "suite.json"
    suite = json.loads(suite_path.read_text(encoding="utf-8"))
    suite["cases"].append(case_id)
    suite_path.write_text(json.dumps(suite), encoding="utf-8")
    return case_dir

  def baseline(self):
    baseline = self.root / "baseline"
    shutil.copytree(self.skill, baseline)
    (baseline / "marker.txt").write_text("baseline", encoding="utf-8")
    return baseline

  def command(self, operation, baseline=None, extra=None):
    command = [
      "python3",
      str(SCRIPT),
      operation,
      "--skill",
      str(self.skill),
    ]
    if baseline is not None:
      command.extend(["--baseline", str(baseline)])
    if operation in {"plan", "probe-change", "validate-change"}:
      command.extend([
        "--impact",
        "cross-cutting",
        "--case",
        "affected",
      ])
    if operation != "plan":
      command.extend([
        "--codex-command",
        str(self.fake),
        "--artifacts-dir",
        str(self.root / "artifacts"),
      ])
    command.extend(extra or [])
    return command

  def invoke(self, operation, baseline=None, extra=None, env=None):
    return subprocess.run(
      self.command(operation, baseline, extra),
      text=True,
      capture_output=True,
      check=False,
      env={**os.environ, **(env or {})},
    )

  def test_help_and_parser_expose_diagnostic_workflow_and_campaign_controls(self):
    runner = load_runner()
    args = runner.parse_args([
      "plan",
      "--skill",
      str(self.skill),
      "--baseline",
      str(self.skill),
      "--impact",
      "static",
      "--workflow",
      "diagnostic",
      "--campaign-ledger",
      str(self.root / "ledger.json"),
      "--approved-cumulative-model-sessions",
      "12",
    ])

    self.assertEqual("diagnostic", args.workflow)
    self.assertEqual(self.root / "ledger.json", args.campaign_ledger)
    self.assertEqual(12, args.approved_cumulative_model_sessions)
    for operation in ("plan", "probe-change", "validate-change"):
      completed = subprocess.run(
        ["python3", str(SCRIPT), operation, "--help"],
        text=True,
        capture_output=True,
        check=False,
      )
      self.assertEqual(0, completed.returncode, completed.stderr)
      self.assertIn("--campaign-ledger", completed.stdout)
      self.assertIn("--approved-cumulative-model-sessions", completed.stdout)

  def test_plans_count_diagnostic_once_and_promotion_with_early_regression(self):
    self.add_case("affected", judge=False)
    self.add_case("regression", judge=True)
    baseline = self.baseline()

    diagnostic = self.invoke(
      "plan",
      baseline,
      ["--workflow", "diagnostic"],
    )
    promotion = self.invoke(
      "plan",
      baseline,
      ["--workflow", "promotion"],
    )

    diagnostic_plan = json.loads(diagnostic.stdout)
    promotion_plan = json.loads(promotion.stdout)
    self.assertEqual(0, diagnostic.returncode, diagnostic.stderr)
    self.assertEqual(4, diagnostic_plan["sessions"]["total"])
    self.assertEqual(
      ["baseline-red", "candidate-observation", "remaining-suite-regression", "structural-validation"],
      diagnostic_plan["steps"],
    )
    self.assertEqual(6, promotion_plan["sessions"]["total"])
    self.assertEqual(
      [
        "baseline-red",
        "candidate-green-1",
        "remaining-suite-regression",
        "candidate-green-2-and-3",
        "structural-validation",
      ],
      promotion_plan["steps"],
    )
    self.assertEqual("promotion", load_runner().parse_args([
      "plan",
      "--skill",
      str(self.skill),
      "--baseline",
      str(baseline),
      "--impact",
      "cross-cutting",
      "--case",
      "affected",
    ]).workflow)

  def test_fingerprints_cover_prompt_fixture_oracle_and_both_sources(self):
    case_dir = self.add_case(
      "affected",
      oracle="from pathlib import Path\nassert Path('result.txt').read_text() == 'ok'\n",
    )
    baseline = self.baseline()

    def plan():
      completed = self.invoke("plan", baseline, ["--workflow", "promotion"])
      self.assertEqual(0, completed.returncode, completed.stderr)
      return json.loads(completed.stdout)

    initial = plan()
    self.assertIn("affected", initial["case_fingerprints"])
    self.assertEqual({"baseline", "candidate"}, set(initial["source_fingerprints"]))
    mutations = [
      (case_dir / "prompt.md", "changed prompt"),
      (case_dir / "fixture" / "input.txt", "fixture"),
      (case_dir / "oracle" / "check.py", "raise SystemExit(1)\n"),
      (self.skill / "marker.txt", "changed source"),
      (baseline / "marker.txt", "changed baseline"),
    ]
    previous = initial
    for path, content in mutations:
      path.write_text(content, encoding="utf-8")
      current = plan()
      self.assertNotEqual(previous["evaluation_fingerprint"], current["evaluation_fingerprint"])
      previous = current

  def test_hidden_oracle_runs_without_being_copied_to_executor_workspace(self):
    self.add_case(
      "affected",
      oracle=(
        "from pathlib import Path\n"
        "assert Path('result.txt').read_text() == 'ok'\n"
        "assert not list(Path('.').rglob('oracle'))\n"
        "assert not list(Path('.').rglob('check.py'))\n"
      ),
    )

    completed = subprocess.run(
      [
        "python3",
        str(SCRIPT),
        "run",
        "--skill",
        str(self.skill),
        "--case",
        "affected",
        "--source",
        "working-tree",
        "--codex-command",
        str(self.fake),
        "--artifacts-dir",
        str(self.root / "artifacts"),
      ],
      text=True,
      capture_output=True,
      check=False,
    )

    report = json.loads(completed.stdout)
    self.assertEqual(0, completed.returncode, json.dumps(report, indent=2))
    result = report["results"][0]
    self.assertTrue(result["oracle"]["enabled"])
    self.assertTrue(result["oracle"]["passed"])
    self.assertNotIn("oracle", "\n".join(result["changed_paths"]))

  def test_usage_preserves_complete_counts_and_unknown_values(self):
    self.add_case("affected")

    complete = subprocess.run(
      [
        "python3",
        str(SCRIPT),
        "run",
        "--skill",
        str(self.skill),
        "--case",
        "affected",
        "--source",
        "working-tree",
        "--codex-command",
        str(self.fake),
        "--artifacts-dir",
        str(self.root / "artifacts-complete"),
      ],
      text=True,
      capture_output=True,
      check=False,
      env={**os.environ, "FAKE_CODEX_USAGE": "complete"},
    )
    incomplete = subprocess.run(
      [
        "python3",
        str(SCRIPT),
        "run",
        "--skill",
        str(self.skill),
        "--case",
        "affected",
        "--source",
        "working-tree",
        "--codex-command",
        str(self.fake),
        "--artifacts-dir",
        str(self.root / "artifacts-incomplete"),
      ],
      text=True,
      capture_output=True,
      check=False,
    )

    complete_usage = json.loads(complete.stdout)["usage"]
    incomplete_usage = json.loads(incomplete.stdout)["usage"]
    self.assertTrue(complete_usage["complete"])
    self.assertEqual(11, complete_usage["input_tokens"])
    self.assertEqual(3, complete_usage["cached_input_tokens"])
    self.assertEqual(5, complete_usage["output_tokens"])
    self.assertEqual(16, complete_usage["total_tokens"])
    self.assertFalse(incomplete_usage["complete"])
    for field in ("input_tokens", "cached_input_tokens", "output_tokens", "total_tokens"):
      self.assertIsNone(incomplete_usage[field])

  def test_validate_change_runs_regression_between_candidate_one_and_two(self):
    self.add_case("affected")
    self.add_case("regression")
    baseline = self.baseline()

    completed = self.invoke(
      "validate-change",
      baseline,
      [
        "--model",
        "executor",
        "--reasoning-effort",
        "medium",
        "--approved-model-sessions",
        "5",
      ],
    )

    report = json.loads(completed.stdout)
    self.assertEqual(0, completed.returncode, json.dumps(report, indent=2))
    self.assertEqual(
      [
        ("baseline", None),
        ("candidate", 1),
        ("regression", None),
        ("candidate", 2),
        ("candidate", 3),
      ],
      [(result["role"], result.get("repetition")) for result in report["results"]],
    )

  def test_probe_collects_contract_failures_but_stops_on_infrastructure(self):
    self.add_case("affected", required="missing-affected.txt")
    self.add_case("regression", required="missing-regression.txt")
    baseline = self.baseline()

    contract = self.invoke(
      "probe-change",
      baseline,
      [
        "--model",
        "executor",
        "--reasoning-effort",
        "medium",
        "--approved-model-sessions",
        "3",
      ],
      env={"FAKE_CODEX_MODE": "contract"},
    )
    infrastructure = self.invoke(
      "probe-change",
      baseline,
      [
        "--model",
        "executor",
        "--reasoning-effort",
        "medium",
        "--approved-model-sessions",
        "3",
      ],
      env={"FAKE_CODEX_MODE": "infrastructure"},
    )

    contract_report = json.loads(contract.stdout)
    infrastructure_report = json.loads(infrastructure.stdout)
    self.assertFalse(contract_report["promotion_eligible"])
    self.assertEqual(3, len(contract_report["results"]))
    self.assertTrue(all(
      result["failure_category"] == "contract"
      for result in contract_report["results"]
    ))
    self.assertEqual("infrastructure", infrastructure_report["failure_category"])
    self.assertEqual(1, len(infrastructure_report["results"]))

  def test_campaign_ledger_blocks_without_effects_and_records_failed_consumption(self):
    self.add_case("affected", required="missing.txt")
    baseline = self.baseline()
    ledger = self.root / "campaign.json"
    common = [
      "--model",
      "executor",
      "--reasoning-effort",
      "medium",
      "--approved-model-sessions",
      "2",
      "--campaign-ledger",
      str(ledger),
    ]

    blocked = self.invoke(
      "probe-change",
      baseline,
      common + ["--approved-cumulative-model-sessions", "1"],
    )

    blocked_plan = json.loads(blocked.stdout)
    self.assertEqual(2, blocked.returncode, blocked.stderr)
    self.assertIn(
      "insufficient-cumulative-model-session-budget",
      [item["code"] for item in blocked_plan["execution_blockers"]],
    )
    self.assertFalse(ledger.exists())
    self.assertFalse((self.root / "artifacts").exists())

    failed = self.invoke(
      "probe-change",
      baseline,
      common + ["--approved-cumulative-model-sessions", "2"],
      env={"FAKE_CODEX_MODE": "contract", "FAKE_CODEX_USAGE": "complete"},
    )

    failed_report = json.loads(failed.stdout)
    stored = json.loads(ledger.read_text(encoding="utf-8"))
    self.assertNotEqual(0, failed.returncode)
    self.assertEqual(2, stored["consumed_model_sessions"])
    self.assertEqual(2, failed_report["campaign"]["consumed_after"])
    self.assertEqual(2, failed_report["model_sessions"]["total"])

  def test_migrated_oracles_reject_recorded_defect_shapes(self):
    skill_root = Path(__file__).parents[2]
    cases_root = skill_root / "evals" / "cases"
    defects = {
      "explicit-runtime-promotion-workflow": {
        "plan.json": "{}",
        "validation.json": "{}",
      },
      "impact-gate-selection": {
        "plan-exit-code.txt": "2\n",
        "plan-stderr.log": "plan rejected required arguments\n",
      },
      "load-skill-creator-before-scaffold": {
        "weather-brief/SKILL.md": "---\nname: weather-brief\ndescription: Test.\n---\n",
      },
      "eval-before-behavior": {
        "target-skill/SKILL.md": "PRIVATE refusal added without RED evidence\n",
      },
      "self-evolution-candidate": {
        "baseline/SKILL.md": "baseline\n",
        "skills/candidate/SKILL.md": "wrong destination\n",
      },
    }

    for case_id, files in defects.items():
      with self.subTest(case_id=case_id):
        workspace = self.root / f"replay-{case_id}"
        workspace.mkdir()
        for relative, content in files.items():
          path = workspace / relative
          path.parent.mkdir(parents=True, exist_ok=True)
          path.write_text(content, encoding="utf-8")
        manifest = json.loads(
          (cases_root / case_id / "case.json").read_text(encoding="utf-8")
        )
        command = manifest["oracle"]["commands"][0]["argv"]
        oracle_dir = (cases_root / case_id / "oracle").resolve()
        argv = [
          item.replace("{oracle_dir}", str(oracle_dir))
          for item in command
        ]
        completed = subprocess.run(
          argv,
          cwd=workspace,
          text=True,
          capture_output=True,
          check=False,
        )
        self.assertNotEqual(0, completed.returncode)
        fixture = cases_root / case_id / "fixture"
        if fixture.exists():
          self.assertFalse(any(
            path.name == next(oracle_dir.iterdir()).name
            for path in fixture.rglob("*")
            if path.is_file()
          ))

  def test_runner_progress_regression_matches_disabled_judge_behavior(self):
    skill_root = Path(__file__).parents[2]
    completed = subprocess.run(
      [
        "python3",
        str(SCRIPT),
        "run",
        "--skill",
        str(skill_root),
        "--case",
        "runner-progress-output",
        "--source",
        "working-tree",
        "--artifacts-dir",
        str(self.root / "progress-artifacts"),
      ],
      text=True,
      capture_output=True,
      check=False,
    )

    self.assertEqual(0, completed.returncode, completed.stderr)
    report = json.loads(completed.stdout)
    self.assertEqual("PASS", report["status"])
    self.assertEqual(0, report["model_sessions"]["total"])

  def test_campaign_releases_reservation_when_workspace_creation_fails(self):
    self.add_case("affected")
    baseline = self.baseline()
    ledger = self.root / "campaign-workspace-error.json"
    (self.root / "artifacts").write_text("not a directory", encoding="utf-8")

    completed = self.invoke(
      "probe-change",
      baseline,
      [
        "--model",
        "executor",
        "--reasoning-effort",
        "medium",
        "--approved-model-sessions",
        "2",
        "--campaign-ledger",
        str(ledger),
        "--approved-cumulative-model-sessions",
        "2",
      ],
    )

    report = json.loads(completed.stdout)
    stored = json.loads(ledger.read_text(encoding="utf-8"))
    self.assertEqual(1, completed.returncode)
    self.assertEqual("ERROR", report["status"])
    self.assertEqual([], stored["active_reservations"])
    self.assertEqual(0, stored["consumed_model_sessions"])
    self.assertEqual("ERROR", stored["history"][-1]["status"])

  def test_primary_workflow_oracle_accepts_four_step_zero_session_flow(self):
    skill_root = Path(__file__).parents[2]
    case_dir = (
      skill_root
      / "evals"
      / "cases"
      / "explicit-runtime-promotion-workflow"
    )
    workspace = self.root / "primary-workflow"
    shutil.copytree(case_dir / "fixture", workspace)
    installed = workspace / ".agents" / "skills" / "develop-skill-with-evals"
    installed.parent.mkdir(parents=True)
    shutil.copytree(
      skill_root,
      installed,
      ignore=shutil.ignore_patterns("evals", "__pycache__", "*.pyc"),
    )
    renderer = workspace / "sample-skill" / "scripts" / "render.py"
    renderer.write_text(
      renderer.read_text(encoding="utf-8").replace(
        "sys.argv[1].upper()",
        "sys.argv[1].strip().upper()",
      ),
      encoding="utf-8",
    )
    audit_runner = workspace / "audit-runner"
    fake_codex = workspace / "fake-codex"
    audit_runner.chmod(0o755)
    fake_codex.chmod(0o755)
    common = [
      "--skill", "sample-skill",
      "--baseline", "sample-baseline",
      "--impact", "deterministic",
      "--model", "gpt-5.6-sol",
      "--reasoning-effort", "medium",
      "--judge-model", "gpt-5.6-terra",
      "--judge-reasoning-effort", "medium",
    ]
    operations = [
      ("diagnostic-plan.json", ["plan", *common, "--workflow", "diagnostic"]),
      (
        "diagnostic.json",
        [
          "probe-change", *common,
          "--codex-command", "./fake-codex",
          "--approved-model-sessions", "0",
        ],
      ),
      ("promotion-plan.json", ["plan", *common, "--workflow", "promotion"]),
      (
        "validation.json",
        [
          "validate-change", *common,
          "--codex-command", "./fake-codex",
          "--approved-model-sessions", "0",
        ],
      ),
    ]
    for output_name, arguments in operations:
      completed = subprocess.run(
        [str(audit_runner), *arguments],
        cwd=workspace,
        text=True,
        capture_output=True,
        check=False,
      )
      self.assertEqual(0, completed.returncode, completed.stderr)
      (workspace / output_name).write_text(completed.stdout, encoding="utf-8")

    for arguments in (
      ["--help"],
      ["plan", "--help"],
      ["probe-change", "--help"],
      ["validate-change", "--help"],
    ):
      completed = subprocess.run(
        [str(audit_runner), *arguments],
        cwd=workspace,
        text=True,
        capture_output=True,
        check=False,
      )
      self.assertEqual(0, completed.returncode, completed.stderr)

    oracle = case_dir / "oracle" / "check_workflow.py"
    checked = subprocess.run(
      ["python3", str(oracle)],
      cwd=workspace,
      text=True,
      capture_output=True,
      check=False,
    )
    self.assertEqual(0, checked.returncode, checked.stderr)
    self.assertFalse((workspace / "unexpected-nested-model-session").exists())
    self.assertFalse((installed / "evals").exists())

  def test_primary_workflow_restricts_behavior_change_to_renderer(self):
    skill_root = Path(__file__).parents[2]
    case_dir = (
      skill_root
      / "evals"
      / "cases"
      / "explicit-runtime-promotion-workflow"
    )
    manifest = json.loads((case_dir / "case.json").read_text(encoding="utf-8"))
    prompt = (case_dir / "prompt.md").read_text(encoding="utf-8")

    self.assertIn(
      "sample-skill/SKILL.md",
      manifest["mechanical"]["forbidden_changed_paths"],
    )
    self.assertIn("Update only", prompt)
    self.assertIn("Do not edit `sample-skill/SKILL.md`", prompt)

  def test_skill_creator_evidence_location_is_unambiguous(self):
    skill_root = Path(__file__).parents[2]
    case_dir = (
      skill_root
      / "evals"
      / "cases"
      / "load-skill-creator-before-scaffold"
    )
    manifest = json.loads((case_dir / "case.json").read_text(encoding="utf-8"))
    prompt = (case_dir / "prompt.md").read_text(encoding="utf-8")

    self.assertIn(
      "creation-evidence.json",
      manifest["mechanical"]["required_paths"],
    )
    self.assertIn(
      "weather-brief/creation-evidence.json",
      manifest["mechanical"]["forbidden_changed_paths"],
    )
    self.assertIn("at the workspace root", prompt)
    self.assertIn("outside `./weather-brief`", prompt)


if __name__ == "__main__":
  unittest.main()
