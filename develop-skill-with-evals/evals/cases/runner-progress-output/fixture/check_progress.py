#!/usr/bin/env python3
import json
import errno
import os
from pathlib import Path
import pty
import subprocess


root = Path.cwd()
runner = Path(os.environ["SKILL_EVAL_SKILL_DIR"]) / "scripts" / "run_skill_evals.py"
base = [
  "python3",
  str(runner),
  "run",
  "--skill",
  str(root / "sample-skill"),
  "--case",
  "write-result",
  "--source",
  "working-tree",
  "--codex-command",
  str(root / "fake-codex"),
  "--artifacts-dir",
  str(root / "nested-artifacts"),
]
expected = [
  "Preparing run",
  "Case write-result: preparing workspace",
  "Case write-result: running executor",
  "Case write-result: running mechanical checks",
  "Case write-result: PASS",
  "Final result: PASS",
]


def read_pty(fd):
  chunks = []
  while True:
    try:
      chunk = os.read(fd, 4096)
    except OSError as error:
      if error.errno == errno.EIO:
        break
      raise
    if not chunk:
      break
    chunks.append(chunk)
  os.close(fd)
  return b"".join(chunks).decode().replace("\r\n", "\n")


def assert_report(stdout):
  report = json.loads(stdout)
  assert report["operation"] == "run", report
  assert report["status"] == "PASS", report
  assert report["results"][0]["case_id"] == "write-result", report


pipe = subprocess.run(base, text=True, capture_output=True, check=False)
assert pipe.returncode == 0, pipe.stderr
assert pipe.stderr == "", pipe.stderr
assert_report(pipe.stdout)

forced = subprocess.run([*base, "--progress"], text=True, capture_output=True, check=False)
assert forced.returncode == 0, forced.stderr
assert forced.stderr.splitlines() == expected, forced.stderr
assert "executor-internal-output" not in forced.stderr
assert_report(forced.stdout)

master, slave = pty.openpty()
automatic = subprocess.Popen(base, text=True, stdout=subprocess.PIPE, stderr=slave)
os.close(slave)
automatic_stdout, _ = automatic.communicate(timeout=10)
automatic_stderr = read_pty(master)
assert automatic.returncode == 0, automatic_stderr
assert automatic_stderr.splitlines() == expected, automatic_stderr
assert_report(automatic_stdout)

master, slave = pty.openpty()
quiet = subprocess.Popen([*base, "--quiet"], text=True, stdout=subprocess.PIPE, stderr=slave)
os.close(slave)
quiet_stdout, _ = quiet.communicate(timeout=10)
quiet_stderr = read_pty(master)
assert quiet.returncode == 0, quiet_stderr
assert quiet_stderr == "", quiet_stderr
assert_report(quiet_stdout)

delayed = subprocess.Popen(
  [*base, "--progress"],
  text=True,
  stdout=subprocess.PIPE,
  stderr=subprocess.PIPE,
  env={**os.environ, "FAKE_CODEX_DELAY": "0.5"},
)
first_line = delayed.stderr.readline()
assert first_line == "Preparing run\n", first_line
assert delayed.poll() is None
delayed_stdout, delayed_stderr = delayed.communicate(timeout=10)
assert delayed.returncode == 0, delayed_stderr
assert [first_line.strip(), *delayed_stderr.splitlines()] == expected
assert_report(delayed_stdout)
