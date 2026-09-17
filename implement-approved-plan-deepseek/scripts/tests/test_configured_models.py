import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import test_workflow_state as legacy


EFFORTS = {
  "implementer": "low", "committer": "low", "validator": "off",
  "habit-curator": "off", "mutation-analyst": "off", "structural-reviewer": "low",
}


class ConfiguredModelsTest(unittest.TestCase):
  def cli(self, state, *args):
    return subprocess.run([sys.executable, str(legacy.SCRIPT), "--state", str(state), *args], capture_output=True, text=True)

  def selections(self):
    return {role: {"session_id": role + "-thread", "provider": "configured-provider", "model": "configured-model", "effort": effort} for role, effort in EFFORTS.items()}

  def legacy_state(self, root):
    helper = legacy.WorkflowStateCliTest()
    state = helper.initialize_v3(root)
    helper.register_specialists(state, specialists=legacy.V3_SPECIALISTS)
    return state

  def test_migration_preserves_execution_state_and_is_idempotent(self):
    with tempfile.TemporaryDirectory() as directory:
      state = self.legacy_state(Path(directory))
      before = json.loads(state.read_text())
      args = ("migrate-models", "--selections", json.dumps(self.selections()), "--reason", "Configured connection")
      result = self.cli(state, *args)
      self.assertEqual(0, result.returncode, result.stderr)
      after = json.loads(state.read_text())
      expected = copy.deepcopy(before)
      for key in ("schema_version", "sessions", "updated_at"):
        expected[key] = after[key]
      expected["model_changes"] = after["model_changes"]
      self.assertEqual(expected, after)
      self.assertEqual(4, after["schema_version"])
      self.assertEqual(self.selections(), after["sessions"])
      self.assertEqual(before["sessions"], after["model_changes"][0]["before"])
      self.assertEqual(0, self.cli(state, *args).returncode)
      self.assertEqual(after, json.loads(state.read_text()))

  def test_invalid_migration_does_not_rewrite_the_legacy_ledger(self):
    with tempfile.TemporaryDirectory() as directory:
      state = self.legacy_state(Path(directory))
      before = state.read_bytes()
      for field, value in (("session_id", "replacement"), ("provider", ""), ("effort", "invalid")):
        selections = self.selections()
        selections["validator"][field] = value
        result = self.cli(state, "migrate-models", "--selections", json.dumps(selections), "--reason", "Configured connection")
        self.assertNotEqual(0, result.returncode)
        self.assertEqual(before, state.read_bytes())

  def test_schema_four_retains_leases_and_requires_all_specialists(self):
    with tempfile.TemporaryDirectory() as directory:
      root = Path(directory)
      plan = root / "plan.md"
      plan.write_text("Approved plan\n")
      state = root / "state.json"
      result = self.cli(state, "init", "--slug", "demo", "--plan", str(plan), "--repo", str(root), "--branch", "demo", "--base", "main", "--base-sha", legacy.BASE_SHA, "--provider", "configured-provider")
      self.assertEqual(0, result.returncode, result.stderr)
      self.assertEqual(0, self.cli(state, "acquire", "--owner", "coordinator").returncode)
      self.assertNotEqual(0, self.cli(state, "transition", "--to", "implementing").returncode)
      for role, chat in self.selections().items():
        result = self.cli(state, "register-session", "--role", role, "--session-id", chat["session_id"], "--provider", chat["provider"], "--model", chat["model"], "--effort", chat["effort"])
        self.assertEqual(0, result.returncode, result.stderr)
      self.assertEqual(0, self.cli(state, "transition", "--to", "implementing").returncode)
      self.assertNotEqual(0, self.cli(state, "acquire", "--owner", "validator").returncode)
      self.assertNotEqual(0, self.cli(state, "transition", "--to", "delivery-ready").returncode)

  def test_model_updates_preserve_session_identity_and_record_changes(self):
    with tempfile.TemporaryDirectory() as directory:
      state = self.legacy_state(Path(directory))
      result = self.cli(state, "migrate-models", "--selections", json.dumps(self.selections()), "--reason", "Configured connection")
      self.assertEqual(0, result.returncode, result.stderr)
      args = ("register-session", "--role", "validator", "--session-id", "validator-thread", "--provider", "next-provider", "--model", "next-model", "--effort", "low")
      self.assertEqual(0, self.cli(state, *args).returncode)
      after = json.loads(state.read_text())
      self.assertEqual("next-provider", after["sessions"]["validator"]["provider"])
      self.assertEqual("validator", after["model_changes"][-1]["role"])
      self.assertNotEqual(0, self.cli(state, *args[:4], "replacement-thread", *args[5:]).returncode)

  def test_migrated_workflow_still_requires_current_mutation_evidence(self):
    with tempfile.TemporaryDirectory() as directory:
      state = legacy.WorkflowStateCliTest().prepare_v3_mutation_testing(Path(directory))
      result = self.cli(state, "migrate-models", "--selections", json.dumps(self.selections()), "--reason", "Configured connection")
      self.assertEqual(0, result.returncode, result.stderr)
      before = state.read_bytes()
      result = self.cli(state, "transition", "--to", "structural-review")
      self.assertNotEqual(0, result.returncode)
      self.assertEqual(before, state.read_bytes())


if __name__ == "__main__":
  unittest.main()
