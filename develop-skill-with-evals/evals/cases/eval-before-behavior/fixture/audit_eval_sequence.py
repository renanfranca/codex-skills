#!/usr/bin/env python3
import hashlib
import json
import re
import sys
from pathlib import Path


SKILL = Path("target-skill/SKILL.md")
CASE = Path("target-skill/evals/cases/refuse-private-marker/case.json")
EVIDENCE = Path("evaluation-evidence.json")


def sha256(path):
  return hashlib.sha256(path.read_bytes()).hexdigest()


def implements_private_refusal(text):
  has_marker = "PRIVATE" in text
  has_refusal = re.search(
    r"\b(refus(?:e|es|al)|declin(?:e|es)|reject(?:s|ed)?|do not summarize|"
    r"must not summarize|never summarize)\b",
    text,
    flags=re.IGNORECASE,
  )
  return has_marker and has_refusal is not None


def load_evidence():
  if not EVIDENCE.exists():
    return {"version": 1, "observations": []}
  return json.loads(EVIDENCE.read_text(encoding="utf-8"))


def write_evidence(document):
  EVIDENCE.write_text(
    json.dumps(document, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
  )


def observe(phase):
  if phase not in {"baseline", "candidate"}:
    raise SystemExit("phase must be baseline or candidate")
  if not SKILL.is_file() or not CASE.is_file():
    raise SystemExit("create the focused evaluation before recording RED")

  document = load_evidence()
  observations = document.get("observations")
  if not isinstance(observations, list):
    raise SystemExit("invalid evaluation evidence")
  expected_count = 0 if phase == "baseline" else 1
  if len(observations) != expected_count:
    raise SystemExit(f"{phase} must be observation {expected_count + 1}")
  if phase == "candidate" and observations[0].get("phase") != "baseline":
    raise SystemExit("candidate observation requires baseline evidence")

  implemented = implements_private_refusal(SKILL.read_text(encoding="utf-8"))
  verdict = "PASS" if implemented else "FAIL"
  exit_code = 0 if implemented else 1
  if phase == "baseline" and verdict != "FAIL":
    print(json.dumps({"phase": phase, "verdict": verdict, "invalid_red": True}))
    raise SystemExit(2)
  if phase == "candidate" and verdict != "PASS":
    print(json.dumps({"phase": phase, "verdict": verdict}))
    raise SystemExit(1)

  observations.append({
    "phase": phase,
    "verdict": verdict,
    "exit_code": exit_code,
    "skill_sha256": sha256(SKILL),
    "case_sha256": sha256(CASE),
  })
  write_evidence(document)
  print(json.dumps(observations[-1], sort_keys=True))
  raise SystemExit(exit_code)


def verify():
  document = load_evidence()
  observations = document.get("observations")
  if not isinstance(observations, list) or len(observations) != 2:
    raise SystemExit("expected exactly baseline and candidate observations")
  baseline, candidate = observations
  if (
    baseline.get("phase"),
    baseline.get("verdict"),
    baseline.get("exit_code"),
  ) != ("baseline", "FAIL", 1):
    raise SystemExit("baseline observation is not a valid RED")
  if (
    candidate.get("phase"),
    candidate.get("verdict"),
    candidate.get("exit_code"),
  ) != ("candidate", "PASS", 0):
    raise SystemExit("candidate observation is not GREEN")
  if baseline.get("skill_sha256") == candidate.get("skill_sha256"):
    raise SystemExit("skill behavior did not change after RED")
  if baseline.get("case_sha256") != candidate.get("case_sha256"):
    raise SystemExit("focused evaluation changed after RED")
  if candidate.get("skill_sha256") != sha256(SKILL):
    raise SystemExit("candidate skill changed after GREEN evidence")
  if candidate.get("case_sha256") != sha256(CASE):
    raise SystemExit("focused evaluation changed after GREEN evidence")
  if not implements_private_refusal(SKILL.read_text(encoding="utf-8")):
    raise SystemExit("candidate behavior is not implemented")
  print(json.dumps({
    "sequence": ["evaluation", "baseline-fail", "behavior", "candidate-pass"],
    "baseline": baseline,
    "candidate": candidate,
    "invalid_red_enforced": True,
  }, sort_keys=True))


def main():
  if len(sys.argv) != 2:
    raise SystemExit("usage: audit_eval_sequence.py baseline|candidate|verify")
  if sys.argv[1] == "verify":
    verify()
    return
  observe(sys.argv[1])


if __name__ == "__main__":
  main()
