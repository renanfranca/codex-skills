import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


SCRIPT = Path(__file__).parents[1] / "export_codex_transcript.py"
SPEC = importlib.util.spec_from_file_location("export_codex_transcript", SCRIPT)
assert SPEC and SPEC.loader
exporter = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(exporter)


class ExportCodexTranscriptTest(unittest.TestCase):
  def setUp(self):
    self.thread_id = "task-123"
    self.records = [
      self.record(0, "session_meta", {"id": self.thread_id}),
      self.record(
        1,
        "response_item",
        {
          "type": "message",
          "role": "developer",
          "content": [{"type": "input_text", "text": "hidden instruction"}],
        },
      ),
      self.record(
        2,
        "response_item",
        {
          "type": "message",
          "role": "user",
          "content": [{"type": "input_text", "text": "<environment_context>hidden</environment_context>"}],
          "internal_chat_message_metadata_passthrough": {
            "content_item_kinds": ["environments.environment_context"]
          },
        },
      ),
      self.record(
        3,
        "turn_context",
        {
          "model": "gpt-5.6-sol",
          "effort": "low",
          "current_date": "2026-09-04",
          "timezone": "America/Bahia",
        },
      ),
      self.record(
        4,
        "response_item",
        {
          "type": "function_call_output",
          "name": "create_thread",
          "call_id": "create-1",
          "output": "Implement SPEC.md verbatim.",
        },
      ),
      self.record(
        5,
        "response_item",
        {
          "type": "message",
          "role": "assistant",
          "phase": "commentary",
          "content": [{"type": "output_text", "text": "Starting work."}],
        },
      ),
      self.record(6, "response_item", {"type": "reasoning", "encrypted_content": "hidden"}),
      self.record(
        7,
        "response_item",
        {
          "type": "custom_tool_call",
          "name": "exec",
          "call_id": "call-1",
          "input": "run --api-key=sk-abcdefghijklmnopqrstuvwxyz",
        },
      ),
      self.record(
        8,
        "response_item",
        {
          "type": "custom_tool_call_output",
          "call_id": "call-1",
          "output": [{"type": "input_text", "text": "first\n"}, {"type": "input_text", "text": "second"}],
        },
      ),
      self.record(9, "event_msg", {"type": "token_count"}),
    ]

  @staticmethod
  def record(ordinal, record_type, payload):
    return {
      "timestamp": f"2026-09-04T10:00:{ordinal:02d}.000Z",
      "ordinal": ordinal,
      "type": record_type,
      "payload": payload,
    }

  def write_rollout(self, directory, records=None):
    path = Path(directory) / "rollout-task-123.jsonl"
    selected = records if records is not None else self.records
    path.write_text(
      "".join(json.dumps(record) + "\n" for record in selected), encoding="utf-8"
    )
    return path

  def test_exports_visible_records_in_order_and_redacts_secrets(self):
    with tempfile.TemporaryDirectory() as directory:
      source = self.write_rollout(directory)
      loaded = exporter.load_records(source)

      transcript = exporter.render_transcript(
        loaded,
        source,
        self.thread_id,
        "gpt-5.6-sol",
        "low",
        "calculator-sol-low",
      )

    self.assertIn("Implement SPEC.md verbatim.", transcript)
    self.assertIn("Assistant (commentary)", transcript)
    self.assertIn("Starting work.", transcript)
    self.assertIn("Tool call `exec`", transcript)
    self.assertIn("Tool result `exec`", transcript)
    self.assertIn("first\nsecond", transcript)
    self.assertIn("Private or encrypted reasoning was excluded.", transcript)
    self.assertIn("Internal developer instructions were excluded.", transcript)
    self.assertIn("Injected plugin or environment context was excluded.", transcript)
    self.assertNotIn("hidden instruction", transcript)
    self.assertNotIn("sk-abcdefghijklmnopqrstuvwxyz", transcript)
    self.assertIn("[REDACTED]", transcript)
    self.assertLess(transcript.index("Implement SPEC.md"), transcript.index("Starting work."))
    self.assertIn("Last included ordinal: `9`", transcript)

  def test_output_is_deterministic(self):
    with tempfile.TemporaryDirectory() as directory:
      source = self.write_rollout(directory)
      loaded = exporter.load_records(source)
      first = exporter.render_transcript(
        loaded, source, self.thread_id, "gpt-5.6-sol", "low", "branch"
      )
      second = exporter.render_transcript(
        loaded, source, self.thread_id, "gpt-5.6-sol", "low", "branch"
      )

    self.assertEqual(first, second)

  def test_rejects_model_or_effort_mismatch(self):
    with tempfile.TemporaryDirectory() as directory:
      source = self.write_rollout(directory)
      loaded = exporter.load_records(source)

      with self.assertRaisesRegex(exporter.ExportError, "model mismatch"):
        exporter.render_transcript(
          loaded, source, self.thread_id, "gpt-5.6-terra", "low", "branch"
        )
      with self.assertRaisesRegex(exporter.ExportError, "reasoning effort mismatch"):
        exporter.render_transcript(
          loaded, source, self.thread_id, "gpt-5.6-sol", "xhigh", "branch"
        )

  def test_rejects_non_monotonic_ordinals(self):
    records = [self.records[0], self.record(0, "event_msg", {"type": "duplicate"})]
    with tempfile.TemporaryDirectory() as directory:
      source = self.write_rollout(directory, records)

      with self.assertRaisesRegex(exporter.ExportError, "not greater"):
        exporter.load_records(source)

  def test_redacts_tool_fields_that_repeat_internal_instructions(self):
    record = self.record(
      10,
      "response_item",
      {
        "type": "custom_tool_call_output",
        "call_id": "call-2",
        "output": "prefix <skills_instructions>private</skills_instructions>",
      },
    )

    rendered = exporter.render_response_item(record, {"call-2": "exec"})

    self.assertIn("[REDACTED: internal instructions]", rendered)
    self.assertNotIn("private", rendered)

  def test_rejects_unknown_visible_response_type(self):
    record = self.record(
      10, "response_item", {"type": "future_visible_item", "content": "data"}
    )

    with self.assertRaisesRegex(exporter.ExportError, "unsupported response_item"):
      exporter.render_response_item(record, {})


if __name__ == "__main__":
  unittest.main()
