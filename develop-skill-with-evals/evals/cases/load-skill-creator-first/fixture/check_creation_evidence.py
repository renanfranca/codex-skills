#!/usr/bin/env python3
import json
from pathlib import Path


evidence = json.loads(
  Path("creation-evidence.json").read_text(encoding="utf-8")
)
skill_creator_path = evidence["skill_creator_path"]
scaffold_argv = evidence["scaffold_argv"]
assert isinstance(skill_creator_path, str)
assert skill_creator_path.endswith("/.system/skill-creator/SKILL.md")
assert isinstance(scaffold_argv, list)
assert scaffold_argv
assert all(isinstance(argument, str) for argument in scaffold_argv)
assert any(argument.endswith("/.system/skill-creator/scripts/init_skill.py") for argument in scaffold_argv)
assert "weather-brief" in scaffold_argv
assert "--path" in scaffold_argv
assert Path("weather-brief/SKILL.md").is_file()

print(json.dumps({
  "skill_creator_loaded": skill_creator_path,
  "official_scaffold_argv": scaffold_argv,
  "created_skill": "weather-brief/SKILL.md",
}, sort_keys=True))
