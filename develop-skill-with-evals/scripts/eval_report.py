#!/usr/bin/env python3
"""Deterministic helpers for durable skill evaluation evidence."""

from __future__ import annotations

import difflib
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
from typing import Any


MAX_CAPTURE_BYTES = 32768
MAX_DIFF_BYTES_PER_FILE = 12000
MAX_DIFF_BYTES_PER_REPORT = 64000
MAX_FRAGMENT_BYTES = 2000
MAX_FACT_TEXT = 4000
SECRET_PATTERNS = (
  re.compile(r"\b(sk-[A-Za-z0-9_-]{8,})"),
  re.compile(r"(?i)\b(bearer)\s+[A-Za-z0-9._~+/=-]{8,}"),
  re.compile(
    r"(?i)\b(api[_-]?key|access[_-]?token|auth[_-]?token|password|secret)"
    r"(\s*[:=]\s*)"
    r"([^\s,'\"}]+)"
  ),
)
REPORT_SCHEMA_VERSION = 1


def canonical_json(value: Any) -> str:
  return json.dumps(
    value,
    sort_keys=True,
    separators=(",", ":"),
    ensure_ascii=False,
  )


def sha256_bytes(value: bytes) -> str:
  return hashlib.sha256(value).hexdigest()


def report_digest(report: dict[str, Any]) -> str:
  payload = dict(report)
  payload.pop("report_digest", None)
  return sha256_bytes(canonical_json(payload).encode("utf-8"))


def validate_report(report: dict[str, Any], source: str = "report") -> None:
  required = {
    "schema_version",
    "operation",
    "provenance",
    "started_at",
    "finished_at",
    "duration_ms",
    "skill",
    "fingerprints",
    "environment",
    "billing",
    "runtime",
    "sessions",
    "usage",
    "pricing",
    "api_reference_estimate",
    "observations",
    "limitations",
    "report_digest",
  }
  missing = sorted(required - report.keys())
  if missing:
    raise ValueError(f"{source} is missing report fields: {', '.join(missing)}")
  if report.get("schema_version") != REPORT_SCHEMA_VERSION:
    raise ValueError(
      f"{source} uses unsupported report schema version "
      f"{report.get('schema_version')!r}"
    )
  operation = report.get("operation")
  if not isinstance(operation, dict) or not isinstance(operation.get("id"), str):
    raise ValueError(f"{source} has no valid operation id")
  skill = report.get("skill")
  if not isinstance(skill, dict) or not isinstance(skill.get("name"), str):
    raise ValueError(f"{source} has no valid skill name")
  if report.get("provenance") != "executed":
    raise ValueError(f"{source} has unsupported provenance")
  if not isinstance(report.get("observations"), list):
    raise ValueError(f"{source} observations must be an array")
  if report.get("billing", {}).get("actual_charge_observed") is not False:
    raise ValueError(f"{source} must record actual_charge_observed as false")
  if report.get("api_reference_estimate", {}).get("actual_charge") is not False:
    raise ValueError(f"{source} must record actual_charge as false")
  digest = report.get("report_digest")
  if not isinstance(digest, dict) or digest.get("algorithm") != "sha256":
    raise ValueError(f"{source} has no valid SHA-256 report digest")
  expected = report_digest(report)
  if digest.get("value") != expected:
    raise ValueError(
      f"{source} report digest mismatch: expected {expected}, "
      f"found {digest.get('value')}"
    )


def load_report(path: Path) -> dict[str, Any]:
  with path.open(encoding="utf-8") as stream:
    report = json.load(stream)
  if not isinstance(report, dict):
    raise ValueError(f"Report must contain a JSON object: {path}")
  validate_report(report, str(path))
  return report


def atomic_write_text(path: Path, value: str) -> None:
  path.parent.mkdir(parents=True, exist_ok=True)
  descriptor, temporary_name = tempfile.mkstemp(
    prefix=f".{path.name}.",
    dir=path.parent,
  )
  temporary = Path(temporary_name)
  try:
    with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
      stream.write(value)
      stream.flush()
      os.fsync(stream.fileno())
    os.replace(temporary, path)
  finally:
    if temporary.exists():
      temporary.unlink()


def evidence_path_allowed(relative_path: str) -> bool:
  path = Path(relative_path)
  parts = path.parts
  if ".git" in parts or "__pycache__" in parts:
    return False
  if len(parts) >= 2 and parts[0] == ".agents" and parts[1] == "skills":
    return False
  if any(part.startswith(".eval-") for part in parts) or path.suffix == ".pyc":
    return False
  return True


