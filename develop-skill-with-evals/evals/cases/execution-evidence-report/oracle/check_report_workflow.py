#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path


root = Path.cwd()
stdout_report = json.loads(
  (root / ".eval-evaluation.json").read_text(encoding="utf-8")
)
assert stdout_report["operation"] == "run"
assert stdout_report["status"] == "PASS"
assert stdout_report["model_sessions"] == {"executor": 1, "judge": 0, "total": 1}
assert stdout_report["artifacts"] is None

report_paths = list((root / ".eval-evidence").glob("*/report.json"))
assert len(report_paths) == 1
report_path = report_paths[0]
report = json.loads(report_path.read_text(encoding="utf-8"))
assert report["operation"]["type"] == "run"
assert report["operation"]["status"] == "PASS"
assert report["provenance"] == "executed"
assert report["runtime"]["executor"]["model"] == "fixture-model"
assert report["runtime"]["executor"]["reasoning_effort"] == "medium"
assert report["environment"]["codex_cli"]["version"] == "codex-cli fixture"
assert report["environment"]["authentication"]["mode"] == "chatgpt"
assert report["billing"]["mode"] == "chatgpt-plan"
assert report["api_reference_estimate"]["actual_charge"] is False
assert report["api_reference_estimate"]["amount"] == 0.0000335
assert report["sessions"]["executed"] == {
  "executor": 1,
  "judge": 0,
  "total": 1
}
assert len(report["observations"]) == 1
observation = report["observations"][0]
assert observation["status"] == "PASS"
assert observation["prompt"] == "Create `result.txt` containing exactly `ok`.\n"
assert observation["usage"]["reasoning_output_tokens"] == 2
assert observation["evidence"]["changed_files"] == ["result.txt"]
assert ".eval-private" not in observation["evidence"]["diff"]
assert observation["executor"]["response"]["diagnosis"]
assert observation["executor"]["response"]["validation"]
assert observation["mechanical"]["passed"] is True
assert observation["oracle"]["passed"] is True
assert observation["judge"]["executed"] is False
assert observation["workspace"]["retention"] == "removed"
assert not Path(observation["workspace"]["original_path"]).exists()

digest_payload = dict(report)
digest = digest_payload.pop("report_digest")
encoded = json.dumps(
  digest_payload,
  sort_keys=True,
  separators=(",", ":"),
  ensure_ascii=False,
).encode("utf-8")
assert digest == {
  "algorithm": "sha256",
  "value": hashlib.sha256(encoded).hexdigest()
}

generated_markdown = report_path.with_name("report.md")
assert generated_markdown.is_file()
assert generated_markdown.read_bytes() == (
  root / ".eval-replayed-report.md"
).read_bytes()
markdown = generated_markdown.read_text(encoding="utf-8")
assert "API reference estimate" in markdown
assert "not an actual charge" in markdown
assert ".eval-private" not in markdown
