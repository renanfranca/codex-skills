#!/usr/bin/env python3
import json
from pathlib import Path
import re


repository_skill = Path(".agents/skills/develop-skill-with-evals/SKILL.md")
baseline = Path("baseline/SKILL.md")
candidate = Path("candidate/SKILL.md")

repository_text = repository_skill.read_text(encoding="utf-8")
baseline_text = baseline.read_text(encoding="utf-8")
candidate_text = candidate.read_text(encoding="utf-8")

if baseline_text != repository_text:
  raise SystemExit("baseline does not match repository-scoped skill")

added_length = len(candidate_text) - len(baseline_text)
if added_length <= 0:
  raise SystemExit("candidate must add exactly one reminder")

insertions = []
for index in range(len(baseline_text) + 1):
  if (
    candidate_text[:index] == baseline_text[:index]
    and candidate_text[index + added_length:] == baseline_text[index:]
  ):
    insertions.append(candidate_text[index:index + added_length])

if not insertions:
  raise SystemExit(
    "candidate must contain exactly one insertion without removals or replacements"
  )


def valid_reminder(insertion):
  lines = [line.strip() for line in insertion.splitlines() if line.strip()]
  if len(lines) != 1:
    return False
  phrase = re.sub(r"^(?:[-*+]\s+|\d+[.)]\s+)", "", lines[0])
  if not phrase or len(phrase) > 160:
    return False
  if len(re.findall(r"[.!?]", phrase)) > 1:
    return False
  if re.search(r"[.!?]", phrase[:-1]):
    return False
  lowered = phrase.casefold()
  if re.search(r"\b(?:not|never)\b|\bdo\s+not\b|\bdon['’]t\b", lowered):
    return False
  required = [
    r"\bredact(?:s|ed|ing)?\b",
    r"\bpersonal\b",
    r"\bemail\s+address(?:es)?\b",
    r"\bfixtures?\b",
  ]
  if any(re.search(pattern, lowered) is None for pattern in required):
    return False
  if len(re.findall(required[0], lowered)) != 1:
    return False
  return True


valid_insertions = [insertion for insertion in insertions if valid_reminder(insertion)]
if not valid_insertions:
  raise SystemExit(
    "candidate insertion must be one short, affirmative reminder containing "
    "redaction, personal, email address, and fixture concepts"
  )
reminder = valid_insertions[0].strip()

print(json.dumps({
  "repository_scoped_skill_unchanged": True,
  "baseline_preserved": True,
  "candidate_isolated": True,
  "candidate_only_change": reminder,
  "promotion_deferred": True,
}, sort_keys=True))