def capture_evidence_snapshot(root: Path) -> dict[str, dict[str, Any]]:
  captured: dict[str, dict[str, Any]] = {}
  for path in sorted(root.rglob("*")):
    if not path.is_file():
      continue
    relative = path.relative_to(root).as_posix()
    if not evidence_path_allowed(relative):
      continue
    size = path.stat().st_size
    with path.open("rb") as stream:
      content = stream.read(MAX_CAPTURE_BYTES + 1)
    captured[relative] = {
      "sha256": _file_hash(path),
      "size": size,
      "content": content[:MAX_CAPTURE_BYTES],
      "capture_truncated": len(content) > MAX_CAPTURE_BYTES,
    }
  return captured


def build_file_evidence(
  before: dict[str, dict[str, Any]],
  after: dict[str, dict[str, Any]],
) -> dict[str, Any]:
  changed_files = sorted(
    path
    for path in before.keys() | after.keys()
    if before.get(path, {}).get("sha256") != after.get(path, {}).get("sha256")
  )
  diff_parts: list[str] = []
  fragments: list[dict[str, Any]] = []
  truncations: list[dict[str, str]] = []
  report_bytes = 0

  for relative in changed_files:
    old = before.get(relative)
    new = after.get(relative)
    old_text = _decode_text(old)
    new_text = _decode_text(new)
    fragment = {
      "path": relative,
      "before_sha256": old["sha256"] if old else None,
      "after_sha256": new["sha256"] if new else None,
      "before_size": old["size"] if old else None,
      "after_size": new["size"] if new else None,
      "before": _limited_fragment(old_text),
      "after": _limited_fragment(new_text),
      "binary": (
        (old is not None and old_text is None)
        or (new is not None and new_text is None)
      ),
    }
    fragments.append(fragment)
    if (old and old["capture_truncated"]) or (new and new["capture_truncated"]):
      truncations.append({"path": relative, "reason": "file capture limit"})

    if fragment["binary"]:
      file_diff = (
        f"Binary file {relative} changed "
        f"({fragment['before_sha256']} -> {fragment['after_sha256']})\n"
      )
    else:
      file_diff = "".join(
        difflib.unified_diff(
          (old_text or "").splitlines(keepends=True),
          (new_text or "").splitlines(keepends=True),
          fromfile=f"a/{relative}" if old else "/dev/null",
          tofile=f"b/{relative}" if new else "/dev/null",
        )
      )
    encoded = file_diff.encode("utf-8")
    if len(encoded) > MAX_DIFF_BYTES_PER_FILE:
      encoded = encoded[:MAX_DIFF_BYTES_PER_FILE]
      file_diff = encoded.decode("utf-8", errors="ignore")
      truncations.append({"path": relative, "reason": "per file diff limit"})
    remaining = MAX_DIFF_BYTES_PER_REPORT - report_bytes
    if remaining <= 0:
      truncations.append({"path": relative, "reason": "report diff limit"})
      continue
    if len(encoded) > remaining:
      encoded = encoded[:remaining]
      file_diff = encoded.decode("utf-8", errors="ignore")
      truncations.append({"path": relative, "reason": "report diff limit"})
    file_diff = redact_text(file_diff)
    diff_parts.append(file_diff)
    report_bytes += len(file_diff.encode("utf-8"))

  return {
    "changed_files": changed_files,
    "diff": "".join(diff_parts),
    "fragments": fragments,
    "truncated": bool(truncations),
    "truncations": truncations,
    "limits": {
      "capture_bytes_per_file": MAX_CAPTURE_BYTES,
      "diff_bytes_per_file": MAX_DIFF_BYTES_PER_FILE,
      "diff_bytes_per_report": MAX_DIFF_BYTES_PER_REPORT,
      "fragment_bytes": MAX_FRAGMENT_BYTES,
    },
  }


def sanitize_fact(value: Any) -> Any:
  if isinstance(value, str):
    redacted = redact_text(value)
    encoded = redacted.encode("utf-8")
    if len(encoded) <= MAX_FACT_TEXT:
      return redacted
    return encoded[:MAX_FACT_TEXT].decode("utf-8", errors="ignore") + "\n[truncated]"
  if isinstance(value, list):
    return [sanitize_fact(item) for item in value]
  if isinstance(value, dict):
    return {key: sanitize_fact(item) for key, item in value.items()}
  return value


