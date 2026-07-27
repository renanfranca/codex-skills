import os
from pathlib import Path
import subprocess
import tempfile


skill_under_test = Path(os.environ["SKILL_EVAL_SKILL_DIR"])
oracle = (
  skill_under_test
  / "evals"
  / "cases"
  / "self-evolution-candidate"
  / "oracle"
  / "check_self_evolution.py"
)
skill_instructions = (skill_under_test / "SKILL.md").read_text(encoding="utf-8")
eval_contract = (
  skill_under_test / "references" / "eval-contract.md"
).read_text(encoding="utf-8")

required_rule = (
  "Require literal text in a hidden oracle only when the public prompt "
  "requires that same literal text."
)
assert required_rule in skill_instructions
assert (
  "A hidden oracle may require literal text only when the public prompt "
  "requires that same literal text."
) in eval_contract

base_text = "# Sample skill\n\nKeep fixtures minimal.\n"


def add_before_marker(text, reminder):
  return text.replace(
    "Keep fixtures minimal.",
    reminder + "\nKeep fixtures minimal.",
    1,
  )


def run_oracle(installed, baseline, candidate):
  with tempfile.TemporaryDirectory(dir=Path.cwd()) as temporary:
    workspace = Path(temporary)
    installed_path = (
      workspace / ".agents" / "skills" / "develop-skill-with-evals"
    )
    installed_path.mkdir(parents=True)
    (workspace / "baseline").mkdir()
    (workspace / "candidate").mkdir()
    (installed_path / "SKILL.md").write_text(installed, encoding="utf-8")
    (workspace / "baseline" / "SKILL.md").write_text(
      baseline,
      encoding="utf-8",
    )
    (workspace / "candidate" / "SKILL.md").write_text(
      candidate,
      encoding="utf-8",
    )
    return subprocess.run(
      ["python3", str(oracle)],
      cwd=workspace,
      text=True,
      capture_output=True,
      check=False,
    )


valid_reminders = [
  "Redact personal email addresses from fixtures.",
  "Explicitly redact personal email addresses from fixtures.",
  "REDACTS personal email addresses from fixtures.",
  "Personal email address from a fixture is redacted.",
  "Redacting personal email addresses from fixtures.",
]
for reminder in valid_reminders:
  result = run_oracle(
    base_text,
    base_text,
    add_before_marker(base_text, reminder),
  )
  assert result.returncode == 0, (reminder, result.stderr)

invalid_reminders = {
  "missing redaction": "Remove personal email addresses from fixtures.",
  "missing personal": "Redact email addresses from fixtures.",
  "missing email address": "Redact personal identifiers from fixtures.",
  "missing fixture": "Redact personal email addresses from examples.",
  "negated with not": "Do not redact personal email addresses from fixtures.",
  "negated with never": "Never redact personal email addresses from fixtures.",
}
for name, reminder in invalid_reminders.items():
  result = run_oracle(
    base_text,
    base_text,
    add_before_marker(base_text, reminder),
  )
  assert result.returncode != 0, name

two_insertions = (
  "Redact personal email addresses from fixtures.\n"
  + base_text
  + "Redact personal email addresses from fixtures.\n"
)
assert run_oracle(base_text, base_text, two_insertions).returncode != 0

extra_change = add_before_marker(
  base_text.replace("minimal", "small"),
  "Redact personal email addresses from fixtures.",
)
assert run_oracle(base_text, base_text, extra_change).returncode != 0

valid_candidate = add_before_marker(
  base_text,
  "Explicitly redact personal email addresses from fixtures.",
)
modified_baseline = base_text.replace("minimal", "small")
assert run_oracle(base_text, modified_baseline, valid_candidate).returncode != 0

modified_installed = base_text.replace("minimal", "small")
assert run_oracle(modified_installed, base_text, valid_candidate).returncode != 0
