import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
CASE_ROOT = (
  REPOSITORY_ROOT
  / "implement-execplan"
  / "evals"
  / "cases"
  / "documentation-impact-contract"
)
ORACLE = CASE_ROOT / "oracle" / "check_documentation_impact.py"

REQUIRED_SECTIONS = (
  "Purpose / Big Picture",
  "Milestones",
  "Progress",
  "Decisions",
  "Risks and Mitigations",
  "Validation Strategy",
  "Documentation Impact",
  "Lessons Learned",
)


def plan(sections):
  return "\n\n".join(
    f"## {heading}\n\n{sections.get(heading, 'Required plan content.')}"
    for heading in REQUIRED_SECTIONS
  ) + "\n"


class ImplementExecplanOracleTest(unittest.TestCase):
  def setUp(self):
    self.temporary = tempfile.TemporaryDirectory()
    self.workspace = Path(self.temporary.name)
    plans = self.workspace / "plans"
    plans.mkdir()
    self.write_public_validation("Validate README.md and config.json.")

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

  def write_internal_documentation_impact(self, documentation_impact):
    (self.workspace / "plans" / "internal-change.md").write_text(
      plan({"Documentation Impact": documentation_impact}),
      encoding="utf-8",
    )

  def write_public_validation(self, validation):
    (self.workspace / "plans" / "public-change.md").write_text(
      plan(
        {
          "Milestones": "Update README.md and config.json for timeout_seconds.",
          "Validation Strategy": validation,
          "Documentation Impact": (
            "Document timeout_seconds in README.md and config.json."
          ),
        }
      ),
      encoding="utf-8",
    )

  def test_accepts_concrete_unchanged_documentation_justification(self):
    self.write_internal_documentation_impact(
      "README.md remains accurate without edits because it documents only "
      "public behavior. config.json remains accurate without edits because "
      "the public key is unchanged."
    )

    result = self.run_oracle()

    self.assertEqual(result.returncode, 0, result.stderr)

  def test_rejects_documentation_names_without_a_no_change_justification(self):
    self.write_internal_documentation_impact(
      "The canonical sources are README.md and config.json."
    )

    result = self.run_oracle()

    self.assertEqual(result.returncode, 1)
    self.assertIn("lacks an explicit no change justification", result.stderr)

  def test_accepts_cross_referenced_canonical_documentation_validation(self):
    self.write_public_validation(
      "Parse config.json and inspect every public field occurrence across "
      "code, tests, and canonical documentation."
    )
    self.write_internal_documentation_impact(
      "README.md and config.json remain accurate without edits because "
      "the public contract is unchanged."
    )

    result = self.run_oracle()

    self.assertEqual(result.returncode, 0, result.stderr)

  def test_rejects_public_validation_that_ignores_documentation(self):
    self.write_public_validation("Run the unit tests.")
    self.write_internal_documentation_impact(
      "README.md and config.json remain accurate without edits because "
      "the public contract is unchanged."
    )

    result = self.run_oracle()

    self.assertEqual(result.returncode, 1)
    self.assertIn("omits documentation reconciliation", result.stderr)


if __name__ == "__main__":
  unittest.main()