def redact_text(value: str) -> str:
  redacted = SECRET_PATTERNS[0].sub("[REDACTED]", value)
  redacted = SECRET_PATTERNS[1].sub(r"\1 [REDACTED]", redacted)
  redacted = SECRET_PATTERNS[2].sub(r"\1\2[REDACTED]", redacted)
  return redacted


def codex_environment(codex_command: str) -> dict[str, Any]:
  version = _metadata_command([codex_command, "--version"])
  login = _metadata_command([codex_command, "login", "status"])
  login_text = (login or "").lower()
  if "chatgpt" in login_text:
    authentication = {
      "status": "available",
      "mode": "chatgpt",
    }
    billing_mode = "chatgpt-plan"
  elif "api key" in login_text or "api_key" in login_text or "apikey" in login_text:
    authentication = {
      "status": "available",
      "mode": "api-key",
    }
    billing_mode = "api"
  else:
    authentication = {
      "status": "unavailable" if login is None else "available",
      "mode": "unknown",
    }
    billing_mode = "chatgpt-plan-or-unknown"
  return {
    "codex_cli": {
      "status": "available" if version is not None else "unavailable",
      "version": version,
    },
    "authentication": authentication,
    "billing_mode": billing_mode,
  }


def load_pricing(path: Path | None) -> dict[str, Any]:
  if path is None:
    return {
      "applied": False,
      "snapshot": None,
      "limitations": ["No explicit pricing file was supplied."],
    }
  with path.open(encoding="utf-8") as stream:
    pricing = json.load(stream)
  if not isinstance(pricing, dict):
    raise ValueError("Pricing file must contain a JSON object")
  required = {
    "version",
    "effective_date",
    "source",
    "currency",
    "unit",
    "models",
    "limitations",
  }
  missing = sorted(required - pricing.keys())
  if missing:
    raise ValueError(f"Pricing file is missing fields: {', '.join(missing)}")
  if pricing["version"] != 1:
    raise ValueError("Pricing file version must be 1")
  if pricing["unit"] != "per_million_tokens":
    raise ValueError("Pricing file unit must be per_million_tokens")
  if not isinstance(pricing["models"], dict):
    raise ValueError("Pricing file models must be an object")
  if not isinstance(pricing["limitations"], list) or not all(
    isinstance(value, str) for value in pricing["limitations"]
  ):
    raise ValueError("Pricing file limitations must be an array of strings")
  for model, rates in pricing["models"].items():
    if not isinstance(model, str) or not isinstance(rates, dict):
      raise ValueError("Every pricing model must map to an object")
    for field in ("input", "cached_input", "output"):
      value = rates.get(field)
      if not isinstance(value, (int, float)) or value < 0:
        raise ValueError(f"Pricing model {model} requires non-negative {field}")
    long_context = rates.get("long_context")
    if long_context is not None:
      if not isinstance(long_context, dict):
        raise ValueError(f"Pricing model {model} long_context must be an object")
      required_long_context = {
        "input_token_threshold",
        "input_multiplier",
        "output_multiplier",
        "applies_per",
      }
      if set(long_context) != required_long_context:
        raise ValueError(
          f"Pricing model {model} long_context requires exactly "
          f"{sorted(required_long_context)}"
        )
      if (
        not isinstance(long_context["input_token_threshold"], int)
        or long_context["input_token_threshold"] < 0
      ):
        raise ValueError(
          f"Pricing model {model} requires a non-negative long context threshold"
        )
      for field in ("input_multiplier", "output_multiplier"):
        value = long_context[field]
        if not isinstance(value, (int, float)) or value < 1:
          raise ValueError(
            f"Pricing model {model} requires {field} of at least one"
          )
      if long_context["applies_per"] != "request":
        raise ValueError(
          f"Pricing model {model} long_context applies_per must be request"
        )
  return {
    "applied": True,
    "snapshot": pricing,
    "limitations": pricing["limitations"],
  }


