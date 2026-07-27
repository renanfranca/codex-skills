import copy
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import tempfile


ALLOWED_EVIDENCE = {
  "changed_paths",
  "executor_response",
  "judge",
  "mechanical",
  "oracle",
}


def fail(message):
  raise ValueError(message)


def load_json(path):
  try:
    return json.loads(path.read_text(encoding="utf-8"))
  except (OSError, json.JSONDecodeError) as error:
    fail(f"cannot load {path}: {error}")


def sha256(path):
  return hashlib.sha256(path.read_bytes()).hexdigest()


def substantive_sections(path):
  headings = []
  for line in path.read_text(encoding="utf-8").splitlines():
    match = re.match(r"^## ([^#].*)$", line)
    if match and match.group(1) != "Contents":
      headings.append(match.group(1))
  return headings


def validate_evidence(evidence, case, location):
  if not isinstance(evidence, list) or not evidence:
    fail(f"{location} must declare evidence")
  unknown = set(evidence) - ALLOWED_EVIDENCE
  if unknown:
    fail(f"{location} has unknown evidence: {sorted(unknown)}")
  if "mechanical" in evidence and not case.get("mechanical"):
    fail(f"{location} declares mechanical evidence without mechanical checks")
  if "judge" in evidence and not case.get("judge", {}).get("enabled", False):
    fail(f"{location} declares judge evidence without an enabled judge")
  if "oracle" in evidence and not case.get("oracle", {}).get("commands"):
    fail(f"{location} declares oracle evidence without oracle commands")
  if (
    {"executor_response", "changed_paths"} & set(evidence)
    and case.get("kind") == "deterministic"
  ):
    fail(f"{location} declares executor evidence for a deterministic case")


def validate_mappings(mappings, cases, location):
  if not isinstance(mappings, list) or not mappings:
    fail(f"{location} has no coverage mappings")
  dimensions = set()
  for index, mapping in enumerate(mappings):
    item = f"{location}.mappings[{index}]"
    case_id = mapping.get("case_id")
    if case_id not in cases:
      fail(f"{item} references unknown case {case_id!r}")
    dimension = mapping.get("dimension")
    if not isinstance(dimension, str) or not dimension.strip():
      fail(f"{item} has an empty dimension")
    if dimension in dimensions:
      fail(f"{location} has duplicate dimension {dimension!r}")
    dimensions.add(dimension)
    validate_evidence(mapping.get("evidence"), cases[case_id], item)


def validate_guarantee(item, location):
  guarantee = item.get("guarantee")
  if guarantee not in {"complete", "partial"}:
    fail(f"{location} has invalid guarantee {guarantee!r}")
  limitation = item.get("limitation")
  if guarantee == "partial" and (
    not isinstance(limitation, str) or not limitation.strip()
  ):
    fail(f"{location} partial coverage requires a limitation")
  if guarantee == "complete" and limitation is not None:
    fail(f"{location} complete coverage must not declare a limitation")


def load_cases(skill_dir, suite):
  case_root = skill_dir / "evals" / "cases"
  suite_ids = suite.get("cases")
  if not isinstance(suite_ids, list) or not suite_ids:
    fail("suite must contain cases")
  if len(suite_ids) != len(set(suite_ids)):
    fail("suite contains duplicate case ids")

  on_disk = {path.parent.name for path in case_root.glob("*/case.json")}
  missing = set(suite_ids) - on_disk
  orphaned = on_disk - set(suite_ids)
  if missing:
    fail(f"suite cases missing on disk: {sorted(missing)}")
  if orphaned:
    fail(f"orphaned cases not present in suite: {sorted(orphaned)}")

  cases = {}
  for case_id in suite_ids:
    case = load_json(case_root / case_id / "case.json")
    if case.get("id") != case_id:
      fail(f"case id mismatch for {case_id}")
    cases[case_id] = case
  return cases


