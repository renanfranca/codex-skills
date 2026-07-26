#!/usr/bin/env python3
"""Render a canonical skill evaluation evidence report as Markdown."""

import argparse
import json
from pathlib import Path
from typing import Any

from eval_report import atomic_write_text, load_report, validate_report


def render_report(report: dict[str, Any]) -> str:
  validate_report(report)
  operation = report["operation"]
  estimate = report["api_reference_estimate"]
  lines = [
    f"# Evaluation evidence: {operation['id']}",
    "",
    f"- Operation: `{operation['type']}`",
    f"- Status: `{operation['status']}`",
    f"- Provenance: `{report['provenance']}`",
    f"- Started: `{report['started_at']}`",
    f"- Finished: `{report['finished_at']}`",
    f"- Duration: `{report['duration_ms']} ms`",
    f"- Executor model: `{report['runtime']['executor']['model'] or 'configured default'}`",
    f"- Executor effort: `{report['runtime']['executor']['reasoning_effort'] or 'configured default'}`",
    f"- Codex CLI: `{report['environment']['codex_cli']['version'] or 'unavailable'}`",
    f"- Authentication: `{report['environment']['authentication']['mode']}`",
    f"- Runner SHA-256: `{report['environment']['runner']['sha256']}`",
    "",
    "## Consumption",
    "",
    _usage_line(report["usage"]),
    _usage_event_summary(report["usage"]),
    (
      f"- Sessions: planned `{report['sessions']['planned']['total']}`, "
      f"executed `{report['sessions']['executed']['total']}`"
    ),
    "",
    "## API reference estimate",
    "",
  ]
  if estimate["available"]:
    lines.extend([
      (
        f"- Reference amount: `{estimate['amount']:.12f} "
        f"{estimate['currency']}`"
      ),
      f"- Billing mode: `{estimate['billing_mode']}`",
      "- This is not an actual charge.",
    ])
  else:
    lines.extend([
      "- Reference amount: unavailable",
      "- This is not an actual charge.",
    ])
    if estimate.get("base_rate_amount") is not None:
      lines.append(
        f"- Base-rate amount: `{estimate['base_rate_amount']:.12f} "
        f"{estimate['currency']}`"
      )
  lines.append(f"- Estimate status: `{estimate.get('status', 'unavailable')}`")
  for limitation in estimate["limitations"]:
    lines.append(f"- Limitation: {limitation}")

  for index, observation in enumerate(report["observations"], start=1):
    lines.extend([
      "",
      f"## Observation {index}: {observation['case_id']}",
      "",
      f"- Status: `{observation['status']}`",
      f"- Role: `{observation['role']}`",
      f"- Repetition: `{observation['repetition']}`",
      f"- Duration: `{observation['duration_ms']} ms`",
      f"- Workspace retention: `{observation['workspace']['retention']}`",
      _usage_line(observation["usage"]),
      _usage_event_summary(observation["usage"]),
      "",
      "### Executor account",
      "",
    ])
    response = observation["executor"].get("response")
    if response is None:
      lines.append("Executor did not provide a structured response.")
    else:
      lines.append(f"Diagnosis: {response.get('diagnosis', '')}")
      for field in (
        "approach",
        "decisions",
        "rejected_alternatives",
        "key_changes",
        "validation",
      ):
        lines.append("")
        lines.append(f"{field.replace('_', ' ').title()}:")
        values = response.get(field, [])
        if values:
          lines.extend(f"- {value}" for value in values)
        else:
          lines.append("- None recorded.")
    lines.extend([
      "",
      "### Mechanical facts",
      "",
      f"- Mechanical result: `{'PASS' if observation['mechanical']['passed'] else 'FAIL'}`",
      f"- Oracle result: `{'PASS' if observation['oracle']['passed'] else 'FAIL'}`",
      f"- Judge verdict: `{observation['judge']['verdict']}`",
    ])
    for fact in observation["mechanical"].get("checks", []):
      lines.append(
        f"- `{fact['name']}`: `{'PASS' if fact['passed'] else 'FAIL'}`"
      )
    lines.extend([
      "",
      "### Changed files",
      "",
    ])
    changed = observation["evidence"]["changed_files"]
    lines.extend(f"- `{path}`" for path in changed)
    if not changed:
      lines.append("- None.")
    lines.extend([
      "",
      "### Sanitized diff",
      "",
      "```diff",
      observation["evidence"]["diff"].rstrip(),
      "```",
    ])
    if observation["evidence"]["truncated"]:
      lines.extend(["", "Truncations:"])
      lines.extend(
        f"- `{item['path']}`: {item['reason']}"
        for item in observation["evidence"]["truncations"]
      )

  lines.extend([
    "",
    "## Integrity",
    "",
    (
      f"- Report digest: `{report['report_digest']['algorithm']}:"
      f"{report['report_digest']['value']}`"
    ),
    "",
  ])
  rendered = "\n".join(lines)
  return "\n".join(line.rstrip() for line in rendered.split("\n"))


def _usage_line(usage: dict[str, Any]) -> str:
  return (
    "- Tokens: "
    f"input `{_display(usage.get('input_tokens'))}`, "
    f"cached input `{_display(usage.get('cached_input_tokens'))}`, "
    f"output `{_display(usage.get('output_tokens'))}`, "
    f"reasoning output `{_display(usage.get('reasoning_output_tokens'))}`"
  )


def _usage_event_summary(usage: dict[str, Any]) -> str:
  events = usage.get("events", [])
  scopes = sorted({
    event.get("scope", "unknown")
    for event in events
    if isinstance(event, dict)
  })
  return (
    f"- Normalized usage events: `{usage.get('event_count', len(events))}`, "
    f"complete `{str(usage.get('events_complete', False)).lower()}`, "
    f"scopes `{', '.join(scopes) if scopes else 'none'}`"
  )


def _display(value: Any) -> str:
  return "unknown" if value is None else str(value)


def main() -> int:
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("--input", type=Path, required=True)
  parser.add_argument("--output", type=Path, required=True)
  args = parser.parse_args()
  report = load_report(args.input)
  atomic_write_text(args.output, render_report(report))
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
