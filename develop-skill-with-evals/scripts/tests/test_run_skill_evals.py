import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock

from jsonschema import Draft202012Validator


SCRIPT = Path(os.environ.get("RUN_SKILL_EVALS_SCRIPT", Path(__file__).parents[1] / "run_skill_evals.py"))


def load_runner():
  spec = importlib.util.spec_from_file_location("run_skill_evals", SCRIPT)
  module = importlib.util.module_from_spec(spec)
  spec.loader.exec_module(module)
  return module


class TtyBuffer:
  def __init__(self):
    self.value = ""

  def isatty(self):
    return True

  def write(self, value):
    self.value += value
    return len(value)

  def flush(self):
    return None


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
      "import json, os, pathlib, sys, time\n"
      "out = pathlib.Path(sys.argv[sys.argv.index('-o') + 1])\n"
      "cwd = pathlib.Path(sys.argv[sys.argv.index('-C') + 1])\n"
      "mode = os.environ.get('FAKE_CODEX_MODE', 'pass')\n"
      "time.sleep(float(os.environ.get('FAKE_CODEX_DELAY', '0')))\n"
      "if os.environ.get('FAKE_CODEX_STDERR'): print(os.environ['FAKE_CODEX_STDERR'], file=sys.stderr)\n"
      "if mode == 'pass': (cwd / 'result.txt').write_text('ok')\n"
      "if mode == 'mutate-skill': (cwd / '.agents/skills/sample-skill/SKILL.md').write_text('changed')\n"
      "response = {'summary': mode, 'classification': 'Design risk', 'evidence': ['fixture'], 'files_changed': ['result.txt']}\n"
      "out.write_text(json.dumps(response))\n",
      encoding="utf-8",
    )
    self.fake.chmod(0o755)

  def tearDown(self):
    self.temp.cleanup()

  def command(self, *args):
    return ["python3", str(SCRIPT), *args, "--codex-command", str(self.fake), "--artifacts-dir", str(self.root / "artifacts")]

  def invoke(self, *args, env=None):
    command = self.command(*args)
    return subprocess.run(command, text=True, capture_output=True, env={**os.environ, **(env or {})}, check=False)

  def add_case(self, skill, case_id, manifest, prompt="Test request"):
    case_dir = skill / "evals" / "cases" / case_id
    (case_dir / "fixture").mkdir(parents=True)
    (case_dir / "case.json").write_text(json.dumps({"id": case_id, **manifest}), encoding="utf-8")
    if prompt is not None:
      (case_dir / "prompt.md").write_text(prompt, encoding="utf-8")
    suite_path = skill / "evals" / "suite.json"
    suite = json.loads(suite_path.read_text(encoding="utf-8"))
    suite["cases"].append(case_id)
    suite_path.write_text(json.dumps(suite), encoding="utf-8")
    return case_dir

  def test_parser_requires_exactly_case_or_all(self):
    runner = load_runner()

    with self.assertRaises(SystemExit):
      runner.parse_args(["run", "--skill", str(self.skill), "--source", "working-tree"])

  def test_all_commands_accept_runtime_selection_options(self):
    runner = load_runner()
    common = [
      "--model", "gpt-5.6-sol",
      "--reasoning-effort", "medium",
      "--judge-model", "gpt-5.6-terra",
      "--judge-reasoning-effort", "high",
    ]
    commands = [
      ["run", "--skill", str(self.skill), "--case", "write-result"],
      ["verify-change", "--skill", str(self.skill), "--case", "write-result"],
      ["stability", "--skill", str(self.skill), "--case", "write-result"],
      ["plan", "--skill", str(self.skill), "--baseline", str(self.skill), "--impact", "scoped", "--case", "write-result"],
      ["probe-change", "--skill", str(self.skill), "--baseline", str(self.skill), "--impact", "scoped", "--case", "write-result"],
      ["validate-change", "--skill", str(self.skill), "--baseline", str(self.skill), "--impact", "scoped", "--case", "write-result"],
    ]

    for command in commands:
      with self.subTest(operation=command[0]):
        args = runner.parse_args(command + common)
        self.assertEqual("gpt-5.6-sol", args.model)
        self.assertEqual("medium", args.reasoning_effort)
        self.assertEqual("gpt-5.6-terra", args.judge_model)
        self.assertEqual("high", args.judge_reasoning_effort)

  def test_all_command_help_lists_runtime_selection_options(self):
    for operation in ("run", "verify-change", "stability", "plan", "probe-change", "validate-change"):
      with self.subTest(operation=operation):
        completed = subprocess.run(
          ["python3", str(SCRIPT), operation, "--help"],
          text=True, capture_output=True, check=False,
        )
        self.assertEqual(0, completed.returncode, completed.stderr)
        for option in (
          "--model",
          "--reasoning-effort",
          "--judge-model",
          "--judge-reasoning-effort",
        ):
          self.assertIn(option, completed.stdout)

  def test_public_plan_and_result_validate_against_schemas(self):
    skill_root = Path(__file__).parents[2]
    plan_schema = json.loads(
      (skill_root / "references" / "eval-plan.schema.json").read_text(encoding="utf-8")
    )
    result_schema = json.loads(
      (skill_root / "references" / "eval-result.schema.json").read_text(encoding="utf-8")
    )
    baseline = self.root / "baseline-schema"
    subprocess.run(["cp", "-a", str(self.skill), str(baseline)], check=True)
    plan_completed = subprocess.run(
      [
        "python3", str(SCRIPT), "plan", "--skill", str(self.skill),
        "--baseline", str(baseline), "--impact", "scoped",
        "--case", "write-result", "--model", "gpt-5.6-sol",
        "--reasoning-effort", "medium",
      ],
      text=True, capture_output=True, check=False,
    )
    result_completed = self.invoke(
      "run", "--skill", str(self.skill), "--case", "write-result",
      "--source", "working-tree",
    )

    self.assertEqual(0, plan_completed.returncode, plan_completed.stderr)
    self.assertEqual(0, result_completed.returncode, result_completed.stderr)
    Draft202012Validator(plan_schema).validate(json.loads(plan_completed.stdout))
    Draft202012Validator(result_schema).validate(json.loads(result_completed.stdout))

  def test_plan_reports_runtime_sources_inheritance_and_stable_fingerprint(self):
    baseline = self.root / "baseline-runtime"
    subprocess.run(["cp", "-a", str(self.skill), str(baseline)], check=True)
    second_baseline = self.root / "second-baseline-runtime"
    subprocess.run(["cp", "-a", str(self.skill), str(second_baseline)], check=True)
    base_command = [
      "plan", "--skill", str(self.skill), "--baseline", str(baseline),
      "--impact", "scoped", "--case", "write-result",
      "--model", "gpt-5.6-sol", "--reasoning-effort", "medium",
    ]

    first = subprocess.run(
      ["python3", str(SCRIPT), *base_command],
      text=True, capture_output=True, check=False,
    )
    second_command = [
      value if value != str(baseline) else str(second_baseline)
      for value in base_command
    ]
    second = subprocess.run(
      ["python3", str(SCRIPT), *second_command],
      text=True, capture_output=True, check=False,
    )

    first_plan = json.loads(first.stdout)
    second_plan = json.loads(second.stdout)
    self.assertEqual(0, first.returncode, first.stderr)
    self.assertTrue(first_plan["runtime"]["complete"])
    self.assertEqual("promotion", first_plan["runtime"]["audit_quality"])
    self.assertEqual("cli", first_plan["runtime"]["executor"]["model_source"])
    self.assertEqual("gpt-5.6-sol", first_plan["runtime"]["judge"]["model"])
    self.assertEqual("executor", first_plan["runtime"]["judge"]["model_source"])
    self.assertEqual(first_plan["runtime_fingerprint"], second_plan["runtime_fingerprint"])

  def test_validate_change_aggregates_runtime_and_budget_blockers_without_side_effects(self):
    baseline = self.root / "baseline-blockers"
    subprocess.run(["cp", "-a", str(self.skill), str(baseline)], check=True)

    completed = self.invoke(
      "validate-change", "--skill", str(self.skill), "--baseline", str(baseline),
      "--impact", "scoped", "--case", "write-result",
      "--approved-model-sessions", "0", "--progress",
    )

    plan = json.loads(completed.stdout)
    self.assertEqual(2, completed.returncode, completed.stderr)
    self.assertEqual([
      "executor-runtime-explicit-required",
      "insufficient-model-session-budget",
    ], [blocker["code"] for blocker in plan["execution_blockers"]])
    self.assertFalse((self.root / "artifacts").exists())
    self.assertIn("Preparing validate-change", completed.stderr)

  def test_codex_model_is_propagated_but_runtime_remains_exploratory(self):
    completed = self.invoke(
      "run", "--skill", str(self.skill), "--case", "write-result",
      "--source", "working-tree",
      env={"CODEX_MODEL": "environment-model"},
    )

    report = json.loads(completed.stdout)
    self.assertEqual(0, completed.returncode, completed.stderr)
    self.assertEqual("environment-model", report["model"])
    self.assertEqual("environment", report["runtime"]["executor"]["model_source"])
    self.assertEqual("exploratory", report["runtime"]["audit_quality"])

  def test_role_specific_runtime_is_passed_and_actual_sessions_are_aggregated(self):
    log = self.root / "runtime-argv.jsonl"
    self.fake.write_text(
      "#!/usr/bin/env python3\n"
      "import json, os, pathlib, sys\n"
      "with pathlib.Path(os.environ['FAKE_CODEX_LOG']).open('a') as stream: stream.write(json.dumps(sys.argv[1:]) + '\\n')\n"
      "schema = pathlib.Path(sys.argv[sys.argv.index('--output-schema') + 1])\n"
      "out = pathlib.Path(sys.argv[sys.argv.index('-o') + 1])\n"
      "cwd = pathlib.Path(sys.argv[sys.argv.index('-C') + 1])\n"
      "if 'judge' in schema.name: response = {'verdict': 'PASS', 'rationale': 'ok', 'evidence': []}\n"
      "else:\n"
      "  (cwd / 'result.txt').write_text('ok')\n"
      "  response = {'summary': 'done', 'classification': 'test', 'evidence': [], 'files_changed': ['result.txt']}\n"
      "out.write_text(json.dumps(response))\n",
      encoding="utf-8",
    )
    self.fake.chmod(0o755)
    manifest_path = self.skill / "evals" / "cases" / "write-result" / "case.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["judge"] = {"enabled": True, "criteria": ["The result exists."]}
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    completed = self.invoke(
      "run", "--skill", str(self.skill), "--case", "write-result",
      "--source", "working-tree",
      "--model", "gpt-5.6-sol", "--reasoning-effort", "medium",
      "--judge-model", "gpt-5.6-terra", "--judge-reasoning-effort", "high",
      env={"FAKE_CODEX_LOG": str(log)},
    )

    report = json.loads(completed.stdout)
    argv = [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()]
    self.assertEqual(0, completed.returncode, completed.stderr)
    self.assertEqual({"executor": 1, "judge": 1, "total": 2}, report["model_sessions"])
    self.assertEqual(["--model", "gpt-5.6-sol"], argv[0][1:3])
    self.assertIn('model_reasoning_effort="medium"', argv[0])
    self.assertEqual(["--model", "gpt-5.6-terra"], argv[1][1:3])
    self.assertIn('model_reasoning_effort="high"', argv[1])

  def test_plan_is_side_effect_free_and_reports_static_zero_session_gate(self):
    baseline = self.root / "baseline-plan"
    subprocess.run(["cp", "-a", str(self.skill), str(baseline)], check=True)
    artifacts = self.root / "plan-artifacts"

    completed = subprocess.run(
      [
        "python3",
        str(SCRIPT),
        "plan",
        "--skill",
        str(self.skill),
        "--baseline",
        str(baseline),
        "--impact",
        "static",
      ],
      text=True,
      capture_output=True,
      check=False,
    )

    plan = json.loads(completed.stdout)
    self.assertEqual(0, completed.returncode, completed.stderr)
    self.assertEqual("plan", plan["operation"])
    self.assertEqual("static", plan["impact"])
    self.assertEqual([], plan["selected_cases"])
    self.assertEqual(0, plan["sessions"]["total"])
    self.assertFalse(plan["approval_required"])
    self.assertFalse(artifacts.exists())

  def test_static_plan_does_not_require_an_evaluation_suite(self):
    skill = self.root / "docs-only-skill"
    skill.mkdir()
    (skill / "SKILL.md").write_text(
      "---\nname: docs-only-skill\ndescription: Test.\n---\n", encoding="utf-8"
    )
    baseline = self.root / "docs-only-baseline"
    subprocess.run(["cp", "-a", str(skill), str(baseline)], check=True)

    completed = subprocess.run(
      [
        "python3", str(SCRIPT), "plan", "--skill", str(skill),
        "--baseline", str(baseline), "--impact", "static",
      ],
      text=True, capture_output=True, check=False,
    )

    plan = json.loads(completed.stdout)
    self.assertEqual(0, completed.returncode, completed.stderr)
    self.assertEqual(0, plan["sessions"]["total"])
    self.assertEqual(["structural-validation"], plan["steps"])

  def test_plan_counts_exact_sessions_for_scoped_and_cross_cutting_impacts(self):
    self.add_case(
      self.skill,
      "semantic-judge",
      {
        "kind": "behavioral",
        "prompt_file": "prompt.md",
        "mechanical": {"expected_exit_code": 0},
        "judge": {"enabled": True, "criteria": ["The request is complete."]},
      },
    )
    baseline = self.root / "baseline-counts"
    subprocess.run(["cp", "-a", str(self.skill), str(baseline)], check=True)

    scoped = subprocess.run(
      [
        "python3", str(SCRIPT), "plan", "--skill", str(self.skill),
        "--baseline", str(baseline), "--impact", "scoped", "--case", "semantic-judge",
      ],
      text=True, capture_output=True, check=False,
    )
    cross_cutting = subprocess.run(
      [
        "python3", str(SCRIPT), "plan", "--skill", str(self.skill),
        "--baseline", str(baseline), "--impact", "cross-cutting", "--case", "semantic-judge",
      ],
      text=True, capture_output=True, check=False,
    )

    scoped_plan = json.loads(scoped.stdout)
    cross_plan = json.loads(cross_cutting.stdout)
    self.assertEqual(0, scoped.returncode, scoped.stderr)
    self.assertEqual({"executor": 4, "judge": 4, "total": 8}, {
      key: scoped_plan["sessions"][key] for key in ("executor", "judge", "total")
    })
    self.assertFalse(scoped_plan["approval_required"])
    self.assertEqual(["write-result"], cross_plan["regression_cases"])
    self.assertEqual(9, cross_plan["sessions"]["total"])
    self.assertTrue(cross_plan["approval_required"])

  def test_plan_proposes_the_current_runner_for_target_skill_validation(self):
    baseline = self.root / "baseline-command"
    subprocess.run(["cp", "-a", str(self.skill), str(baseline)], check=True)

    completed = subprocess.run(
      [
        "python3", str(SCRIPT), "plan", "--skill", str(self.skill),
        "--baseline", str(baseline), "--impact", "scoped", "--case", "write-result",
      ],
      text=True, capture_output=True, check=False,
    )

    plan = json.loads(completed.stdout)
    self.assertEqual(0, completed.returncode, completed.stderr)
    self.assertEqual(str(SCRIPT.resolve()), plan["commands"][0].split()[1])

  def test_deterministic_case_runs_commands_without_model_sessions(self):
    (self.skill / "marker.txt").write_text("good", encoding="utf-8")
    self.add_case(
      self.skill,
      "check-marker",
      {
        "kind": "deterministic",
        "mechanical": {
          "commands": [{
            "argv": [
              "python3", "-c",
              "import os; from pathlib import Path; assert (Path(os.environ['SKILL_EVAL_SKILL_DIR']) / 'marker.txt').read_text() == 'good'",
            ],
            "exit_code": 0,
          }]
        },
        "judge": {"enabled": False, "criteria": []},
      },
      prompt=None,
    )

    completed = self.invoke(
      "run", "--skill", str(self.skill), "--case", "check-marker", "--source", "working-tree"
    )

    report = json.loads(completed.stdout)
    result = report["results"][0]
    self.assertEqual(0, completed.returncode, completed.stderr)
    self.assertEqual("PASS", result["status"])
    self.assertFalse(result["executor"]["enabled"])
    self.assertFalse(result["judge"]["enabled"])
    self.assertEqual(0, result["model_sessions"]["total"])

  def test_deterministic_manifest_rejects_executor_or_enabled_judge(self):
    self.add_case(
      self.skill,
      "invalid-deterministic",
      {
        "kind": "deterministic",
        "prompt_file": "prompt.md",
        "mechanical": {"commands": [{"argv": ["python3", "-c", "pass"]}]},
        "judge": {"enabled": True, "criteria": []},
      },
    )
    baseline = self.root / "baseline-invalid"
    subprocess.run(["cp", "-a", str(self.skill), str(baseline)], check=True)

    completed = subprocess.run(
      [
        "python3", str(SCRIPT), "plan", "--skill", str(self.skill),
        "--baseline", str(baseline), "--impact", "deterministic",
      ],
      text=True, capture_output=True, check=False,
    )

    report = json.loads(completed.stdout)
    self.assertEqual(1, completed.returncode)
    self.assertEqual("ERROR", report["status"])
    self.assertIn("forbids executor configuration", report["results"][0]["error"])

  def test_validate_change_runs_deterministic_red_once_and_candidate_three_times(self):
    (self.skill / "marker.txt").write_text("good", encoding="utf-8")
    self.add_case(
      self.skill,
      "deterministic-red-green",
      {
        "kind": "deterministic",
        "mechanical": {
          "commands": [{
            "argv": [
              "python3", "-c",
              "import os; from pathlib import Path; assert (Path(os.environ['SKILL_EVAL_SKILL_DIR']) / 'marker.txt').read_text() == 'good'",
            ]
          }]
        },
        "judge": {"enabled": False, "criteria": []},
      },
      prompt=None,
    )
    baseline = self.root / "baseline-deterministic"
    subprocess.run(["cp", "-a", str(self.skill), str(baseline)], check=True)
    (baseline / "marker.txt").write_text("bad", encoding="utf-8")

    completed = self.invoke(
      "validate-change", "--skill", str(self.skill), "--baseline", str(baseline),
      "--impact", "deterministic", "--case", "deterministic-red-green",
    )

    report = json.loads(completed.stdout)
    self.assertEqual(0, completed.returncode, completed.stderr)
    self.assertEqual("PASS", report["status"])
    self.assertEqual(["baseline", "candidate", "candidate", "candidate"], [
      result["role"] for result in report["results"]
    ])
    self.assertEqual(0, report["plan"]["sessions"]["total"])

  def test_validate_change_allows_exactly_eight_semantic_sessions(self):
    (self.skill / "marker.txt").write_text("candidate", encoding="utf-8")
    manifest = json.loads(
      (self.skill / "evals" / "cases" / "write-result" / "case.json").read_text(encoding="utf-8")
    )
    manifest["judge"] = {
      "enabled": True,
      "criteria": ["The requested result exists."],
      "no_action_acceptable": False,
    }
    (self.skill / "evals" / "cases" / "write-result" / "case.json").write_text(
      json.dumps(manifest), encoding="utf-8"
    )
    baseline = self.root / "baseline-eight"
    subprocess.run(["cp", "-a", str(self.skill), str(baseline)], check=True)
    (baseline / "marker.txt").write_text("baseline", encoding="utf-8")
    self.fake.write_text(
      "#!/usr/bin/env python3\n"
      "import json, pathlib, sys\n"
      "schema = pathlib.Path(sys.argv[sys.argv.index('--output-schema') + 1])\n"
      "out = pathlib.Path(sys.argv[sys.argv.index('-o') + 1])\n"
      "cwd = pathlib.Path(sys.argv[sys.argv.index('-C') + 1])\n"
      "if 'judge' in schema.name:\n"
      "  response = {'verdict': 'PASS', 'rationale': 'observable', 'evidence': ['result']}\n"
      "else:\n"
      "  marker = next((cwd / '.agents/skills').glob('*/marker.txt'))\n"
      "  if marker.read_text() == 'candidate': (cwd / 'result.txt').write_text('ok')\n"
      "  response = {'summary': 'done', 'classification': 'test', 'evidence': [], 'files_changed': ['result.txt']}\n"
      "out.write_text(json.dumps(response))\n",
      encoding="utf-8",
    )
    self.fake.chmod(0o755)

    completed = self.invoke(
      "validate-change", "--skill", str(self.skill), "--baseline", str(baseline),
      "--impact", "scoped", "--case", "write-result",
      "--model", "gpt-5.6-sol", "--reasoning-effort", "medium",
    )

    report = json.loads(completed.stdout)
    self.assertEqual(0, completed.returncode, completed.stderr)
    self.assertEqual("PASS", report["status"])
    self.assertEqual(8, report["plan"]["sessions"]["total"])
    self.assertFalse(report["plan"]["approval_required"])
    self.assertEqual(7, report["model_sessions"]["total"])
    self.assertEqual(7, sum(result["model_sessions"]["total"] for result in report["results"]))

  def test_validate_change_refuses_unapproved_sessions_before_artifacts_or_models(self):
    self.add_case(
      self.skill,
      "semantic-judge",
      {
        "kind": "behavioral",
        "prompt_file": "prompt.md",
        "mechanical": {"expected_exit_code": 0},
        "judge": {"enabled": True, "criteria": ["The request is complete."]},
      },
    )
    baseline = self.root / "baseline-budget"
    subprocess.run(["cp", "-a", str(self.skill), str(baseline)], check=True)

    completed = self.invoke(
      "validate-change", "--skill", str(self.skill), "--baseline", str(baseline),
      "--impact", "cross-cutting", "--case", "semantic-judge",
      "--model", "gpt-5.6-sol", "--reasoning-effort", "medium",
    )

    plan = json.loads(completed.stdout)
    self.assertEqual(2, completed.returncode, completed.stderr)
    self.assertEqual("plan", plan["operation"])
    self.assertEqual(9, plan["sessions"]["total"])
    self.assertTrue(plan["approval_required"])
    self.assertFalse((self.root / "artifacts").exists())

  def test_validate_change_accepts_explicit_larger_session_budget(self):
    self.add_case(
      self.skill,
      "semantic-judge",
      {
        "kind": "behavioral",
        "prompt_file": "prompt.md",
        "mechanical": {"expected_exit_code": 0},
        "judge": {"enabled": True, "criteria": ["The request is complete."]},
      },
    )
    baseline = self.root / "baseline-approved"
    subprocess.run(["cp", "-a", str(self.skill), str(baseline)], check=True)

    completed = self.invoke(
      "validate-change", "--skill", str(self.skill), "--baseline", str(baseline),
      "--impact", "cross-cutting", "--case", "semantic-judge",
      "--approved-model-sessions", "9",
      "--model", "gpt-5.6-sol", "--reasoning-effort", "medium",
    )

    report = json.loads(completed.stdout)
    self.assertNotEqual(2, completed.returncode)
    self.assertEqual("validate-change", report["operation"])
    self.assertFalse(report["plan"]["approval_required"])

  def test_cross_cutting_regression_excludes_affected_cases(self):
    (self.skill / "marker.txt").write_text("good", encoding="utf-8")
    self.add_case(
      self.skill,
      "affected-deterministic",
      {
        "kind": "deterministic",
        "mechanical": {
          "commands": [{
            "argv": [
              "python3", "-c",
              "import os; from pathlib import Path; assert (Path(os.environ['SKILL_EVAL_SKILL_DIR']) / 'marker.txt').read_text() == 'good'",
            ]
          }]
        },
        "judge": {"enabled": False, "criteria": []},
      },
      prompt=None,
    )
    (self.skill / "evals" / "suite.json").write_text(
      json.dumps({"version": 1, "cases": ["affected-deterministic", "write-result"]}),
      encoding="utf-8",
    )
    baseline = self.root / "baseline-cross"
    subprocess.run(["cp", "-a", str(self.skill), str(baseline)], check=True)
    (baseline / "marker.txt").write_text("bad", encoding="utf-8")

    completed = self.invoke(
      "validate-change", "--skill", str(self.skill), "--baseline", str(baseline),
      "--impact", "cross-cutting", "--case", "affected-deterministic",
      "--model", "gpt-5.6-sol", "--reasoning-effort", "medium",
    )

    report = json.loads(completed.stdout)
    self.assertEqual(0, completed.returncode, completed.stderr)
    self.assertEqual(["write-result"], report["plan"]["regression_cases"])
    self.assertEqual(4, [result["case_id"] for result in report["results"]].count("affected-deterministic"))
    self.assertEqual(1, [result["case_id"] for result in report["results"]].count("write-result"))
    self.assertEqual("regression", report["results"][2]["role"])
    self.assertEqual(["candidate", "candidate"], [
      result["role"] for result in report["results"][-2:]
    ])

  def test_validate_change_reports_unstable_candidate_signatures(self):
    counter = self.root / "validation-counter"
    (self.skill / "marker.txt").write_text("good", encoding="utf-8")
    command = (
      "import os, pathlib, sys; "
      "skill=pathlib.Path(os.environ['SKILL_EVAL_SKILL_DIR']); "
      "sys.exit(1) if (skill/'marker.txt').read_text() != 'good' else None; "
      f"counter=pathlib.Path({str(counter)!r}); "
      "n=int(counter.read_text()) if counter.exists() else 0; "
      "counter.write_text(str(n+1)); "
      "pathlib.Path('even.txt' if n % 2 == 0 else 'odd.txt').write_text('ok')"
    )
    self.add_case(
      self.skill,
      "unstable-deterministic",
      {
        "kind": "deterministic",
        "mechanical": {"commands": [{"argv": ["python3", "-c", command]}]},
        "judge": {"enabled": False, "criteria": []},
      },
      prompt=None,
    )
    baseline = self.root / "baseline-unstable"
    subprocess.run(["cp", "-a", str(self.skill), str(baseline)], check=True)
    (baseline / "marker.txt").write_text("bad", encoding="utf-8")

    completed = self.invoke(
      "validate-change", "--skill", str(self.skill), "--baseline", str(baseline),
      "--impact", "deterministic", "--case", "unstable-deterministic",
    )

    report = json.loads(completed.stdout)
    self.assertEqual(1, completed.returncode)
    self.assertEqual("UNSTABLE", report["status"])
    self.assertEqual(4, len(report["results"]))

  def test_validate_change_stops_after_first_candidate_failure_without_retry(self):
    (self.skill / "marker.txt").write_text("bad", encoding="utf-8")
    self.add_case(
      self.skill,
      "always-failing",
      {
        "kind": "deterministic",
        "mechanical": {
          "commands": [{
            "argv": [
              "python3", "-c",
              "import os; from pathlib import Path; assert (Path(os.environ['SKILL_EVAL_SKILL_DIR']) / 'marker.txt').read_text() == 'good'",
            ]
          }]
        },
        "judge": {"enabled": False, "criteria": []},
      },
      prompt=None,
    )
    baseline = self.root / "baseline-failing"
    subprocess.run(["cp", "-a", str(self.skill), str(baseline)], check=True)

    completed = self.invoke(
      "validate-change", "--skill", str(self.skill), "--baseline", str(baseline),
      "--impact", "deterministic", "--case", "always-failing",
    )

    report = json.loads(completed.stdout)
    self.assertEqual(1, completed.returncode)
    self.assertEqual("FAIL", report["status"])
    self.assertEqual(["baseline", "candidate"], [result["role"] for result in report["results"]])

  def test_run_uses_isolated_workspace_and_passes_mechanical_checks(self):
    completed = self.invoke("run", "--skill", str(self.skill), "--case", "write-result", "--source", "working-tree")

    report = json.loads(completed.stdout)
    self.assertEqual(0, completed.returncode, completed.stderr)
    self.assertEqual("PASS", report["status"])
    self.assertEqual("configured-default", report["model"])
    self.assertEqual(["write-result"], [result["case_id"] for result in report["results"]])
    self.assertFalse((self.root / "result.txt").exists())
    self.assertIsNone(report["artifacts"])
    self.assertEqual("", completed.stderr)

  def test_progress_is_automatic_when_stderr_is_a_tty(self):
    runner = load_runner()
    stderr = TtyBuffer()
    stdout = tempfile.SpooledTemporaryFile(mode="w+")
    argv = self.command(
      "run", "--skill", str(self.skill), "--case", "write-result", "--source", "working-tree"
    )[2:]

    with mock.patch.object(runner.sys, "stderr", stderr), mock.patch.object(runner.sys, "stdout", stdout):
      exit_code = runner.main(argv)

    stdout.seek(0)
    report = json.load(stdout)
    self.assertEqual(0, exit_code)
    self.assertEqual("PASS", report["status"])
    self.assertIn("Preparing run", stderr.value)
    self.assertIn("Case write-result: running executor", stderr.value)
    self.assertIn("Final result: PASS", stderr.value)

  def test_progress_is_silent_when_stderr_is_a_pipe(self):
    completed = self.invoke(
      "run", "--skill", str(self.skill), "--case", "write-result", "--source", "working-tree"
    )

    json.loads(completed.stdout)
    self.assertEqual(0, completed.returncode, completed.stderr)
    self.assertEqual("", completed.stderr)

  def test_forced_progress_is_flushed_before_a_delayed_executor_finishes(self):
    process = subprocess.Popen(
      self.command(
        "run",
        "--skill",
        str(self.skill),
        "--case",
        "write-result",
        "--source",
        "working-tree",
        "--progress",
      ),
      text=True,
      stdout=subprocess.PIPE,
      stderr=subprocess.PIPE,
      env={**os.environ, "FAKE_CODEX_DELAY": "1"},
    )

    first_line = process.stderr.readline()
    still_running = process.poll() is None
    stdout, remaining_stderr = process.communicate(timeout=5)

    self.assertTrue(still_running)
    self.assertEqual("Preparing run\n", first_line)
    self.assertEqual(0, process.returncode, remaining_stderr)
    self.assertEqual("PASS", json.loads(stdout)["status"])

  def test_quiet_suppresses_progress_even_when_stderr_is_a_tty(self):
    runner = load_runner()
    stderr = TtyBuffer()
    stdout = tempfile.SpooledTemporaryFile(mode="w+")
    argv = self.command(
      "run",
      "--skill",
      str(self.skill),
      "--case",
      "write-result",
      "--source",
      "working-tree",
      "--quiet",
    )[2:]

    with mock.patch.object(runner.sys, "stderr", stderr), mock.patch.object(runner.sys, "stdout", stdout):
      exit_code = runner.main(argv)

    stdout.seek(0)
    self.assertEqual(0, exit_code)
    self.assertEqual("PASS", json.load(stdout)["status"])
    self.assertEqual("", stderr.value)

  def test_progress_and_quiet_are_mutually_exclusive(self):
    completed = self.invoke(
      "run",
      "--skill",
      str(self.skill),
      "--case",
      "write-result",
      "--source",
      "working-tree",
      "--progress",
      "--quiet",
    )

    self.assertEqual(2, completed.returncode)
    self.assertEqual("", completed.stdout)
    self.assertIn("not allowed with argument", completed.stderr)

  def test_progress_reports_phases_in_order(self):
    completed = self.invoke(
      "run",
      "--skill",
      str(self.skill),
      "--case",
      "write-result",
      "--source",
      "working-tree",
      "--progress",
      env={"FAKE_CODEX_STDERR": "executor-internal-output"},
    )

    expected = [
      "Preparing run",
      "Case write-result: preparing workspace",
      "Case write-result: running executor",
      "Case write-result: running mechanical checks",
      "Case write-result: PASS",
      "Final result: PASS",
    ]
    self.assertEqual(expected, completed.stderr.splitlines())
    report = json.loads(completed.stdout)
    self.assertEqual("PASS", report["status"])
    self.assertNotIn("executor-internal-output", completed.stderr)
    self.assertIn("executor-internal-output", report["results"][0]["executor"]["stderr"])

  def test_progress_does_not_announce_disabled_judge(self):
    manifest_path = self.skill / "evals" / "cases" / "write-result" / "case.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["judge"]["enabled"] = False
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    completed = self.invoke(
      "run",
      "--skill",
      str(self.skill),
      "--case",
      "write-result",
      "--source",
      "working-tree",
      "--progress",
    )

    self.assertEqual(0, completed.returncode, completed.stderr)
    self.assertNotIn("running judge", completed.stderr)

  def test_verify_change_and_stability_progress_include_context(self):
    baseline = self.root / "baseline-progress"
    subprocess.run(["cp", "-a", str(self.skill), str(baseline)], check=True)

    verified = self.invoke(
      "verify-change",
      "--skill",
      str(self.skill),
      "--case",
      "write-result",
      "--baseline",
      str(baseline),
      "--progress",
    )
    stable = self.invoke(
      "stability",
      "--skill",
      str(self.skill),
      "--case",
      "write-result",
      "--runs",
      "3",
      "--progress",
    )

    self.assertIn("Case write-result [baseline]: running executor", verified.stderr)
    self.assertIn("Case write-result [candidate]: running executor", verified.stderr)
    self.assertIn("Case write-result [repetition 1/3]: running executor", stable.stderr)
    self.assertIn("Case write-result [repetition 2/3]: running executor", stable.stderr)
    self.assertIn("Case write-result [repetition 3/3]: running executor", stable.stderr)
    json.loads(verified.stdout)
    self.assertEqual("PASS", json.loads(stable.stdout)["status"])

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

  def test_mechanical_failure_skips_judge_and_counts_only_executor(self):
    manifest_path = self.skill / "evals" / "cases" / "write-result" / "case.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["mechanical"]["required_paths"] = ["missing.txt"]
    manifest["judge"] = {"enabled": True, "criteria": ["The output is complete."]}
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    completed = self.invoke(
      "run", "--skill", str(self.skill), "--case", "write-result", "--source", "working-tree"
    )

    report = json.loads(completed.stdout)
    self.assertEqual(1, completed.returncode)
    self.assertEqual("FAIL", report["status"])
    self.assertEqual("SKIPPED", report["results"][0]["judge"]["verdict"])
    self.assertFalse(report["results"][0]["judge"]["executed"])
    self.assertEqual({"executor": 1, "judge": 0, "total": 1}, report["model_sessions"])

  def test_mechanical_check_detects_skill_self_modification(self):
    completed = self.invoke(
      "run", "--skill", str(self.skill), "--case", "write-result", "--source", "working-tree", env={"FAKE_CODEX_MODE": "mutate-skill"}
    )

    report = json.loads(completed.stdout)
    self.assertEqual(1, completed.returncode)
    self.assertEqual("FAIL", report["status"])
    checks = report["results"][0]["mechanical"]["checks"]
    self.assertIn("evaluated skill remained unchanged", [check["name"] for check in checks if not check["passed"]])

  def test_snapshot_ignores_python_cache_artifacts(self):
    runner = load_runner()
    (self.skill / "__pycache__").mkdir()
    (self.skill / "__pycache__" / "module.cpython-310.pyc").write_bytes(b"before")
    before = runner.snapshot(self.skill)

    (self.skill / "__pycache__" / "module.cpython-310.pyc").write_bytes(b"after")
    (self.skill / "nested.pyc").write_bytes(b"generated")

    self.assertEqual(before, runner.snapshot(self.skill))

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
