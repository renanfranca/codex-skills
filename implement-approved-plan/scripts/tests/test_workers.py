import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import test_workflow_state as legacy

BASE_SHA = legacy.BASE_SHA


DEFAULT_WORKERS = {
  "implementation": {
    "roles": ["coordinator", "implementer"], "model": "gpt-6-sol", "effort": "medium",
  },
  "quality": {
    "roles": ["committer", "validator", "mutation-analyst", "habit-curator"],
    "model": "gpt-6-luna", "effort": "high",
  },
  "structural-review": {
    "roles": ["structural-reviewer"], "model": "gpt-6-sol", "effort": "medium",
  },
}


def separate_workers():
  return {
    role: {"roles": [role], "model": worker["model"], "effort": worker["effort"]}
    for worker in DEFAULT_WORKERS.values() for role in worker["roles"]
  }


class WorkerCliTest(unittest.TestCase):
  run_cli = legacy.WorkflowStateCliTest.run_cli
  validation_plan = legacy.WorkflowStateCliTest.validation_plan

  def init_args(self, root, workers=None, active=()):
    root.mkdir(parents=True, exist_ok=True)
    plan = root / "demo.md"
    plan.write_text("# Approved plan\n", encoding="utf-8")
    args = [
      "init", "--slug", "demo", "--plan", str(plan), "--repo", str(root),
      "--branch", "codex/demo", "--base", "main", "--base-sha", BASE_SHA,
      "--validation-plan", str(self.validation_plan(root, active=active)),
    ]
    if workers is not None:
      path = root / "workers.json"
      path.write_text(json.dumps(workers), encoding="utf-8")
      args.extend(["--worker-plan", str(path)])
    return args

  def initialize(self, root, workers=None, active=()):
    state = root / "demo.workflow.json"
    self.ok(state, *self.init_args(root, workers, active))
    return state

  def ok(self, state, *args):
    result = self.run_cli(state, *args)
    self.assertEqual(0, result.returncode, result.stderr)
    return json.loads(result.stdout)

  def reject(self, state, *args):
    before = state.read_bytes() if state.exists() else None
    result = self.run_cli(state, *args)
    self.assertEqual(2, result.returncode, result.stderr)
    self.assertEqual(before, state.read_bytes() if state.exists() else None)
    return result.stderr

  def register(self, state, worker_id, settings, thread=None):
    return self.ok(
      state, "register-worker", "--worker", worker_id,
      "--thread-id", thread or f"{worker_id}-thread",
      "--model", settings["model"], "--effort", settings["effort"],
    )

  def test_default_and_arbitrary_partitions_are_persistent_and_idempotent(self):
    split = copy.deepcopy(DEFAULT_WORKERS)
    split["quality"]["roles"].remove("mutation-analyst")
    split["mutation"] = {"roles": ["mutation-analyst"], "model": "gpt-6-luna", "effort": "high"}
    single = {"all-roles": {
      "roles": list(separate_workers()), "model": "gpt-6-sol", "effort": "medium",
    }}
    for workers in (None, separate_workers(), split, single):
      with self.subTest(workers=workers), tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        state = self.initialize(root, workers)
        ledger = self.ok(state, "show")
        self.assertEqual(6, ledger["schema_version"])
        self.assertEqual(workers or DEFAULT_WORKERS, ledger["worker_selection"])
        self.assertEqual({}, ledger["workers"])
        self.assertNotIn("chats", ledger)
        self.assertNotIn("model_selection", ledger)
        before = state.read_bytes()
        self.ok(state, *self.init_args(root, workers))
        self.assertEqual(before, state.read_bytes())
        self.ok(state, *self.init_args(root))
        self.assertEqual(before, state.read_bytes())
        for worker_id, settings in (workers or DEFAULT_WORKERS).items():
          self.register(state, worker_id, settings)
          before = state.read_bytes()
          self.register(state, worker_id, settings)
          self.assertEqual(before, state.read_bytes())
        self.ok(state, "transition", "--to", "implementing")
        self.reject(state, *self.init_args(root, separate_workers() if workers != separate_workers() else single))
        changed = copy.deepcopy(workers or DEFAULT_WORKERS)
        next(iter(changed.values()))["effort"] = "ultra"
        self.reject(state, *self.init_args(root, changed))

  def test_invalid_partitions_are_rejected_before_state_creation(self):
    invalid = [None, [], {}, {"Bad_ID": DEFAULT_WORKERS["implementation"]}]
    for edit in ("missing", "duplicate", "unknown", "empty", "model", "effort", "extra", "roles-type"):
      workers = copy.deepcopy(DEFAULT_WORKERS)
      if edit == "missing":
        workers["quality"]["roles"].remove("validator")
      elif edit == "duplicate":
        workers["quality"]["roles"].append("implementer")
      elif edit == "unknown":
        workers["quality"]["roles"].append("invented")
      elif edit == "empty":
        workers["unused"] = {"roles": [], "model": "model", "effort": "medium"}
      elif edit == "roles-type":
        workers["quality"]["roles"] = [None]
      elif edit == "extra":
        workers["quality"]["thread_id"] = "premature"
      else:
        workers["quality"][edit] = " " if edit == "model" else "invalid"
      invalid.append(workers)
    for workers in invalid:
      with self.subTest(workers=workers), tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        args = self.init_args(root, {})
        (root / "workers.json").write_text(json.dumps(workers), encoding="utf-8")
        self.reject(root / "demo.workflow.json", *args)

  def test_registration_rejects_unknown_conflicting_or_duplicate_identities(self):
    with tempfile.TemporaryDirectory() as directory:
      state = self.initialize(Path(directory))
      for worker, thread, model, effort in (
        ("unknown", "thread", "gpt-6-sol", "medium"),
        ("implementation", "", "gpt-6-sol", "medium"),
        ("implementation", "thread", "other", "medium"),
        ("implementation", "thread", "gpt-6-sol", "high"),
      ):
        self.reject(state, "register-worker", "--worker", worker, "--thread-id", thread,
                    "--model", model, "--effort", effort)
      self.register(state, "implementation", DEFAULT_WORKERS["implementation"], "shared")
      self.reject(state, "register-worker", "--worker", "quality", "--thread-id", "shared",
                  "--model", "gpt-6-luna", "--effort", "high")
      self.reject(state, "register-worker", "--worker", "implementation", "--thread-id", "different",
                  "--model", "gpt-6-sol", "--effort", "medium")
      self.assertIn("register-worker", self.reject(
        state, "register-chat", "--role", "implementer", "--thread-id", "thread",
        "--model", "gpt-6-sol", "--effort", "medium",
      ))
      self.assertIn("--worker-plan", self.reject(
        state, *self.init_args(Path(directory)), "--model", "implementer=gpt-6-sol:high",
      ))

  def test_leases_require_registration_and_switch_roles_even_in_one_worker(self):
    with tempfile.TemporaryDirectory() as directory:
      state = self.initialize(Path(directory))
      self.reject(state, "acquire", "--owner", "coordinator")
      self.register(state, "implementation", DEFAULT_WORKERS["implementation"])
      lease = self.ok(state, "acquire", "--owner", "coordinator")
      self.assertEqual("implementation", lease["worker"])
      self.reject(state, "acquire", "--owner", "implementer")
      self.reject(state, "release", "--owner", "implementer")
      self.ok(state, "release", "--owner", "coordinator")
      self.ok(state, "acquire", "--owner", "implementer")
      self.reject(state, "record-commit", "--sha", "b" * 40, "--kind", "implementation",
                  "--subject", "feat: behavior")
      self.reject(state, "record-gate", "--name", "initial-verify", "--status", "passed", "--details", "ok")

  def test_startup_requires_coordinator_and_mandatory_workers(self):
    workers = separate_workers()
    with tempfile.TemporaryDirectory() as directory:
      state = self.initialize(Path(directory), workers)
      for worker_id in ("implementer", "committer", "validator", "structural-reviewer"):
        self.register(state, worker_id, workers[worker_id])
      self.assertIn("coordinator", self.reject(state, "transition", "--to", "implementing"))
      self.register(state, "coordinator", workers["coordinator"])
      self.ok(state, "transition", "--to", "implementing")
      self.reject(state, "acquire", "--owner", "mutation-analyst")
      self.reject(state, "acquire", "--owner", "habit-curator")

  def test_optional_activation_reuses_existing_worker_or_requires_new_registration(self):
    for workers in (DEFAULT_WORKERS, separate_workers()):
      with self.subTest(workers=workers), tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        state = self.initialize(root, workers)
        for worker_id, settings in workers.items():
          if set(settings["roles"]) <= {"mutation-analyst", "habit-curator"}:
            continue
          self.register(state, worker_id, settings)
        self.ok(state, "transition", "--to", "implementing")
        self.ok(state, "acquire", "--owner", "coordinator")
        path = self.validation_plan(root, active=("mutation", "habit"))
        self.ok(state, "update-validation-plan", "--file", str(path), "--note", "User confirmed checks")
        self.ok(state, "release", "--owner", "coordinator")
        if workers != DEFAULT_WORKERS:
          self.reject(state, "transition", "--to", "implemented")
          for role in ("mutation-analyst", "habit-curator"):
            self.register(state, role, workers[role])
        self.ok(state, "transition", "--to", "implemented")
        self.assertEqual(workers, self.ok(state, "show")["worker_selection"])
        registered = self.ok(state, "show")["workers"]
        self.ok(state, "transition", "--to", "habit-checking")
        self.ok(state, "transition", "--to", "implementing", "--note", "Coordinator routes confirmed exclusions")
        self.ok(state, "acquire", "--owner", "coordinator")
        path = self.validation_plan(root, active=())
        self.ok(state, "update-validation-plan", "--file", str(path), "--note", "User confirmed exclusions")
        self.ok(state, "release", "--owner", "coordinator")
        self.reject(state, "acquire", "--owner", "mutation-analyst")
        self.assertEqual(registered, self.ok(state, "show")["workers"])
        self.ok(state, "acquire", "--owner", "coordinator")
        path = self.validation_plan(root, active=("mutation", "habit"))
        self.ok(state, "update-validation-plan", "--file", str(path), "--note", "User confirmed reactivation")
        self.ok(state, "release", "--owner", "coordinator")
        self.ok(state, "acquire", "--owner", "mutation-analyst")
        self.ok(state, "release", "--owner", "mutation-analyst")
        self.assertEqual(registered, self.ok(state, "show")["workers"])

  def test_full_workflows_preserve_gates_delivery_ci_and_cleanup(self):
    split = copy.deepcopy(DEFAULT_WORKERS)
    split["quality"]["roles"].remove("mutation-analyst")
    split["mutation"] = {"roles": ["mutation-analyst"], "model": "gpt-6-luna", "effort": "high"}
    single = {"all-roles": {"roles": list(separate_workers()), "model": "gpt-6-sol", "effort": "medium"}}
    for workers in (DEFAULT_WORKERS, separate_workers(), split, single):
      for active in ((), ("verify", "sonar", "mutation", "habit")):
        with self.subTest(workers=workers, active=active), tempfile.TemporaryDirectory() as directory:
          root = Path(directory)
          state = self.initialize(root, workers, active)
          for worker_id, settings in workers.items():
            if not active and set(settings["roles"]) <= {"habit-curator", "mutation-analyst"}:
              continue
            self.register(state, worker_id, settings)
          self.ok(state, "transition", "--to", "implementing")
          self.ok(state, "transition", "--to", "implemented")
          if active:
            self.ok(state, "transition", "--to", "habit-checking")
            self.reject(state, "transition", "--to", "checkpoint-committing")
            self.ok(state, "acquire", "--owner", "habit-curator")
            self.ok(state, "record-habit", "--status", "clean", "--details", "zero findings")
            self.ok(state, "release", "--owner", "habit-curator")
          else:
            self.reject(state, "transition", "--to", "habit-checking")
          self.ok(state, "transition", "--to", "checkpoint-committing")
          self.reject(state, "transition", "--to", "initial-validating")
          self.ok(state, "acquire", "--owner", "committer")
          self.ok(state, "record-commit", "--sha", "b" * 40, "--kind", "implementation", "--subject", "feat: behavior")
          self.ok(state, "release", "--owner", "committer")
          for stage in ("initial", "final"):
            self.ok(state, "transition", "--to", f"{stage}-validating")
            destination = ("mutation-testing" if stage == "initial" else "mutation-rechecking") if active else (
              "structural-review" if stage == "initial" else "delivery-ready"
            )
            self.reject(state, "transition", "--to", destination)
            self.ok(state, "acquire", "--owner", "validator")
            self.reject(state, "record-commit", "--sha", "b" * 40, "--kind", "correction", "--subject", "fix: issue")
            self.ok(state, "record-gate", "--name", f"{stage}-verify",
                    "--status", "passed" if active else "not-applicable", "--details", "observed checks")
            if active:
              self.ok(state, "record-gate", "--name", f"{stage}-sonar", "--status", "passed", "--details", "ok")
            else:
              self.reject(state, "record-gate", "--name", f"{stage}-sonar", "--status", "passed", "--details", "absent")
            self.ok(state, "release", "--owner", "validator")
            self.ok(state, "transition", "--to", destination)
            if active:
              artifact_dir = root / ".agent" / "tmp"
              artifact_dir.mkdir(parents=True, exist_ok=True)
              log = artifact_dir / f"{stage}.log"
              log.write_text("mutation evidence\n", encoding="utf-8")
              self.reject(state, "transition", "--to", "structural-review" if stage == "initial" else "delivery-ready")
              self.ok(state, "acquire", "--owner", "mutation-analyst")
              args = [
                "record-mutation", "--runner", "pit", "--analyzed-sha", ("b" if stage == "initial" else "d") * 40,
                "--fingerprint", "c" * 64, "--target-class", "example.Service*", "--log", str(log),
                "--details", "observed mutation evidence",
              ]
              if stage == "initial":
                report = artifact_dir / "report.xml"
                report.write_text("<report/>\n", encoding="utf-8")
                args.extend(["--result", "passed", "--generated", "1", "--killed", "1", "--report", str(report)])
              else:
                args.extend(["--result", "reused", "--reused-from-sha", "b" * 40, "--reused-from-fingerprint", "c" * 64])
              self.ok(state, *args)
              self.ok(state, "release", "--owner", "mutation-analyst")
              self.ok(state, "transition", "--to", "structural-review" if stage == "initial" else "delivery-ready")
            if stage == "initial":
              self.ok(state, "acquire", "--owner", "structural-reviewer")
              self.ok(state, "release", "--owner", "structural-reviewer")
              if active:
                self.ok(state, "transition", "--to", "habit-rechecking")
                self.ok(state, "acquire", "--owner", "habit-curator")
                self.ok(state, "record-habit", "--status", "clean", "--details", "fresh zero findings")
                self.ok(state, "release", "--owner", "habit-curator")
                self.ok(state, "transition", "--to", "final-committing")
                self.ok(state, "acquire", "--owner", "committer")
                self.ok(state, "record-commit", "--sha", "d" * 40, "--kind", "structural-refactor", "--subject", "refactor: structure")
                self.ok(state, "release", "--owner", "committer")
          self.ok(state, "acquire", "--owner", "coordinator")
          self.ok(state, "record-pr", "--repo", "example/demo", "--number", "12",
                  "--url", "https://example.test/pull/12", "--status", "OPEN")
          self.ok(state, "release", "--owner", "coordinator")
          self.ok(state, "transition", "--to", "pr-open")
          self.ok(state, "transition", "--to", "ci-monitoring")
          self.reject(state, "transition", "--to", "ready-for-merge")
          self.ok(state, "record-ci", "--status", "passed", "--run-id", "1",
                  "--url", "https://example.test/ci/1", "--details", "observed CI pass")
          self.ok(state, "transition", "--to", "ready-for-merge")
          self.reject(state, "cleanup", "--github-status", "CLOSED", "--repo", "example/demo", "--number", "12")
          self.reject(state, "cleanup", "--github-status", "MERGED", "--repo", "other/demo", "--number", "12")
          self.ok(state, "cleanup", "--github-status", "MERGED", "--repo", "example/demo", "--number", "12")
          self.assertFalse(state.exists())
          self.assertFalse((root / "demo.md").exists())
          self.assertTrue((root / "workers.json").exists())
          self.assertTrue((root / "validation.json").exists())
          if active:
            self.assertTrue((root / ".agent" / "tmp" / "report.xml").exists())

  def test_concurrent_roles_in_same_worker_cannot_both_acquire(self):
    with tempfile.TemporaryDirectory() as directory:
      state = self.initialize(Path(directory))
      self.register(state, "quality", DEFAULT_WORKERS["quality"])
      processes = [subprocess.Popen(
        [sys.executable, str(legacy.SCRIPT), "--state", str(state), "acquire", "--owner", role],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
      ) for role in ("committer", "validator")]
      outputs = [process.communicate(timeout=10) for process in processes]
      self.assertEqual([0, 2], sorted(process.returncode for process in processes), outputs)
      lease = self.ok(state, "show")["checkout_lease"]
      self.assertEqual("quality", lease["worker"])
      self.ok(state, "release", "--owner", lease["owner"])

  def test_all_legacy_schemas_read_without_rewriting_or_accepting_workers(self):
    fixtures = legacy.WorkflowStateCliTest()
    with tempfile.TemporaryDirectory() as directory:
      root = Path(directory)
      for version in range(1, 6):
        fixture_root = root / str(version)
        fixture_root.mkdir()
        if version == 1:
          state = fixtures.initialize_legacy(fixture_root)
        elif version == 2:
          state = fixtures.initialize_v2(fixture_root)
        elif version == 3:
          state = fixtures.initialize_v3(fixture_root)
        else:
          state = fixtures.initialize_v5(fixture_root)
          if version == 4:
            ledger = json.loads(state.read_text(encoding="utf-8"))
            ledger["schema_version"] = 4
            del ledger["validation_plan"]
            del ledger["validation_history"]
            state.write_text(json.dumps(ledger), encoding="utf-8")
        before = state.read_bytes()
        shown = self.ok(state, "show")
        self.assertEqual(version, shown["schema_version"])
        self.assertEqual(before, state.read_bytes())
        self.reject(state, "register-worker", "--worker", "implementation", "--thread-id", "thread",
                    "--model", "gpt-6-sol", "--effort", "medium")
        self.assertNotIn("worker_selection", shown)

  def test_ci_inventory_and_one_retry_are_preserved_in_v6(self):
    with tempfile.TemporaryDirectory() as directory:
      root = Path(directory)
      state = self.initialize(root)
      for worker_id, settings in DEFAULT_WORKERS.items():
        self.register(state, worker_id, settings)
      validation = self.validation_plan(root, active=())
      inventory = json.loads(validation.read_text(encoding="utf-8"))
      for check_id in ("ci-tests", "ci-analysis"):
        inventory["checks"].append({
          "id": check_id, "kind": "ci", "status": "selected", "execution": "ci", "command": "",
          "source": "CI configuration", "owner": "coordinator", "reason": "",
        })
      validation.write_text(json.dumps(inventory), encoding="utf-8")
      self.ok(state, "acquire", "--owner", "coordinator")
      self.ok(state, "update-validation-plan", "--file", str(validation), "--note", "User confirmed CI checks")
      self.ok(state, "release", "--owner", "coordinator")
      for phase in ("implementing", "implemented", "checkpoint-committing"):
        self.ok(state, "transition", "--to", phase)
      self.ok(state, "acquire", "--owner", "committer")
      self.ok(state, "record-commit", "--sha", "b" * 40, "--kind", "implementation", "--subject", "feat: behavior")
      self.ok(state, "release", "--owner", "committer")
      for phase, stage in (("initial-validating", "initial"), ("structural-review", None), ("final-validating", "final")):
        self.ok(state, "transition", "--to", phase)
        if stage:
          self.ok(state, "acquire", "--owner", "validator")
          self.ok(state, "record-gate", "--name", f"{stage}-verify", "--status", "not-applicable", "--details", "CI only")
          self.ok(state, "release", "--owner", "validator")
      self.ok(state, "transition", "--to", "delivery-ready")
      self.ok(state, "acquire", "--owner", "coordinator")
      self.ok(state, "record-pr", "--repo", "example/demo", "--number", "12",
              "--url", "https://example.test/pull/12", "--status", "OPEN")
      self.ok(state, "release", "--owner", "coordinator")
      self.ok(state, "transition", "--to", "pr-open")
      self.ok(state, "transition", "--to", "ci-monitoring")
      arguments = ["record-ci", "--run-id", "1", "--url", "https://example.test/ci/1", "--details", "CI evidence"]
      self.reject(state, *arguments, "--status", "passed", "--check-id", "unknown")
      self.ok(state, *arguments, "--status", "transient-failed", "--check-id", "ci-tests")
      self.ok(state, *arguments, "--status", "retrying", "--check-id", "ci-tests")
      self.ok(state, *arguments, "--status", "transient-failed", "--check-id", "ci-analysis")
      self.reject(state, *arguments, "--status", "retrying", "--check-id", "ci-analysis")
      self.ok(state, *arguments, "--status", "passed")
      self.reject(state, "transition", "--to", "ready-for-merge")
      self.ok(state, *arguments, "--status", "passed", "--check-id", "ci-tests")
      self.reject(state, "transition", "--to", "ready-for-merge")
      self.ok(state, *arguments, "--status", "passed", "--check-id", "ci-analysis")
      self.ok(state, "transition", "--to", "ready-for-merge")


  def test_corrupt_workers_and_lease_are_rejected_without_rewriting(self):
    with tempfile.TemporaryDirectory() as directory:
      state = self.initialize(Path(directory))
      for worker_id, settings in DEFAULT_WORKERS.items():
        self.register(state, worker_id, settings)
      self.ok(state, "acquire", "--owner", "coordinator")
      original = self.ok(state, "show")
      for corruption in ("selection", "pair", "identity", "lease", "missing-worker", "legacy"):
        ledger = copy.deepcopy(original)
        if corruption == "selection":
          ledger["worker_selection"]["quality"]["roles"].remove("validator")
        elif corruption == "pair":
          ledger["workers"]["quality"]["effort"] = "medium"
        elif corruption == "identity":
          ledger["workers"]["quality"]["thread_id"] = ledger["workers"]["implementation"]["thread_id"]
        elif corruption == "lease":
          ledger["checkout_lease"]["worker"] = "quality"
        elif corruption == "missing-worker":
          del ledger["workers"]["implementation"]
        else:
          ledger["chats"] = {}
        state.write_text(json.dumps(ledger), encoding="utf-8")
        self.reject(state, "show")


if __name__ == "__main__":
  unittest.main()
