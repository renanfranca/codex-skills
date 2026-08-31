import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest


SCRIPT = Path(__file__).parents[1] / "workflow_state.py"


class WorkflowStateCliTest(unittest.TestCase):
  def run_cli(self, state, *args):
    return subprocess.run(
      [sys.executable, str(SCRIPT), "--state", str(state), *args],
      capture_output=True,
      text=True,
      check=False,
    )

  def initialize(self, root, slug="demo"):
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
    )
    self.assertEqual(0, result.returncode, result.stderr)
    return state

  def prepare_pull_request_prerequisites(
    self,
    root,
    *,
    record_habit=True,
    record_baseline=True,
  ):
    state = self.initialize(root)
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
      )

      self.assertEqual(0, result.returncode, result.stderr)
      ledger = json.loads(state.read_text(encoding="utf-8"))
      self.assertEqual("demo", ledger["slug"])
      self.assertEqual(str(plan.resolve()), ledger["plan_path"])
      self.assertEqual(str(root.resolve()), ledger["repository"])
      self.assertEqual("codex/demo", ledger["branch"])
      self.assertEqual("main", ledger["base"])
      self.assertEqual("initialized", ledger["phase"])
      self.assertEqual({}, ledger["chats"])
      self.assertEqual([], ledger["commits"])
      self.assertEqual({}, ledger["gates"])
      self.assertIsNone(ledger["habit"])
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

  def test_register_chat_records_the_required_specialist_identity(self):
    with tempfile.TemporaryDirectory() as directory:
      root = Path(directory)
      state = self.initialize(root)

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

  def test_checkout_lease_rejects_a_second_owner(self):
    with tempfile.TemporaryDirectory() as directory:
      state = self.initialize(Path(directory))
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
      state = self.initialize(root)
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
      state = self.initialize(Path(directory))
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
      state = self.initialize(Path(directory))

      result = self.run_cli(state, "transition", "--to", "structural-review")

      self.assertEqual(2, result.returncode)
      self.assertIn("invalid transition", result.stderr.lower())
      ledger = json.loads(state.read_text(encoding="utf-8"))
      self.assertEqual("initialized", ledger["phase"])
      self.assertEqual(1, len(ledger["history"]))

  def test_repeating_the_current_transition_is_idempotent(self):
    with tempfile.TemporaryDirectory() as directory:
      state = self.initialize(Path(directory))
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

  def test_record_commit_is_idempotent_by_commit_sha(self):
    with tempfile.TemporaryDirectory() as directory:
      state = self.initialize(Path(directory))
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
      state = self.initialize(Path(directory))
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
      state = self.initialize(Path(directory))
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
      state = self.initialize(Path(directory))
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

  def test_record_pr_rejects_creation_before_the_final_gate(self):
    with tempfile.TemporaryDirectory() as directory:
      state = self.initialize(Path(directory))

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

  def test_cleanup_preserves_files_without_confirmed_merged_status(self):
    with tempfile.TemporaryDirectory() as directory:
      root = Path(directory)
      state = self.initialize(root)
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

  def test_failed_atomic_write_preserves_the_previous_ledger(self):
    with tempfile.TemporaryDirectory() as directory:
      root = Path(directory)
      state = self.initialize(root)
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
      state = self.initialize(Path(directory))
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
      state = self.initialize(root)
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
      state = self.initialize(Path(directory))
      ledger = json.loads(state.read_text(encoding="utf-8"))
      ledger["commits"] = [{}]
      corrupt = json.dumps(ledger, indent=2, sort_keys=True) + "\n"
      state.write_text(corrupt, encoding="utf-8")

      result = self.run_cli(state, "show")

      self.assertEqual(2, result.returncode)
      self.assertIn("corrupt ledger", result.stderr.lower())
      self.assertNotIn("traceback", result.stderr.lower())
      self.assertEqual(corrupt, state.read_text(encoding="utf-8"))

  def test_show_rejects_a_phase_that_disagrees_with_history(self):
    with tempfile.TemporaryDirectory() as directory:
      state = self.initialize(Path(directory))
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
      state = self.initialize(Path(directory))
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
      state = self.initialize(Path(directory))
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
      state = self.initialize(Path(directory))
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
