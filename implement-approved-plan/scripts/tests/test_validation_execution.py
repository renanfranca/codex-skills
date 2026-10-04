import json
import os
from pathlib import Path
import shlex
import signal
import subprocess
import sys
import tempfile
import time
import unittest


RUNNER = Path(__file__).resolve().parents[1] / "run_validation.py"


class ValidationExecutionTest(unittest.TestCase):
  def setUp(self):
    self.directory = tempfile.TemporaryDirectory()
    self.addCleanup(self.directory.cleanup)
    self.root = Path(self.directory.name)
    subprocess.run(["git", "init", "-q", str(self.root)], check=True)
    subprocess.run(["git", "-C", str(self.root), "-c", "user.name=Fixture",
                    "-c", "user.email=fixture@example.test", "commit", "--allow-empty", "-qm", "fixture"], check=True)
    self.tmp = self.root / ".agent/tmp"
    self.tmp.mkdir(parents=True)

  def command(self, code, name="check.py"):
    script = self.root / name
    script.write_text(code, encoding="utf-8")
    return f"{shlex.quote(sys.executable)} {shlex.quote(str(script))}"

  def arguments(self, checks, config, phase="initial-validating", role="validator"):
    inventory = self.tmp / "inventory.json"
    checks = list(checks)
    for kind, owner in (("sonar", "validator"), ("mutation", "mutation-analyst"), ("habit", "habit-curator")):
      if not any(c["kind"] == kind for c in checks):
        checks.append({"id": kind, "kind": kind, "status": "skipped", "execution": "none", "command": "",
                       "source": "fixture", "owner": owner, "reason": "not configured"})
    if not any(c["kind"] == "verify" for c in checks):
      checks.append({"id": "verify", "kind": "verify", "status": "skipped", "execution": "none", "command": "",
                     "source": "fixture", "owner": "validator", "reason": "not configured"})
    inventory.write_text(json.dumps({"checks": checks}), encoding="utf-8")
    path = self.tmp / "collectors.json"
    path.write_text(json.dumps(config), encoding="utf-8")
    return [sys.executable, str(RUNNER), "--repo", str(self.root),
            "--inventory", str(inventory), "--config", str(path), "--phase", phase, "--role", role]

  def check(self, command, check_id="verify", kind="verify", owner="validator", execution="local"):
    return {"id": check_id, "kind": kind, "status": "selected", "execution": execution,
            "command": command, "source": "fixture", "owner": owner, "reason": ""}

  def run_checks(self, checks, config, phase="initial-validating", role="validator", extra=()):
    result = subprocess.run(self.arguments(checks, config, phase, role) + list(extra),
                            capture_output=True, text=True, timeout=20)
    self.assertIn(result.returncode, (0, 1), result.stderr)
    self.assertLessEqual(len(result.stdout.encode("utf-8")), 16384)
    return result, json.loads(result.stdout)

  def test_complete_large_log_and_compact_traceable_evidence(self):
    command = self.command("print('x' * 300000)\nprint('ERROR relevant diagnosis')\n")

    result, summary = self.run_checks([self.check(command)], {"verify": {"collector": "generic"}})

    self.assertEqual(0, result.returncode)
    check = summary["checks"][0]
    self.assertEqual(command, check["command"])
    self.assertEqual(300026, Path(check["artifacts"]["log"]).stat().st_size)
    self.assertEqual("completed", check["execution"]["status"])
    self.assertEqual(0, check["execution"]["exit_code"])
    self.assertEqual("needs-analysis", check["evaluation"]["status"])
    self.assertIsNone(check["metrics"])
    self.assertIn("ERROR relevant diagnosis", check["diagnostics"])
    self.assertEqual(40, len(check["revision"]))
    self.assertEqual(64, len(check["fingerprint"]))
    self.assertEqual(1, check["execution"]["invocations"])
    self.assertGreaterEqual(check["duration_seconds"], 0)
    self.assertTrue(Path(check["artifacts"]["evidence"]).is_file())
    self.assertTrue(Path(check["artifacts"]["inputs"]).is_file())

  def test_incompatible_report_formats_reject_the_whole_run_before_commands(self):
    supported = {
      "maven": {"junit", "jacoco", "artifact"}, "kof": {"kof", "artifact"},
      "pit": {"pit", "artifact"}, "generic": {"artifact"}, "habit": {"artifact"},
    }
    for collector, formats in supported.items():
      for report_format in {"junit", "jacoco", "kof", "pit", "artifact"} - formats:
        with self.subTest(collector=collector, report_format=report_format):
          checks = [self.check("touch first-ran", "first"), self.check("touch invalid-ran")]
          config = {"first": {"collector": "generic"}, "verify": {
            "collector": collector, "reports": [{"glob": "report.xml", "format": report_format}],
          }}

          result = subprocess.run(self.arguments(checks, config), capture_output=True, text=True)

          self.assertEqual(2, result.returncode, result.stdout)
          error = json.loads(result.stdout)["error"]
          for detail in ("verify", collector, report_format, "report.xml"):
            self.assertIn(detail, error)
          self.assertFalse((self.root / "first-ran").exists())
          self.assertFalse((self.root / "invalid-ran").exists())

  def test_generic_conclusion_is_a_bounded_utf8_tail_with_the_complete_log(self):
    for ending in ("one\ntwo\nthree\nfour\nfive\n", "á" * 400 + "\nconclusão final\n"):
      with self.subTest(ending=ending[-20:]):
        output = "ignored early output\n" + ending
        command = self.command(f"print({output!r}, end='')\n")

        result, summary = self.run_checks([self.check(command)], {"verify": {"collector": "generic"}})

        self.assertEqual(0, result.returncode)
        check = summary["checks"][0]
        conclusion = check["conclusion"]
        self.assertLessEqual(len(conclusion.splitlines()), 4)
        self.assertLessEqual(len(conclusion.encode("utf-8")), 512)
        self.assertTrue(conclusion.endswith(ending.rstrip().splitlines()[-1]))
        self.assertNotIn("ignored early output", conclusion)
        self.assertEqual(output, Path(check["artifacts"]["log"]).read_text())
        self.assertEqual(conclusion, json.loads(Path(check["artifacts"]["evidence"]).read_text())["conclusion"])

  def test_invalid_required_xml_is_parsed_by_its_collector_and_retained(self):
    for collector, report_format in (("maven", "junit"), ("maven", "jacoco"), ("pit", "pit")):
      with self.subTest(collector=collector, report_format=report_format):
        command = self.command("from pathlib import Path\nPath('report.xml').write_text('<broken')\n"
                               "Path('tests.xml').write_text('<testsuite tests=\"1\"/>')\n")
        reports = [{"glob": "report.xml", "format": report_format, "required": True}]
        if report_format == "jacoco":
          reports.append({"glob": "tests.xml", "format": "junit", "required": True})

        result, summary = self.run_checks([self.check(command)], {"verify": {"collector": collector, "reports": reports}})

        self.assertEqual(1, result.returncode)
        check = summary["checks"][0]
        self.assertEqual(collector, check["collector"])
        self.assertEqual("completed", check["execution"]["status"])
        self.assertEqual("error", check["collection"]["status"])
        self.assertEqual("blocked", check["evaluation"]["status"])
        self.assertIn("collection error", " ".join(check["collection"]["issues"]))
        copied = next(r for r in check["artifacts"]["reports"] if r["format"] == report_format)
        self.assertEqual("<broken", Path(copied["path"]).read_text())

  def test_earlier_shell_and_pipeline_failures_survive_later_success_without_retries(self):
    for command in ("false; printf 'later success\\n'", "false | cat; printf 'later success\\n'"):
      with self.subTest(command=command):
        result, summary = self.run_checks([self.check(command)], {"verify": {"collector": "generic"}})

        self.assertEqual(1, result.returncode)
        check = summary["checks"][0]
        self.assertEqual(0, check["execution"]["exit_code"])
        self.assertEqual("failed", check["execution"]["status"])
        self.assertIn(1, check["execution"]["shell_failures"])
        self.assertEqual(1, check["execution"]["invocations"])
        self.assertIn("later success", Path(check["artifacts"]["log"]).read_text())

  def test_only_selected_local_checks_of_active_role_run_in_order(self):
    first = self.command("from pathlib import Path\nPath('order').write_text('first')\n", "first.py")
    second = self.command("from pathlib import Path\nassert Path('order').read_text() == 'first'\nPath('order').write_text('first,second')\n", "second.py")
    checks = [self.check(first, "first"), self.check("exit 8", "ci", execution="ci", owner="coordinator"),
              self.check("exit 9", "mutation", kind="mutation", owner="mutation-analyst"),
              self.check(second, "second")]

    result, summary = self.run_checks(checks, {"first": {"collector": "generic"}, "second": {"collector": "generic"}})

    self.assertEqual(0, result.returncode)
    self.assertEqual(["first", "second"], [c["id"] for c in summary["checks"]])
    self.assertEqual("first,second", (self.root / "order").read_text())
    rejected = subprocess.run(self.arguments(checks, {}, role="mutation-analyst"), capture_output=True)
    self.assertEqual(2, rejected.returncode)

  def test_cancellation_preserves_log_and_blocks_without_running_remaining_checks(self):
    command = self.command("from pathlib import Path\nimport time\nprint('started', flush=True)\nPath('started').touch()\ntime.sleep(30)\nPath('finished').touch()\n")
    arguments = self.arguments([self.check(command), self.check("touch unintended", "later")],
                               {"verify": {"collector": "generic"}, "later": {"collector": "generic"}})
    process = subprocess.Popen(arguments, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    deadline = time.monotonic() + 5
    while not (self.root / "started").exists() and time.monotonic() < deadline:
      time.sleep(0.01)
    self.assertTrue((self.root / "started").exists())

    process.send_signal(signal.SIGTERM)
    output, error = process.communicate(timeout=5)

    self.assertEqual(1, process.returncode, error)
    summary = json.loads(output)
    self.assertEqual("cancelled", summary["checks"][0]["execution"]["status"])
    self.assertEqual("blocked", summary["checks"][0]["evaluation"]["status"])
    self.assertEqual("started\n", Path(summary["checks"][0]["artifacts"]["log"]).read_text())
    self.assertFalse((self.root / "finished").exists())
    self.assertFalse((self.root / "unintended").exists())

  def test_maven_aggregates_leaf_suites_once_and_keeps_coverage_separate(self):
    command = self.command("""from pathlib import Path
p = Path('target/surefire-reports'); p.mkdir(parents=True)
(p/'TEST-suite.xml').write_text('<testsuites tests="99"><testsuite name="outer" tests="99"><testsuite name="leaf" tests="3" failures="1" errors="0" skipped="1"><testcase name="broken"><failure message="assertion failed"/></testcase></testsuite></testsuite></testsuites>')
p = Path('target/failsafe-reports'); p.mkdir(parents=True)
(p/'TEST-it.xml').write_text('<testsuite name="it" tests="2" failures="0" errors="0" skipped="0"/>')
(p/'failsafe-summary.xml').write_text('<failsafe-summary><completed>2</completed><errors>0</errors><failures>0</failures><skipped>0</skipped></failsafe-summary>')
Path('target/jacoco.xml').write_text('<report><package><counter type="LINE" missed="99" covered="99"/></package><counter type="LINE" missed="1" covered="9"/></report>')
""")
    reports = [{"glob": "target/*-reports/*.xml", "format": "junit", "required": True},
               {"glob": "target/surefire-reports/*.xml", "format": "junit", "required": True},
               {"glob": "target/jacoco.xml", "format": "jacoco", "required": False}]

    result, summary = self.run_checks([self.check(command)], {"verify": {"collector": "maven", "reports": reports}})

    self.assertEqual(1, result.returncode)
    check = summary["checks"][0]
    self.assertEqual(0, check["execution"]["exit_code"])
    self.assertEqual("complete", check["collection"]["status"])
    self.assertEqual({"tests": 5, "failures": 1, "errors": 0, "skipped": 1}, check["metrics"]["tests"])
    self.assertEqual({"missed": 1, "covered": 9}, check["metrics"]["coverage"][0]["counters"]["LINE"])
    self.assertEqual("blocked", check["evaluation"]["status"])
    self.assertEqual(4, len(check["artifacts"]["reports"]))

  def test_missing_invalid_or_stale_required_reports_never_support_green(self):
    for state in ("missing", "invalid", "stale", "undeclared"):
      with self.subTest(state=state):
        path = self.root / "report.xml"
        path.unlink(missing_ok=True)
        code = "pass\n"
        if state == "stale":
          path.write_text('<testsuite tests="3" failures="0"/>')
          os.utime(path, (1, 1))
        if state == "invalid":
          code = "from pathlib import Path\nPath('report.xml').write_text('<broken')\n"
        command = self.command(code)
        reports = [] if state == "undeclared" else [{"glob": "report.xml", "format": "junit", "required": True}]

        result, summary = self.run_checks([self.check(command)], {"verify": {"collector": "maven", "reports": reports}})

        self.assertEqual(1, result.returncode)
        self.assertEqual("error", summary["checks"][0]["collection"]["status"])
        self.assertEqual("blocked", summary["checks"][0]["evaluation"]["status"])

  def test_kof_preserves_each_suite_and_target_failure_despite_later_success(self):
    command = self.command("""from pathlib import Path
Path('jvm.log').write_text('Suite: broken.kf\\nFAIL broken\\n1 failed of 2 tests\\nsuite broken: 0 passed, 1 failed\\n0 passed, 1 failed\\nSuite: good.kf\\n0 failed of 3 tests\\nsuite good: 1 passed, 0 failed\\n1 passed, 0 failed\\n')
Path('js.log').write_text('Suite: js.kf\\n0 failed of 4 tests\\n1 passed, 0 failed\\n')
""")
    reports = [{"glob": "jvm.log", "format": "kof", "target": "jvm", "required": True},
               {"glob": "js.log", "format": "kof", "target": "js", "required": True}]

    result, summary = self.run_checks([self.check(command)], {"verify": {"collector": "kof", "reports": reports}})

    self.assertEqual(1, result.returncode)
    check = summary["checks"][0]
    self.assertEqual("completed", check["execution"]["status"])
    self.assertEqual(5, check["metrics"]["targets"]["jvm"]["tests"])
    self.assertEqual(1, check["metrics"]["targets"]["jvm"]["failed"])
    self.assertEqual(4, check["metrics"]["targets"]["js"]["tests"])
    self.assertEqual(0, check["metrics"]["targets"]["js"]["failed"])
    self.assertEqual(3, len(check["findings"]))
    self.assertEqual("blocked", check["evaluation"]["status"])

  def test_pit_keeps_individual_survivors_and_uncovered_mutants_for_chat_analysis(self):
    command = self.command("""from pathlib import Path
p = Path('target/pit-reports'); p.mkdir(parents=True)
(p/'mutations.xml').write_text('<mutations><mutation status="KILLED"><mutatedClass>demo.A</mutatedClass><lineNumber>1</lineNumber><mutator>M</mutator></mutation><mutation status="SURVIVED"><mutatedClass>demo.A</mutatedClass><lineNumber>2</lineNumber><mutator>M</mutator></mutation><mutation status="NO_COVERAGE"><mutatedClass>demo.A</mutatedClass><lineNumber>3</lineNumber><mutator>M</mutator></mutation></mutations>')
(p/'index.html').write_text('<html>report</html>')
""")
    config = {"pit": {"collector": "pit", "reports": [
      {"glob": "target/pit-reports/mutations.xml", "format": "pit", "required": True},
      {"glob": "target/pit-reports/*.html", "format": "artifact", "required": True}]}}

    result, summary = self.run_checks([self.check(command, "pit", "mutation", "mutation-analyst")], config,
                                      "mutation-testing", "mutation-analyst")

    self.assertEqual(0, result.returncode)
    check = summary["checks"][0]
    self.assertEqual({"generated": 3, "killed": 1, "survived": 1, "no_coverage": 1, "execution_errors": 0}, check["metrics"])
    self.assertEqual(["KILLED", "SURVIVED", "NO_COVERAGE"], [m["status"] for m in check["findings"]])
    self.assertEqual("needs-analysis", check["evaluation"]["status"])
    self.assertEqual(2, check["evaluation"]["unclassified_mutants"])
    self.assertEqual(2, len(check["artifacts"]["reports"]))

  def test_invalid_pit_run_cannot_be_accepted_even_with_zero_exit(self):
    for xml in ('<mutations/>', '<mutations><mutation status="RUN_ERROR"><mutatedClass>A</mutatedClass><lineNumber>1</lineNumber><mutator>M</mutator></mutation></mutations>', '<mutations><mutation status="SURVIVED"/></mutations>'):
      with self.subTest(xml=xml):
        command = self.command(f"from pathlib import Path\nPath('pit.xml').write_text({xml!r})\n")
        config = {"pit": {"collector": "pit", "reports": [{"glob": "pit.xml", "format": "pit", "required": True}]}}

        result, summary = self.run_checks([self.check(command, "pit", "mutation", "mutation-analyst")], config,
                                          "mutation-testing", "mutation-analyst")

        self.assertEqual(1, result.returncode)
        self.assertEqual("blocked", summary["checks"][0]["evaluation"]["status"])

  def test_habit_guidance_is_retained_and_each_native_stage_runs_once_with_config(self):
    directory = self.root / "bin"
    directory.mkdir()
    for name, code in {
      "habit-hooks": "raise AssertionError('wrapper should not run')",
      "habit-sensors": "import sys, json\nfrom pathlib import Path\nassert sys.argv[1:] == ['--all', '--config', 'custom.toml']\nPath('sensor-calls').write_text('one')\nprint(json.dumps([{'smell': 'nested', 'locations': []}]))",
      "habit-mapper": "import sys, json\nfrom pathlib import Path\nassert sys.argv[1:] == ['--config', 'custom.toml']\nassert json.load(sys.stdin)[0]['smell'] == 'nested'\nPath('mapper-calls').write_text('one')\nprint('Consider simplifying this function')",
    }.items():
      script = directory / name
      script.write_text(f"#!{sys.executable}\n{code}\n")
      script.chmod(0o755)
    command = f"{shlex.quote(str(directory / 'habit-hooks'))} --all --config custom.toml"

    result, summary = self.run_checks([self.check(command, "habit", "habit", "habit-curator")],
                                      {"habit": {"collector": "habit"}}, "habit-checking", "habit-curator")

    self.assertEqual(0, result.returncode)
    check = summary["checks"][0]
    self.assertEqual(1, check["metrics"]["raw_findings"])
    self.assertEqual([0, 0], [s["exit_code"] for s in check["execution"]["stages"]])
    self.assertEqual([1, 1], [s["invocations"] for s in check["execution"]["stages"]])
    self.assertEqual("needs-analysis", check["evaluation"]["status"])
    self.assertEqual("guidance", check["evaluation"]["habit_status"])
    self.assertIn("Consider simplifying", Path(check["artifacts"]["guides"]).read_text())
    self.assertEqual("nested", json.loads(Path(check["artifacts"]["sensors"]).read_text())[0]["smell"])

  def test_habit_distinguishes_enforcement_from_any_stage_tool_failure(self):
    directory = self.root / "bin"
    directory.mkdir()
    (directory / "habit-hooks").write_text('')
    (directory / "habit-hooks").chmod(0o755)
    for sensor_code, mapper_code, expected in ((0, 1, "blocked"), (1, 0, "tool-error"), (0, 2, "tool-error")):
      with self.subTest(sensor=sensor_code, mapper=mapper_code):
        for name, code in {"habit-sensors": f"print('[{{\"smell\": \"nested\"}}]')\nraise SystemExit({sensor_code})",
                           "habit-mapper": f"import sys\nsys.stdin.read()\nprint('guide')\nraise SystemExit({mapper_code})"}.items():
          script = directory / name
          script.write_text(f"#!{sys.executable}\n{code}\n")
          script.chmod(0o755)

        result, summary = self.run_checks([self.check(str(directory / "habit-hooks"), "habit", "habit", "habit-curator")],
                                          {"habit": {"collector": "habit"}}, "habit-checking", "habit-curator")

        self.assertEqual(1, result.returncode)
        check = summary["checks"][0]
        self.assertEqual(expected, check["evaluation"]["habit_status"])
        self.assertEqual([sensor_code, mapper_code], [s["exit_code"] for s in check["execution"]["stages"]])
        self.assertEqual("blocked", check["evaluation"]["status"])

  def test_large_findings_are_compact_but_identification_metrics_and_full_evidence_remain(self):
    command = self.command("from pathlib import Path\nm = '<mutation status=\"SURVIVED\"><mutatedClass>A</mutatedClass><lineNumber>1</lineNumber><mutator>M</mutator><description>' + ('z' * 2000) + '</description></mutation>'\nPath('pit.xml').write_text('<mutations>' + m * 100 + '</mutations>')\n")
    config = {"pit": {"collector": "pit", "reports": [{"glob": "pit.xml", "format": "pit", "required": True}]}}

    result, summary = self.run_checks([self.check(command, "pit", "mutation", "mutation-analyst")], config,
                                      "mutation-testing", "mutation-analyst")

    check = summary["checks"][0]
    self.assertEqual("pit", check["id"])
    self.assertEqual(100, check["metrics"]["survived"])
    self.assertEqual(100, check["evaluation"]["unclassified_mutants"])
    complete = json.loads(Path(check["artifacts"]["evidence"]).read_text())
    self.assertEqual(100, len(complete["findings"]))
    self.assertEqual(2000, len(complete["findings"][0]["description"]))
    self.assertTrue(summary["summary_truncated"])

  def test_report_failure_evidence_cannot_be_hidden_by_inconsistent_maven_totals(self):
    command = self.command("""from pathlib import Path
p = Path('target/failsafe-reports'); p.mkdir(parents=True)
(p/'TEST-it.xml').write_text('<testsuite tests="1" failures="0"><testcase name="broken"><failure message="failed"/></testcase></testsuite>')
(p/'failsafe-summary.xml').write_text('<failsafe-summary result="254"><completed>1</completed><errors>0</errors><failures>1</failures><skipped>0</skipped></failsafe-summary>')
""")

    result, summary = self.run_checks([self.check(command)], {"verify": {"collector": "maven", "reports": [
      {"glob": "target/failsafe-reports/*.xml", "format": "junit", "required": True}]}})

    self.assertEqual(1, result.returncode)
    self.assertEqual("blocked", summary["checks"][0]["evaluation"]["status"])

  def test_invalid_configuration_blocks_before_any_command_or_outside_config_write(self):
    command = self.command("from pathlib import Path\nPath('unintended').touch()\n")
    arguments = self.arguments([self.check(command)], {"verify": {"collector": "maven", "reports": [
      {"glob": "../*.xml", "format": "junit", "required": True}]}})

    result = subprocess.run(arguments, capture_output=True)

    self.assertEqual(2, result.returncode)
    self.assertFalse((self.root / "unintended").exists())

  def test_input_fingerprint_tracks_explicit_ignored_inputs_and_preserves_effective_command(self):
    (self.root / '.gitignore').write_text('runtime.conf\n')
    (self.root / 'runtime.conf').write_text('one')
    command = self.command("print('ok')\n")
    config = {"verify": {"collector": "generic", "inputs": ["runtime.conf"]}}
    _, first = self.run_checks([self.check(command)], config)
    (self.root / 'runtime.conf').write_text('two')

    _, second = self.run_checks([self.check(command)], config)

    self.assertNotEqual(first["checks"][0]["fingerprint"], second["checks"][0]["fingerprint"])
    self.assertEqual(command, second["checks"][0]["command"])
    manifest = json.loads(Path(second["checks"][0]["artifacts"]["inputs"]).read_text())
    self.assertIn('runtime.conf', [f['path'] for f in manifest['files']])

  def test_custom_habit_commands_use_generic_execution_without_second_scan_or_metrics(self):
    command = self.command("from pathlib import Path\nPath('calls').write_text('one')\nprint('guidance from custom tool')\n")

    result, summary = self.run_checks([self.check(command, "custom", "habit", "habit-curator")],
                                      {"custom": {"collector": "habit"}}, "habit-checking", "habit-curator")

    self.assertEqual(0, result.returncode)
    check = summary['checks'][0]
    self.assertEqual('generic', check['collector'])
    self.assertIsNone(check['metrics'])
    self.assertEqual('needs-analysis', check['evaluation']['status'])
    self.assertEqual(1, check['execution']['invocations'])
    self.assertEqual('one', (self.root / 'calls').read_text())

  def test_kof_keeps_directory_suites_and_leaves_unknown_test_counts_unknown(self):
    command = self.command("print('PASS a.kf\\nsuite .: 1 passed, 0 failed\\nsuite integration: 0 passed, 1 failed\\n1 passed, 1 failed')\n")

    result, summary = self.run_checks([self.check(command)], {"verify": {"collector": "kof", "target": "native"}})

    self.assertEqual(1, result.returncode)
    metrics = summary['checks'][0]['metrics']['targets']['native']
    self.assertIsNone(metrics['tests'])
    self.assertIsNone(metrics['failed'])
    self.assertEqual(1, metrics['files_failed'])
    self.assertEqual(['.', 'integration'], [s['suite'] for s in metrics['directory_suites']])

  def test_explicit_focal_manifest_in_workflow_scratch_is_fingerprinted(self):
    manifest = self.tmp / 'focal.json'
    manifest.write_text('{"target": "A", "test_blob": "one"}')
    command = self.command("print('ok')\n")
    config = {"verify": {"collector": "generic", "inputs": ['.agent/tmp/focal.json']}}
    _, first = self.run_checks([self.check(command)], config)
    manifest.write_text('{"target": "A", "test_blob": "two"}')

    _, second = self.run_checks([self.check(command)], config)

    self.assertNotEqual(first['checks'][0]['fingerprint'], second['checks'][0]['fingerprint'])

  def test_invalid_habit_json_preserves_both_stage_codes_and_reports_collection_tool_error(self):
    directory = self.root / 'bin'
    directory.mkdir()
    for name, code in {'habit-hooks': 'pass', 'habit-sensors': "print('invalid json')",
                       'habit-mapper': "import sys\nsys.stdin.read()\nprint('invalid input')\nraise SystemExit(2)"}.items():
      path = directory / name
      path.write_text(f'#!{sys.executable}\n{code}\n')
      path.chmod(0o755)

    result, summary = self.run_checks([self.check(str(directory / 'habit-hooks'), 'habit', 'habit', 'habit-curator')],
                                      {'habit': {'collector': 'habit'}}, 'habit-checking', 'habit-curator')

    self.assertEqual(1, result.returncode)
    check = summary['checks'][0]
    self.assertEqual('error', check['collection']['status'])
    self.assertEqual('tool-error', check['evaluation']['habit_status'])
    self.assertEqual([0, 2], [s['exit_code'] for s in check['execution']['stages']])
    self.assertEqual('invalid json\n', Path(check['artifacts']['sensors']).read_text())

  def test_opaque_maven_artifacts_do_not_suppress_actual_summary_metrics(self):
    command = self.command("""from pathlib import Path
p = Path('target/failsafe-reports'); p.mkdir(parents=True)
(p/'TEST-it.xml').write_text('<testsuite tests="3"/>')
(p/'failsafe-summary.xml').write_text('<failsafe-summary><completed>3</completed><errors>0</errors><failures>0</failures><skipped>0</skipped></failsafe-summary>')
""")

    _, summary = self.run_checks([self.check(command)], {'verify': {'collector': 'maven', 'reports': [
      {'glob': 'target/failsafe-reports/failsafe-summary.xml', 'format': 'junit', 'required': True},
      {'glob': 'target/failsafe-reports/TEST-it.xml', 'format': 'artifact', 'required': False}]}})

    self.assertEqual(3, summary['checks'][0]['metrics']['tests']['tests'])

  def test_canonical_habit_path_resolves_in_the_consuming_repository(self):
    directory = self.root / 'bin'
    directory.mkdir()
    for name, code in {'habit-hooks': 'pass', 'habit-sensors': "print('[]')",
                       'habit-mapper': "import sys\nsys.stdin.read()\nprint('native output')"}.items():
      path = directory / name
      path.write_text(f'#!{sys.executable}\n{code}\n')
      path.chmod(0o755)

    result, summary = self.run_checks([self.check('./bin/habit-hooks', 'habit', 'habit', 'habit-curator')],
                                      {'habit': {'collector': 'habit'}}, 'habit-checking', 'habit-curator')

    self.assertEqual(0, result.returncode)
    self.assertEqual('habit', summary['checks'][0]['collector'])
    self.assertEqual(0, summary['checks'][0]['metrics']['raw_findings'])
    self.assertEqual(2, len(summary['checks'][0]['execution']['stages']))


if __name__ == "__main__":
  unittest.main()
