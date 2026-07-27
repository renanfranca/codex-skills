#!/usr/bin/env python3
import json
from pathlib import Path


UNTOUCHED_SCAFFOLD_MESSAGE = (
  "weather-brief/SKILL.md no longer looks like the untouched official scaffold"
)


def fail(message):
  raise SystemExit(message)


evidence_path = Path("creation-evidence.json")
if not evidence_path.is_file():
  fail("creation-evidence.json is missing from the workspace root")

try:
  evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
except (OSError, UnicodeError, json.JSONDecodeError):
  fail("creation-evidence.json must contain valid JSON")

if not isinstance(evidence, dict):
  fail("creation-evidence.json must contain a JSON object")

skill_creator_path = evidence.get("skill_creator_path")
if (
  not isinstance(skill_creator_path, str)
  or not skill_creator_path.endswith(".system/skill-creator/SKILL.md")
):
  fail("skill_creator_path must point to .system/skill-creator/SKILL.md")

scaffold_argv = evidence.get("scaffold_argv")
if (
  not isinstance(scaffold_argv, list)
  or not scaffold_argv
  or not all(isinstance(argument, str) for argument in scaffold_argv)
):
  fail("scaffold_argv must be a non-empty list of strings")

if not any(
  argument.endswith(".system/skill-creator/scripts/init_skill.py")
  for argument in scaffold_argv
):
  fail("scaffold_argv must invoke the official init_skill.py")

if "weather-brief" not in scaffold_argv:
  fail("scaffold_argv must include weather-brief")

if "--path" not in scaffold_argv:
  fail("scaffold_argv must include --path followed by a destination")
path_index = scaffold_argv.index("--path")
if (
  path_index + 1 >= len(scaffold_argv)
  or not scaffold_argv[path_index + 1]
  or scaffold_argv[path_index + 1].startswith("--")
):
  fail("scaffold_argv must include --path followed by a destination")

skill_path = Path("weather-brief/SKILL.md")
if not skill_path.is_file():
  fail("weather-brief/SKILL.md was not generated")

agent_metadata_path = Path("weather-brief/agents/openai.yaml")
if not agent_metadata_path.is_file():
  fail("weather-brief/agents/openai.yaml was not generated")

try:
  skill_text = skill_path.read_text(encoding="utf-8")
except (OSError, UnicodeError):
  fail(UNTOUCHED_SCAFFOLD_MESSAGE)
if "[TODO:" not in skill_text:
  fail(UNTOUCHED_SCAFFOLD_MESSAGE)

print(json.dumps({
  "skill_creator_loaded": skill_creator_path,
  "official_scaffold_argv": scaffold_argv,
  "created_skill": "weather-brief/SKILL.md",
  "created_agent_metadata": "weather-brief/agents/openai.yaml",
}, sort_keys=True))
