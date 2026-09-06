import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest


SCRIPT = Path(__file__).parents[1] / "workflow_state.py"
V2_SPECIALISTS = {
  "implementer": ("gpt-5.6-sol", "xhigh"),
  "committer": ("gpt-5.6-terra", "xhigh"),
  "validator": ("gpt-5.6-luna", "xhigh"),
  "habit-curator": ("gpt-5.6-luna", "xhigh"),
  "structural-reviewer": ("gpt-5.6-sol", "xhigh"),
}
V3_SPECIALISTS = {
  **V2_SPECIALISTS,
  "mutation-analyst": ("gpt-5.6-luna", "xhigh"),
}
BASE_SHA = "a" * 40


class WorkflowStateCliTest(unittest.TestCase):
  def run_cli(self, state, *args):
    return subprocess.run(
      [sys.executable, str(SCRIPT), "--state", str(state), *args],
      capture_output=True,
      text=True,
      check=False,
    )

  def initialize_v2(self, root, slug="demo"):
    plan = root / f"{slug}.md"
    state = root / f"{slug}.workflow.json"
    plan.write_text("# Approved plan\n", encoding="utf-8")
    timestamp = "2026-09-06T00:00:00+00:00"
    ledger = {
      "schema_version": 2,
      "slug": slug,
      "plan_path": str(plan.resolve()),
      "repository": str(root.resolve()),
      "branch": f"codex/{slug}",
      "base": "main",
      "phase": "initialized",
      "chats": {},
      "commits": [],
      "gates": {},
      "habit": None,
      "habit_observations": [],
      "pull_request": None,
      "ci": None,
      "checkout_lease": None,
      "history": [{"at": timestamp, "from": None, "to": "initialized"}],
      "created_at": timestamp,
      "updated_at": timestamp,
    }
    state.write_text(
      json.dumps(ledger, indent=2, sort_keys=True) + "\n",
      encoding="utf-8",
    )
    return state

  def initialize_v3(self, root, slug="demo"):
    plan = root / f"{slug}.md"
    state = root / f"{slug}.workflow.json"
    plan.write_text("# Approved plan\n", encoding="utf-8")
    result = self.run_cli(
      state,
      "init",
      "--slug",
      slug,
      "--plan",
      str(plan),
      "--repo",
      str(root),
      "--branch",
      f"codex/{slug}",
      "--base",
      "main",
      "--base-sha",
      BASE_SHA,
    )
    self.assertEqual(0, result.returncode, result.stderr)
    return state

  def register_specialists(
    self,
    state,
    *,
    specialists=V2_SPECIALISTS,
    omitted_role=None,
    empty_role=None,
  ):
    for role, (model, effort) in specialists.items():
      if role == omitted_role:
        continue
      result = self.run_cli(
        state,
        "register-chat",
        "--role",
        role,
        "--thread-id",
        "" if role == empty_role else f"{role}-thread",
        "--model",
        model,
        "--effort",
        effort,
      )
      self.assertEqual(0, result.returncode, result.stderr)

  def initialize_for_implementation(self, root, slug="demo"):
    state = self.initialize_v2(root, slug)
    self.register_specialists(state)
    return state

  def initialize_v3_for_implementation(self, root, slug="demo"):
    state = self.initialize_v3(root, slug)
    self.register_specialists(state, specialists=V3_SPECIALISTS)
    return state

  def initialize_legacy(self, root, slug="demo"):
    state = self.initialize_v2(root, slug)
    ledger = json.loads(state.read_text(encoding="utf-8"))
    ledger["schema_version"] = 1
    state.write_text(
      json.dumps(ledger, indent=2, sort_keys=True) + "\n",
      encoding="utf-8",
    )
    return state

  def prepare_v2_habit_check(self, root):
    state = self.initialize_for_implementation(root)
    for phase in ("implementing", "implemented", "habit-checking"):
      result = self.run_cli(state, "transition", "--to", phase)
      self.assertEqual(0, result.returncode, result.stderr)
    acquired = self.run_cli(state, "acquire", "--owner", "habit-curator")
    self.assertEqual(0, acquired.returncode, acquired.stderr)
    return state

  def prepare_v3_initial_validation(self, root):
    state = self.initialize_v3_for_implementation(root)
    for phase in ("implementing", "implemented", "habit-checking"):
      result = self.run_cli(state, "transition", "--to", phase)
      self.assertEqual(0, result.returncode, result.stderr)
    acquired = self.run_cli(state, "acquire", "--owner", "habit-curator")
    self.assertEqual(0, acquired.returncode, acquired.stderr)
    habit = self.run_cli(
      state,
      "record-habit",
      "--status",
      "clean",
      "--details",
      "quick check has zero raw findings",
    )
    self.assertEqual(0, habit.returncode, habit.stderr)
    released = self.run_cli(state, "release", "--owner", "habit-curator")
    self.assertEqual(0, released.returncode, released.stderr)
    committing = self.run_cli(state, "transition", "--to", "checkpoint-committing")
    self.assertEqual(0, committing.returncode, committing.stderr)
    acquired = self.run_cli(state, "acquire", "--owner", "committer")
    self.assertEqual(0, acquired.returncode, acquired.stderr)
    committed = self.run_cli(
      state,
      "record-commit",
      "--sha",
      "b" * 40,
      "--kind",
      "implementation",
      "--subject",
      "feat(demo): implement behavior",
    )
    self.assertEqual(0, committed.returncode, committed.stderr)
    released = self.run_cli(state, "release", "--owner", "committer")
    self.assertEqual(0, released.returncode, released.stderr)
    validating = self.run_cli(state, "transition", "--to", "initial-validating")
    self.assertEqual(0, validating.returncode, validating.stderr)
    return state

  def prepare_v3_mutation_testing(self, root):
    state = self.prepare_v3_initial_validation(root)
    acquired = self.run_cli(state, "acquire", "--owner", "validator")
    self.assertEqual(0, acquired.returncode, acquired.stderr)
    for name in ("initial-verify", "initial-sonar"):
      gate = self.run_cli(
        state,
        "record-gate",
        "--name",
        name,
        "--status",
        "passed",
        "--details",
        f"{name} passed",
      )
      self.assertEqual(0, gate.returncode, gate.stderr)
    released = self.run_cli(state, "release", "--owner", "validator")
    self.assertEqual(0, released.returncode, released.stderr)
    mutation = self.run_cli(state, "transition", "--to", "mutation-testing")
    self.assertEqual(0, mutation.returncode, mutation.stderr)
    return state

  def write_mutation_artifacts(self, root, classifications, prefix="mutation"):
    artifacts = root / ".agent" / "tmp"
    artifacts.mkdir(parents=True, exist_ok=True)
    log = artifacts / f"{prefix}.log"
    log.write_text("complete mutation runner output\n", encoding="utf-8")
    report = artifacts / f"{prefix}-pit-report"
    report.mkdir()
    classifications_path = artifacts / f"{prefix}-classifications.json"
    classifications_path.write_text(
      json.dumps(classifications, indent=2, sort_keys=True) + "\n",
      encoding="utf-8",
    )
    return log, report, classifications_path

  def prepare_v3_mutation_rechecking(self, root):
    state = self.prepare_v3_mutation_testing(root)
    log, report, classifications = self.write_mutation_artifacts(root, [])
    acquired = self.run_cli(state, "acquire", "--owner", "mutation-analyst")
    self.assertEqual(0, acquired.returncode, acquired.stderr)
    mutation = self.run_cli(
      state,
      "record-mutation",
      "--runner",
      "pit",
      "--result",
      "passed",
      "--analyzed-sha",
      "b" * 40,
      "--fingerprint",
      "c" * 64,
      "--target-class",
      "com.example.OrderService*",
      "--generated",
      "2",
      "--killed",
      "2",
      "--classification-file",
      str(classifications),
      "--log",
      str(log),
      "--report",
      str(report),
      "--details",
      "PIT completed with all mutants killed",
    )
    self.assertEqual(0, mutation.returncode, mutation.stderr)
    released = self.run_cli(state, "release", "--owner", "mutation-analyst")
    self.assertEqual(0, released.returncode, released.stderr)
    reviewed = self.run_cli(state, "transition", "--to", "structural-review")
    self.assertEqual(0, reviewed.returncode, reviewed.stderr)
    rechecking = self.run_cli(state, "transition", "--to", "habit-rechecking")
    self.assertEqual(0, rechecking.returncode, rechecking.stderr)
    acquired = self.run_cli(state, "acquire", "--owner", "habit-curator")
    self.assertEqual(0, acquired.returncode, acquired.stderr)
    habit = self.run_cli(
      state,
      "record-habit",
      "--status",
      "clean",
      "--details",
      "post-review check has zero raw findings",
    )
    self.assertEqual(0, habit.returncode, habit.stderr)
    released = self.run_cli(state, "release", "--owner", "habit-curator")
    self.assertEqual(0, released.returncode, released.stderr)
    validating = self.run_cli(state, "transition", "--to", "final-validating")
    self.assertEqual(0, validating.returncode, validating.stderr)
    acquired = self.run_cli(state, "acquire", "--owner", "validator")
    self.assertEqual(0, acquired.returncode, acquired.stderr)
    for name in ("final-verify", "final-sonar"):
      gate = self.run_cli(
        state,
        "record-gate",
        "--name",
        name,
        "--status",
        "passed",
        "--details",
        f"{name} passed",
      )
      self.assertEqual(0, gate.returncode, gate.stderr)
    released = self.run_cli(state, "release", "--owner", "validator")
    self.assertEqual(0, released.returncode, released.stderr)
    mutation_recheck = self.run_cli(
      state,
      "transition",
      "--to",
      "mutation-rechecking",
    )
    self.assertEqual(0, mutation_recheck.returncode, mutation_recheck.stderr)
    return state

  def prepare_v2_checkpoint_commit(self, root):
    state = self.prepare_v2_habit_check(root)
    habit = self.run_cli(
      state,
      "record-habit",
      "--status",
      "clean",
      "--details",
      "quick check has zero raw findings",
    )
    self.assertEqual(0, habit.returncode, habit.stderr)
    released = self.run_cli(state, "release", "--owner", "habit-curator")
    self.assertEqual(0, released.returncode, released.stderr)
    transitioned = self.run_cli(
      state,
      "transition",
      "--to",
      "checkpoint-committing",
    )
    self.assertEqual(0, transitioned.returncode, transitioned.stderr)
    return state

  def advance_v2_checkpoint_to_habit_recheck(self, state):
    acquired = self.run_cli(state, "acquire", "--owner", "committer")
    self.assertEqual(0, acquired.returncode, acquired.stderr)
    committed = self.run_cli(
      state,
      "record-commit",
      "--sha",
      "observation123",
      "--kind",
      "implementation",
      "--subject",
      "feat(demo): implement behavior",
    )
    self.assertEqual(0, committed.returncode, committed.stderr)
    released = self.run_cli(state, "release", "--owner", "committer")
    self.assertEqual(0, released.returncode, released.stderr)
    validating = self.run_cli(state, "transition", "--to", "initial-validating")
    self.assertEqual(0, validating.returncode, validating.stderr)
    acquired = self.run_cli(state, "acquire", "--owner", "validator")
    self.assertEqual(0, acquired.returncode, acquired.stderr)
    for name in ("initial-verify", "initial-sonar"):
      gate = self.run_cli(
        state,
        "record-gate",
        "--name",
        name,
        "--status",
        "passed",
        "--details",
        f"{name} passed",
      )
      self.assertEqual(0, gate.returncode, gate.stderr)
    released = self.run_cli(state, "release", "--owner", "validator")
    self.assertEqual(0, released.returncode, released.stderr)
    reviewing = self.run_cli(state, "transition", "--to", "structural-review")
    self.assertEqual(0, reviewing.returncode, reviewing.stderr)
    rechecking = self.run_cli(state, "transition", "--to", "habit-rechecking")
    self.assertEqual(0, rechecking.returncode, rechecking.stderr)

  def prepare_v2_initial_validation(self, root):
    state = self.prepare_v2_checkpoint_commit(root)
    acquired = self.run_cli(state, "acquire", "--owner", "committer")
    self.assertEqual(0, acquired.returncode, acquired.stderr)
    committed = self.run_cli(
      state,
      "record-commit",
      "--sha",
      "abc1234",
      "--kind",
      "implementation",
      "--subject",
      "feat(demo): implement behavior",
    )
    self.assertEqual(0, committed.returncode, committed.stderr)
    released = self.run_cli(state, "release", "--owner", "committer")
    self.assertEqual(0, released.returncode, released.stderr)
    transitioned = self.run_cli(
      state,
      "transition",
      "--to",
      "initial-validating",
    )
    self.assertEqual(0, transitioned.returncode, transitioned.stderr)
    return state

  def prepare_v2_structural_review(self, root):
    state = self.prepare_v2_initial_validation(root)
    acquired = self.run_cli(state, "acquire", "--owner", "validator")
    self.assertEqual(0, acquired.returncode, acquired.stderr)
    for name in ("initial-verify", "initial-sonar"):
      gate = self.run_cli(
        state,
        "record-gate",
        "--name",
        name,
        "--status",
        "passed",
        "--details",
        f"{name} passed",
      )
      self.assertEqual(0, gate.returncode, gate.stderr)
    released = self.run_cli(state, "release", "--owner", "validator")
    self.assertEqual(0, released.returncode, released.stderr)
    transitioned = self.run_cli(state, "transition", "--to", "structural-review")
    self.assertEqual(0, transitioned.returncode, transitioned.stderr)
    return state

  def prepare_v2_habit_recheck(self, root):
    state = self.prepare_v2_structural_review(root)
    transitioned = self.run_cli(state, "transition", "--to", "habit-rechecking")
    self.assertEqual(0, transitioned.returncode, transitioned.stderr)
    acquired = self.run_cli(state, "acquire", "--owner", "habit-curator")
    self.assertEqual(0, acquired.returncode, acquired.stderr)
    habit = self.run_cli(
      state,
      "record-habit",
      "--status",
      "clean",
      "--details",
      "post-review check has zero raw findings",
    )
    self.assertEqual(0, habit.returncode, habit.stderr)
    released = self.run_cli(state, "release", "--owner", "habit-curator")
    self.assertEqual(0, released.returncode, released.stderr)
    return state

  def prepare_v2_final_validation(self, root):
    state = self.prepare_v2_habit_recheck(root)
    transitioned = self.run_cli(state, "transition", "--to", "final-validating")
    self.assertEqual(0, transitioned.returncode, transitioned.stderr)
    return state

  def prepare_v2_delivery(self, root):
    state = self.prepare_v2_final_validation(root)
    acquired = self.run_cli(state, "acquire", "--owner", "validator")
    self.assertEqual(0, acquired.returncode, acquired.stderr)
    for name in ("final-verify", "final-sonar"):
      gate = self.run_cli(
        state,
        "record-gate",
        "--name",
        name,
        "--status",
        "passed",
        "--details",
        f"{name} passed",
      )
      self.assertEqual(0, gate.returncode, gate.stderr)
    released = self.run_cli(state, "release", "--owner", "validator")
    self.assertEqual(0, released.returncode, released.stderr)
    transitioned = self.run_cli(state, "transition", "--to", "delivery-ready")
    self.assertEqual(0, transitioned.returncode, transitioned.stderr)
    return state

  def prepare_v2_pull_request(self, root):
    state = self.prepare_v2_delivery(root)
    acquired = self.run_cli(state, "acquire", "--owner", "coordinator")
    self.assertEqual(0, acquired.returncode, acquired.stderr)
    pull_request = self.run_cli(
      state,
      "record-pr",
      "--repo",
      "owner/demo",
      "--number",
      "12",
      "--url",
      "https://example.test/pull/12",
      "--status",
      "OPEN",
    )
    self.assertEqual(0, pull_request.returncode, pull_request.stderr)
    transitioned = self.run_cli(state, "transition", "--to", "pr-open")
    self.assertEqual(0, transitioned.returncode, transitioned.stderr)
    released = self.run_cli(state, "release", "--owner", "coordinator")
    self.assertEqual(0, released.returncode, released.stderr)
    return state

  def prepare_pull_request_prerequisites(
    self,
    root,
    *,
    record_habit=True,
    record_baseline=True,
  ):
    state = self.initialize_legacy(root)
    for phase in ("implementing", "implemented"):
      result = self.run_cli(state, "transition", "--to", phase)
      self.assertEqual(0, result.returncode, result.stderr)
    self.assertEqual(0, self.run_cli(state, "acquire", "--owner", "committer").returncode)
    commit = self.run_cli(
      state,
      "record-commit",
      "--sha",
      "abc1234",
      "--kind",
      "implementation",
      "--subject",
      "feat(demo): implement behavior",
    )
    self.assertEqual(0, commit.returncode, commit.stderr)
    self.assertEqual(0, self.run_cli(state, "release", "--owner", "committer").returncode)
    for phase in ("committed", "initial-validating"):
      result = self.run_cli(state, "transition", "--to", phase)
      self.assertEqual(0, result.returncode, result.stderr)
    self.assertEqual(0, self.run_cli(state, "acquire", "--owner", "validator").returncode)
    for name in ("initial", "public-checkpoint"):
      gate = self.run_cli(
        state,
        "record-gate",
        "--name",
        name,
        "--status",
        "passed",
        "--details",
        f"{name} passed",
      )
      self.assertEqual(0, gate.returncode, gate.stderr)
    self.assertEqual(0, self.run_cli(state, "release", "--owner", "validator").returncode)
    for phase in ("coordinator-review", "habit-curation"):
      result = self.run_cli(state, "transition", "--to", phase)
      self.assertEqual(0, result.returncode, result.stderr)
    if record_habit:
      self.assertEqual(
        0,
        self.run_cli(state, "acquire", "--owner", "habit-curator").returncode,
      )
      habit = self.run_cli(
        state,
        "record-habit",
        "--status",
        "not-applicable",
        "--details",
        "habit unavailable",
      )
      self.assertEqual(0, habit.returncode, habit.stderr)
      self.assertEqual(
        0,
        self.run_cli(state, "release", "--owner", "habit-curator").returncode,
      )
    for phase in ("structural-review", "final-validating"):
      result = self.run_cli(state, "transition", "--to", phase)
      self.assertEqual(0, result.returncode, result.stderr)
    self.assertEqual(0, self.run_cli(state, "acquire", "--owner", "validator").returncode)
    final_gate = self.run_cli(
      state,
      "record-gate",
      "--name",
      "final",
      "--status",
      "passed",
      "--details",
      "final gate passed",
    )
    self.assertEqual(0, final_gate.returncode, final_gate.stderr)
    self.assertEqual(0, self.run_cli(state, "release", "--owner", "validator").returncode)
    self.assertEqual(0, self.run_cli(state, "transition", "--to", "habit-frozen").returncode)
    if record_baseline:
      self.assertEqual(
        0,
        self.run_cli(state, "acquire", "--owner", "committer").returncode,
      )
      baseline = self.run_cli(
        state,
        "record-commit",
        "--sha",
        "def5678",
        "--kind",
        "baseline",
        "--subject",
        "chore(demo): record baseline",
      )
      self.assertEqual(0, baseline.returncode, baseline.stderr)
      self.assertEqual(
        0,
        self.run_cli(state, "release", "--owner", "committer").returncode,
      )
    self.assertEqual(0, self.run_cli(state, "transition", "--to", "baseline-committed").returncode)
    self.assertEqual(0, self.run_cli(state, "acquire", "--owner", "coordinator").returncode)
    return state

  def prepare_pull_request(self, root):
    state = self.prepare_pull_request_prerequisites(root)
    arguments = (
      "record-pr",
      "--repo",
      "owner/demo",
      "--number",
      "12",
      "--url",
      "https://example.test/pull/12",
      "--status",
      "OPEN",
    )
    pull_request = self.run_cli(state, *arguments)
    self.assertEqual(0, pull_request.returncode, pull_request.stderr)
    before_repeat = state.read_text(encoding="utf-8")
    repeated = self.run_cli(state, *arguments)
    self.assertEqual(0, repeated.returncode, repeated.stderr)
    self.assertEqual(before_repeat, state.read_text(encoding="utf-8"))
    self.assertEqual(0, self.run_cli(state, "transition", "--to", "pr-open").returncode)
    self.assertEqual(0, self.run_cli(state, "release", "--owner", "coordinator").returncode)
    return state

  def test_init_creates_a_complete_ledger(self):
    with tempfile.TemporaryDirectory() as directory:
      root = Path(directory)
      plan = root / "demo.md"
      state = root / "demo.workflow.json"
      plan.write_text("# Approved plan\n", encoding="utf-8")

      result = self.run_cli(
        state,
        "init",
        "--slug",
        "demo",
        "--plan",
        str(plan),
        "--repo",
        str(root),
        "--branch",
        "codex/demo",
        "--base",
        "main",
        "--base-sha",
        BASE_SHA,
      )

      self.assertEqual(0, result.returncode, result.stderr)
      ledger = json.loads(state.read_text(encoding="utf-8"))
      self.assertEqual(3, ledger["schema_version"])
      self.assertEqual("demo", ledger["slug"])
      self.assertEqual(str(plan.resolve()), ledger["plan_path"])
      self.assertEqual(str(root.resolve()), ledger["repository"])
      self.assertEqual("codex/demo", ledger["branch"])
      self.assertEqual("main", ledger["base"])
      self.assertEqual(BASE_SHA, ledger["base_sha"])
      self.assertEqual("initialized", ledger["phase"])
      self.assertEqual({}, ledger["chats"])
      self.assertEqual([], ledger["commits"])
      self.assertEqual({}, ledger["gates"])
      self.assertIsNone(ledger["habit"])
      self.assertEqual([], ledger["habit_observations"])
      self.assertEqual([], ledger["mutation_attempts"])
      self.assertIsNone(ledger["pull_request"])
      self.assertIsNone(ledger["ci"])
      self.assertIsNone(ledger["checkout_lease"])
      self.assertEqual("initialized", ledger["history"][0]["to"])

  def test_init_is_idempotent_for_the_same_plan(self):
    with tempfile.TemporaryDirectory() as directory:
      root = Path(directory)
      plan = root / "demo.md"
      state = root / "demo.workflow.json"
      plan.write_text("# Approved plan\n", encoding="utf-8")
      arguments = (
        "init",
        "--slug",
        "demo",
        "--plan",
        str(plan),
        "--repo",
        str(root),
        "--branch",
        "codex/demo",
        "--base",
        "main",
        "--base-sha",
        BASE_SHA,
      )
      first = self.run_cli(state, *arguments)
      before = state.read_text(encoding="utf-8")

      second = self.run_cli(state, *arguments)

      self.assertEqual(0, first.returncode, first.stderr)
      self.assertEqual(0, second.returncode, second.stderr)
      self.assertEqual(before, state.read_text(encoding="utf-8"))

  def test_show_rejects_a_corrupt_ledger_without_changing_it(self):
    with tempfile.TemporaryDirectory() as directory:
      state = Path(directory) / "demo.workflow.json"
      corrupt_content = "{not-json\n"
      state.write_text(corrupt_content, encoding="utf-8")

      result = self.run_cli(state, "show")

      self.assertEqual(2, result.returncode)
      self.assertIn("corrupt ledger", result.stderr.lower())
      self.assertEqual(corrupt_content, state.read_text(encoding="utf-8"))

  def test_show_reads_a_legacy_v1_ledger_without_rewriting_it(self):
    with tempfile.TemporaryDirectory() as directory:
      state = self.initialize_v2(Path(directory))
      self.register_specialists(state)
      ledger = json.loads(state.read_text(encoding="utf-8"))
      ledger["schema_version"] = 1
      ledger["chats"]["habit-curator"]["model"] = "gpt-5.6-sol"
      legacy_content = json.dumps(ledger, indent=2, sort_keys=True) + "\n"
      state.write_text(legacy_content, encoding="utf-8")

      result = self.run_cli(state, "show")

      self.assertEqual(0, result.returncode, result.stderr)
      self.assertEqual(1, json.loads(result.stdout)["schema_version"])
      self.assertEqual(legacy_content, state.read_text(encoding="utf-8"))

  def test_show_reads_an_existing_v2_ledger_without_the_observation_field(self):
    with tempfile.TemporaryDirectory() as directory:
      state = self.initialize_v2(Path(directory))
      ledger = json.loads(state.read_text(encoding="utf-8"))
      del ledger["habit_observations"]
      existing_content = json.dumps(ledger, indent=2, sort_keys=True) + "\n"
      state.write_text(existing_content, encoding="utf-8")

      result = self.run_cli(state, "show")

      self.assertEqual(0, result.returncode, result.stderr)
      self.assertNotIn("habit_observations", json.loads(result.stdout))
      self.assertEqual(existing_content, state.read_text(encoding="utf-8"))

  def test_register_chat_records_the_required_specialist_identity(self):
    with tempfile.TemporaryDirectory() as directory:
      root = Path(directory)
      state = self.initialize_v2(root)

      result = self.run_cli(
        state,
        "register-chat",
        "--role",
        "implementer",
        "--thread-id",
        "thread-123",
        "--model",
        "gpt-5.6-sol",
        "--effort",
        "xhigh",
      )

      self.assertEqual(0, result.returncode, result.stderr)
      ledger = json.loads(state.read_text(encoding="utf-8"))
      self.assertEqual(
        {
          "thread_id": "thread-123",
          "model": "gpt-5.6-sol",
          "effort": "xhigh",
        },
        ledger["chats"]["implementer"],
      )

  def test_schema_v2_registers_the_exact_specialist_matrix(self):
    with tempfile.TemporaryDirectory() as directory:
      state = self.initialize_v2(Path(directory))

      self.register_specialists(state)

      ledger = json.loads(state.read_text(encoding="utf-8"))
      self.assertEqual(
        {
          role: {
            "thread_id": f"{role}-thread",
            "model": model,
            "effort": effort,
          }
          for role, (model, effort) in V2_SPECIALISTS.items()
        },
        ledger["chats"],
      )

  def test_schema_v2_requires_complete_non_empty_specialist_registration(self):
    with tempfile.TemporaryDirectory() as directory:
      root = Path(directory)
      scenarios = (
        *(("missing", role) for role in V2_SPECIALISTS),
        *(("empty", role) for role in V2_SPECIALISTS),
      )
      for condition, role in scenarios:
        with self.subTest(condition=condition, role=role):
          case_root = root / f"{condition}-{role}"
          case_root.mkdir()
          state = self.initialize_v2(case_root)
          self.register_specialists(
            state,
            omitted_role=role if condition == "missing" else None,
            empty_role=role if condition == "empty" else None,
          )
          before = state.read_text(encoding="utf-8")

          result = self.run_cli(state, "transition", "--to", "implementing")

          self.assertEqual(2, result.returncode)
          self.assertEqual(before, state.read_text(encoding="utf-8"))

  def test_schema_v3_requires_mutation_analyst_luna_xhigh_before_implementation(self):
    with tempfile.TemporaryDirectory() as directory:
      root = Path(directory)
      state = self.initialize_v3(root)
      self.register_specialists(
        state,
        specialists=V3_SPECIALISTS,
        omitted_role="mutation-analyst",
      )
      before_missing = state.read_text(encoding="utf-8")

      missing = self.run_cli(state, "transition", "--to", "implementing")

      self.assertEqual(2, missing.returncode)
      self.assertIn("mutation-analyst", missing.stderr)
      self.assertEqual(before_missing, state.read_text(encoding="utf-8"))

      for model, effort in (("gpt-5.6-sol", "xhigh"), ("gpt-5.6-luna", "high")):
        with self.subTest(model=model, effort=effort):
          rejected = self.run_cli(
            state,
            "register-chat",
            "--role",
            "mutation-analyst",
            "--thread-id",
            "mutation-thread",
            "--model",
            model,
            "--effort",
            effort,
          )

          self.assertEqual(2, rejected.returncode)
          self.assertEqual(before_missing, state.read_text(encoding="utf-8"))

      accepted = self.run_cli(
        state,
        "register-chat",
        "--role",
        "mutation-analyst",
        "--thread-id",
        "mutation-thread",
        "--model",
        "gpt-5.6-luna",
        "--effort",
        "xhigh",
      )
      transitioned = self.run_cli(state, "transition", "--to", "implementing")

      self.assertEqual(0, accepted.returncode, accepted.stderr)
      self.assertEqual(0, transitioned.returncode, transitioned.stderr)
      ledger = json.loads(state.read_text(encoding="utf-8"))
      self.assertEqual(
        {
          role: {
            "thread_id": (
              "mutation-thread" if role == "mutation-analyst" else f"{role}-thread"
            ),
            "model": model,
            "effort": effort,
          }
          for role, (model, effort) in V3_SPECIALISTS.items()
        },
        ledger["chats"],
      )

  def test_schema_v3_enters_mutation_testing_only_after_initial_validation(self):
    with tempfile.TemporaryDirectory() as directory:
      state = self.prepare_v3_initial_validation(Path(directory))
      before = state.read_text(encoding="utf-8")

      blocked = self.run_cli(state, "transition", "--to", "mutation-testing")

      self.assertEqual(2, blocked.returncode)
      self.assertEqual(before, state.read_text(encoding="utf-8"))

      acquired = self.run_cli(state, "acquire", "--owner", "validator")
      self.assertEqual(0, acquired.returncode, acquired.stderr)
      for name in ("initial-verify", "initial-sonar"):
        gate = self.run_cli(
          state,
          "record-gate",
          "--name",
          name,
          "--status",
          "passed",
          "--details",
          f"{name} passed",
        )
        self.assertEqual(0, gate.returncode, gate.stderr)
      released = self.run_cli(state, "release", "--owner", "validator")
      direct_review = self.run_cli(state, "transition", "--to", "structural-review")
      mutation = self.run_cli(state, "transition", "--to", "mutation-testing")

      self.assertEqual(0, released.returncode, released.stderr)
      self.assertEqual(2, direct_review.returncode)
      self.assertEqual(0, mutation.returncode, mutation.stderr)
      self.assertEqual(
        "mutation-testing",
        json.loads(state.read_text(encoding="utf-8"))["phase"],
      )

  def test_schema_v3_rejects_unclassified_survivors_and_blocks_structural_review(self):
    with tempfile.TemporaryDirectory() as directory:
      root = Path(directory)
      state = self.prepare_v3_mutation_testing(root)
      log, report, classifications = self.write_mutation_artifacts(
        root,
        [
          {
            "mutant_id": "OrderService.java:42:CONDITIONALS_BOUNDARY",
            "outcome": "survived",
            "classification": "equivalent",
            "justification": "The boundary is normalized by the public constructor.",
          }
        ],
      )
      blocked_review = self.run_cli(state, "transition", "--to", "structural-review")
      self.assertEqual(2, blocked_review.returncode)
      acquired = self.run_cli(state, "acquire", "--owner", "mutation-analyst")
      self.assertEqual(0, acquired.returncode, acquired.stderr)
      before = state.read_text(encoding="utf-8")

      rejected = self.run_cli(
        state,
        "record-mutation",
        "--runner",
        "pit",
        "--result",
        "passed",
        "--analyzed-sha",
        "b" * 40,
        "--fingerprint",
        "c" * 64,
        "--target-class",
        "com.example.OrderService*",
        "--generated",
        "4",
        "--killed",
        "2",
        "--survived",
        "1",
        "--no-coverage",
        "1",
        "--classification-file",
        str(classifications),
        "--log",
        str(log),
        "--report",
        str(report),
        "--details",
        "PIT completed but one no-coverage mutant was not classified",
      )

      self.assertEqual(2, rejected.returncode)
      self.assertIn("classified", rejected.stderr.lower())
      self.assertEqual(before, state.read_text(encoding="utf-8"))

  def test_schema_v3_accepts_zero_actionable_findings_and_justified_equivalents(self):
    with tempfile.TemporaryDirectory() as directory:
      root = Path(directory)
      state = self.prepare_v3_mutation_testing(root)
      log, report, classifications = self.write_mutation_artifacts(
        root,
        [
          {
            "mutant_id": "OrderService.java:42:CONDITIONALS_BOUNDARY",
            "outcome": "survived",
            "classification": "equivalent",
            "justification": "The boundary is normalized by the public constructor.",
          },
          {
            "mutant_id": "OrderService.java:57:NULL_RETURNS",
            "outcome": "no-coverage",
            "classification": "equivalent",
            "justification": "The generated null is rejected by a non-null record component.",
          },
        ],
      )
      acquired = self.run_cli(state, "acquire", "--owner", "mutation-analyst")
      self.assertEqual(0, acquired.returncode, acquired.stderr)

      recorded = self.run_cli(
        state,
        "record-mutation",
        "--runner",
        "pit",
        "--result",
        "passed",
        "--analyzed-sha",
        "b" * 40,
        "--fingerprint",
        "c" * 64,
        "--target-class",
        "com.example.OrderService*",
        "--generated",
        "4",
        "--killed",
        "2",
        "--survived",
        "1",
        "--no-coverage",
        "1",
        "--classification-file",
        str(classifications),
        "--log",
        str(log),
        "--report",
        str(report),
        "--details",
        "PIT completed with no actionable findings",
      )
      released = self.run_cli(state, "release", "--owner", "mutation-analyst")
      reviewed = self.run_cli(state, "transition", "--to", "structural-review")

      self.assertEqual(0, recorded.returncode, recorded.stderr)
      self.assertEqual(0, released.returncode, released.stderr)
      self.assertEqual(0, reviewed.returncode, reviewed.stderr)
      ledger = json.loads(state.read_text(encoding="utf-8"))
      attempt = ledger["mutation_attempts"][-1]
      self.assertEqual("initial", attempt["stage"])
      self.assertEqual("passed", attempt["result"])
      self.assertEqual(["com.example.OrderService*"], attempt["target_classes"])
      self.assertEqual(2, len(attempt["classifications"]))
      self.assertEqual(0, attempt["actionable_findings"])
      self.assertEqual(".agent/tmp/mutation.log", attempt["log_path"])
      self.assertEqual([".agent/tmp/mutation-pit-report"], attempt["report_paths"])

  def test_schema_v3_records_not_applicable_without_calling_it_passed(self):
    with tempfile.TemporaryDirectory() as directory:
      root = Path(directory)
      for reason, targets in (
        ("runner-unavailable", ["com.example.OrderService*"]),
        ("no-production-changes", []),
      ):
        with self.subTest(reason=reason):
          case_root = root / reason
          case_root.mkdir()
          state = self.prepare_v3_mutation_testing(case_root)
          artifacts = case_root / ".agent" / "tmp"
          artifacts.mkdir(parents=True, exist_ok=True)
          log = artifacts / "mutation-assessment.log"
          log.write_text(f"not applicable: {reason}\n", encoding="utf-8")
          acquired = self.run_cli(state, "acquire", "--owner", "mutation-analyst")
          self.assertEqual(0, acquired.returncode, acquired.stderr)
          arguments = [
            "record-mutation",
            "--runner",
            "pit",
            "--result",
            "not-applicable",
            "--analyzed-sha",
            "b" * 40,
            "--fingerprint",
            "c" * 64,
            "--not-applicable-reason",
            reason,
            "--log",
            str(log),
            "--details",
            f"Mutation testing is not applicable because {reason}",
          ]
          for target in targets:
            arguments.extend(("--target-class", target))

          recorded = self.run_cli(state, *arguments)
          released = self.run_cli(state, "release", "--owner", "mutation-analyst")
          reviewed = self.run_cli(state, "transition", "--to", "structural-review")

          self.assertEqual(0, recorded.returncode, recorded.stderr)
          self.assertEqual(0, released.returncode, released.stderr)
          self.assertEqual(0, reviewed.returncode, reviewed.stderr)
          attempt = json.loads(state.read_text(encoding="utf-8"))[
            "mutation_attempts"
          ][-1]
          self.assertEqual("not-applicable", attempt["result"])
          self.assertNotEqual("passed", attempt["result"])
          self.assertEqual(reason, attempt["not_applicable_reason"])

  def test_schema_v3_rejects_actionable_errors_and_unaccounted_mutants(self):
    with tempfile.TemporaryDirectory() as directory:
      root = Path(directory)
      state = self.prepare_v3_mutation_testing(root)
      log, report, classifications = self.write_mutation_artifacts(
        root,
        [
          {
            "mutant_id": "OrderService.java:42:NEGATE_CONDITIONALS",
            "outcome": "survived",
            "classification": "behavior-gap",
            "justification": "The public rejection path lacks a boundary example.",
          }
        ],
        prefix="actionable",
      )
      acquired = self.run_cli(state, "acquire", "--owner", "mutation-analyst")
      self.assertEqual(0, acquired.returncode, acquired.stderr)
      before = state.read_text(encoding="utf-8")

      actionable = self.run_cli(
        state,
        "record-mutation",
        "--runner",
        "pit",
        "--result",
        "passed",
        "--analyzed-sha",
        "b" * 40,
        "--fingerprint",
        "c" * 64,
        "--target-class",
        "com.example.OrderService*",
        "--generated",
        "1",
        "--survived",
        "1",
        "--classification-file",
        str(classifications),
        "--log",
        str(log),
        "--report",
        str(report),
        "--details",
        "One behavior gap remains",
      )

      self.assertEqual(2, actionable.returncode)
      self.assertIn("zero actionable", actionable.stderr.lower())
      self.assertEqual(before, state.read_text(encoding="utf-8"))

      empty_classifications = root / ".agent" / "tmp" / "empty-classifications.json"
      empty_classifications.write_text("[]\n", encoding="utf-8")
      execution_error = self.run_cli(
        state,
        "record-mutation",
        "--runner",
        "pit",
        "--result",
        "passed",
        "--analyzed-sha",
        "b" * 40,
        "--fingerprint",
        "c" * 64,
        "--target-class",
        "com.example.OrderService*",
        "--execution-errors",
        "1",
        "--classification-file",
        str(empty_classifications),
        "--log",
        str(log),
        "--report",
        str(report),
        "--details",
        "The mutation runner reported an execution error",
      )

      self.assertEqual(2, execution_error.returncode)
      self.assertIn("zero execution errors", execution_error.stderr.lower())
      self.assertEqual(before, state.read_text(encoding="utf-8"))

      unaccounted = self.run_cli(
        state,
        "record-mutation",
        "--runner",
        "pit",
        "--result",
        "passed",
        "--analyzed-sha",
        "b" * 40,
        "--fingerprint",
        "c" * 64,
        "--target-class",
        "com.example.OrderService*",
        "--generated",
        "2",
        "--killed",
        "1",
        "--classification-file",
        str(empty_classifications),
        "--log",
        str(log),
        "--report",
        str(report),
        "--details",
        "One generated mutant has no terminal outcome",
      )

      self.assertEqual(2, unaccounted.returncode)
      self.assertIn("account for every generated mutant", unaccounted.stderr.lower())
      self.assertEqual(before, state.read_text(encoding="utf-8"))

  def test_schema_v3_records_partial_environment_failure_without_accepting_the_gate(self):
    with tempfile.TemporaryDirectory() as directory:
      root = Path(directory)
      state = self.prepare_v3_mutation_testing(root)
      artifacts = root / ".agent" / "tmp"
      artifacts.mkdir(parents=True, exist_ok=True)
      log = artifacts / "mutation-environment-failure.log"
      log.write_text("worker process terminated before classification\n", encoding="utf-8")
      acquired = self.run_cli(state, "acquire", "--owner", "mutation-analyst")
      self.assertEqual(0, acquired.returncode, acquired.stderr)

      failed = self.run_cli(
        state,
        "record-mutation",
        "--runner",
        "pit",
        "--result",
        "failed",
        "--failure-kind",
        "environmental",
        "--analyzed-sha",
        "b" * 40,
        "--fingerprint",
        "c" * 64,
        "--target-class",
        "com.example.OrderService*",
        "--generated",
        "3",
        "--killed",
        "1",
        "--survived",
        "1",
        "--execution-errors",
        "1",
        "--log",
        str(log),
        "--details",
        "PIT worker terminated before the remaining mutants were classified",
      )
      released = self.run_cli(state, "release", "--owner", "mutation-analyst")
      review = self.run_cli(state, "transition", "--to", "structural-review")

      self.assertEqual(0, failed.returncode, failed.stderr)
      self.assertEqual(0, released.returncode, released.stderr)
      self.assertEqual(2, review.returncode)
      attempt = json.loads(state.read_text(encoding="utf-8"))["mutation_attempts"][-1]
      self.assertEqual("failed", attempt["result"])
      self.assertEqual("environmental", attempt["failure_kind"])
      self.assertEqual([], attempt["classifications"])

  def test_schema_v3_reuses_mutation_only_when_inputs_are_unchanged(self):
    with tempfile.TemporaryDirectory() as directory:
      root = Path(directory)
      state = self.prepare_v3_mutation_rechecking(root)
      before_gate = state.read_text(encoding="utf-8")

      blocked = self.run_cli(state, "transition", "--to", "delivery-ready")

      self.assertEqual(2, blocked.returncode)
      self.assertEqual(before_gate, state.read_text(encoding="utf-8"))
      artifacts = root / ".agent" / "tmp"
      reuse_log = artifacts / "mutation-reuse.log"
      reuse_log.write_text("inputs compared with initial attempt\n", encoding="utf-8")
      acquired = self.run_cli(state, "acquire", "--owner", "mutation-analyst")
      self.assertEqual(0, acquired.returncode, acquired.stderr)
      before_mismatch = state.read_text(encoding="utf-8")
      common_arguments = [
        "record-mutation",
        "--runner",
        "pit",
        "--result",
        "reused",
        "--analyzed-sha",
        "d" * 40,
        "--target-class",
        "com.example.OrderService*",
        "--reused-from-sha",
        "b" * 40,
        "--reused-from-fingerprint",
        "c" * 64,
        "--log",
        str(reuse_log),
        "--details",
        "Production, eligible tests, and PIT configuration are unchanged",
      ]

      mismatch = self.run_cli(
        state,
        *common_arguments,
        "--fingerprint",
        "e" * 64,
      )

      self.assertEqual(2, mismatch.returncode)
      self.assertIn("unchanged inputs", mismatch.stderr.lower())
      self.assertEqual(before_mismatch, state.read_text(encoding="utf-8"))

      reused = self.run_cli(
        state,
        *common_arguments,
        "--fingerprint",
        "c" * 64,
      )
      released = self.run_cli(state, "release", "--owner", "mutation-analyst")
      delivered = self.run_cli(state, "transition", "--to", "delivery-ready")

      self.assertEqual(0, reused.returncode, reused.stderr)
      self.assertEqual(0, released.returncode, released.stderr)
      self.assertEqual(0, delivered.returncode, delivered.stderr)
      attempts = json.loads(state.read_text(encoding="utf-8"))["mutation_attempts"]
      self.assertEqual(2, len(attempts))
      self.assertEqual("reused", attempts[-1]["result"])
      self.assertEqual("b" * 40, attempts[-1]["reused_from_sha"])
      self.assertEqual("c" * 64, attempts[-1]["reused_from_fingerprint"])
      self.assertEqual(attempts[0]["metrics"], attempts[-1]["metrics"])

  def test_schema_v3_requires_a_new_run_after_relevant_inputs_change(self):
    with tempfile.TemporaryDirectory() as directory:
      root = Path(directory)
      state = self.prepare_v3_mutation_rechecking(root)
      log, report, classifications = self.write_mutation_artifacts(
        root,
        [],
        prefix="final-mutation",
      )
      acquired = self.run_cli(state, "acquire", "--owner", "mutation-analyst")
      self.assertEqual(0, acquired.returncode, acquired.stderr)

      rerun = self.run_cli(
        state,
        "record-mutation",
        "--runner",
        "pit",
        "--result",
        "passed",
        "--analyzed-sha",
        "d" * 40,
        "--fingerprint",
        "e" * 64,
        "--target-class",
        "com.example.OrderService*",
        "--generated",
        "3",
        "--killed",
        "3",
        "--classification-file",
        str(classifications),
        "--log",
        str(log),
        "--report",
        str(report),
        "--details",
        "Relevant tests changed, so PIT was executed again",
      )
      released = self.run_cli(state, "release", "--owner", "mutation-analyst")
      delivered = self.run_cli(state, "transition", "--to", "delivery-ready")

      self.assertEqual(0, rerun.returncode, rerun.stderr)
      self.assertEqual(0, released.returncode, released.stderr)
      self.assertEqual(0, delivered.returncode, delivered.stderr)
      attempts = json.loads(state.read_text(encoding="utf-8"))["mutation_attempts"]
      self.assertEqual(["initial", "final"], [item["stage"] for item in attempts])
      self.assertEqual("passed", attempts[-1]["result"])
      self.assertEqual("e" * 64, attempts[-1]["fingerprint"])

  def test_schema_v3_blocks_pull_request_without_final_mutation_evidence(self):
    with tempfile.TemporaryDirectory() as directory:
      state = self.prepare_v3_mutation_rechecking(Path(directory))
      acquired = self.run_cli(state, "acquire", "--owner", "coordinator")
      self.assertEqual(0, acquired.returncode, acquired.stderr)
      before = state.read_text(encoding="utf-8")

      pull_request = self.run_cli(
        state,
        "record-pr",
        "--repo",
        "owner/demo",
        "--number",
        "12",
        "--url",
        "https://example.test/pull/12",
        "--status",
        "OPEN",
      )

      self.assertEqual(2, pull_request.returncode)
      self.assertEqual(before, state.read_text(encoding="utf-8"))

  def test_checkout_lease_rejects_a_second_owner(self):
    with tempfile.TemporaryDirectory() as directory:
      state = self.initialize_v2(Path(directory))
      first = self.run_cli(state, "acquire", "--owner", "implementer")

      second = self.run_cli(state, "acquire", "--owner", "committer")

      self.assertEqual(0, first.returncode, first.stderr)
      self.assertEqual(2, second.returncode)
      self.assertIn("held by implementer", second.stderr)
      ledger = json.loads(state.read_text(encoding="utf-8"))
      self.assertEqual("implementer", ledger["checkout_lease"]["owner"])

  def test_concurrent_checkout_lease_acquisition_elects_one_owner(self):
    with tempfile.TemporaryDirectory() as directory:
      root = Path(directory)
      state = self.initialize_v2(root)
      ready = root / "ready"
      ready.mkdir()
      continue_marker = root / "continue"
      (root / "sitecustomize.py").write_text(
        """import fcntl
import json
import os
from pathlib import Path
import sys
import time

original_load = json.load
original_flock = fcntl.flock


def coordinated_flock(descriptor, operation):
  if "acquire" in sys.argv and operation & fcntl.LOCK_EX:
    owner = sys.argv[sys.argv.index("--owner") + 1]
    (Path(os.environ["WORKFLOW_TEST_READY"]) / f"{owner}.lock-attempt").touch()
  return original_flock(descriptor, operation)


def coordinated_load(stream, *args, **kwargs):
  value = original_load(stream, *args, **kwargs)
  target = os.environ.get("WORKFLOW_TEST_STATE")
  if (
    target
    and os.path.realpath(stream.name) == os.path.realpath(target)
    and value.get("checkout_lease") is None
    and "acquire" in sys.argv
  ):
    owner = sys.argv[sys.argv.index("--owner") + 1]
    (Path(os.environ["WORKFLOW_TEST_READY"]) / owner).touch()
    deadline = time.monotonic() + 10
    marker = Path(os.environ["WORKFLOW_TEST_CONTINUE"])
    while not marker.exists():
      if time.monotonic() >= deadline:
        raise RuntimeError("concurrent acquire test timed out")
      time.sleep(0.01)
  return value


fcntl.flock = coordinated_flock
json.load = coordinated_load
""",
        encoding="utf-8",
      )
      environment = os.environ.copy()
      environment["PYTHONPATH"] = os.pathsep.join(
        filter(None, (str(root), environment.get("PYTHONPATH")))
      )
      environment["WORKFLOW_TEST_STATE"] = str(state)
      environment["WORKFLOW_TEST_READY"] = str(ready)
      environment["WORKFLOW_TEST_CONTINUE"] = str(continue_marker)

      commands = {
        owner: [
          sys.executable,
          str(SCRIPT),
          "--state",
          str(state),
          "acquire",
          "--owner",
          owner,
        ]
        for owner in ("implementer", "committer")
      }
      processes = {}
      processes["implementer"] = subprocess.Popen(
        commands["implementer"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=environment,
      )
      first_ready_deadline = time.monotonic() + 5
      while not (ready / "implementer").exists():
        if time.monotonic() >= first_ready_deadline:
          break
        time.sleep(0.01)
      processes["committer"] = subprocess.Popen(
        commands["committer"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=environment,
      )
      second_ready_deadline = time.monotonic() + 5
      while not any(
        marker.exists()
        for marker in (ready / "committer", ready / "committer.lock-attempt")
      ):
        if processes["committer"].poll() is not None:
          break
        if time.monotonic() >= second_ready_deadline:
          break
        time.sleep(0.01)

      continue_marker.touch()
      observations = []
      for owner, process in processes.items():
        stdout, stderr = process.communicate(timeout=10)
        observations.append((owner, process.returncode, stdout, stderr))

      self.assertTrue((ready / "implementer").exists(), observations)
      self.assertEqual([0, 2], sorted(item[1] for item in observations), observations)
      winner = next(owner for owner, status, _, _ in observations if status == 0)
      rejected = next(item for item in observations if item[1] == 2)
      self.assertIn(f"held by {winner}", rejected[3])
      shown = self.run_cli(state, "show")
      self.assertEqual(0, shown.returncode, shown.stderr)
      ledger = json.loads(shown.stdout)
      self.assertEqual(winner, ledger["checkout_lease"]["owner"])
      released = self.run_cli(state, "release", "--owner", winner)
      reacquired = self.run_cli(state, "acquire", "--owner", rejected[0])
      self.assertEqual(0, released.returncode, released.stderr)
      self.assertEqual(0, reacquired.returncode, reacquired.stderr)

  def test_only_the_lease_owner_can_release_the_checkout(self):
    with tempfile.TemporaryDirectory() as directory:
      state = self.initialize_v2(Path(directory))
      acquired = self.run_cli(state, "acquire", "--owner", "validator")

      rejected = self.run_cli(state, "release", "--owner", "coordinator")
      released = self.run_cli(state, "release", "--owner", "validator")

      self.assertEqual(0, acquired.returncode, acquired.stderr)
      self.assertEqual(2, rejected.returncode)
      self.assertIn("held by validator", rejected.stderr)
      self.assertEqual(0, released.returncode, released.stderr)
      ledger = json.loads(state.read_text(encoding="utf-8"))
      self.assertIsNone(ledger["checkout_lease"])

  def test_transition_rejects_skipping_required_phases(self):
    with tempfile.TemporaryDirectory() as directory:
      state = self.initialize_v2(Path(directory))

      result = self.run_cli(state, "transition", "--to", "structural-review")

      self.assertEqual(2, result.returncode)
      self.assertIn("invalid transition", result.stderr.lower())
      ledger = json.loads(state.read_text(encoding="utf-8"))
      self.assertEqual("initialized", ledger["phase"])
      self.assertEqual(1, len(ledger["history"]))

  def test_repeating_the_current_transition_is_idempotent(self):
    with tempfile.TemporaryDirectory() as directory:
      state = self.initialize_for_implementation(Path(directory))
      first = self.run_cli(
        state,
        "transition",
        "--to",
        "implementing",
        "--note",
        "TDD started",
      )
      before = state.read_text(encoding="utf-8")

      second = self.run_cli(
        state,
        "transition",
        "--to",
        "implementing",
        "--note",
        "TDD started",
      )

      self.assertEqual(0, first.returncode, first.stderr)
      self.assertEqual(0, second.returncode, second.stderr)
      self.assertEqual(before, state.read_text(encoding="utf-8"))
      ledger = json.loads(before)
      self.assertEqual("initialized", ledger["history"][1]["from"])
      self.assertEqual("implementing", ledger["history"][1]["to"])
      self.assertEqual("TDD started", ledger["history"][1]["note"])

  def test_schema_v2_routes_implemented_work_through_a_habit_check(self):
    with tempfile.TemporaryDirectory() as directory:
      state = self.initialize_for_implementation(Path(directory))
      for phase in ("implementing", "implemented"):
        result = self.run_cli(state, "transition", "--to", phase)
        self.assertEqual(0, result.returncode, result.stderr)

      result = self.run_cli(state, "transition", "--to", "habit-checking")

      self.assertEqual(0, result.returncode, result.stderr)
      ledger = json.loads(state.read_text(encoding="utf-8"))
      self.assertEqual("habit-checking", ledger["phase"])
      self.assertEqual("implemented", ledger["history"][-1]["from"])

  def test_record_commit_is_idempotent_by_commit_sha(self):
    with tempfile.TemporaryDirectory() as directory:
      state = self.initialize_legacy(Path(directory))
      acquired = self.run_cli(state, "acquire", "--owner", "committer")
      arguments = (
        "record-commit",
        "--sha",
        "abc1234",
        "--kind",
        "implementation",
        "--subject",
        "feat(demo): implement behavior",
      )

      first = self.run_cli(state, *arguments)
      second = self.run_cli(state, *arguments)

      self.assertEqual(0, acquired.returncode, acquired.stderr)
      self.assertEqual(0, first.returncode, first.stderr)
      self.assertEqual(0, second.returncode, second.stderr)
      ledger = json.loads(state.read_text(encoding="utf-8"))
      self.assertEqual(1, len(ledger["commits"]))
      self.assertEqual("abc1234", ledger["commits"][0]["sha"])
      self.assertEqual("implementation", ledger["commits"][0]["kind"])

  def test_record_gate_preserves_validation_evidence(self):
    with tempfile.TemporaryDirectory() as directory:
      state = self.initialize_legacy(Path(directory))
      acquired = self.run_cli(state, "acquire", "--owner", "validator")

      result = self.run_cli(
        state,
        "record-gate",
        "--name",
        "initial",
        "--status",
        "passed",
        "--details",
        "42 tests passed; coverage 100%",
        "--url",
        "https://example.test/run/1",
      )

      self.assertEqual(0, acquired.returncode, acquired.stderr)
      self.assertEqual(0, result.returncode, result.stderr)
      gate = json.loads(state.read_text(encoding="utf-8"))["gates"]["initial"][0]
      self.assertEqual("passed", gate["status"])
      self.assertEqual("42 tests passed; coverage 100%", gate["details"])
      self.assertEqual("https://example.test/run/1", gate["url"])

  def test_structural_review_requires_a_green_public_checkpoint(self):
    with tempfile.TemporaryDirectory() as directory:
      state = self.initialize_legacy(Path(directory))
      for phase in (
        "implementing",
        "implemented",
        "committed",
        "initial-validating",
        "coordinator-review",
        "habit-curation",
      ):
        result = self.run_cli(state, "transition", "--to", phase)
        self.assertEqual(0, result.returncode, result.stderr)

      result = self.run_cli(state, "transition", "--to", "structural-review")

      self.assertEqual(2, result.returncode)
      self.assertIn("public-checkpoint", result.stderr)
      ledger = json.loads(state.read_text(encoding="utf-8"))
      self.assertEqual("habit-curation", ledger["phase"])

  def test_record_habit_marks_an_unavailable_tool_as_not_applicable(self):
    with tempfile.TemporaryDirectory() as directory:
      state = self.initialize_legacy(Path(directory))
      acquired = self.run_cli(state, "acquire", "--owner", "habit-curator")

      result = self.run_cli(
        state,
        "record-habit",
        "--status",
        "not-applicable",
        "--details",
        "habit command is not installed",
      )

      self.assertEqual(0, acquired.returncode, acquired.stderr)
      self.assertEqual(0, result.returncode, result.stderr)
      habit = json.loads(state.read_text(encoding="utf-8"))["habit"]
      self.assertEqual("not-applicable", habit["status"])
      self.assertEqual("habit command is not installed", habit["details"])

  def test_schema_v2_records_clean_habit_only_with_zero_raw_findings(self):
    with tempfile.TemporaryDirectory() as directory:
      state = self.prepare_v2_habit_check(Path(directory))
      before = state.read_text(encoding="utf-8")

      rejected = self.run_cli(
        state,
        "record-habit",
        "--status",
        "clean",
        "--details",
        "one raw finding remains",
        "--finding-count",
        "1",
      )

      self.assertEqual(2, rejected.returncode)
      self.assertEqual(before, state.read_text(encoding="utf-8"))

      recorded = self.run_cli(
        state,
        "record-habit",
        "--status",
        "clean",
        "--details",
        "quick check has zero raw findings",
      )

      self.assertEqual(0, recorded.returncode, recorded.stderr)
      self.assertNotEqual(before, state.read_text(encoding="utf-8"))
      habit = json.loads(state.read_text(encoding="utf-8"))["habit"]
      self.assertEqual("clean", habit["status"])
      self.assertEqual("quick", habit["stage"])
      self.assertEqual(0, habit["finding_count"])

  def test_schema_v2_records_ratcheted_habit_only_for_an_unchanged_baseline(self):
    with tempfile.TemporaryDirectory() as directory:
      state = self.prepare_v2_habit_check(Path(directory))
      before = state.read_text(encoding="utf-8")

      rejected = self.run_cli(
        state,
        "record-habit",
        "--status",
        "ratcheted",
        "--details",
        "baseline provenance is missing",
        "--finding-count",
        "4",
      )

      self.assertEqual(2, rejected.returncode)
      self.assertEqual(before, state.read_text(encoding="utf-8"))

      recorded = self.run_cli(
        state,
        "record-habit",
        "--status",
        "ratcheted",
        "--details",
        "authorized baseline unchanged; no active findings added",
        "--finding-count",
        "4",
        "--active-finding-count",
        "0",
        "--baseline-authorized",
        "--baseline-unchanged",
      )

      self.assertEqual(0, recorded.returncode, recorded.stderr)
      habit = json.loads(state.read_text(encoding="utf-8"))["habit"]
      self.assertEqual("ratcheted", habit["status"])
      self.assertEqual(4, habit["finding_count"])
      self.assertEqual(0, habit["active_finding_count"])
      self.assertTrue(habit["baseline_authorized"])
      self.assertTrue(habit["baseline_unchanged"])

  def test_schema_v2_records_snoozed_habit_only_with_explicit_user_authorization(self):
    with tempfile.TemporaryDirectory() as directory:
      state = self.prepare_v2_habit_check(Path(directory))
      before = state.read_text(encoding="utf-8")

      rejected = self.run_cli(
        state,
        "record-habit",
        "--status",
        "snoozed",
        "--details",
        "no user authorization recorded",
        "--finding-count",
        "2",
      )

      self.assertEqual(2, rejected.returncode)
      self.assertEqual(before, state.read_text(encoding="utf-8"))

      recorded = self.run_cli(
        state,
        "record-habit",
        "--status",
        "snoozed",
        "--details",
        "user explicitly authorized the existing snooze",
        "--finding-count",
        "2",
        "--user-authorized-snooze",
      )

      self.assertEqual(0, recorded.returncode, recorded.stderr)
      habit = json.loads(state.read_text(encoding="utf-8"))["habit"]
      self.assertEqual("snoozed", habit["status"])
      self.assertTrue(habit["user_authorized_snooze"])

  def test_schema_v2_records_not_applicable_only_when_habit_is_unavailable(self):
    with tempfile.TemporaryDirectory() as directory:
      state = self.prepare_v2_habit_check(Path(directory))
      before = state.read_text(encoding="utf-8")

      rejected = self.run_cli(
        state,
        "record-habit",
        "--status",
        "not-applicable",
        "--details",
        "availability was not checked",
      )

      self.assertEqual(2, rejected.returncode)
      self.assertEqual(before, state.read_text(encoding="utf-8"))

      recorded = self.run_cli(
        state,
        "record-habit",
        "--status",
        "not-applicable",
        "--details",
        "habit executable is unavailable",
        "--tool-unavailable",
      )

      self.assertEqual(0, recorded.returncode, recorded.stderr)
      habit = json.loads(state.read_text(encoding="utf-8"))["habit"]
      self.assertEqual("not-applicable", habit["status"])
      self.assertTrue(habit["tool_unavailable"])

  def test_schema_v2_rejects_legacy_habit_freeze_controls(self):
    with tempfile.TemporaryDirectory() as directory:
      state = self.prepare_v2_habit_check(Path(directory))
      before = state.read_text(encoding="utf-8")

      result = self.run_cli(
        state,
        "record-habit",
        "--status",
        "clean",
        "--details",
        "legacy controls must not be used",
        "--snoozed-until-changed",
        "--pruned",
      )

      self.assertEqual(2, result.returncode)
      self.assertEqual(before, state.read_text(encoding="utf-8"))

  def test_schema_v2_rejects_negative_habit_finding_counts_atomically(self):
    with tempfile.TemporaryDirectory() as directory:
      state = self.prepare_v2_habit_check(Path(directory))
      before = state.read_text(encoding="utf-8")

      result = self.run_cli(
        state,
        "record-habit",
        "--status",
        "snoozed",
        "--details",
        "invalid negative raw count",
        "--finding-count",
        "-1",
        "--user-authorized-snooze",
      )

      self.assertEqual(2, result.returncode)
      self.assertEqual(before, state.read_text(encoding="utf-8"))

  def test_schema_v2_requires_current_quick_habit_evidence_before_checkpoint(self):
    with tempfile.TemporaryDirectory() as directory:
      state = self.prepare_v2_habit_check(Path(directory))
      before = state.read_text(encoding="utf-8")

      blocked = self.run_cli(
        state,
        "transition",
        "--to",
        "checkpoint-committing",
      )

      self.assertEqual(2, blocked.returncode)
      self.assertEqual(before, state.read_text(encoding="utf-8"))

      habit = self.run_cli(
        state,
        "record-habit",
        "--status",
        "clean",
        "--details",
        "quick check has zero raw findings",
      )
      released = self.run_cli(state, "release", "--owner", "habit-curator")
      transitioned = self.run_cli(
        state,
        "transition",
        "--to",
        "checkpoint-committing",
      )

      self.assertEqual(0, habit.returncode, habit.stderr)
      self.assertEqual(0, released.returncode, released.stderr)
      self.assertEqual(0, transitioned.returncode, transitioned.stderr)
      self.assertEqual(
        "checkpoint-committing",
        json.loads(state.read_text(encoding="utf-8"))["phase"],
      )

  def test_schema_v2_no_configured_files_observation_satisfies_only_quick_check(self):
    with tempfile.TemporaryDirectory() as directory:
      state = self.prepare_v2_habit_check(Path(directory))
      released = self.run_cli(state, "release", "--owner", "habit-curator")
      self.assertEqual(0, released.returncode, released.stderr)
      acquired = self.run_cli(state, "acquire", "--owner", "coordinator")
      self.assertEqual(0, acquired.returncode, acquired.stderr)

      observed = self.run_cli(
        state,
        "record-habit-observation",
        "--kind",
        "no-configured-files",
        "--details",
        "habit-hooks reported nothing scanned because no files are configured",
      )
      released = self.run_cli(state, "release", "--owner", "coordinator")
      transitioned = self.run_cli(
        state,
        "transition",
        "--to",
        "checkpoint-committing",
      )

      self.assertEqual(0, observed.returncode, observed.stderr)
      self.assertEqual(0, released.returncode, released.stderr)
      self.assertEqual(0, transitioned.returncode, transitioned.stderr)
      ledger = json.loads(state.read_text(encoding="utf-8"))
      self.assertIsNone(ledger["habit"])
      self.assertEqual("no-configured-files", ledger["habit_observations"][-1]["kind"])
      self.assertEqual("quick", ledger["habit_observations"][-1]["stage"])
      self.assertEqual("checkpoint-committing", ledger["phase"])

      self.advance_v2_checkpoint_to_habit_recheck(state)
      before_final = state.read_text(encoding="utf-8")

      blocked = self.run_cli(state, "transition", "--to", "final-validating")

      self.assertEqual(2, blocked.returncode)
      self.assertEqual(before_final, state.read_text(encoding="utf-8"))

  def test_schema_v2_reclassifies_premature_quick_habit_evidence_auditably(self):
    with tempfile.TemporaryDirectory() as directory:
      state = self.prepare_v2_habit_check(Path(directory))
      classified = self.run_cli(
        state,
        "record-habit",
        "--status",
        "not-applicable",
        "--details",
        "premature tool-unavailable classification",
        "--tool-unavailable",
      )
      self.assertEqual(0, classified.returncode, classified.stderr)
      released = self.run_cli(state, "release", "--owner", "habit-curator")
      self.assertEqual(0, released.returncode, released.stderr)
      acquired = self.run_cli(state, "acquire", "--owner", "coordinator")
      self.assertEqual(0, acquired.returncode, acquired.stderr)
      arguments = (
        "record-habit-observation",
        "--kind",
        "no-configured-files",
        "--details",
        "tool installed but no repository files were configured or scanned",
        "--reclassify-current",
      )

      reclassified = self.run_cli(state, *arguments)
      after_reclassification = state.read_text(encoding="utf-8")
      repeated = self.run_cli(state, *arguments)

      self.assertEqual(0, reclassified.returncode, reclassified.stderr)
      self.assertEqual(0, repeated.returncode, repeated.stderr)
      self.assertEqual(after_reclassification, state.read_text(encoding="utf-8"))
      ledger = json.loads(after_reclassification)
      self.assertIsNone(ledger["habit"])
      observation = ledger["habit_observations"][-1]
      self.assertEqual("no-configured-files", observation["kind"])
      self.assertEqual("not-applicable", observation["reclassified_habit"]["status"])
      self.assertEqual(
        "premature tool-unavailable classification",
        observation["reclassified_habit"]["details"],
      )

  def test_schema_v2_requires_coordinator_authorization_for_corrections(self):
    with tempfile.TemporaryDirectory() as directory:
      state = self.prepare_v2_habit_check(Path(directory))
      released = self.run_cli(state, "release", "--owner", "habit-curator")
      self.assertEqual(0, released.returncode, released.stderr)
      before = state.read_text(encoding="utf-8")

      blocked = self.run_cli(state, "transition", "--to", "implementing")

      self.assertEqual(2, blocked.returncode)
      self.assertEqual(before, state.read_text(encoding="utf-8"))

      transitioned = self.run_cli(
        state,
        "transition",
        "--to",
        "implementing",
        "--note",
        "Coordinator authorized a deterministic low-risk correction",
      )

      self.assertEqual(0, transitioned.returncode, transitioned.stderr)
      event = json.loads(transitioned.stdout)
      self.assertEqual("habit-checking", event["from"])
      self.assertEqual("implementing", event["to"])
      self.assertTrue(event["note"])

  def test_schema_v2_preserves_its_existing_corrective_review_routes(self):
    with tempfile.TemporaryDirectory() as directory:
      root = Path(directory)
      scenarios = (
        (self.prepare_v2_habit_recheck, "structural-review"),
        (self.prepare_v2_final_validation, "habit-rechecking"),
        (self.prepare_v2_final_validation, "structural-review"),
      )
      for index, (prepare, target) in enumerate(scenarios):
        with self.subTest(target=target):
          case_root = root / str(index)
          case_root.mkdir()
          state = prepare(case_root)

          transitioned = self.run_cli(
            state,
            "transition",
            "--to",
            target,
            "--note",
            "Coordinator routed the existing schema-v2 corrective flow",
          )

          self.assertEqual(0, transitioned.returncode, transitioned.stderr)
          self.assertEqual(
            target,
            json.loads(state.read_text(encoding="utf-8"))["phase"],
          )

  def test_schema_v2_records_fresh_habit_evidence_after_a_corrective_loop(self):
    with tempfile.TemporaryDirectory() as directory:
      state = self.prepare_v2_structural_review(Path(directory))
      for phase in ("implementing", "implemented", "habit-checking"):
        arguments = ["transition", "--to", phase]
        if phase == "implementing":
          arguments.extend(
            ("--note", "Coordinator authorized a deterministic correction")
          )
        transitioned = self.run_cli(state, *arguments)
        self.assertEqual(0, transitioned.returncode, transitioned.stderr)
      acquired = self.run_cli(state, "acquire", "--owner", "habit-curator")
      self.assertEqual(0, acquired.returncode, acquired.stderr)

      repeated = self.run_cli(
        state,
        "record-habit",
        "--status",
        "clean",
        "--details",
        "quick check has zero raw findings",
      )
      released = self.run_cli(state, "release", "--owner", "habit-curator")
      transitioned = self.run_cli(
        state,
        "transition",
        "--to",
        "checkpoint-committing",
      )

      self.assertEqual(0, repeated.returncode, repeated.stderr)
      self.assertEqual(0, released.returncode, released.stderr)
      self.assertEqual(0, transitioned.returncode, transitioned.stderr)
      habit = json.loads(state.read_text(encoding="utf-8"))["habit"]
      self.assertEqual(1, len(habit["history"]))
      self.assertEqual(
        "checkpoint-committing",
        json.loads(state.read_text(encoding="utf-8"))["phase"],
      )

  def test_schema_v2_requires_a_current_checkpoint_commit_before_validation(self):
    with tempfile.TemporaryDirectory() as directory:
      state = self.prepare_v2_checkpoint_commit(Path(directory))
      before = state.read_text(encoding="utf-8")

      blocked = self.run_cli(
        state,
        "transition",
        "--to",
        "initial-validating",
      )

      self.assertEqual(2, blocked.returncode)
      self.assertEqual(before, state.read_text(encoding="utf-8"))

      acquired = self.run_cli(state, "acquire", "--owner", "committer")
      committed = self.run_cli(
        state,
        "record-commit",
        "--sha",
        "abc1234",
        "--kind",
        "implementation",
        "--subject",
        "feat(demo): implement behavior",
      )
      released = self.run_cli(state, "release", "--owner", "committer")
      transitioned = self.run_cli(
        state,
        "transition",
        "--to",
        "initial-validating",
      )

      self.assertEqual(0, acquired.returncode, acquired.stderr)
      self.assertEqual(0, committed.returncode, committed.stderr)
      self.assertEqual(0, released.returncode, released.stderr)
      self.assertEqual(0, transitioned.returncode, transitioned.stderr)
      ledger = json.loads(state.read_text(encoding="utf-8"))
      self.assertEqual("checkpoint-committing", ledger["commits"][-1]["phase"])
      self.assertEqual("initial-validating", ledger["phase"])

  def test_schema_v2_requires_initial_verify_and_sonar_before_structural_review(self):
    with tempfile.TemporaryDirectory() as directory:
      state = self.prepare_v2_initial_validation(Path(directory))
      acquired = self.run_cli(state, "acquire", "--owner", "validator")
      self.assertEqual(0, acquired.returncode, acquired.stderr)

      verify = self.run_cli(
        state,
        "record-gate",
        "--name",
        "initial-verify",
        "--status",
        "passed",
        "--details",
        "clean verify passed",
      )
      blocked = self.run_cli(state, "transition", "--to", "structural-review")

      self.assertEqual(0, verify.returncode, verify.stderr)
      self.assertEqual(2, blocked.returncode)
      self.assertEqual(
        "initial-validating",
        json.loads(state.read_text(encoding="utf-8"))["phase"],
      )

      sonar = self.run_cli(
        state,
        "record-gate",
        "--name",
        "initial-sonar",
        "--status",
        "passed",
        "--details",
        "sonar passed",
      )
      released = self.run_cli(state, "release", "--owner", "validator")
      transitioned = self.run_cli(state, "transition", "--to", "structural-review")

      self.assertEqual(0, sonar.returncode, sonar.stderr)
      self.assertEqual(0, released.returncode, released.stderr)
      self.assertEqual(0, transitioned.returncode, transitioned.stderr)
      self.assertEqual(
        "structural-review",
        json.loads(state.read_text(encoding="utf-8"))["phase"],
      )

  def test_schema_v2_records_fresh_validation_gates_after_a_corrective_loop(self):
    with tempfile.TemporaryDirectory() as directory:
      state = self.prepare_v2_structural_review(Path(directory))
      for phase in ("implementing", "implemented", "habit-checking"):
        arguments = ["transition", "--to", phase]
        if phase == "implementing":
          arguments.extend(
            ("--note", "Coordinator authorized a deterministic correction")
          )
        transitioned = self.run_cli(state, *arguments)
        self.assertEqual(0, transitioned.returncode, transitioned.stderr)
      acquired = self.run_cli(state, "acquire", "--owner", "habit-curator")
      self.assertEqual(0, acquired.returncode, acquired.stderr)
      habit = self.run_cli(
        state,
        "record-habit",
        "--status",
        "clean",
        "--details",
        "quick check has zero raw findings",
      )
      self.assertEqual(0, habit.returncode, habit.stderr)
      released = self.run_cli(state, "release", "--owner", "habit-curator")
      self.assertEqual(0, released.returncode, released.stderr)
      committing = self.run_cli(state, "transition", "--to", "checkpoint-committing")
      self.assertEqual(0, committing.returncode, committing.stderr)
      acquired = self.run_cli(state, "acquire", "--owner", "committer")
      self.assertEqual(0, acquired.returncode, acquired.stderr)
      commit = self.run_cli(
        state,
        "record-commit",
        "--sha",
        "correct123",
        "--kind",
        "correction",
        "--subject",
        "fix(demo): correct behavior",
      )
      self.assertEqual(0, commit.returncode, commit.stderr)
      released = self.run_cli(state, "release", "--owner", "committer")
      self.assertEqual(0, released.returncode, released.stderr)
      validating = self.run_cli(state, "transition", "--to", "initial-validating")
      self.assertEqual(0, validating.returncode, validating.stderr)
      acquired = self.run_cli(state, "acquire", "--owner", "validator")
      self.assertEqual(0, acquired.returncode, acquired.stderr)

      for name in ("initial-verify", "initial-sonar"):
        gate = self.run_cli(
          state,
          "record-gate",
          "--name",
          name,
          "--status",
          "passed",
          "--details",
          f"{name} passed",
        )
        self.assertEqual(0, gate.returncode, gate.stderr)
      released = self.run_cli(state, "release", "--owner", "validator")
      transitioned = self.run_cli(state, "transition", "--to", "structural-review")

      self.assertEqual(0, released.returncode, released.stderr)
      self.assertEqual(0, transitioned.returncode, transitioned.stderr)
      gates = json.loads(state.read_text(encoding="utf-8"))["gates"]
      self.assertEqual(2, len(gates["initial-verify"]))
      self.assertEqual(2, len(gates["initial-sonar"]))

  def test_schema_v2_requires_a_fresh_habit_recheck_after_structural_review(self):
    with tempfile.TemporaryDirectory() as directory:
      state = self.prepare_v2_structural_review(Path(directory))
      rechecking = self.run_cli(state, "transition", "--to", "habit-rechecking")
      self.assertEqual(0, rechecking.returncode, rechecking.stderr)
      before = state.read_text(encoding="utf-8")

      blocked = self.run_cli(state, "transition", "--to", "final-validating")

      self.assertEqual(2, blocked.returncode)
      self.assertEqual(before, state.read_text(encoding="utf-8"))

      acquired = self.run_cli(state, "acquire", "--owner", "habit-curator")
      habit = self.run_cli(
        state,
        "record-habit",
        "--status",
        "clean",
        "--details",
        "post-review check has zero raw findings",
      )
      released = self.run_cli(state, "release", "--owner", "habit-curator")
      transitioned = self.run_cli(state, "transition", "--to", "final-validating")

      self.assertEqual(0, acquired.returncode, acquired.stderr)
      self.assertEqual(0, habit.returncode, habit.stderr)
      self.assertEqual(0, released.returncode, released.stderr)
      self.assertEqual(0, transitioned.returncode, transitioned.stderr)
      ledger = json.loads(state.read_text(encoding="utf-8"))
      self.assertEqual("final", ledger["habit"]["stage"])
      self.assertEqual("quick", ledger["habit"]["history"][-1]["stage"])
      self.assertEqual("final-validating", ledger["phase"])

  def test_schema_v2_requires_a_commit_when_post_review_work_has_a_delta(self):
    with tempfile.TemporaryDirectory() as directory:
      state = self.prepare_v2_habit_recheck(Path(directory))
      committing = self.run_cli(state, "transition", "--to", "final-committing")
      self.assertEqual(0, committing.returncode, committing.stderr)
      before = state.read_text(encoding="utf-8")

      blocked = self.run_cli(state, "transition", "--to", "final-validating")

      self.assertEqual(2, blocked.returncode)
      self.assertEqual(before, state.read_text(encoding="utf-8"))

      acquired = self.run_cli(state, "acquire", "--owner", "committer")
      committed = self.run_cli(
        state,
        "record-commit",
        "--sha",
        "def5678",
        "--kind",
        "structural-refactor",
        "--subject",
        "refactor(demo): reduce structural coupling",
      )
      released = self.run_cli(state, "release", "--owner", "committer")
      transitioned = self.run_cli(state, "transition", "--to", "final-validating")

      self.assertEqual(0, acquired.returncode, acquired.stderr)
      self.assertEqual(0, committed.returncode, committed.stderr)
      self.assertEqual(0, released.returncode, released.stderr)
      self.assertEqual(0, transitioned.returncode, transitioned.stderr)
      ledger = json.loads(state.read_text(encoding="utf-8"))
      self.assertEqual("final-committing", ledger["commits"][-1]["phase"])
      self.assertEqual("final-validating", ledger["phase"])

  def test_schema_v2_requires_final_verify_and_sonar_before_delivery(self):
    with tempfile.TemporaryDirectory() as directory:
      state = self.prepare_v2_final_validation(Path(directory))
      acquired = self.run_cli(state, "acquire", "--owner", "validator")
      self.assertEqual(0, acquired.returncode, acquired.stderr)

      verify = self.run_cli(
        state,
        "record-gate",
        "--name",
        "final-verify",
        "--status",
        "passed",
        "--details",
        "final clean verify passed",
      )
      blocked = self.run_cli(state, "transition", "--to", "delivery-ready")

      self.assertEqual(0, verify.returncode, verify.stderr)
      self.assertEqual(2, blocked.returncode)
      self.assertEqual(
        "final-validating",
        json.loads(state.read_text(encoding="utf-8"))["phase"],
      )

      sonar = self.run_cli(
        state,
        "record-gate",
        "--name",
        "final-sonar",
        "--status",
        "passed",
        "--details",
        "final sonar passed",
      )
      released = self.run_cli(state, "release", "--owner", "validator")
      transitioned = self.run_cli(state, "transition", "--to", "delivery-ready")

      self.assertEqual(0, sonar.returncode, sonar.stderr)
      self.assertEqual(0, released.returncode, released.stderr)
      self.assertEqual(0, transitioned.returncode, transitioned.stderr)
      self.assertEqual(
        "delivery-ready",
        json.loads(state.read_text(encoding="utf-8"))["phase"],
      )

  def test_record_pr_rejects_creation_before_the_final_gate(self):
    with tempfile.TemporaryDirectory() as directory:
      state = self.initialize_legacy(Path(directory))

      result = self.run_cli(
        state,
        "record-pr",
        "--repo",
        "owner/demo",
        "--number",
        "12",
        "--url",
        "https://example.test/pull/12",
        "--status",
        "OPEN",
      )

      self.assertEqual(2, result.returncode)
      self.assertIn("final gate", result.stderr.lower())
      ledger = json.loads(state.read_text(encoding="utf-8"))
      self.assertIsNone(ledger["pull_request"])

  def test_schema_v2_records_a_pull_request_without_a_baseline_commit(self):
    with tempfile.TemporaryDirectory() as directory:
      state = self.prepare_v2_delivery(Path(directory))
      acquired = self.run_cli(state, "acquire", "--owner", "coordinator")

      pull_request = self.run_cli(
        state,
        "record-pr",
        "--repo",
        "owner/demo",
        "--number",
        "12",
        "--url",
        "https://example.test/pull/12",
        "--status",
        "OPEN",
      )
      transitioned = self.run_cli(state, "transition", "--to", "pr-open")

      self.assertEqual(0, acquired.returncode, acquired.stderr)
      self.assertEqual(0, pull_request.returncode, pull_request.stderr)
      self.assertEqual(0, transitioned.returncode, transitioned.stderr)
      ledger = json.loads(state.read_text(encoding="utf-8"))
      self.assertFalse(any(commit["kind"] == "baseline" for commit in ledger["commits"]))
      self.assertEqual("OPEN", ledger["pull_request"]["status"])
      self.assertEqual("pr-open", ledger["phase"])

  def test_record_pr_rejects_missing_habit_evidence_without_changing_the_ledger(self):
    with tempfile.TemporaryDirectory() as directory:
      state = self.prepare_pull_request_prerequisites(
        Path(directory),
        record_habit=False,
      )
      before = state.read_text(encoding="utf-8")

      result = self.run_cli(
        state,
        "record-pr",
        "--repo",
        "owner/demo",
        "--number",
        "12",
        "--url",
        "https://example.test/pull/12",
        "--status",
        "OPEN",
      )

      self.assertEqual(2, result.returncode)
      self.assertIn("habit evidence", result.stderr.lower())
      self.assertEqual(before, state.read_text(encoding="utf-8"))

  def test_record_pr_rejects_missing_baseline_commit_without_changing_the_ledger(self):
    with tempfile.TemporaryDirectory() as directory:
      state = self.prepare_pull_request_prerequisites(
        Path(directory),
        record_baseline=False,
      )
      before = state.read_text(encoding="utf-8")

      result = self.run_cli(
        state,
        "record-pr",
        "--repo",
        "owner/demo",
        "--number",
        "12",
        "--url",
        "https://example.test/pull/12",
        "--status",
        "OPEN",
      )

      self.assertEqual(2, result.returncode)
      self.assertIn("baseline commit", result.stderr.lower())
      self.assertEqual(before, state.read_text(encoding="utf-8"))

  def test_ci_allows_only_one_retry_for_transient_failure(self):
    with tempfile.TemporaryDirectory() as directory:
      state = self.prepare_pull_request(Path(directory))
      events = (
        ("transient-failed", "run-1"),
        ("retrying", "run-2"),
        ("transient-failed", "run-2"),
      )
      for status, run_id in events:
        result = self.run_cli(
          state,
          "record-ci",
          "--status",
          status,
          "--run-id",
          run_id,
          "--url",
          f"https://example.test/{run_id}",
          "--details",
          status,
        )
        self.assertEqual(0, result.returncode, result.stderr)

      second_retry = self.run_cli(
        state,
        "record-ci",
        "--status",
        "retrying",
        "--run-id",
        "run-3",
        "--url",
        "https://example.test/run-3",
        "--details",
        "second retry",
      )

      self.assertEqual(2, second_retry.returncode)
      self.assertIn("one transient retry", second_retry.stderr.lower())

  def test_schema_v2_requires_current_passed_ci_before_ready_for_merge(self):
    with tempfile.TemporaryDirectory() as directory:
      state = self.prepare_v2_pull_request(Path(directory))
      monitoring = self.run_cli(state, "transition", "--to", "ci-monitoring")
      self.assertEqual(0, monitoring.returncode, monitoring.stderr)
      before = state.read_text(encoding="utf-8")

      blocked = self.run_cli(state, "transition", "--to", "ready-for-merge")

      self.assertEqual(2, blocked.returncode)
      self.assertEqual(before, state.read_text(encoding="utf-8"))

      ci = self.run_cli(
        state,
        "record-ci",
        "--status",
        "passed",
        "--run-id",
        "run-1",
        "--url",
        "https://example.test/run-1",
        "--details",
        "all required checks passed",
      )
      transitioned = self.run_cli(state, "transition", "--to", "ready-for-merge")

      self.assertEqual(0, ci.returncode, ci.stderr)
      self.assertEqual(0, transitioned.returncode, transitioned.stderr)
      self.assertEqual(
        "ready-for-merge",
        json.loads(state.read_text(encoding="utf-8"))["phase"],
      )

  def test_cleanup_preserves_files_without_confirmed_merged_status(self):
    with tempfile.TemporaryDirectory() as directory:
      root = Path(directory)
      state = self.initialize_v2(root)
      ledger = json.loads(state.read_text(encoding="utf-8"))
      plan = Path(ledger["plan_path"])

      result = self.run_cli(state, "cleanup", "--github-status", "CLOSED")

      self.assertEqual(2, result.returncode)
      self.assertIn("merged", result.stderr.lower())
      self.assertTrue(state.exists())
      self.assertTrue(plan.exists())

  def test_cleanup_removes_only_the_confirmed_merged_plan_files(self):
    with tempfile.TemporaryDirectory() as directory:
      root = Path(directory)
      unrelated = root / "keep.txt"
      unrelated.write_text("keep\n", encoding="utf-8")
      state = self.prepare_pull_request(root)
      plan = Path(json.loads(state.read_text(encoding="utf-8"))["plan_path"])

      result = self.run_cli(
        state,
        "cleanup",
        "--github-status",
        "MERGED",
        "--repo",
        "owner/demo",
        "--number",
        "12",
      )

      self.assertEqual(0, result.returncode, result.stderr)
      self.assertFalse(state.exists())
      self.assertFalse(plan.exists())
      self.assertEqual("keep\n", unrelated.read_text(encoding="utf-8"))

  def test_cleanup_accepts_a_matching_legacy_v1_ledger_after_github_merge(self):
    with tempfile.TemporaryDirectory() as directory:
      root = Path(directory)
      state = self.prepare_pull_request(root)
      ledger = json.loads(state.read_text(encoding="utf-8"))
      plan = Path(ledger["plan_path"])
      state.write_text(
        json.dumps(ledger, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
      )

      result = self.run_cli(
        state,
        "cleanup",
        "--github-status",
        "MERGED",
        "--repo",
        "owner/demo",
        "--number",
        "12",
      )

      self.assertEqual(0, result.returncode, result.stderr)
      self.assertFalse(state.exists())
      self.assertFalse(plan.exists())

  def test_cleanup_accepts_a_matching_v2_ledger_after_github_merge(self):
    with tempfile.TemporaryDirectory() as directory:
      state = self.prepare_v2_pull_request(Path(directory))
      plan = Path(json.loads(state.read_text(encoding="utf-8"))["plan_path"])

      result = self.run_cli(
        state,
        "cleanup",
        "--github-status",
        "MERGED",
        "--repo",
        "owner/demo",
        "--number",
        "12",
      )

      self.assertEqual(0, result.returncode, result.stderr)
      self.assertFalse(state.exists())
      self.assertFalse(plan.exists())

  def test_failed_atomic_write_preserves_the_previous_ledger(self):
    with tempfile.TemporaryDirectory() as directory:
      root = Path(directory)
      state = self.initialize_v2(root)
      before = state.read_text(encoding="utf-8")
      root.chmod(0o500)
      try:
        result = self.run_cli(
          state,
          "register-chat",
          "--role",
          "validator",
          "--thread-id",
          "thread-456",
          "--model",
          "gpt-5.6-luna",
          "--effort",
          "xhigh",
        )
      finally:
        root.chmod(0o700)

      self.assertEqual(2, result.returncode)
      self.assertIn("unable to write ledger", result.stderr.lower())
      self.assertNotIn("traceback", result.stderr.lower())
      self.assertEqual(before, state.read_text(encoding="utf-8"))

  def test_habit_freeze_requires_full_classification_snooze_and_prune(self):
    with tempfile.TemporaryDirectory() as directory:
      state = self.initialize_legacy(Path(directory))
      acquired = self.run_cli(state, "acquire", "--owner", "habit-curator")

      result = self.run_cli(
        state,
        "record-habit",
        "--status",
        "frozen",
        "--details",
        "one finding remains",
        "--finding-count",
        "2",
        "--classified-count",
        "1",
      )

      self.assertEqual(0, acquired.returncode, acquired.stderr)
      self.assertEqual(2, result.returncode)
      self.assertIn("every finding", result.stderr.lower())
      self.assertIsNone(json.loads(state.read_text(encoding="utf-8"))["habit"])

  def test_init_rejects_reusing_a_state_path_for_a_different_plan_identity(self):
    with tempfile.TemporaryDirectory() as directory:
      root = Path(directory)
      state = self.initialize_v2(root)
      before = state.read_text(encoding="utf-8")

      result = self.run_cli(
        state,
        "init",
        "--slug",
        "demo",
        "--plan",
        str(root / "demo.md"),
        "--repo",
        str(root),
        "--branch",
        "codex/different",
        "--base",
        "main",
        "--base-sha",
        BASE_SHA,
      )

      self.assertEqual(2, result.returncode)
      self.assertIn("different plan identity", result.stderr.lower())
      self.assertEqual(before, state.read_text(encoding="utf-8"))

  def test_show_rejects_a_truncated_ledger_with_a_known_schema_version(self):
    with tempfile.TemporaryDirectory() as directory:
      state = Path(directory) / "demo.workflow.json"
      truncated = '{"schema_version": 1, "slug": "demo"}\n'
      state.write_text(truncated, encoding="utf-8")

      result = self.run_cli(state, "show")

      self.assertEqual(2, result.returncode)
      self.assertIn("corrupt ledger", result.stderr.lower())
      self.assertNotIn("traceback", result.stderr.lower())
      self.assertEqual(truncated, state.read_text(encoding="utf-8"))

  def test_show_rejects_corrupt_nested_workflow_records(self):
    with tempfile.TemporaryDirectory() as directory:
      state = self.initialize_v2(Path(directory))
      ledger = json.loads(state.read_text(encoding="utf-8"))
      ledger["commits"] = [{}]
      corrupt = json.dumps(ledger, indent=2, sort_keys=True) + "\n"
      state.write_text(corrupt, encoding="utf-8")

      result = self.run_cli(state, "show")

      self.assertEqual(2, result.returncode)
      self.assertIn("corrupt ledger", result.stderr.lower())
      self.assertNotIn("traceback", result.stderr.lower())
      self.assertEqual(corrupt, state.read_text(encoding="utf-8"))

  def test_show_rejects_v3_reuse_that_does_not_match_its_initial_attempt(self):
    with tempfile.TemporaryDirectory() as directory:
      state = self.prepare_v3_mutation_rechecking(Path(directory))
      ledger = json.loads(state.read_text(encoding="utf-8"))
      initial = ledger["mutation_attempts"][0]
      forged_reuse = {
        **initial,
        "stage": "final",
        "result": "reused",
        "analyzed_sha": "d" * 40,
        "log_path": ".agent/tmp/forged-reuse.log",
        "reused_from_sha": initial["analyzed_sha"],
        "reused_from_fingerprint": "f" * 64,
        "recorded_at": "9999-01-01T00:00:00+00:00",
      }
      ledger["mutation_attempts"].append(forged_reuse)
      corrupt = json.dumps(ledger, indent=2, sort_keys=True) + "\n"
      state.write_text(corrupt, encoding="utf-8")

      result = self.run_cli(state, "show")

      self.assertEqual(2, result.returncode)
      self.assertIn("corrupt ledger", result.stderr.lower())
      self.assertEqual(corrupt, state.read_text(encoding="utf-8"))

  def test_show_rejects_a_phase_that_disagrees_with_history(self):
    with tempfile.TemporaryDirectory() as directory:
      state = self.initialize_v2(Path(directory))
      ledger = json.loads(state.read_text(encoding="utf-8"))
      ledger["phase"] = "implementing"
      corrupt = json.dumps(ledger, indent=2, sort_keys=True) + "\n"
      state.write_text(corrupt, encoding="utf-8")

      result = self.run_cli(state, "show")

      self.assertEqual(2, result.returncode)
      self.assertIn("corrupt ledger", result.stderr.lower())
      self.assertNotIn("traceback", result.stderr.lower())
      self.assertEqual(corrupt, state.read_text(encoding="utf-8"))

  def test_show_rejects_a_discontinuous_history_chain(self):
    with tempfile.TemporaryDirectory() as directory:
      state = self.initialize_for_implementation(Path(directory))
      for phase in ("implementing", "implemented"):
        transitioned = self.run_cli(state, "transition", "--to", phase)
        self.assertEqual(0, transitioned.returncode, transitioned.stderr)
      ledger = json.loads(state.read_text(encoding="utf-8"))
      ledger["history"][-1]["from"] = "initialized"
      ledger["history"][-1]["to"] = "implementing"
      ledger["phase"] = "implementing"
      corrupt = json.dumps(ledger, indent=2, sort_keys=True) + "\n"
      state.write_text(corrupt, encoding="utf-8")

      result = self.run_cli(state, "show")

      self.assertEqual(2, result.returncode)
      self.assertIn("corrupt ledger", result.stderr.lower())
      self.assertNotIn("traceback", result.stderr.lower())
      self.assertEqual(corrupt, state.read_text(encoding="utf-8"))

  def test_show_rejects_a_history_transition_outside_the_workflow_graph(self):
    with tempfile.TemporaryDirectory() as directory:
      state = self.initialize_for_implementation(Path(directory))
      for phase in ("implementing", "implemented"):
        transitioned = self.run_cli(state, "transition", "--to", phase)
        self.assertEqual(0, transitioned.returncode, transitioned.stderr)
      ledger = json.loads(state.read_text(encoding="utf-8"))
      ledger["history"][-1]["to"] = "committed"
      ledger["phase"] = "committed"
      corrupt = json.dumps(ledger, indent=2, sort_keys=True) + "\n"
      state.write_text(corrupt, encoding="utf-8")

      result = self.run_cli(state, "show")

      self.assertEqual(2, result.returncode)
      self.assertIn("corrupt ledger", result.stderr.lower())
      self.assertNotIn("traceback", result.stderr.lower())
      self.assertEqual(corrupt, state.read_text(encoding="utf-8"))

  def test_show_accepts_a_valid_corrective_history_loop(self):
    with tempfile.TemporaryDirectory() as directory:
      state = self.initialize_legacy(Path(directory))
      for phase in (
        "implementing",
        "implemented",
        "committed",
        "initial-validating",
        "implementing",
      ):
        transitioned = self.run_cli(state, "transition", "--to", phase)
        self.assertEqual(0, transitioned.returncode, transitioned.stderr)

      result = self.run_cli(state, "show")

      self.assertEqual(0, result.returncode, result.stderr)
      ledger = json.loads(result.stdout)
      self.assertEqual("implementing", ledger["phase"])
      self.assertEqual("initial-validating", ledger["history"][-1]["from"])
      self.assertEqual("implementing", ledger["history"][-1]["to"])


if __name__ == "__main__":
  unittest.main()
