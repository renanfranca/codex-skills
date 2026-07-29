import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
CASE_ROOT = (
  REPOSITORY_ROOT
  / "execplan-tdd"
  / "evals"
  / "cases"
  / "incomplete-profile-gate"
)
ORACLE = CASE_ROOT / "oracle" / "check_no_edits.py"
FIXTURE = CASE_ROOT / "fixture"
DOCUMENTATION_CASE_ROOT = (
  REPOSITORY_ROOT
  / "execplan-tdd"
  / "evals"
  / "cases"
  / "documentation-only-boundary"
)
DOCUMENTATION_ORACLE = DOCUMENTATION_CASE_ROOT / "oracle" / "check_boundary.py"
DOCUMENTATION_FIXTURE = DOCUMENTATION_CASE_ROOT / "fixture"


def write_response(workspace, **overrides):
  response = {
    "summary": "Stopped because the public checkpoint and canonical documentation sources are missing.",
    "classification": "blocked_incomplete_workflow_profile",
    "evidence": [
      "The repository profile omits a public checkpoint.",
      "The repository profile omits canonical documentation sources.",
    ],
    "files_changed": [],
    "diagnosis": "Repository level clarification is required before implementation.",
    "approach": [],
    "decisions": ["Stopped without editing files."],
    "rejected_alternatives": ["Did not invent missing commands or documentation sources."],
    "key_changes": [],
    "validation": [],
  }
  response.update(overrides)
  (workspace / ".eval-executor-response.json").write_text(
    json.dumps(response),
    encoding="utf-8",
  )


class ExecplanTddOracleTest(unittest.TestCase):
  def setUp(self):
    self.temporary = tempfile.TemporaryDirectory()
    self.workspace = Path(self.temporary.name)
    shutil.copytree(FIXTURE, self.workspace, dirs_exist_ok=True)
    subprocess.run(
      ["git", "init", "-q"],
      cwd=self.workspace,
      check=True,
    )
    write_response(self.workspace)

  def tearDown(self):
    self.temporary.cleanup()

  def run_oracle(self):
    return subprocess.run(
      ["python3", str(ORACLE)],
      cwd=self.workspace,
      capture_output=True,
      text=True,
      check=False,
    )

  def test_incomplete_profile_oracle_ignores_runner_git_metadata(self):
    result = self.run_oracle()

    self.assertEqual(result.returncode, 0, result.stderr)

  def test_incomplete_profile_oracle_rejects_project_edits(self):
    (self.workspace / "pricing.py").write_text(
      "def total(cents):\n  return cents - 100\n",
      encoding="utf-8",
    )

    result = self.run_oracle()

    self.assertEqual(result.returncode, 1)
    self.assertIn("blocked workflow edited pricing.py", result.stderr)

  def test_incomplete_profile_oracle_rejects_a_vague_blocked_response(self):
    write_response(
      self.workspace,
      summary="Blocked.",
      evidence=[],
      diagnosis="",
      decisions=[],
      rejected_alternatives=[],
    )

    result = self.run_oracle()

    self.assertEqual(result.returncode, 1)
    self.assertIn("missing profile fields", result.stderr)


class DocumentationBoundaryOracleTest(unittest.TestCase):
  def setUp(self):
    self.temporary = tempfile.TemporaryDirectory()
    self.workspace = Path(self.temporary.name)
    shutil.copytree(DOCUMENTATION_FIXTURE, self.workspace, dirs_exist_ok=True)
    subprocess.run(
      ["git", "init", "-q"],
      cwd=self.workspace,
      check=True,
    )
    (self.workspace / "README.md").write_text(
      "# Pricing\n\nThe `total` command returns cents as an integer.\n",
      encoding="utf-8",
    )
    write_response(
      self.workspace,
      summary="Corrected the isolated README statement.",
      classification="documentation_only",
      evidence=["README now says cents."],
      files_changed=["README.md"],
      diagnosis="The implementation already returns cents.",
      decisions=["No ExecPlan is required for this documentation only correction."],
      rejected_alternatives=[],
    )

  def tearDown(self):
    self.temporary.cleanup()

  def run_oracle(self):
    return subprocess.run(
      ["python3", str(DOCUMENTATION_ORACLE)],
      cwd=self.workspace,
      capture_output=True,
      text=True,
      check=False,
    )

  def test_documentation_boundary_ignores_only_harness_metadata(self):
    result = self.run_oracle()

    self.assertEqual(result.returncode, 0, result.stderr)

  def test_documentation_boundary_rejects_an_execplan(self):
    plans = self.workspace / ".plans"
    plans.mkdir()
    (plans / "unnecessary-exec-plan.md").write_text(
      "# Unnecessary plan\n",
      encoding="utf-8",
    )

    result = self.run_oracle()

    self.assertEqual(result.returncode, 1)
    self.assertIn("created files", result.stderr)


class NewSkillCaseManifestTest(unittest.TestCase):
  def test_repository_profile_case_observes_implicit_skill_selection(self):
    manifest_path = (
      REPOSITORY_ROOT
      / "execplan-tdd"
      / "evals"
      / "cases"
      / "repository-profile-implementation"
      / "case.json"
    )

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    self.assertIs(manifest["implicit_skill"], True)
    prompt = (manifest_path.parent / manifest["prompt_file"]).read_text(
      encoding="utf-8",
    )
    self.assertNotIn("$execplan-tdd", prompt)

  def test_complete_oracles_disable_all_semantic_judges(self):
    manifests = [
      REPOSITORY_ROOT
      / "execplan-tdd"
      / "evals"
      / "cases"
      / case_id
      / "case.json"
      for case_id in (
        "documentation-only-boundary",
        "incomplete-profile-gate",
        "repository-profile-implementation",
      )
    ]
    manifests.append(
      REPOSITORY_ROOT
      / "implement-execplan"
      / "evals"
      / "cases"
      / "documentation-impact-contract"
      / "case.json"
    )

    for manifest_path in manifests:
      with self.subTest(manifest=str(manifest_path)):
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(
          {"enabled": False, "criteria": []},
          manifest["judge"],
        )


if __name__ == "__main__":
  unittest.main()
