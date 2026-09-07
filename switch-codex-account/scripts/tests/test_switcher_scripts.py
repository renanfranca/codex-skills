import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import unittest


SKILL_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = SKILL_ROOT / "scripts"


class RegistryHelperTests(unittest.TestCase):
  def setUp(self):
    self.temporary = tempfile.TemporaryDirectory()
    self.root = Path(self.temporary.name)
    self.registry = self.root / "registry.json"
    self.registry.write_text(
      json.dumps(
        {
          "schema_version": 3,
          "active_account_key": "example-account-b",
          "accounts": [
            {
              "account_key": "example-account-a",
              "email": "first@example.test",
              "alias": "",
              "plan": "plus",
            },
            {
              "account_key": "example-account-b",
              "email": "second@example.test",
              "alias": "",
              "plan": "plus",
            },
          ],
        }
      ),
      encoding="utf-8",
    )

  def tearDown(self):
    self.temporary.cleanup()

  def helper(self, *arguments):
    return subprocess.run(
      ["node", str(SCRIPTS / "registry-helper.mjs"), *arguments],
      text=True,
      capture_output=True,
      check=False,
    )

  def test_suggested_pair_puts_active_account_first(self):
    result = self.helper("suggested-pair", str(self.registry))
    self.assertEqual(0, result.returncode, result.stderr)
    rows = result.stdout.splitlines()
    self.assertTrue(rows[0].startswith("example-account-b\tsecond@example.test"))
    self.assertTrue(rows[1].startswith("example-account-a\tfirst@example.test"))

  def test_adopts_legacy_portuguese_mapping(self):
    config = self.root / "config.json"
    config.write_text(
      json.dumps(
        {
          "accounts": {
            "conta-a": {"account_key": "example-account-a"},
            "conta-b": {"account_key": "example-account-b"},
          }
        }
      ),
      encoding="utf-8",
    )
    result = self.helper("existing-pair", str(self.registry), str(config))
    self.assertEqual(0, result.returncode, result.stderr)
    self.assertEqual(
      ["example-account-a", "example-account-b"],
      [line.split("\t", 1)[0] for line in result.stdout.splitlines()],
    )

  def test_rejects_duplicate_email_selection(self):
    value = json.loads(self.registry.read_text(encoding="utf-8"))
    value["accounts"][1]["email"] = "FIRST@example.test"
    self.registry.write_text(json.dumps(value), encoding="utf-8")
    result = self.helper("selected-pair", str(self.registry), "1", "2")
    self.assertNotEqual(0, result.returncode)
    self.assertIn("duplicate emails", result.stderr)

  def test_rejects_an_email_that_matches_an_unselected_alias(self):
    value = json.loads(self.registry.read_text(encoding="utf-8"))
    value["accounts"].append(
      {
        "account_key": "example-account-c",
        "email": "third@example.test",
        "alias": "first@example.test-secondary",
        "plan": "plus",
      }
    )
    self.registry.write_text(json.dumps(value), encoding="utf-8")
    result = self.helper("selected-pair", str(self.registry), "1", "2")
    self.assertNotEqual(0, result.returncode)
    self.assertIn("ambiguous", result.stderr)


class GeneratedConfigTests(unittest.TestCase):
  def test_writer_creates_only_the_expected_schema(self):
    with tempfile.TemporaryDirectory() as temporary:
      output = Path(temporary) / "config.json"
      environment = os.environ.copy()
      environment.update(
        {
          "SWITCHER_CONFIG_DISTRO": "Example-Distro",
          "SWITCHER_CONFIG_CODEX_HOME_LINUX": "/mnt/c/Users/example/.codex",
          "SWITCHER_CONFIG_CODEX_HOME_WINDOWS": r"C:\Users\example\.codex",
          "SWITCHER_CONFIG_NODE_LINUX": "/home/example/bin/node",
          "SWITCHER_CONFIG_CODEX_AUTH_JS_LINUX": "/home/example/codex-auth.js",
          "SWITCHER_CONFIG_ACCOUNT_A_EMAIL": "first@example.test",
          "SWITCHER_CONFIG_ACCOUNT_A_KEY": "example-account-a",
          "SWITCHER_CONFIG_ACCOUNT_B_EMAIL": "second@example.test",
          "SWITCHER_CONFIG_ACCOUNT_B_KEY": "example-account-b",
        }
      )
      result = subprocess.run(
        ["node", str(SCRIPTS / "write-config.mjs"), str(output)],
        env=environment,
        text=True,
        capture_output=True,
        check=False,
      )
      self.assertEqual(0, result.returncode, result.stderr)
      config = json.loads(output.read_text(encoding="utf-8"))
      self.assertEqual("codex-auth 0.2.10", config["codex_auth_version"])
      self.assertEqual(2, config["schema_version"])
      self.assertEqual(10, config["force_timeout_seconds"])
      self.assertEqual(
        {"account-a", "account-b"}, set(config["accounts"].keys())
      )
      self.assertNotIn("token", output.read_text(encoding="utf-8").lower())