def api_reference_estimate(
  pricing: dict[str, Any],
  usage: dict[str, Any],
  model: str | None,
  billing_mode: str,
) -> dict[str, Any]:
  base = {
    "available": False,
    "status": "unavailable",
    "currency": (
      pricing["snapshot"]["currency"]
      if pricing.get("snapshot")
      else None
    ),
    "amount": None,
    "base_rate_amount": None,
    "actual_charge": False,
    "billing_mode": billing_mode,
    "calculation": None,
    "long_context_assessment": None,
    "limitations": [
      "This is an API reference estimate, not an observed charge.",
      *pricing.get("limitations", []),
    ],
  }
  if not pricing.get("applied") or model is None:
    return base
  rates = pricing["snapshot"]["models"].get(model)
  if rates is None:
    base["limitations"].append(f"No price entry exists for model {model}.")
    return base
  required_usage = ("input_tokens", "cached_input_tokens", "output_tokens")
  if not all(isinstance(usage.get(field), int) for field in required_usage):
    base["limitations"].append("Observed token usage is incomplete.")
    return base
  input_tokens = usage["input_tokens"]
  cached_tokens = usage["cached_input_tokens"]
  output_tokens = usage["output_tokens"]
  uncached_tokens = max(input_tokens - cached_tokens, 0)
  input_cost = uncached_tokens * rates["input"] / 1_000_000
  cached_cost = cached_tokens * rates["cached_input"] / 1_000_000
  output_cost = output_tokens * rates["output"] / 1_000_000
  amount = input_cost + cached_cost + output_cost
  rounded_base_amount = round(amount, 12)
  long_context = rates.get("long_context")
  long_context_assessment = None
  if long_context is not None:
    threshold = long_context["input_token_threshold"]
    triggering_events = [
      event
      for event in usage.get("events", [])
      if (
        isinstance(event.get("input_tokens"), int)
        and event["input_tokens"] > threshold
      )
    ]
    long_context_assessment = {
      "input_token_threshold": threshold,
      "applies_per": long_context["applies_per"],
      "triggering_event_sequences": [
        event["sequence"] for event in triggering_events
      ],
      "observed_event_scopes": sorted({
        event.get("scope", "unknown") for event in triggering_events
      }),
    }
    if triggering_events and any(
      event.get("scope") != long_context["applies_per"]
      for event in triggering_events
    ):
      return {
        **base,
        "status": "indeterminate-long-context",
        "base_rate_amount": rounded_base_amount,
        "long_context_assessment": long_context_assessment,
        "limitations": [
          *base["limitations"],
          (
            "A reported usage event exceeded a request-scoped threshold, "
            "but the event is not request scoped; the exact multiplier "
            "cannot be audited."
          ),
        ],
      }
  return {
    **base,
    "available": True,
    "status": "complete",
    "amount": rounded_base_amount,
    "base_rate_amount": rounded_base_amount,
    "long_context_assessment": long_context_assessment,
    "calculation": {
      "model": model,
      "unit": "per_million_tokens",
      "tokens": {
        "uncached_input": uncached_tokens,
        "cached_input": cached_tokens,
        "output": output_tokens,
        "reasoning_output": usage.get("reasoning_output_tokens"),
      },
      "rates": rates,
      "components": {
        "input": round(input_cost, 12),
        "cached_input": round(cached_cost, 12),
        "output": round(output_cost, 12),
      },
      "reasoning_note": (
        "Reasoning output tokens are reported separately and are not added "
        "again because they are a subset of output tokens."
      ),
    },
  }


def _file_hash(path: Path) -> str:
  digest = hashlib.sha256()
  with path.open("rb") as stream:
    for block in iter(lambda: stream.read(65536), b""):
      digest.update(block)
  return digest.hexdigest()


def _decode_text(entry: dict[str, Any] | None) -> str | None:
  if entry is None:
    return ""
  content = entry["content"]
  if b"\0" in content:
    return None
  try:
    return content.decode("utf-8")
  except UnicodeDecodeError:
    return None


def _limited_fragment(value: str | None) -> str | None:
  if value is None:
    return None
  redacted = redact_text(value)
  encoded = redacted.encode("utf-8")
  if len(encoded) <= MAX_FRAGMENT_BYTES:
    return redacted
  return (
    encoded[:MAX_FRAGMENT_BYTES].decode("utf-8", errors="ignore")
    + "\n[truncated]"
  )


def _metadata_command(command: list[str]) -> str | None:
  try:
    completed = subprocess.run(
      command,
      text=True,
      capture_output=True,
      check=False,
      timeout=10,
    )
  except (OSError, subprocess.SubprocessError):
    return None
  if completed.returncode != 0:
    return None
  output = completed.stdout.strip() or completed.stderr.strip()
  if not output:
    return None
  return output.splitlines()[0][:160]
