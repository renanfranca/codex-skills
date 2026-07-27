import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


CASE_ID = "load-skill-creator-before-scaffold"
EXPECTED_REQUIRED_PATHS = {
  "creation-evidence.json",
  "weather-brief/SKILL.md",
  "weather-brief/agents/openai.yaml",
}
EXPECTED_FORBIDDEN_PATHS = {
  ".agents/skills/**",
  "weather-brief/creation-evidence.json",
  "weather-brief/evals/**",
  "weather-brief/scripts/**",
  "weather-brief/references/**",
  "weather-brief/assets/**",
  "baseline/**",
  "candidate/**",
  "eval-reports/**",
  "evaluation-reports/**",
}


class LoadSkillCreatorContractTests(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    configured_root = os.environ.get("SKILL_UNDER_TEST")
    cls.skill_root = (
      Path(configured_root).resolve()
      if configured_root
      else Path(__file__).parents[2]
    )
    cls.case_dir = cls.skill_root / "evals" / "cases" / CASE_ID
    if not cls.case_dir.is_dir():
      raise AssertionError(
        f"expected renamed case directory is missing: {cls.case_dir}"
      )
    cls.manifest = json.loads(
      (cls.case_dir / "case.json").read_text(encoding="utf-8")
    )
    cls.prompt = (cls.case_dir / "prompt.md").read_text(encoding="utf-8")
    cls.oracle = cls.case_dir / "oracle" / "check_creation_evidence.py"

  def write_valid_workspace(self, root):
    skill_dir = root / "weather-brief"
    (skill_dir / "agents").mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
      "---\n"
      "name: weather-brief\n"
      "description: [TODO: Describe this skill.]\n"
      "---\n\n"
      "# Weather Brief\n\n"
      "[TODO: Complete this scaffold.]\n",
      encoding="utf-8",
    )
    (skill_dir / "agents" / "openai.yaml").write_text(
      "interface:\n"
      "  display_name: \"Weather Brief\"\n"
      "  short_description: \"TODO\"\n"
      "  default_prompt: \"TODO\"\n",
      encoding="utf-8",
    )
    (root / "creation-evidence.json").write_text(
      json.dumps({
        "skill_creator_path": (
          "/opt/codex/skills/.system/skill-creator/SKILL.md"
        ),
        "scaffold_argv": [
          "python3",
          "/opt/codex/skills/.system/skill-creator/scripts/init_skill.py",
          "weather-brief",
          "--path",
          ".",
        ],
      }),
      encoding="utf-8",
    )

  def run_oracle(self, root):
    return subprocess.run(
      ["python3", str(self.oracle)],
      cwd=root,
      text=True,
      capture_output=True,
      check=False,
    )

  def assert_oracle_failure(self, mutate, expected_message):
    with tempfile.TemporaryDirectory() as temporary:
      root = Path(temporary)
      self.write_valid_workspace(root)
      mutate(root)
      completed = self.run_oracle(root)
    self.assertNotEqual(0, completed.returncode)
    self.assertEqual(expected_message, completed.stderr.strip())
    self.assertNotIn("Traceback", completed.stderr)

  def update_evidence(self, root, **updates):
    evidence_path = root / "creation-evidence.json"
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    evidence.update(updates)
    evidence_path.write_text(json.dumps(evidence), encoding="utf-8")

  def test_case_id_and_directory_are_renamed(self):
    self.assertEqual(CASE_ID, self.manifest["id"])
    self.assertEqual(CASE_ID, self.case_dir.name)

  def test_prompt_stops_after_untouched_scaffold_and_evidence(self):
    required_phrases = [
      "before creating or editing any file inside `./weather-brief`",
      "official `init_skill.py`",
      "Do not customize",
      "Do not create evaluations",
      "baseline",
      "candidate",
      "reports",
      "Do not run nested Codex sessions",
      "subagents",
      "fresh agents",
      "Stop as soon as",
      "Do not commit",
    ]
    for phrase in required_phrases:
      with self.subTest(phrase=phrase):
        self.assertIn(phrase, self.prompt)

  def test_manifest_limits_required_and_forbidden_paths(self):
    mechanical = self.manifest["mechanical"]
    self.assertEqual(
      EXPECTED_REQUIRED_PATHS,
      set(mechanical["required_paths"]),
    )
    self.assertTrue(
      EXPECTED_FORBIDDEN_PATHS.issubset(
        set(mechanical["forbidden_changed_paths"])
      )
    )
    self.assertFalse(self.manifest["judge"]["enabled"])

  def test_oracle_contains_specific_contract_messages(self):
    expected_messages = [
      "creation-evidence.json is missing from the workspace root",
      "creation-evidence.json must contain valid JSON",
      "creation-evidence.json must contain a JSON object",
      "skill_creator_path must point to .system/skill-creator/SKILL.md",
      "scaffold_argv must be a non-empty list of strings",
      "scaffold_argv must invoke the official init_skill.py",
      "scaffold_argv must include weather-brief",
      "scaffold_argv must include --path followed by a destination",
      "weather-brief/SKILL.md was not generated",
      "weather-brief/agents/openai.yaml was not generated",
      (
        "weather-brief/SKILL.md no longer looks like the untouched "
        "official scaffold"
      ),
    ]
    oracle_source = self.oracle.read_text(encoding="utf-8")
    for message in expected_messages:
      with self.subTest(message=message):
        self.assertIn(message, oracle_source)

  def test_oracle_accepts_minimal_valid_scaffold(self):
    with tempfile.TemporaryDirectory() as temporary:
      root = Path(temporary)
      self.write_valid_workspace(root)
      completed = self.run_oracle(root)
    self.assertEqual(0, completed.returncode, completed.stderr)
    result = json.loads(completed.stdout)
    self.assertEqual("weather-brief/SKILL.md", result["created_skill"])
    self.assertEqual(
      "weather-brief/agents/openai.yaml",
      result["created_agent_metadata"],
    )

  def test_oracle_rejects_missing_evidence(self):
    self.assert_oracle_failure(
      lambda root: (root / "creation-evidence.json").unlink(),
      "creation-evidence.json is missing from the workspace root",
    )

  def test_oracle_rejects_invalid_json(self):
    self.assert_oracle_failure(
      lambda root: (root / "creation-evidence.json").write_text(
        "{not json",
        encoding="utf-8",
      ),
      "creation-evidence.json must contain valid JSON",
    )

  def test_oracle_rejects_non_object_evidence(self):
    self.assert_oracle_failure(
      lambda root: (root / "creation-evidence.json").write_text(
        "[]",
        encoding="utf-8",
      ),
      "creation-evidence.json must contain a JSON object",
    )

  def test_oracle_rejects_wrong_skill_creator_path(self):
    self.assert_oracle_failure(
      lambda root: self.update_evidence(
        root,
        skill_creator_path="/tmp/not-skill-creator/SKILL.md",
      ),
      "skill_creator_path must point to .system/skill-creator/SKILL.md",
    )

  def test_oracle_rejects_invalid_argv(self):
    self.assert_oracle_failure(
      lambda root: self.update_evidence(root, scaffold_argv=["python3", 7]),
      "scaffold_argv must be a non-empty list of strings",
    )

  def test_oracle_rejects_wrong_initializer(self):
    self.assert_oracle_failure(
      lambda root: self.update_evidence(
        root,
        scaffold_argv=[
          "python3",
          "/tmp/init_skill.py",
          "weather-brief",
          "--path",
          ".",
        ],
      ),
      "scaffold_argv must invoke the official init_skill.py",
    )

  def test_oracle_rejects_missing_skill_name(self):
    self.assert_oracle_failure(
      lambda root: self.update_evidence(
        root,
        scaffold_argv=[
          "python3",
          "/opt/codex/skills/.system/skill-creator/scripts/init_skill.py",
          "different-skill",
          "--path",
          ".",
        ],
      ),
      "scaffold_argv must include weather-brief",
    )

  def test_oracle_rejects_path_without_destination(self):
    self.assert_oracle_failure(
      lambda root: self.update_evidence(
        root,
        scaffold_argv=[
          "python3",
          "/opt/codex/skills/.system/skill-creator/scripts/init_skill.py",
          "weather-brief",
          "--path",
        ],
      ),
      "scaffold_argv must include --path followed by a destination",
    )

  def test_oracle_rejects_missing_skill_file(self):
    self.assert_oracle_failure(
      lambda root: (root / "weather-brief" / "SKILL.md").unlink(),
      "weather-brief/SKILL.md was not generated",
    )

  def test_oracle_rejects_missing_agent_metadata(self):
    self.assert_oracle_failure(
      lambda root: (
        root / "weather-brief" / "agents" / "openai.yaml"
      ).unlink(),
      "weather-brief/agents/openai.yaml was not generated",
    )

  def test_oracle_rejects_customized_scaffold(self):
    self.assert_oracle_failure(
      lambda root: (root / "weather-brief" / "SKILL.md").write_text(
        "---\n"
        "name: weather-brief\n"
        "description: Creates a weather brief.\n"
        "---\n",
        encoding="utf-8",
      ),
      (
        "weather-brief/SKILL.md no longer looks like the untouched "
        "official scaffold"
      ),
    )


if __name__ == "__main__":
  unittest.main()