class DispatcherTests(unittest.TestCase):
  def setUp(self):
    self.temporary = tempfile.TemporaryDirectory()
    self.root = Path(self.temporary.name)
    self.power_shell = self.root / "powershell"
    self.scheduler = self.root / "schtasks"
    self.scheduler_log = self.root / "scheduler.log"
    self.power_shell.write_text(
      "#!/usr/bin/env bash\n"
      "if [[ \"$*\" == *'-StatusOnly'* ]]; then\n"
      "  printf '%s\\n' '{\"active\":\"account-a\",\"accounts\":{\"account-a\":true,\"account-b\":true},\"last_result\":null}'\n"
      "else\n"
      "  printf '%s\\n' '{\"status\":\"valid\",\"target\":\"account-b\"}'\n"
      "fi\n",
      encoding="utf-8",
    )
    self.scheduler.write_text(
      "#!/usr/bin/env bash\nprintf '%s\\n' \"$*\" > \"$SWITCHER_TEST_SCHEDULER_LOG\"\n",
      encoding="utf-8",
    )
    self.power_shell.chmod(0o755)
    self.scheduler.chmod(0o755)
    self.environment = os.environ.copy()
    self.environment.update(
      {
        "SWITCHER_POWERSHELL": str(self.power_shell),
        "SWITCHER_SCHTASKS": str(self.scheduler),
        "SWITCHER_CONTROLLER_WINDOWS": r"C:\Runtime\Switch-CodexAccount.ps1",
        "SWITCHER_TEST_SCHEDULER_LOG": str(self.scheduler_log),
      }
    )

  def tearDown(self):
    self.temporary.cleanup()

  def dispatch(self, operation):
    return subprocess.run(
      ["bash", str(SCRIPTS / "dispatch.sh"), operation],
      env=self.environment,
      text=True,
      capture_output=True,
      check=False,
    )

  def test_status_returns_controller_json(self):
    result = self.dispatch("status")
    self.assertEqual(0, result.returncode, result.stderr)
    self.assertEqual("account-a", json.loads(result.stdout)["active"])

  def test_switch_runs_only_the_expected_task(self):
    result = self.dispatch("account-b")
    self.assertEqual(0, result.returncode, result.stderr)
    self.assertEqual("accepted", json.loads(result.stdout)["status"])
    self.assertEqual(
      r"/Run /TN \Codex Account Switch\Account B",
      self.scheduler_log.read_text(encoding="utf-8").strip(),
    )

  def test_invalid_operation_is_rejected_before_scheduler(self):
    result = self.dispatch("automatic")
    self.assertEqual(2, result.returncode)
    self.assertFalse(self.scheduler_log.exists())


