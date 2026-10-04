#!/usr/bin/env python3

import argparse
from collections import deque
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import shutil
import shlex
import subprocess
import sys
import tempfile
import time
import xml.etree.ElementTree as ET

from workflow_state import validation_plan_is_valid


LIMIT = 16 * 1024
REPORT_FORMATS = {
  "maven": ("junit", "jacoco", "artifact"), "kof": ("kof", "artifact"),
  "pit": ("pit", "artifact"), "generic": ("artifact",), "habit": ("artifact",),
}
PHASES = {
  "initial-validating": "validator", "final-validating": "validator",
  "habit-checking": "habit-curator", "habit-rechecking": "habit-curator",
  "mutation-testing": "mutation-analyst", "mutation-rechecking": "mutation-analyst",
}


def encoded(value):
  return (json.dumps(value, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")


def save(path, value):
  path.write_bytes(encoded(value))


def git(repo, *args):
  return subprocess.check_output(["git", "-C", str(repo), *args], stderr=subprocess.DEVNULL)


def fingerprint(repo, check, config):
  names = set(git(repo, "ls-files", "--cached", "--others", "--exclude-standard", "-z").decode().split("\0"))
  explicit_names = set()
  for pattern in config.get("inputs", []):
    paths = [p for p in repo.glob(pattern) if p.is_file()]
    if not paths:
      raise ValueError(f"missing configured input: {pattern}")
    explicit_names.update(str(p.relative_to(repo)) for p in paths)
  names.update(explicit_names)
  output_names = {str(p.relative_to(repo)) for spec in config.get("reports", []) for p in repo.glob(spec["glob"]) if p.is_file()}
  files = []
  for name in sorted(names - output_names):
    path = repo / name
    if name and (not name.startswith(".agent/tmp/") or name in explicit_names):
      files.append({"path": name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None})
  manifest = {"command": check["command"], "collector_config": config, "files": files}
  return manifest, hashlib.sha256(json.dumps(manifest, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()


def diagnostics(log):
  found = []
  with log.open(encoding="utf-8", errors="replace") as stream:
    for line in stream:
      if re.search(r"error|fail|exception|surviv|no.coverage|blocked", line, re.I):
        found.append(line.strip()[:500])
        found = found[-8:]
  return found


def conclusion(log):
  lines = deque(maxlen=4)
  with log.open(encoding="utf-8", errors="replace") as stream:
    for line in stream:
      if line.strip():
        lines.append(line.rstrip().encode("utf-8")[-512:].decode("utf-8", errors="ignore"))
  return "\n".join(lines).encode("utf-8")[-512:].decode("utf-8", errors="ignore")


def run_process(argv, repo, stdout, stderr, stdin=None, pass_fds=()):
  try:
    process = subprocess.Popen(argv, cwd=repo, stdout=stdout, stderr=stderr, stdin=stdin,
                               pass_fds=pass_fds, start_new_session=True)
  except OSError as error:
    destination = stderr if stderr != subprocess.STDOUT else stdout
    destination.write((str(error) + "\n").encode())
    destination.flush()
    return 127, False
  try:
    return process.wait(), False
  except KeyboardInterrupt:
    os.killpg(process.pid, signal.SIGTERM)
    try:
      code = process.wait(timeout=1)
    except subprocess.TimeoutExpired:
      os.killpg(process.pid, signal.SIGKILL)
      code = process.wait()
    return code, True


def habit_command(command, repo):
  lexer = shlex.shlex(command, posix=True, punctuation_chars=True)
  lexer.whitespace_split = True
  args = list(lexer)
  if not args or Path(args[0]).name != "habit-hooks" or any(
    any(c in token for c in "|&;<>()`$\n") for token in args
  ) or any(a in args[1:] for a in ("init", "--help", "-h", "--version")):
    return None
  executable = args[0]
  if "/" in executable and not Path(executable).is_absolute():
    executable = str(repo / executable)
  search_path = os.pathsep.join(str(Path(p) if Path(p).is_absolute() else repo / p) for p in os.environ.get("PATH", os.defpath).split(os.pathsep))
  wrapper = shutil.which(executable, path=search_path)
  if wrapper is None:
    raise ValueError("habit-hooks executable unavailable")
  parent = Path(wrapper).resolve().parent
  def sibling(name):
    path = parent / name
    return str(path) if path.is_file() else name
  parser = argparse.ArgumentParser(add_help=False)
  parser.add_argument("--config")
  known, _ = parser.parse_known_args(args[1:])
  return [sibling("habit-sensors"), *args[1:]], [sibling("habit-mapper"), *(["--config", known.config] if known.config else [])]


def execute_habit(commands, repo, attempt):
  started = time.monotonic()
  stages = []
  sensors = attempt / "sensors.json"
  guides = attempt / "guides.log"
  sensor_error = attempt / "sensors.stderr.log"
  mapper_error = attempt / "mapper.stderr.log"
  with sensors.open("wb") as output, sensor_error.open("wb") as error:
    code, cancelled = run_process(commands[0], repo, output, error)
  stages.append({"name": "sensors", "command": commands[0], "exit_code": code, "invocations": 1})
  mapper_code = None
  if not cancelled:
    with sensors.open("rb") as input_file, guides.open("wb") as output, mapper_error.open("wb") as error:
      mapper_code, cancelled = run_process(commands[1], repo, output, error, stdin=input_file)
    stages.append({"name": "mapper", "command": commands[1], "exit_code": mapper_code, "invocations": 1})
  with (attempt / "command.log").open("wb") as log:
    for path in (sensor_error, guides, mapper_error):
      if path.exists():
        with path.open("rb") as stream:
          shutil.copyfileobj(stream, log)
  effective = mapper_code or code
  status = "cancelled" if cancelled else ("completed" if effective == 0 else "failed")
  return {"status": status, "exit_code": effective, "invocations": 1, "stages": stages}, time.monotonic() - started


def habit(attempt, execution):
  findings = json.loads((attempt / "sensors.json").read_text(encoding="utf-8"))
  if not isinstance(findings, list) or any(not isinstance(f, dict) or not isinstance(f.get("smell"), str) for f in findings):
    raise ValueError("invalid Habit sensor JSON")
  stages = execution["stages"]
  tool_error = len(stages) != 2 or stages[0]["exit_code"] != 0 or stages[1]["exit_code"] not in (0, 1) or any(f["smell"] == "incomplete-run" for f in findings)
  blocked = len(stages) == 2 and stages[1]["exit_code"] == 1
  status = "tool-error" if tool_error else ("blocked" if blocked else ("guidance" if findings else "needs-analysis"))
  return {"raw_findings": len(findings), "active_findings": None}, findings, tool_error or blocked, status


def execute(command, repo, log):
  start = time.monotonic()
  failures_path = log.with_suffix(".exit-codes")
  with log.open("wb") as output, failures_path.open("w+b") as failures:
    fd = failures.fileno()
    script = f"trap 'printf \"%s\\n\" \"$?\" >&{fd}' ERR\n" + command
    code, cancelled = run_process(["bash", "-E", "-o", "pipefail", "-c", script], repo,
                                  output, subprocess.STDOUT, pass_fds=(fd,))
    failures.seek(0)
    codes = [int(line) for line in failures.read().splitlines()]
  return {"status": "cancelled" if cancelled else ("completed" if code == 0 and not codes else "failed"), "exit_code": code,
          "shell_failures": codes, "invocations": 1}, time.monotonic() - start


def report_snapshot(repo, config):
  return {str(path.resolve()): (path.stat().st_mtime_ns, hashlib.sha256(path.read_bytes()).hexdigest())
          for spec in config.get("reports", []) for path in repo.glob(spec["glob"]) if path.is_file()}


def collect_reports(repo, config, attempt, before, started_ns):
  reports, issues, seen = [], [], set()
  destination = attempt / "reports"
  destination.mkdir()
  for spec in sorted(config.get("reports", []), key=lambda spec: spec["format"] == "artifact"):
    paths = sorted(p for p in repo.glob(spec["glob"]) if p.is_file())
    if not paths and spec.get("required", True):
      issues.append(f"missing required report: {spec['glob']}")
    for path in paths:
      source = str(path.resolve())
      stat = path.stat()
      signature = (stat.st_mtime_ns, hashlib.sha256(path.read_bytes()).hexdigest())
      fresh = stat.st_mtime_ns >= started_ns and before.get(source) != signature
      if not fresh and spec.get("required", True):
        issues.append(f"stale required report: {source}")
      if source in seen:
        continue
      seen.add(source)
      target = destination / path.relative_to(repo)
      target.parent.mkdir(parents=True, exist_ok=True)
      shutil.copy2(path, target)
      report = {"source": source, "path": str(target), "format": spec["format"], "fresh": fresh, "target": spec.get("target")}
      reports.append(report)
  return reports, issues


def nonnegative(value):
  result = int(value)
  if result < 0:
    raise ValueError("negative report count")
  return result


def maven(reports):
  if not any(r["fresh"] and r["format"] == "junit" for r in reports):
    raise ValueError("Maven requires fresh Surefire/Failsafe reports")
  counts = dict.fromkeys(("tests", "failures", "errors", "skipped"), 0)
  coverage, findings, report_failed = [], [], False
  junit_dirs = {str(Path(r["source"]).parent) for r in reports
                if r["fresh"] and r["format"] == "junit" and Path(r["source"]).name.startswith("TEST-")}
  for report in reports:
    if not report["fresh"] or report["format"] == "artifact":
      continue
    root = ET.parse(report["path"]).getroot()
    if report["format"] == "jacoco":
      if root.tag != "report":
        raise ValueError("invalid JaCoCo report root")
      counters = {c.attrib["type"]: {k: nonnegative(c.attrib[k]) for k in ("missed", "covered")}
                  for c in root.findall("counter")}
      coverage.append({"report": report["path"], "counters": counters})
    elif root.tag == "failsafe-summary":
      summary = {key: nonnegative(root.findtext(field)) for key, field in
                 (("tests", "completed"), ("failures", "failures"), ("errors", "errors"), ("skipped", "skipped"))}
      report_failed |= summary["failures"] > 0 or summary["errors"] > 0 or root.get("result", "0") not in ("0", "null", "")
      if str(Path(report["source"]).parent) not in junit_dirs:
        for key, field in (("tests", "completed"), ("failures", "failures"), ("errors", "errors"), ("skipped", "skipped")):
          counts[key] += nonnegative(root.findtext(field))
    elif root.tag in ("testsuite", "testsuites"):
      suites = [r for r in root.iter("testsuite") if r.find("testsuite") is None]
      if not suites:
        raise ValueError("JUnit report contains no test suites")
      for suite in suites:
        values = {key: nonnegative(suite.attrib.get(key, "0")) for key in counts}
        if "tests" not in suite.attrib or sum(values[k] for k in ("failures", "errors", "skipped")) > values["tests"]:
          raise ValueError("inconsistent JUnit counts")
        for key, value in values.items():
          counts[key] += value
        for case in suite.findall("testcase"):
          for failure in list(case.findall("failure")) + list(case.findall("error")):
            report_failed = True
            findings.append({"suite": suite.get("name"), "test": case.get("name"),
                             "message": failure.get("message", failure.text or "")})
    else:
      raise ValueError("invalid Maven report root")
  return {"tests": counts, "coverage": coverage}, findings, bool(report_failed or counts["failures"] or counts["errors"])


def kof(reports, log, config):
  sources = [r for r in reports if r["fresh"] and r["format"] == "kof"]
  if not sources and config.get("target"):
    sources = [{"path": str(log), "target": config["target"]}]
  if not sources:
    raise ValueError("Kof needs a target for the command log or per-target reports")
  targets, suites, failed = {}, [], False
  for report in sources:
    if not report.get("target"):
      raise ValueError("Kof report has no target")
    target = report["target"]
    totals = targets.setdefault(target, {"tests": None, "failed": None, "files_passed": 0, "files_failed": 0, "directory_suites": []})
    name, recognized = "unknown", False
    structured, named_files, file_summaries = [], [], []
    with Path(report["path"]).open(encoding="utf-8", errors="replace") as stream:
      for line in stream:
        line = line.strip()
        if line.startswith("Suite: ") or line.startswith("SUITE "):
          name = line.split(" ", 1)[1]
        match = re.fullmatch(r"(\d+) failed of (\d+) tests", line)
        if match:
          errors, tests = map(int, match.groups())
          if errors > tests:
            raise ValueError("inconsistent Kof counts")
          structured.append({"target": target, "suite": name, "tests": tests, "failed": errors})
          recognized = True
        match = re.fullmatch(r"suite (.*): (\d+) passed, (\d+) failed", line)
        if match:
          named_files.append({"target": target, "suite": match[1], "files_passed": int(match[2]), "files_failed": int(match[3])})
          failed |= int(match[3]) > 0
          recognized = True
        match = re.fullmatch(r"(\d+) passed, (\d+) failed", line)
        if match:
          file_summaries.append((int(match[1]), int(match[2])))
          failed |= int(match[2]) > 0
          recognized = True
        if line.startswith("FAIL "):
          failed = True
        if re.fullmatch(r"no tests with tag .*", line):
          recognized = True
    if not recognized:
      raise ValueError("Kof output has no suite results")
    suites.extend(structured or named_files)
    if structured:
      totals["tests"] = (totals["tests"] or 0) + sum(s["tests"] for s in structured)
      totals["failed"] = (totals["failed"] or 0) + sum(s["failed"] for s in structured)
    totals["directory_suites"].extend(named_files)
    totals["files_passed"] += sum(p for p, f in file_summaries)
    totals["files_failed"] += sum(f for p, f in file_summaries)
    failed |= (totals["failed"] or 0) > 0
  return {"targets": targets}, suites, failed


def pit(reports):
  sources = [r for r in reports if r["fresh"] and r["format"] == "pit"]
  if not sources:
    raise ValueError("PIT requires fresh mutations XML; retain HTML and configure XML output")
  counts = dict.fromkeys(("generated", "killed", "survived", "no_coverage", "execution_errors"), 0)
  mutants = []
  statuses = {"KILLED": "killed", "SURVIVED": "survived", "NO_COVERAGE": "no_coverage"}
  for report in sources:
    root = ET.parse(report["path"]).getroot()
    if root.tag != "mutations":
      raise ValueError("invalid PIT report root")
    for mutation in root.findall("mutation"):
      status = mutation.attrib["status"]
      mutant = {"id": f"{len(mutants) + 1}", "status": status, "report": report["path"],
                "class": mutation.findtext("mutatedClass"), "method": mutation.findtext("mutatedMethod"),
                "descriptor": mutation.findtext("methodDescription"), "line": mutation.findtext("lineNumber"),
                "mutator": mutation.findtext("mutator"), "indexes": [i.text for i in mutation.findall("indexes/index")],
                "description": mutation.findtext("description"), "killing_test": mutation.findtext("killingTest")}
      if not mutant["class"] or not mutant["line"] or not mutant["mutator"]:
        raise ValueError("PIT mutant identity is incomplete")
      mutants.append(mutant)
      counts["generated"] += 1
      counts[statuses.get(status, "execution_errors")] += 1
  if not mutants:
    raise ValueError("PIT produced no mutants")
  return counts, mutants, counts["execution_errors"] > 0


def run_check(repo, check, config, attempt):
  revision = git(repo, "rev-parse", "HEAD").decode().strip()
  manifest, digest = fingerprint(repo, check, config)
  save(attempt / "inputs.json", manifest)
  log = attempt / "command.log"
  before = report_snapshot(repo, config)
  started_ns = time.time_ns()
  commands = habit_command(check["command"], repo) if config["collector"] == "habit" else None
  execution, duration = execute_habit(commands, repo, attempt) if commands else execute(check["command"], repo, log)
  reports, issues = collect_reports(repo, config, attempt, before, started_ns)
  metrics, findings, failed = None, [], False
  habit_status = None
  try:
    if config["collector"] == "maven":
      metrics, findings, failed = maven(reports)
    elif config["collector"] == "kof":
      metrics, findings, failed = kof(reports, log, config)
    elif config["collector"] == "pit":
      metrics, findings, failed = pit(reports)
    elif commands:
      metrics, findings, failed, habit_status = habit(attempt, execution)
  except (ET.ParseError, ValueError, KeyError, TypeError, OSError) as error:
    issues.append(f"collection error: {error}")
    if commands:
      habit_status = "tool-error"
  result = {
    "id": check["id"], "command": check["command"], "collector": "generic" if config["collector"] == "habit" and not commands else config["collector"],
    "revision": revision, "fingerprint": digest,
    "duration_seconds": duration, "execution": execution,
    "collection": {"status": "error" if issues else "complete", "issues": issues}, "metrics": metrics, "findings": findings,
    "evaluation": {"status": "needs-analysis" if execution["status"] == "completed" and not issues and not failed else "blocked"},
    "diagnostics": diagnostics(log),
    "artifacts": {"log": str(log), "inputs": str(attempt / "inputs.json"),
                  "evidence": str(attempt / "evidence.json"), "reports": reports},
  }
  if commands:
    result["artifacts"].update({"sensors": str(attempt / "sensors.json"), "guides": str(attempt / "guides.log"),
                               "sensor_stderr": str(attempt / "sensors.stderr.log"), "mapper_stderr": str(attempt / "mapper.stderr.log")})
    result["evaluation"]["habit_status"] = habit_status
  if result["collector"] == "generic":
    result["conclusion"] = conclusion(log)
  if config["collector"] == "pit" and metrics:
    result["evaluation"]["unclassified_mutants"] = metrics["survived"] + metrics["no_coverage"]
  save(attempt / "evidence.json", result)
  return result


def bounded(summary):
  value = json.loads(json.dumps(summary))
  if len(encoded(value)) <= LIMIT:
    return encoded(value)
  value["summary_truncated"] = True
  for check in value["checks"]:
    for field in ("findings", "diagnostics"):
      if len(check[field]) > 3:
        check[field + "_omitted"] = len(check[field]) - 3
        check[field] = check[field][:3]
    reports = check["artifacts"]["reports"]
    if len(reports) > 3:
      check["artifacts"]["reports_omitted"] = len(reports) - 3
      check["artifacts"]["reports"] = reports[:3]
  def clip(item):
    if isinstance(item, str):
      return item if len(item.encode("utf-8")) <= 1000 else item[:200] + "… [see evidence]"
    if isinstance(item, list):
      return [clip(i) for i in item[:8]]
    if isinstance(item, dict):
      return {k: clip(v) for k, v in item.items()}
    return item
  value["checks"] = [clip(c) for c in value["checks"]]
  while len(encoded(value)) > LIMIT and value["checks"]:
    value["checks"].pop()
    value["checks_omitted"] = value.get("checks_omitted", 0) + 1
  return encoded(value)


def main():
  def cancel(signum, frame):
    raise KeyboardInterrupt

  signal.signal(signal.SIGTERM, cancel)
  parser = argparse.ArgumentParser(description="Run selected local checks once; collect evidence without updating workflow gates.")
  parser.add_argument("--repo", type=Path, required=True)
  parser.add_argument("--inventory", type=Path, required=True)
  parser.add_argument("--config", type=Path, required=True)
  parser.add_argument("--phase", choices=PHASES, required=True)
  parser.add_argument("--role", required=True)
  parser.add_argument("--check-id", action="append")
  args = parser.parse_args()
  try:
    repo = args.repo.resolve(strict=True)
    if not args.config.resolve().is_relative_to(repo / ".agent/tmp"):
      raise ValueError("collector configuration must be under the repository .agent/tmp")
    inventory = json.loads(args.inventory.read_text(encoding="utf-8"))
    if not validation_plan_is_valid(inventory):
      raise ValueError("invalid existing validation inventory")
    config = json.loads(args.config.read_text(encoding="utf-8"))
    if PHASES[args.phase] != args.role:
      raise ValueError("role does not own the active phase")
    selected = [c for c in inventory["checks"] if c["status"] == "selected"
                and c["execution"] == "local" and c["owner"] == args.role]
    if args.check_id:
      if set(args.check_id) - {c["id"] for c in selected}:
        raise ValueError("check IDs must be selected locally for the active role")
      selected = [c for c in selected if c["id"] in args.check_id]
    for check in selected:
      if not isinstance(config, dict) or not isinstance(config.get(check["id"]), dict):
        raise ValueError("each selected check needs explicit collector configuration")
      if config[check["id"]]["collector"] not in REPORT_FORMATS:
        raise ValueError("unsupported collector")
      settings = config[check["id"]]
      for pattern in settings.get("inputs", []):
        if not isinstance(pattern, str) or not pattern or Path(pattern).is_absolute() or ".." in Path(pattern).parts:
          raise ValueError("input globs must stay inside the repository")
      for report in settings.get("reports", []):
        pattern = report["glob"]
        if not isinstance(pattern, str) or not pattern or Path(pattern).is_absolute() or ".." in Path(pattern).parts:
          raise ValueError("report globs must stay inside the repository")
        if report["format"] not in ("junit", "jacoco", "kof", "pit", "artifact"):
          raise ValueError("unknown report format")
        if report["format"] not in REPORT_FORMATS[settings["collector"]]:
          raise ValueError(
            f"check {check['id']}: collector {settings['collector']} does not accept "
            f"report format {report['format']} ({pattern}); supported formats: "
            + ", ".join(REPORT_FORMATS[settings["collector"]])
          )
        if "required" in report and not isinstance(report["required"], bool):
          raise ValueError("required must be boolean")
    started = time.monotonic()
    root = repo / ".agent/tmp/validation"
    root.mkdir(parents=True, exist_ok=True)
    run = Path(tempfile.mkdtemp(prefix=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S-"), dir=root))
    results = []
    for index, check in enumerate(selected):
      attempt = run / f"{index + 1:03d}"
      attempt.mkdir()
      results.append(run_check(repo, check, config[check["id"]], attempt))
      if results[-1]["execution"]["status"] == "cancelled":
        break
    summary = {"phase": args.phase, "role": args.role, "checks": results, "evidence": str(run / "summary.json"),
               "duration_seconds": time.monotonic() - started, "selected_count": len(selected), "executed_count": len(results),
               "blocked_count": sum(c["evaluation"]["status"] == "blocked" for c in results),
               "command_invocations": sum(c["execution"]["invocations"] for c in results),
               "log_bytes": sum(Path(c["artifacts"]["log"]).stat().st_size for c in results)}
    save(run / "summary.json", summary)
    sys.stdout.buffer.write(bounded(summary))
    return int(any(c["evaluation"]["status"] == "blocked" for c in results))
  except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
    sys.stdout.buffer.write(encoded({"error": str(error)[:2000], "evaluation": {"status": "blocked"}}))
    return 2


if __name__ == "__main__":
  sys.exit(main())
