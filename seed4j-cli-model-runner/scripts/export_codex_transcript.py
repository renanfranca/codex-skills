#!/usr/bin/env python3
"""Export the visible portion of one Codex rollout to auditable Markdown."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import sys
from typing import Any


class ExportError(RuntimeError):
  """Raised when a rollout cannot be exported without guessing."""


INTERNAL_MARKERS = (
  "<app-context>",
  "<skills_instructions>",
  "<permissions instructions>",
  "<collaboration_mode>",
  "<apps_instructions>",
  "<plugins_instructions>",
  '"base_instructions"',
  '"role":"developer"',
  '"role": "developer"',
  '"role":"system"',
  '"role": "system"',
)

INTERNAL_CONTENT_KINDS = {
  "plugins.recommendations",
  "environments.environment_context",
}

SECRET_PATTERNS = (
  re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b"),
  re.compile(r"\bsk-[A-Za-z0-9_-]{16,}\b"),
  re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
  re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+/=-]{12,}"),
  re.compile(r"(?i)(https?://[^\s/:]+:)[^\s/@]+(@)"),
  re.compile(
    r"(?i)\b(authorization|api[_-]?key|access[_-]?token|password|secret)"
    r"(\s*[:=]\s*)([\"']?)[^\s,;\"'}]+"
  ),
)

KNOWN_INTERNAL_RECORDS = {
  "event_msg",
  "session_meta",
  "token_usage_record",
  "turn_context",
  "world_state",
}

KNOWN_RESPONSE_ITEMS = {
  "custom_tool_call",
  "custom_tool_call_output",
  "function_call",
  "function_call_output",
  "message",
  "reasoning",
}

DELEGATION_OUTPUTS = {"create_thread", "send_message_to_thread"}


def redact(text: str) -> str:
  lowered = text.lower()
  if any(marker.lower() in lowered for marker in INTERNAL_MARKERS):
    return "[REDACTED: internal instructions]"

  redacted = text
  for pattern in SECRET_PATTERNS:
    if pattern.pattern.startswith("(?i)(https?"):
      redacted = pattern.sub(r"\1[REDACTED]\2", redacted)
    elif "authorization|api" in pattern.pattern:
      redacted = pattern.sub(r"\1\2[REDACTED]", redacted)
    else:
      redacted = pattern.sub("[REDACTED]", redacted)
  return redacted


def fenced(text: str) -> str:
  runs = [len(match.group(0)) for match in re.finditer(r"~+", text)]
  fence = "~" * max(3, (max(runs) + 1) if runs else 3)
  return f"{fence}text\n{text}\n{fence}"


def load_records(path: Path) -> list[dict[str, Any]]:
  records: list[dict[str, Any]] = []
  previous = -1
  with path.open(encoding="utf-8") as source:
    for line_number, line in enumerate(source, start=1):
      try:
        record = json.loads(line)
      except json.JSONDecodeError as error:
        raise ExportError(f"invalid JSON on line {line_number}: {error}") from error

      ordinal = record.get("ordinal")
      if not isinstance(ordinal, int):
        raise ExportError(f"line {line_number} has no integer ordinal")
      if ordinal <= previous:
        raise ExportError(
          f"ordinal {ordinal} on line {line_number} is not greater than {previous}"
        )
      previous = ordinal
      records.append(record)

  if not records:
    raise ExportError("rollout is empty")
  return records


def matching_session(records: list[dict[str, Any]], thread_id: str) -> bool:
  for record in records:
    if record.get("type") != "session_meta":
      continue
    payload = record.get("payload", {})
    return payload.get("id") == thread_id or payload.get("session_id") == thread_id
  return False


def locate_rollout(codex_home: Path, thread_id: str) -> Path:
  session_root = codex_home / "sessions"
  if not session_root.is_dir():
    raise ExportError(f"Codex session directory does not exist: {session_root}")

  candidates: list[Path] = []
  for path in session_root.rglob(f"*{thread_id}*.jsonl"):
    try:
      records = load_records(path)
    except ExportError:
      continue
    if matching_session(records, thread_id):
      candidates.append(path)

  if len(candidates) != 1:
    rendered = ", ".join(str(path) for path in candidates) or "none"
    raise ExportError(
      f"expected exactly one rollout for {thread_id}; found {len(candidates)}: {rendered}"
    )
  return candidates[0]


def validate_context(
  records: list[dict[str, Any]], model: str, effort: str
) -> tuple[str | None, str | None]:
  contexts = [
    record.get("payload", {})
    for record in records
    if record.get("type") == "turn_context"
  ]
  if not contexts:
    raise ExportError("rollout contains no turn_context record")

  for context in contexts:
    observed_model = context.get("model")
    collaboration = context.get("collaboration_mode", {}).get("settings", {})
    observed_effort = context.get("effort") or collaboration.get("reasoning_effort")
    if observed_model != model:
      raise ExportError(f"model mismatch: expected {model}, observed {observed_model}")
    if observed_effort != effort:
      raise ExportError(
        f"reasoning effort mismatch: expected {effort}, observed {observed_effort}"
      )

  first = contexts[0]
  return first.get("current_date"), first.get("timezone")


def content_text(payload: dict[str, Any]) -> str:
  content = payload.get("content")
  if not isinstance(content, list):
    raise ExportError("visible message content is not a list")

  parts: list[str] = []
  for item in content:
    if not isinstance(item, dict) or item.get("type") not in {"input_text", "output_text"}:
      kind = item.get("type") if isinstance(item, dict) else type(item).__name__
      raise ExportError(f"unsupported visible message content type: {kind}")
    text = item.get("text")
    if not isinstance(text, str):
      raise ExportError("visible message text is not a string")
    parts.append(text)
  return "\n".join(parts)


def tool_output_text(output: Any) -> str:
  if isinstance(output, str):
    return output
  if isinstance(output, list):
    parts: list[str] = []
    for item in output:
      if isinstance(item, dict) and isinstance(item.get("text"), str):
        parts.append(item["text"])
      else:
        parts.append(json.dumps(item, ensure_ascii=False, sort_keys=True))
    return "".join(parts)
  return json.dumps(output, ensure_ascii=False, sort_keys=True)


def block(title: str, timestamp: str, ordinal: int, body: str) -> str:
  return f"## {title} — {timestamp} — ordinal {ordinal}\n\n{body}"


def render_response_item(
  record: dict[str, Any], call_names: dict[str, str]
) -> str:
  payload = record.get("payload", {})
  item_type = payload.get("type")
  timestamp = str(record.get("timestamp", "unknown time"))
  ordinal = int(record["ordinal"])

  if item_type not in KNOWN_RESPONSE_ITEMS:
    raise ExportError(f"unsupported response_item type at ordinal {ordinal}: {item_type}")

  if item_type == "reasoning":
    return block(
      "Excluded record",
      timestamp,
      ordinal,
      "Private or encrypted reasoning was excluded.",
    )

  if item_type == "message":
    role = payload.get("role")
    if role in {"developer", "system"}:
      return block(
        "Excluded record",
        timestamp,
        ordinal,
        f"Internal {role} instructions were excluded.",
      )
    if role not in {"assistant", "user"}:
      raise ExportError(f"unsupported visible message role at ordinal {ordinal}: {role}")

    metadata = payload.get("internal_chat_message_metadata_passthrough", {})
    kinds = set(metadata.get("content_item_kinds", [])) if isinstance(metadata, dict) else set()
    if role == "user" and kinds and kinds.issubset(INTERNAL_CONTENT_KINDS):
      return block(
        "Excluded record",
        timestamp,
        ordinal,
        "Injected plugin or environment context was excluded.",
      )

    text = redact(content_text(payload))
    phase = payload.get("phase")
    title = "User" if role == "user" else "Assistant"
    if role == "assistant" and isinstance(phase, str):
      title += f" ({phase})"
    return block(title, timestamp, ordinal, fenced(text))

  call_id = str(payload.get("call_id") or payload.get("id") or "unknown")
  name = str(payload.get("name") or call_names.get(call_id) or "unknown")

  if item_type in {"custom_tool_call", "function_call"}:
    call_names[call_id] = name
    arguments = payload.get("input") if item_type == "custom_tool_call" else payload.get("arguments")
    if not isinstance(arguments, str):
      arguments = json.dumps(arguments, ensure_ascii=False, sort_keys=True)
    body = f"- Call ID: `{call_id}`\n\n### Arguments\n\n{fenced(redact(arguments))}"
    return block(f"Tool call `{name}`", timestamp, ordinal, body)

  output = tool_output_text(payload.get("output"))
  if item_type == "function_call_output" and name in DELEGATION_OUTPUTS:
    return block("User", timestamp, ordinal, fenced(redact(output)))

  body = f"- Call ID: `{call_id}`\n\n### Result\n\n{fenced(redact(output))}"
  return block(f"Tool result `{name}`", timestamp, ordinal, body)


def render_transcript(
  records: list[dict[str, Any]],
  source: Path,
  thread_id: str,
  model: str,
  effort: str,
  branch: str,
) -> str:
  if not matching_session(records, thread_id):
    raise ExportError(f"rollout session does not match task {thread_id}")
  current_date, timezone = validate_context(records, model, effort)

  blocks: list[str] = []
  call_names: dict[str, str] = {}
  for record in records:
    record_type = record.get("type")
    if record_type == "response_item":
      blocks.append(render_response_item(record, call_names))
    elif record_type not in KNOWN_INTERNAL_RECORDS:
      raise ExportError(
        f"unsupported rollout record at ordinal {record.get('ordinal')}: {record_type}"
      )

  if not blocks:
    raise ExportError("rollout contains no auditable response items")

  last_ordinal = records[-1]["ordinal"]
  metadata = [
    "# Conversation Transcript",
    "",
    "## Run metadata",
    "",
    f"- Codex task ID: `{thread_id}`",
    f"- Model: `{model}`",
    f"- Reasoning effort: `{effort}`",
    f"- Branch: `{branch}`",
    f"- Source rollout: `{source.name}`",
    f"- Session date: `{current_date or 'unavailable'}`",
    f"- Timezone: `{timezone or 'unavailable'}`",
    f"- Last included ordinal: `{last_ordinal}`",
    "",
    "## Audit boundary",
    "",
    "This is a chronological export of visible task messages and tool interactions, not a summary or reconstruction. Internal system/developer instructions, injected context, private or encrypted reasoning, lifecycle and usage metadata, and secrets are excluded or redacted. The mechanical export, audit commit, and later coordinator events are outside this task snapshot.",
    "",
    "---",
    "",
  ]
  return "\n".join(metadata) + "\n\n---\n\n".join(blocks) + "\n"


def parse_args(argv: list[str]) -> argparse.Namespace:
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("--thread-id", required=True)
  parser.add_argument("--model", required=True)
  parser.add_argument("--effort", required=True)
  parser.add_argument("--branch", required=True)
  parser.add_argument("--output", type=Path, required=True)
  parser.add_argument("--rollout", type=Path)
  parser.add_argument("--codex-home", type=Path)
  return parser.parse_args(argv)


def require_single_line(label: str, value: str) -> None:
  if not value or "\n" in value or "\r" in value:
    raise ExportError(f"{label} must be a non-empty single line")


def main(argv: list[str] | None = None) -> int:
  args = parse_args(argv or sys.argv[1:])
  try:
    for label in ("thread_id", "model", "effort", "branch"):
      require_single_line(label, getattr(args, label))

    codex_home_value = args.codex_home or (
      Path(os.environ["CODEX_HOME"]) if os.environ.get("CODEX_HOME") else None
    )
    source = args.rollout
    if source is None:
      if codex_home_value is None:
        raise ExportError("set CODEX_HOME or pass --codex-home/--rollout")
      source = locate_rollout(codex_home_value, args.thread_id)
    if not source.is_file():
      raise ExportError(f"rollout does not exist: {source}")

    records = load_records(source)
    transcript = render_transcript(
      records, source, args.thread_id, args.model, args.effort, args.branch
    )
    args.output.write_text(transcript, encoding="utf-8", newline="\n")
    result = {
      "lastOrdinal": records[-1]["ordinal"],
      "output": str(args.output),
      "source": source.name,
      "threadId": args.thread_id,
    }
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0
  except ExportError as error:
    print(f"error: {error}", file=sys.stderr)
    return 2


if __name__ == "__main__":
  raise SystemExit(main())
