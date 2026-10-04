import json
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "workflow_state.py"
ROLES = ["coordinator", "implementer", "committer", "validator", "mutation-analyst",
         "habit-curator", "structural-reviewer"]
MESSAGE = "fix: correct workflow\n\n- Motivation: Require reliable commits.\n- Avoided: Advancing after failure.\n- Improvement: Preserve evidence.\n"


class CommitExecutionTest(unittest.TestCase):
  def setUp(self):
    self.directory = tempfile.TemporaryDirectory()
    self.addCleanup(self.directory.cleanup)
    self.root = Path(self.directory.name)
    self.git("init", "-q", "-b", "workflow-fixture")
    self.git("config", "user.name", "Fixture")
    self.git("config", "user.email", "fixture@example.test")
    self.git("commit", "--allow-empty", "-qm", "fixture")
    (self.root / ".git/info/exclude").write_text("/.agent/tmp/\n")
    self.tmp = self.root / ".agent/tmp"
    self.tmp.mkdir(parents=True)
    self.state = self.tmp / "demo.workflow.json"
    self.message = self.tmp / "candidate.txt"
    self.message.write_text(MESSAGE)
    plan = self.tmp / "plan.md"
    plan.write_text("# Approved plan\n")
    workers = self.tmp / "workers.json"
    workers.write_text(json.dumps({"primary": {"roles": ROLES, "model": "gpt-6-sol", "effort": "medium"}}))
    inventory = self.tmp / "validation.json"
    inventory.write_text(json.dumps({"checks": [
      {"id": kind, "kind": kind, "status": "skipped", "execution": "none", "command": "",
       "source": "fixture", "owner": owner, "reason": "not configured"}
      for kind, owner in (("verify", "validator"), ("sonar", "validator"),
                          ("mutation", "mutation-analyst"), ("habit", "habit-curator"))
    ]}))
    self.ok("init", "--slug", "demo", "--plan", str(plan), "--repo", str(self.root),
            "--branch", "workflow-fixture", "--base", "HEAD", "--base-sha", self.git("rev-parse", "HEAD"),
            "--validation-plan", str(inventory), "--worker-plan", str(workers))
    self.ok("register-worker", "--worker", "primary", "--thread-id", "invoking-chat",
            "--model", "gpt-6-sol", "--effort", "medium")
    self.ok("transition", "--to", "implementing")
    self.ok("transition", "--to", "implemented")
    self.ok("transition", "--to", "checkpoint-committing")
    self.ok("acquire", "--owner", "committer")
    (self.root / "change.txt").write_text("assigned delta\n")
    self.git("add", "change.txt")

  def git(self, *args):
    return subprocess.check_output(["git", "-C", str(self.root), *args], text=True, stderr=subprocess.PIPE).strip()

  def cli(self, *args, fail_registration=False):
    command = [sys.executable, str(SCRIPT)]
    if fail_registration:
      wrapper = (
        "import importlib.util, sys\n"
        "spec = importlib.util.spec_from_file_location('workflow', sys.argv.pop(1))\n"
        "workflow = importlib.util.module_from_spec(spec); spec.loader.exec_module(workflow)\n"
        "original = workflow.write_atomic\n"
        "def fail(path, value):\n"
        "  if path.name == 'demo.workflow.json' and value.get('commits'):\n"
        "    raise workflow.WorkflowError('fixture ledger write failure')\n"
        "  original(path, value)\n"
        "workflow.write_atomic = fail\n"
        "sys.exit(workflow.main())\n"
      )
      command = [sys.executable, "-c", wrapper, str(SCRIPT)]
    return subprocess.run([*command, "--state", str(self.state), *args],
                          capture_output=True, text=True, timeout=15)

  def ok(self, *args):
    result = self.cli(*args)
    self.assertEqual(0, result.returncode, result.stderr)
    return json.loads(result.stdout)

  def commit(self, *extra, fail_registration=False):
    return self.cli("commit-staged", "--message-file", str(self.message),
                    "--kind", "implementation", "--attempt-id", "checkpoint-1", *extra,
                    fail_registration=fail_registration)

  def test_staged_commit_is_proven_and_recorded_once_with_hooks_and_attempt_evidence(self):
    hook = self.root / ".git/hooks/pre-commit"
    hook.write_text("#!/bin/sh\nprintf 'hook ran\\n' >> .agent/tmp/hook-calls\n")
    hook.chmod(0o755)
    previous = self.git("rev-parse", "HEAD")
    staged = self.git("write-tree")

    result = self.commit()

    self.assertEqual(0, result.returncode, result.stderr)
    output = json.loads(result.stdout)
    sha = self.git("rev-parse", "HEAD")
    self.assertNotEqual(previous, sha)
    self.assertEqual(previous, self.git("rev-parse", "HEAD^"))
    self.assertEqual(staged, self.git("rev-parse", "HEAD^{tree}"))
    self.assertEqual(MESSAGE, self.git("show", "-s", "--format=%B", "HEAD") + "\n")
    self.assertEqual("", self.git("diff", "--cached", "--name-only"))
    ledger = self.ok("show")
    self.assertEqual([sha], [c["sha"] for c in ledger["commits"]])
    self.assertEqual("checkpoint-committing", ledger["phase"])
    journal = json.loads(Path(output["journal"]).read_text())
    self.assertEqual(previous, journal["previous_head"])
    self.assertEqual(staged, journal["staged_tree"])
    self.assertEqual(MESSAGE, journal["message"])
    self.assertEqual("recorded", journal["status"])
    self.assertTrue(Path(output["log"]).is_file())
    before = self.state.read_bytes()

    repeated = self.commit()

    self.assertEqual(0, repeated.returncode, repeated.stderr)
    self.assertEqual(before, self.state.read_bytes())
    self.assertEqual(sha, self.git("rev-parse", "HEAD"))
    self.assertEqual("hook ran\n", (self.tmp / "hook-calls").read_text())
    self.ok("release", "--owner", "committer")
    self.ok("transition", "--to", "initial-validating")

  def test_message_limits_block_commit_before_hooks_and_preserve_the_attempt(self):
    hook = self.root / ".git/hooks/pre-commit"
    hook.write_text("#!/bin/sh\ntouch .agent/tmp/hook-ran\n")
    hook.chmod(0o755)
    previous = self.git("rev-parse", "HEAD")
    staged = self.git("write-tree")
    before = self.state.read_bytes()
    for part, message in (
      ("header", "h" * 101 + "\n\nBody.\n"),
      ("body", "fix: subject\n\n" + "b" * 101 + "\n"),
      ("footer", "fix: subject\n\nBody.\n\nRefs: " + "f" * 95 + "\n"),
    ):
      with self.subTest(part=part):
        self.message.write_text(message)

        result = self.commit("--attempt-id", part)

        self.assertEqual(2, result.returncode, result.stderr)
        self.assertIn(part, result.stderr)
        self.assertEqual(previous, self.git("rev-parse", "HEAD"))
        self.assertEqual(staged, self.git("write-tree"))
        self.assertEqual(before, self.state.read_bytes())
        self.assertFalse((self.tmp / "hook-ran").exists())
        journal = next((self.tmp / "commits").glob(f"*/{part}/journal.json"))
        self.assertEqual("failed", json.loads(journal.read_text())["status"])
        self.assertTrue(journal.with_name("command.log").is_file())
        self.assertEqual(2, self.cli("transition", "--to", "initial-validating").returncode)

  def test_native_message_validation_failure_prevents_git_commit(self):
    validator = self.tmp / "lint.py"
    validator.write_text("from pathlib import Path\nimport sys\n"
                         "Path('.agent/tmp/validated-message').write_bytes(Path(sys.argv[1]).read_bytes())\n"
                         "print('native message rejected')\nraise SystemExit(7)\n")
    command = f"{shlex.quote(sys.executable)} {shlex.quote(str(validator))} {{message_file}}"
    previous = self.git("rev-parse", "HEAD")
    staged = self.git("write-tree")
    before = self.state.read_bytes()

    result = self.commit("--validate-command", command)

    self.assertEqual(2, result.returncode, result.stderr)
    self.assertEqual(previous, self.git("rev-parse", "HEAD"))
    self.assertEqual(staged, self.git("write-tree"))
    self.assertEqual(before, self.state.read_bytes())
    self.assertEqual(MESSAGE, (self.tmp / "validated-message").read_text())
    journal_path = next((self.tmp / "commits").glob("*/*/journal.json"))
    journal = json.loads(journal_path.read_text())
    self.assertEqual(7, journal["validation_exit_code"])
    self.assertEqual(0, journal["commit_invocations"])
    self.assertIn("native message rejected", journal_path.with_name("command.log").read_text())
    self.assertEqual(2, self.cli("transition", "--to", "initial-validating").returncode)

  def test_hook_failure_preserves_staging_and_blocks_registration_and_advance(self):
    hook = self.root / ".git/hooks/pre-commit"
    hook.write_text("#!/bin/sh\nprintf 'hook rejection\\n'\nprintf 'one\\n' >> .agent/tmp/hook-calls\nexit 3\n")
    hook.chmod(0o755)
    previous = self.git("rev-parse", "HEAD")
    staged = self.git("write-tree")
    before = self.state.read_bytes()

    result = self.commit()

    self.assertEqual(2, result.returncode, result.stderr)
    self.assertIn("git commit failed", result.stderr)
    self.assertEqual(previous, self.git("rev-parse", "HEAD"))
    self.assertEqual(staged, self.git("write-tree"))
    self.assertEqual(before, self.state.read_bytes())
    journal_path = next((self.tmp / "commits").glob("*/*/journal.json"))
    journal = json.loads(journal_path.read_text())
    self.assertNotEqual(0, journal["exit_code"])
    self.assertEqual("failed", journal["status"])
    self.assertIn("hook rejection", journal_path.with_name("command.log").read_text())
    self.assertEqual(2, self.cli("transition", "--to", "initial-validating").returncode)
    self.assertEqual(2, self.commit().returncode)
    self.assertEqual("one\n", (self.tmp / "hook-calls").read_text())

  def test_registration_failure_recovers_the_existing_commit_without_another_invocation(self):
    hook = self.root / ".git/hooks/pre-commit"
    hook.write_text("#!/bin/sh\nprintf 'one\\n' >> .agent/tmp/hook-calls\n")
    hook.chmod(0o755)
    previous = self.git("rev-parse", "HEAD")
    before = self.state.read_bytes()

    result = self.commit(fail_registration=True)

    self.assertEqual(2, result.returncode, result.stderr)
    self.assertIn("fixture ledger write failure", result.stderr)
    sha = self.git("rev-parse", "HEAD")
    self.assertNotEqual(previous, sha)
    self.assertEqual(before, self.state.read_bytes())
    self.assertEqual(2, self.cli("transition", "--to", "initial-validating").returncode)
    journal_path = next((self.tmp / "commits").glob("*/*/journal.json"))
    self.assertEqual("committed", json.loads(journal_path.read_text())["status"])
    log = journal_path.with_name("command.log").read_bytes()

    recovered = self.commit()

    self.assertEqual(0, recovered.returncode, recovered.stderr)
    self.assertEqual(sha, json.loads(recovered.stdout)["commit"]["sha"])
    self.assertEqual([sha], [c["sha"] for c in self.ok("show")["commits"]])
    self.assertEqual(sha, self.git("rev-parse", "HEAD"))
    self.assertEqual(log, journal_path.with_name("command.log").read_bytes())
    self.assertEqual("one\n", (self.tmp / "hook-calls").read_text())

  def test_recovery_blocks_every_divergence_without_repeating_the_commit(self):
    for divergence in ("head", "message", "staging", "working-tree", "branch", "attempt-settings"):
      with self.subTest(divergence=divergence):
        # Each scenario starts with its own unrecorded commit.
        scenario = CommitExecutionTest()
        scenario.setUp()
        self.addCleanup(scenario.doCleanups)
        result = scenario.commit(fail_registration=True)
        self.assertEqual(2, result.returncode, result.stderr)
        sha = scenario.git("rev-parse", "HEAD")
        if divergence == "head":
          scenario.git("commit", "--allow-empty", "-qm", "later commit")
        elif divergence == "message":
          scenario.message.write_text(MESSAGE.replace("reliable", "different"))
        elif divergence in ("staging", "working-tree"):
          (scenario.root / "change.txt").write_text("different delta\n")
          if divergence == "staging":
            scenario.git("add", "change.txt")
        elif divergence == "branch":
          scenario.git("switch", "-qc", "other-branch")
        head = scenario.git("rev-parse", "HEAD")
        before = scenario.state.read_bytes()
        extras = ("--body-max-length", "120") if divergence == "attempt-settings" else ()

        recovered = scenario.commit(*extras)

        self.assertEqual(2, recovered.returncode, recovered.stderr)
        self.assertEqual(head, scenario.git("rev-parse", "HEAD"))
        self.assertEqual(before, scenario.state.read_bytes())
        self.assertEqual([], scenario.ok("show")["commits"])
        self.assertEqual(sha, json.loads(next((scenario.tmp / "commits").glob("*/*/journal.json")).read_text())["sha"])

  def test_wrong_branch_lease_phase_or_empty_staging_never_invokes_commit(self):
    previous = self.git("rev-parse", "HEAD")
    self.git("switch", "-qc", "other-branch")
    before = self.state.read_bytes()
    rejected = self.commit()
    self.assertEqual(2, rejected.returncode, rejected.stderr)
    self.assertIn("branch", rejected.stderr)
    self.assertEqual(before, self.state.read_bytes())
    self.git("switch", "-q", "workflow-fixture")
    self.ok("release", "--owner", "committer")
    for owner in (None, "validator"):
      with self.subTest(owner=owner):
        if owner:
          self.ok("acquire", "--owner", owner)
        before = self.state.read_bytes()
        rejected = self.commit()
        self.assertEqual(2, rejected.returncode, rejected.stderr)
        self.assertIn("lease", rejected.stderr)
        self.assertEqual(before, self.state.read_bytes())
        if owner:
          self.ok("release", "--owner", owner)
    self.ok("acquire", "--owner", "committer")
    rejected = self.commit("--kind", "structural-refactor")
    self.assertEqual(2, rejected.returncode, rejected.stderr)
    self.assertIn("kind", rejected.stderr)
    self.message.unlink()
    rejected = self.commit()
    self.assertEqual(2, rejected.returncode, rejected.stderr)
    self.assertIn("message file", rejected.stderr)
    self.message.write_text(MESSAGE)
    self.git("restore", "--staged", "change.txt")
    rejected = self.commit()
    self.assertEqual(2, rejected.returncode, rejected.stderr)
    self.assertIn("staging", rejected.stderr)
    self.git("add", "change.txt")
    self.ok("transition", "--to", "implementing", "--note", "correct the assigned delta")
    before = self.state.read_bytes()
    rejected = self.commit()
    self.assertEqual(2, rejected.returncode, rejected.stderr)
    self.assertIn("implementing", rejected.stderr)
    self.assertEqual(before, self.state.read_bytes())
    self.assertEqual(previous, self.git("rev-parse", "HEAD"))
    self.assertEqual("change.txt", self.git("diff", "--cached", "--name-only"))

  def test_discovered_limits_and_native_validation_commit_the_same_full_message(self):
    message = "h" * 110 + "\n\n" + "á" * 111 + "\n\nRefs: " + "f" * 106 + "\n"
    self.message.write_text(message)
    validator = self.tmp / "lint.py"
    validator.write_text("from pathlib import Path\nimport os\n"
                         "Path('.agent/tmp/validated-message').write_bytes(Path(os.environ['COMMIT_MESSAGE_FILE']).read_bytes())\n"
                         "print('native validation passed')\n")

    result = self.commit("--header-max-length", "110", "--body-max-length", "111",
                         "--footer-max-length", "112", "--validate-command",
                         f"{shlex.quote(sys.executable)} {shlex.quote(str(validator))}")

    self.assertEqual(0, result.returncode, result.stderr)
    self.assertEqual(message, (self.tmp / "validated-message").read_text())
    self.assertEqual(message, self.git("show", "-s", "--format=%B", "HEAD") + "\n")
    output = json.loads(result.stdout)
    journal = json.loads(Path(output["journal"]).read_text())
    self.assertEqual(0, journal["validation_exit_code"])
    self.assertEqual(1, journal["commit_invocations"])
    self.assertIn("native validation passed", Path(output["log"]).read_text())

  def test_message_changed_by_a_hook_is_not_registered_and_preserves_the_observed_commit(self):
    hook = self.root / ".git/hooks/commit-msg"
    hook.write_text("#!/bin/sh\nprintf 'fix: hook changed message\\n\\nUnexpected body.\\n' > \"$1\"\n")
    hook.chmod(0o755)
    previous = self.git("rev-parse", "HEAD")
    before = self.state.read_bytes()

    result = self.commit()

    self.assertEqual(2, result.returncode, result.stderr)
    self.assertIn("proof diverged", result.stderr)
    self.assertNotEqual(previous, self.git("rev-parse", "HEAD"))
    self.assertEqual(before, self.state.read_bytes())
    journal_path = next((self.tmp / "commits").glob("*/*/journal.json"))
    journal = json.loads(journal_path.read_text())
    self.assertEqual(self.git("rev-parse", "HEAD"), journal["sha"])
    self.assertEqual("fix: hook changed message\n\nUnexpected body.\n", journal["effective_message"])
    self.assertEqual("failed", journal["status"])
    self.assertEqual(2, self.commit().returncode)
    self.assertEqual(2, self.cli("transition", "--to", "initial-validating").returncode)

  def test_final_commit_requires_its_phase_and_unlocks_only_after_registration(self):
    checkpoint = self.commit()
    self.assertEqual(0, checkpoint.returncode, checkpoint.stderr)
    checkpoint_sha = self.git("rev-parse", "HEAD")
    self.ok("release", "--owner", "committer")
    self.ok("transition", "--to", "initial-validating")
    self.ok("acquire", "--owner", "validator")
    self.ok("record-gate", "--name", "initial-verify", "--status", "not-applicable", "--details", "no local check")
    self.ok("release", "--owner", "validator")
    self.ok("transition", "--to", "structural-review")
    (self.root / "change.txt").write_text("reviewed delta\n")
    self.git("add", "change.txt")
    self.ok("transition", "--to", "final-committing")
    self.ok("acquire", "--owner", "committer")
    self.assertEqual(2, self.cli("transition", "--to", "final-validating").returncode)
    self.assertEqual(2, self.commit("--attempt-id", "final-1").returncode)

    result = self.commit("--attempt-id", "final-1", "--kind", "structural-refactor")

    self.assertEqual(0, result.returncode, result.stderr)
    sha = self.git("rev-parse", "HEAD")
    self.assertEqual(checkpoint_sha, self.git("rev-parse", "HEAD^"))
    commits = self.ok("show")["commits"]
    self.assertEqual([checkpoint_sha, sha], [c["sha"] for c in commits])
    self.assertEqual("final-committing", commits[-1]["phase"])
    self.ok("release", "--owner", "committer")
    self.ok("transition", "--to", "final-validating")

  def test_legacy_ledger_rejects_executor_and_retains_record_commit_interface(self):
    ledger = self.ok("show")
    settings = ledger.pop("worker_selection")["primary"]
    ledger.pop("workers")
    ledger["schema_version"] = 5
    ledger["model_selection"] = {role: {key: settings[key] for key in ("model", "effort")} for role in ROLES}
    ledger["chats"] = {role: {"thread_id": role + "-thread", **ledger["model_selection"][role]}
                       for role in ROLES if role != "coordinator"}
    ledger["checkout_lease"].pop("worker")
    self.state.write_text(json.dumps(ledger))
    before = self.state.read_bytes()
    previous = self.git("rev-parse", "HEAD")

    result = self.commit()

    self.assertEqual(2, result.returncode, result.stderr)
    self.assertIn("requires schema v6", result.stderr)
    self.assertEqual(before, self.state.read_bytes())
    self.assertEqual(previous, self.git("rev-parse", "HEAD"))
    recorded = self.ok("record-commit", "--sha", previous, "--kind", "implementation", "--subject", "legacy commit")
    self.assertEqual(previous, recorded["sha"])
    self.assertEqual(5, self.ok("show")["schema_version"])

  def test_corrupt_attempt_journals_block_recovery_without_a_new_commit(self):
    result = self.commit(fail_registration=True)
    self.assertEqual(2, result.returncode, result.stderr)
    sha = self.git("rev-parse", "HEAD")
    before = self.state.read_bytes()
    journal_path = next((self.tmp / "commits").glob("*/*/journal.json"))
    original = json.loads(journal_path.read_text())
    missing = dict(original)
    missing.pop("checkout_before")
    for corrupt in (None, [], missing):
      with self.subTest(corrupt=type(corrupt).__name__):
        journal_path.write_text(json.dumps(corrupt))

        recovered = self.commit()

        self.assertEqual(2, recovered.returncode, recovered.stderr)
        self.assertIn("journal", recovered.stderr.lower())
        self.assertEqual(sha, self.git("rev-parse", "HEAD"))
        self.assertEqual(before, self.state.read_bytes())

  def test_native_validator_cannot_change_message_bytes_before_commit(self):
    validator = self.tmp / "lint.py"
    validator.write_text("from pathlib import Path\nimport sys\n"
                         "message = Path(sys.argv[1])\n"
                         "message.write_bytes(message.read_bytes().replace(b'\\n', b'\\r\\n'))\n")
    previous = self.git("rev-parse", "HEAD")
    staged = self.git("write-tree")
    before = self.state.read_bytes()

    result = self.commit("--validate-command", f"{shlex.quote(sys.executable)} {shlex.quote(str(validator))} {{message_file}}")

    self.assertEqual(2, result.returncode, result.stderr)
    self.assertEqual(previous, self.git("rev-parse", "HEAD"))
    self.assertEqual(staged, self.git("write-tree"))
    self.assertEqual(before, self.state.read_bytes())
    journal = json.loads(next((self.tmp / "commits").glob("*/*/journal.json")).read_text())
    self.assertEqual(0, journal["commit_invocations"])

  def test_git_failure_without_a_hook_does_not_register_or_advance(self):
    self.git("config", "user.name", "")
    previous = self.git("rev-parse", "HEAD")
    staged = self.git("write-tree")
    before = self.state.read_bytes()

    result = self.commit()

    self.assertEqual(2, result.returncode, result.stderr)
    self.assertIn("git commit failed", result.stderr)
    self.assertEqual(previous, self.git("rev-parse", "HEAD"))
    self.assertEqual(staged, self.git("write-tree"))
    self.assertEqual(before, self.state.read_bytes())
    journal_path = next((self.tmp / "commits").glob("*/*/journal.json"))
    journal = json.loads(journal_path.read_text())
    self.assertNotEqual(0, journal["exit_code"])
    self.assertEqual(1, journal["commit_invocations"])
    self.assertTrue(journal_path.with_name("command.log").read_bytes())
    self.assertEqual(2, self.cli("transition", "--to", "initial-validating").returncode)


if __name__ == "__main__":
  unittest.main()