def validate(skill_dir):
  coverage = load_json(skill_dir / "evals" / "coverage.json")
  suite = load_json(skill_dir / "evals" / "suite.json")
  if coverage.get("version") != 1:
    fail("coverage version must be 1")
  if suite.get("version") != 1:
    fail("suite version must be 1")

  fingerprints = coverage.get("source_fingerprints")
  expected_sources = {
    "SKILL.md",
    "references/design-review-rubric.md",
    "references/java-spring-hexagonal.md",
  }
  if not isinstance(fingerprints, dict) or set(fingerprints) != expected_sources:
    fail("source_fingerprints must name exactly the skill and both references")
  for relative_path, expected in fingerprints.items():
    actual = sha256(skill_dir / relative_path)
    if expected != actual:
      fail(f"stale fingerprint for {relative_path}: expected {actual}, found {expected}")

  cases = load_cases(skill_dir, suite)
  contracts = coverage.get("contracts")
  if not isinstance(contracts, list) or not contracts:
    fail("coverage must declare contracts")
  contract_ids = set()
  for index, contract in enumerate(contracts):
    location = f"contracts[{index}]"
    contract_id = contract.get("id")
    if not isinstance(contract_id, str) or not contract_id.strip():
      fail(f"{location} has an empty id")
    if contract_id in contract_ids:
      fail(f"duplicate contract id {contract_id!r}")
    contract_ids.add(contract_id)
    if not isinstance(contract.get("statement"), str) or not contract["statement"].strip():
      fail(f"{location} has an empty statement")
    validate_guarantee(contract, location)
    validate_mappings(contract.get("mappings"), cases, location)

  families = coverage.get("rubric_families")
  if not isinstance(families, list) or not families:
    fail("coverage must declare rubric families")
  mapped_by_source = {}
  family_ids = set()
  for index, family in enumerate(families):
    location = f"rubric_families[{index}]"
    family_id = family.get("id")
    if not isinstance(family_id, str) or not family_id.strip():
      fail(f"{location} has an empty id")
    if family_id in family_ids:
      fail(f"duplicate rubric family id {family_id!r}")
    family_ids.add(family_id)
    source = family.get("source")
    if source not in expected_sources - {"SKILL.md"}:
      fail(f"{location} has unknown rubric source {source!r}")
    validate_guarantee(family, location)
    sections = family.get("sections")
    if not isinstance(sections, list) or not sections:
      fail(f"{location} has no rubric sections")
    mapped_by_source.setdefault(source, []).extend(sections)
    validate_mappings(family.get("mappings"), cases, location)

  for source in expected_sources - {"SKILL.md"}:
    expected = substantive_sections(skill_dir / source)
    mapped = mapped_by_source.get(source, [])
    duplicates = sorted({section for section in mapped if mapped.count(section) > 1})
    if duplicates:
      fail(f"{source} sections mapped more than once: {duplicates}")
    missing = sorted(set(expected) - set(mapped))
    unknown = sorted(set(mapped) - set(expected))
    if missing:
      fail(f"{source} sections not mapped: {missing}")
    if unknown:
      fail(f"{source} mappings name unknown sections: {unknown}")


def update_coverage(skill_dir, mutate):
  path = skill_dir / "evals" / "coverage.json"
  value = load_json(path)
  mutate(value)
  path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def expect_invalid(source, label, mutate):
  with tempfile.TemporaryDirectory(prefix=f"coverage-{label}-") as temporary:
    candidate = Path(temporary) / "refactor-design"
    shutil.copytree(source, candidate)
    mutate(candidate)
    try:
      validate(candidate)
    except ValueError:
      return
    fail(f"negative self-check did not reject {label}")


def prove_negative_checks(skill_dir):
  expect_invalid(
    skill_dir,
    "stale-fingerprint",
    lambda copy_dir: update_coverage(
      copy_dir,
      lambda coverage: coverage["source_fingerprints"].update({"SKILL.md": "0" * 64}),
    ),
  )
  expect_invalid(
    skill_dir,
    "unknown-case",
    lambda copy_dir: update_coverage(
      copy_dir,
      lambda coverage: coverage["contracts"][0]["mappings"][0].update(
        {"case_id": "unknown-case"}
      ),
    ),
  )

  def add_orphan(copy_dir):
    source = copy_dir / "evals" / "cases" / "cohesive-no-action"
    target = copy_dir / "evals" / "cases" / "orphaned-case"
    shutil.copytree(source, target)
    case_path = target / "case.json"
    case = load_json(case_path)
    case["id"] = "orphaned-case"
    case_path.write_text(json.dumps(case, indent=2) + "\n", encoding="utf-8")

  expect_invalid(skill_dir, "orphaned-case", add_orphan)
  expect_invalid(
    skill_dir,
    "duplicate-dimension",
    lambda copy_dir: update_coverage(
      copy_dir,
      lambda coverage: coverage["contracts"][0]["mappings"].append(
        copy.deepcopy(coverage["contracts"][0]["mappings"][0])
      ),
    ),
  )
  expect_invalid(
    skill_dir,
    "empty-contract",
    lambda copy_dir: update_coverage(
      copy_dir,
      lambda coverage: coverage["contracts"][0].update({"mappings": []}),
    ),
  )
  expect_invalid(
    skill_dir,
    "unmapped-rubric-section",
    lambda copy_dir: update_coverage(
      copy_dir,
      lambda coverage: coverage["rubric_families"][0]["sections"].pop(),
    ),
  )


def main():
  skill_dir_value = os.environ.get("SKILL_EVAL_SKILL_DIR")
  if not skill_dir_value:
    fail("SKILL_EVAL_SKILL_DIR is required")
  skill_dir = Path(skill_dir_value).resolve()
  validate(skill_dir)
  prove_negative_checks(skill_dir)
  print("coverage contract valid")


if __name__ == "__main__":
  main()
