#!/usr/bin/env python3
import json
from pathlib import Path


repository_skill = Path(".agents/skills/develop-skill-with-evals/SKILL.md")
baseline = Path("baseline/SKILL.md")
candidate = Path("candidate/SKILL.md")
reminder = "Redact personal email addresses from fixtures."

repository_text = repository_skill.read_text(encoding="utf-8")
baseline_text = baseline.read_text(encoding="utf-8")
candidate_text = candidate.read_text(encoding="utf-8")

if baseline_text != repository_text:
  raise SystemExit("baseline does not match repository-scoped skill")
if reminder in baseline_text:
  raise SystemExit("baseline already contains the proposed reminder")
if candidate_text.count(reminder) != 1:
  raise SystemExit("candidate must contain the reminder exactly once")
without_reminder = " ".join(candidate_text.replace(reminder, "").split())
normalized_baseline = " ".join(baseline_text.split())
if without_reminder != normalized_baseline:
  raise SystemExit("candidate contains changes beyond the requested reminder")

print(json.dumps({
  "repository_scoped_skill_unchanged": True,
  "baseline_preserved": True,
  "candidate_isolated": True,
  "candidate_only_change": reminder,
  "promotion_deferred": True,
}, sort_keys=True))