class InstallerIntegrationTests(unittest.TestCase):
  def setUp(self):
    self.temporary = tempfile.TemporaryDirectory()
    self.root = Path(self.temporary.name)
    self.fake_bin = self.root / "bin"
    self.fake_bin.mkdir()
    self.codex_home = self.root / "codex-home"
    self.runtime = self.root / "local-app-data" / "CodexAccountSwitcher"
    self.legacy_skill = self.codex_home / "skills" / "switch-codex-account"
    self.rules = self.codex_home / "rules"
    self.registry = self.codex_home / "accounts" / "registry.json"
    self.runtime.mkdir(parents=True)
    self.legacy_skill.mkdir(parents=True)
    self.rules.mkdir(parents=True)
    self.registry.parent.mkdir(parents=True)
    self.registry.write_text(
      json.dumps(
        {
          "schema_version": 3,
          "active_account_key": "example-account-a",
          "auto_switch": {"enabled": False},
          "api": {"usage": False, "account": False},
          "accounts": [
            {
              "account_key": "example-account-a",
              "email": "first@example.test",
              "alias": "",
              "plan": "plus",
            },
            {
              "account_key": "example-account-b",
              "email": "second@example.test",
              "alias": "",
              "plan": "plus",
            },
          ],
        }
      ),
      encoding="utf-8",
    )
    (self.runtime / "config.json").write_text(
      json.dumps(
        {
          "marker": "previous-runtime",
          "accounts": {
            "conta-a": {"account_key": "example-account-a"},
            "conta-b": {"account_key": "example-account-b"},
          },
        }
      ),
      encoding="utf-8",
    )
    (self.runtime / "README.md").write_text("legacy runtime documentation", encoding="utf-8")
    (self.runtime / "last-result.json").write_text('{"status":"legacy"}', encoding="utf-8")
    (self.runtime / "switch.log").write_text("legacy log", encoding="utf-8")
    (self.legacy_skill / "SKILL.md").write_text("legacy skill", encoding="utf-8")
    legacy_dispatch = self.legacy_skill / "scripts" / "dispatch.sh"
    (self.rules / "default.rules").write_text(
      f'prefix_rule(pattern=["/bin/bash", "-lc", "bash {legacy_dispatch} status"], decision="allow")\n'
      'prefix_rule(pattern=["git", "status"], decision="allow")\n',
      encoding="utf-8",
    )
    self.write_executable(
      "powershell",
      "#!/usr/bin/env bash\n"
      "case \"$*\" in\n"
      "  *UserProfile*) printf '%s\\n' 'C:\\\\Example\\\\User' ;;\n"
      "  *LocalApplicationData*) printf '%s\\n' 'C:\\\\Example\\\\LocalAppData' ;;\n"
      "  *-StatusOnly*)\n"
      "    if [[ \"${MOCK_FAIL_STATUS:-0}\" == 1 ]]; then exit 9; fi\n"
      "    printf '%s\\n' '{\"active\":\"account-a\",\"accounts\":{\"account-a\":true,\"account-b\":true},\"last_result\":null}' ;;\n"
      "  *) printf '%s\\n' '{\"status\":\"ok\"}' ;;\n"
      "esac\n",
    )
    self.write_executable("schtasks", "#!/usr/bin/env bash\nexit 0\n")
    self.write_executable(
      "wslpath",
      "#!/usr/bin/env bash\n"
      "if [[ \"$1\" == '-u' && \"$2\" == *'.codex' ]]; then printf '%s\\n' \"$MOCK_CODEX_HOME\";\n"
      "elif [[ \"$1\" == '-u' ]]; then printf '%s\\n' \"$MOCK_LOCAL_APP_DATA/CodexAccountSwitcher\";\n"
      "else printf '%s\\n' 'C:\\\\Mock\\\\Register-CodexAccountSwitcher.ps1'; fi\n",
    )
    self.write_executable(
      "codex-auth",
      "#!/usr/bin/env bash\n"
      "if [[ \"${1:-}\" == '--version' ]]; then printf '%s\\n' 'codex-auth 0.2.10'; fi\n"
      "exit 0\n",
    )
    self.environment = os.environ.copy()
    self.environment.update(
      {
        "PATH": f"{self.fake_bin}:{self.environment['PATH']}",
        "WSL_DISTRO_NAME": "Example-Distro",
        "SWITCHER_ALLOW_NON_DISCOVERY_ROOT": "1",
        "SWITCHER_POWERSHELL": str(self.fake_bin / "powershell"),
        "SWITCHER_SCHTASKS": str(self.fake_bin / "schtasks"),
        "MOCK_CODEX_HOME": str(self.codex_home),
        "MOCK_LOCAL_APP_DATA": str(self.root / "local-app-data"),
      }
    )

  def tearDown(self):
    self.temporary.cleanup()

  def write_executable(self, name, content):
    path = self.fake_bin / name
    path.write_text(content, encoding="utf-8")
    path.chmod(0o755)

  def run_script(self, name, *arguments, **environment_overrides):
    environment = self.environment.copy()
    environment.update(environment_overrides)
    return subprocess.run(
      ["bash", str(SCRIPTS / name), *arguments],
      env=environment,
      text=True,
      capture_output=True,
      check=False,
    )

  def install(self, *arguments, **environment_overrides):
    return self.run_script("install.sh", *arguments, **environment_overrides)

  def test_adopts_runtime_and_removes_only_superseded_installation(self):
    result = self.install()
    self.assertEqual(0, result.returncode, result.stderr)
    self.assertEqual("adopted", json.loads(result.stdout.splitlines()[-1])["mode"])
    config = json.loads((self.runtime / "config.json").read_text(encoding="utf-8"))
    self.assertEqual("example-account-a", config["accounts"]["account-a"]["account_key"])
    self.assertFalse(self.legacy_skill.exists())
    self.assertFalse((self.runtime / "README.md").exists())
    self.assertFalse((self.runtime / "last-result.json").exists())
    self.assertFalse((self.runtime / "switch.log").exists())
    self.assertTrue((self.runtime / "Switch-CodexAccount.ps1").is_file())
    self.assertIn("$HOME/.agents/skills", (self.rules / "switch-codex-account.rules").read_text(encoding="utf-8"))
    default_rules = (self.rules / "default.rules").read_text(encoding="utf-8")
    self.assertNotIn(str(self.legacy_skill), default_rules)
    self.assertIn("git", default_rules)

  def test_failed_status_validation_restores_previous_runtime(self):
    old_config = (self.runtime / "config.json").read_text(encoding="utf-8")
    result = self.install(MOCK_FAIL_STATUS="1")
    self.assertNotEqual(0, result.returncode)
    self.assertEqual(old_config, (self.runtime / "config.json").read_text(encoding="utf-8"))
    self.assertTrue(self.legacy_skill.exists())
    self.assertFalse((self.rules / "switch-codex-account.rules").exists())

  def test_repeated_install_preserves_the_mapping(self):
    first = self.install()
    self.assertEqual(0, first.returncode, first.stderr)
    first_config = (self.runtime / "config.json").read_text(encoding="utf-8")
    result_path = self.runtime / "last-result.json"
    log_path = self.runtime / "switch.log"
    result_path.write_text('{"status":"success"}', encoding="utf-8")
    log_path.write_text("account-a complete success", encoding="utf-8")
    second = self.install()
    self.assertEqual(0, second.returncode, second.stderr)
    self.assertEqual(
      first_config, (self.runtime / "config.json").read_text(encoding="utf-8")
    )
    self.assertEqual('{"status":"success"}', result_path.read_text(encoding="utf-8"))
    self.assertEqual("account-a complete success", log_path.read_text(encoding="utf-8"))

  def test_reconfigure_uses_the_current_account_as_account_a(self):
    result = self.install("--reconfigure")
    self.assertEqual(0, result.returncode, result.stderr)
    self.assertEqual("configured", json.loads(result.stdout.splitlines()[-1])["mode"])
    config = json.loads((self.runtime / "config.json").read_text(encoding="utf-8"))
    self.assertEqual("example-account-a", config["accounts"]["account-a"]["account_key"])

  def test_uninstall_removes_runtime_but_preserves_authentication(self):
    installed = self.install()
    self.assertEqual(0, installed.returncode, installed.stderr)
    auth = self.codex_home / "auth.json"
    auth.write_text('{"tokens":"fixture-only"}', encoding="utf-8")
    result = self.run_script("uninstall.sh")
    self.assertEqual(0, result.returncode, result.stderr)
    self.assertFalse(self.runtime.exists())
    self.assertFalse((self.rules / "switch-codex-account.rules").exists())
    self.assertTrue(auth.exists())
    self.assertTrue(self.registry.exists())
    self.assertTrue((SKILL_ROOT / "SKILL.md").exists())


