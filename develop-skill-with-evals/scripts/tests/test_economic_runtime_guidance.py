import importlib.util
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest import mock

from jsonschema import Draft202012Validator


SCRIPT = Path(
  os.environ.get(
    "RUN_SKILL_EVALS_SCRIPT",
    Path(__file__).parents[1] / "run_skill_evals.py",
  )
)


def load_runner():
  spec = importlib.util.spec_from_file_location("economic_runtime_runner", SCRIPT)
  module = importlib.util.module_from_spec(spec)
  spec.loader.exec_module(module)
  return module


class EconomicRuntimeGuidanceTest(unittest.TestCase):
  def setUp(self):
    self.temp = tempfile.TemporaryDirectory()
    self.root = Path(self.temp.name)
    self.skill = self.root / "sample-skill"
    (self.skill / "evals" / "cases").mkdir(parents=True)
    (self.skill / "SKILL.md").write_text(
      "---\nname: sample-skill\ndescription: Test.\n---\n",
      encoding="utf-8",
    )
    (self.skill / "evals" / "suite.json").write_text(
      json.dumps({"version": 1, "cases": []}),
      encoding="utf-8",
    )

  def tearDown(self):
    self.temp.cleanup()

  def add_case(self, case_id, *, kind="behavioral", oracle=False, judge=False):
    case_dir = self.skill / "evals" / "cases" / case_id
    (case_dir / "fixture").mkdir(parents=True)
    if kind == "deterministic":
      manifest = {
        "id": case_id,
        "kind": "deterministic",
        "mechanical": {
          "commands": [{"argv": ["python3", "-c", "raise SystemExit(0)"]}]
        },
        "judge": {"enabled": False, "criteria": []},
      }
    else:
      manifest = {
        "id": case_id,
        "kind": kind,
        "prompt_file": "prompt.md",
        "mechanical": {"expected_exit_code": 0, "required_paths": ["result.txt"]},
        "judge": {
          "enabled": judge,
          "criteria": ["The result is correct."] if judge else [],
        },
      }
      (case_dir / "prompt.md").write_text("Create result.txt.", encoding="utf-8")
      if oracle:
        (case_dir / "oracle").mkdir()
        (case_dir / "oracle" / "check.py").write_text(
          "from pathlib import Path\nassert Path('result.txt').is_file()\n",
          encoding="utf-8",
        )
        manifest["oracle"] = {
          "commands": [
            {
              "argv": ["python3", "{oracle_dir}/check.py"],
              "exit_code": 0,
            }
          ]
        }
    (case_dir / "case.json").write_text(json.dumps(manifest), encoding="utf-8")
    suite_path = self.skill / "evals" / "suite.json"
    suite = json.loads(suite_path.read_text(encoding="utf-8"))
    suite["cases"].append(case_id)
    suite_path.write_text(json.dumps(suite), encoding="utf-8")

  def baseline(self):
    baseline = self.root / f"baseline-{len(list(self.root.glob('baseline-*')))}"
    shutil.copytree(self.skill, baseline)
    return baseline

  def plan(self, impact, cases=(), runtime=()):
    runner = load_runner()
    baseline = self.baseline()
    argv = [
      "plan",
      "--skill",
      str(self.skill),
      "--baseline",
      str(baseline),
      "--impact",
      impact,
    ]
    for case_id in cases:
      argv.extend(["--case", case_id])
    argv.extend(runtime)
    args = runner.parse_args(argv)
    return runner.build_eval_plan(
      self.skill,
      baseline,
      impact,
      list(cases),
      args,
    )

  def test_static_and_deterministic_plans_recommend_zero_sessions(self):
    static = self.plan("static")
    self.add_case("mechanical", kind="deterministic")
    deterministic = self.plan("deterministic", ("mechanical",))

    for plan in (static, deterministic):
      with self.subTest(impact=plan["impact"]):
        guidance = plan["economic_runtime"]
        self.assertEqual("zero-session", guidance["mode"])
        self.assertIsNone(guidance["executor"]["recommended_model"])
        self.assertIsNone(guidance["judge"]["recommended_model"])
        self.assertIsNone(guidance["executor"]["matches_explicit_runtime"])
        self.assertIsNone(guidance["judge"]["matches_explicit_runtime"])

  def test_scoped_complete_oracle_recommends_luna_and_reports_match_states(self):
    self.add_case("eligible", oracle=True)
    absent = self.plan("scoped", ("eligible",))
    matching = self.plan(
      "scoped",
      ("eligible",),
      ("--model", "gpt-5.6-luna", "--reasoning-effort", "medium"),
    )
    mismatch = self.plan(
      "scoped",
      ("eligible",),
      ("--model", "gpt-5.6-sol", "--reasoning-effort", "medium"),
    )

    self.assertEqual("scoped-complete-oracle", absent["economic_runtime"]["mode"])
    executor = absent["economic_runtime"]["executor"]
    self.assertEqual("gpt-5.6-luna", executor["recommended_model"])
    self.assertEqual("medium", executor["recommended_reasoning_effort"])
    self.assertIsNone(executor["matches_explicit_runtime"])
    self.assertTrue(
      matching["economic_runtime"]["executor"]["matches_explicit_runtime"]
    )
    self.assertFalse(
      mismatch["economic_runtime"]["executor"]["matches_explicit_runtime"]
    )

  def test_explicit_sol_is_preserved_and_mismatch_is_only_a_warning(self):
    self.add_case("eligible", oracle=True)
    plan = self.plan(
      "scoped",
      ("eligible",),
      ("--model", "gpt-5.6-sol", "--reasoning-effort", "medium"),
    )

    self.assertEqual("gpt-5.6-sol", plan["runtime"]["executor"]["model"])
    self.assertIn("--model gpt-5.6-sol", plan["commands"][0])
    self.assertFalse(
      plan["economic_runtime"]["executor"]["matches_explicit_runtime"]
    )
    self.assertTrue(
      any("economic runtime" in warning.lower() for warning in plan["warnings"])
    )
    self.assertEqual([], plan["execution_blockers"])

  def test_manual_selection_covers_incomplete_oracle_judge_and_cross_cutting(self):
    self.add_case("no-oracle")
    no_oracle = self.plan("scoped", ("no-oracle",))

    self.add_case("judged", oracle=True, judge=True)
    judged = self.plan("scoped", ("judged",))
    cross_cutting = self.plan("cross-cutting", ("no-oracle",))

    for plan in (no_oracle, judged, cross_cutting):
      with self.subTest(selected=plan["selected_cases"], impact=plan["impact"]):
        self.assertEqual("manual-selection", plan["economic_runtime"]["mode"])
        self.assertIsNone(
          plan["economic_runtime"]["executor"]["recommended_model"]
        )

    judge = judged["economic_runtime"]["judge"]
    self.assertEqual("gpt-5.6-terra", judge["recommended_model"])
    self.assertEqual("medium", judge["recommended_reasoning_effort"])
    self.assertIsNone(
      no_oracle["economic_runtime"]["judge"]["recommended_model"]
    )

  def test_judge_match_requires_complete_explicit_judge_runtime(self):
    self.add_case("judged", oracle=True, judge=True)
    incomplete = self.plan(
      "scoped",
      ("judged",),
      ("--judge-model", "gpt-5.6-terra"),
    )
    matching = self.plan(
      "scoped",
      ("judged",),
      (
        "--model", "gpt-5.6-sol",
        "--reasoning-effort", "medium",
        "--judge-model", "gpt-5.6-terra",
        "--judge-reasoning-effort", "medium",
      ),
    )
    inherited_mismatch = self.plan(
      "scoped",
      ("judged",),
      (
        "--model", "gpt-5.6-sol",
        "--reasoning-effort", "medium",
      ),
    )

    self.assertIsNone(
      incomplete["economic_runtime"]["judge"]["matches_explicit_runtime"]
    )
    self.assertTrue(
      matching["economic_runtime"]["judge"]["matches_explicit_runtime"]
    )
    self.assertFalse(
      inherited_mismatch["economic_runtime"]["judge"]["matches_explicit_runtime"]
    )

  def test_public_schema_requires_and_validates_economic_runtime(self):
    self.add_case("eligible", oracle=True)
    plan = self.plan("scoped", ("eligible",))
    schema = json.loads(
      (Path(__file__).parents[2] / "references" / "eval-plan.schema.json").read_text(
        encoding="utf-8"
      )
    )

    Draft202012Validator(schema).validate(plan)
    without_guidance = dict(plan)
    without_guidance.pop("economic_runtime")
    with self.assertRaises(Exception):
      Draft202012Validator(schema).validate(without_guidance)

  def test_evaluation_fingerprint_binds_economic_guidance(self):
    self.add_case("eligible", oracle=True)
    runner = load_runner()
    baseline = self.baseline()
    args = runner.parse_args([
      "plan",
      "--skill", str(self.skill),
      "--baseline", str(baseline),
      "--impact", "scoped",
      "--case", "eligible",
    ])
    original = runner.build_eval_plan(
      self.skill, baseline, "scoped", ["eligible"], args
    )
    original_builder = runner.economic_runtime_guidance

    def changed_guidance(*values, **keywords):
      guidance = original_builder(*values, **keywords)
      return {**guidance, "reasons": guidance["reasons"] + ["Policy text changed."]}

    with mock.patch.object(
      runner,
      "economic_runtime_guidance",
      side_effect=changed_guidance,
    ):
      changed = runner.build_eval_plan(
        self.skill, baseline, "scoped", ["eligible"], args
      )

    self.assertEqual(
      original["runtime_fingerprint"],
      changed["runtime_fingerprint"],
    )
    self.assertNotEqual(
      original["evaluation_fingerprint"],
      changed["evaluation_fingerprint"],
    )

  def test_snapshot_stability_contract_includes_economic_runtime(self):
    self.add_case("eligible", oracle=True)
    plan = self.plan("scoped", ("eligible",))
    snapshot_plan = json.loads(json.dumps(plan))
    snapshot_plan["economic_runtime"]["reasons"].append("Changed after planning.")
    runner = load_runner()

    with self.assertRaisesRegex(
      ValueError,
      "Evaluation inputs changed after cost planning",
    ):
      runner.validate_snapshot_plan_stability(plan, snapshot_plan)


if __name__ == "__main__":
  unittest.main()