class PublicPackageSafetyTests(unittest.TestCase):
  def test_package_contains_no_runtime_artifacts_or_personal_paths(self):
    forbidden_names = {"auth.json", "config.json", "last-result.json", "switch.log", "registry.json"}
    files = [
      path
      for path in SKILL_ROOT.rglob("*")
      if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc"
    ]
    self.assertFalse(forbidden_names.intersection(path.name for path in files))
    wsl_users = "/mnt/c/" + "Users/"
    windows_users = re.escape("C:\\" + "Users\\")
    personal_path = re.compile(
      rf"(?:{re.escape(wsl_users)}|{windows_users})(?!example)", re.IGNORECASE
    )
    for path in files:
      content = path.read_text(encoding="utf-8")
      self.assertIsNone(personal_path.search(content), str(path))

  def test_installer_dry_run_is_non_mutating(self):
    environment = os.environ.copy()
    environment.update(
      {
        "SWITCHER_ALLOW_NON_DISCOVERY_ROOT": "1",
        "SWITCHER_TEST_MODE": "1",
      }
    )
    result = subprocess.run(
      ["bash", str(SCRIPTS / "install.sh"), "--dry-run"],
      env=environment,
      text=True,
      capture_output=True,
      check=False,
    )
    self.assertEqual(0, result.returncode, result.stderr)
    self.assertEqual(1, json.loads(result.stdout)["skill_installations"])


if __name__ == "__main__":
  unittest.main()
