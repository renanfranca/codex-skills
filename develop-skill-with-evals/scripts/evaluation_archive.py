#!/usr/bin/env python3
"""Deterministic maintenance and validation for evaluation report archives."""

from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Any

from archive_config import (
  ARCHIVE_CONFIG_NAME,
  configured_pricing_path,
  load_archive_config,
)
from compare_model_reports import compare_report_paths, render_comparison
from eval_report import (
  SECRET_PATTERNS,
  atomic_write_text,
  load_report,
)
from render_eval_report import render_report


FORBIDDEN_SUFFIXES = {".jsonl", ".pyc"}
FORBIDDEN_PARTS = {"oracle", "oracles", "__pycache__", ".agents"}
FORBIDDEN_NAMES = {"transcript.json", "transcript.md"}


def archived_report_paths(archive_root: Path) -> list[Path]:
  return sorted(archive_root.glob("*/operations/*/report.json"))


def build_manifest(archive_root: Path) -> dict[str, Any]:
  entries: list[dict[str, Any]] = []
  operation_ids: set[str] = set()
  for path in archived_report_paths(archive_root):
    report = load_report(path)
    operation_id = report["operation"]["id"]
    if operation_id in operation_ids:
      raise ValueError(f"Duplicate operation id: {operation_id}")
    operation_ids.add(operation_id)
    usage = report["usage"]
    entries.append({
      "skill": report["skill"]["name"],
      "operation_id": operation_id,
      "operation": report["operation"]["type"],
      "status": report["operation"]["status"],
      "model": report["runtime"]["executor"]["model"],
      "reasoning_effort": report["runtime"]["executor"]["reasoning_effort"],
      "sessions": report["sessions"]["executed"]["total"],
      "tokens": {
        "input": usage.get("input_tokens"),
        "cached_input": usage.get("cached_input_tokens"),
        "output": usage.get("output_tokens"),
        "reasoning_output": usage.get("reasoning_output_tokens"),
        "total": usage.get("total_tokens"),
      },
      "duration_ms": report["duration_ms"],
      "digest": report["report_digest"]["value"],
      "path": path.relative_to(archive_root).as_posix(),
    })
  return {
    "version": 1,
    "canonical_format": "report.json",
    "report_count": len(entries),
    "reports": entries,
  }


def render_manifest(manifest: dict[str, Any]) -> str:
  lines = [
    "# Evaluation report archive",
    "",
    f"- Canonical reports: `{manifest['report_count']}`",
    "- Canonical format: `report.json`",
    "- Markdown and comparisons are deterministic projections.",
    "",
    "| Skill | Operation ID | Type | Status | Model | Sessions | Tokens | Duration ms | SHA-256 | Path |",
    "| --- | --- | --- | --- | --- | ---: | ---: | ---: | --- | --- |",
  ]
  for entry in manifest["reports"]:
    lines.append(
      "| "
      + " | ".join([
        entry["skill"],
        entry["operation_id"],
        entry["operation"],
        entry["status"],
        entry["model"] or "configured default",
        str(entry["sessions"]),
        _display(entry["tokens"]["total"]),
        str(entry["duration_ms"]),
        entry["digest"],
        entry["path"],
      ])
      + " |"
    )
  lines.append("")
  return "\n".join(lines)


def rebuild_archive(archive_root: Path) -> dict[str, Any]:
  config_path = archive_root / ARCHIVE_CONFIG_NAME
  config = load_archive_config(config_path)
  configured_pricing_path(config_path, config)
  for path in archived_report_paths(archive_root):
    report = load_report(path)
    atomic_write_text(path.with_name("report.md"), render_report(report))
  manifest = build_manifest(archive_root)
  atomic_write_text(
    archive_root / "manifest.json",
    json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
  )
  atomic_write_text(archive_root / "manifest.md", render_manifest(manifest))
  for comparison in config.get("comparisons", []):
    paths = [
      archive_root
      / comparison["skill"]
      / "operations"
      / operation_id
      / "report.json"
      for operation_id in comparison["operation_ids"]
    ]
    result = compare_report_paths(paths)
    output = (
      archive_root
      / comparison["skill"]
      / "comparisons"
      / comparison["id"]
    )
    atomic_write_text(
      output / "comparison.json",
      json.dumps(result, indent=2, ensure_ascii=False) + "\n",
    )
    atomic_write_text(output / "comparison.md", render_comparison(result))
  return manifest


def validate_archive(archive_root: Path) -> dict[str, Any]:
  config_path = archive_root / ARCHIVE_CONFIG_NAME
  config = load_archive_config(config_path)
  pricing_path = configured_pricing_path(config_path, config)
  errors: list[str] = []
  report_paths = archived_report_paths(archive_root)
  operation_ids: set[str] = set()
  for path in report_paths:
    try:
      report = load_report(path)
      operation_id = report["operation"]["id"]
      archived_skill = path.relative_to(archive_root).parts[0]
      if report["skill"]["name"] != archived_skill:
        errors.append(
          f"skill directory mismatch: {path} contains "
          f"{report['skill']['name']}"
        )
      if operation_id in operation_ids:
        errors.append(f"duplicate operation id: {operation_id}")
      operation_ids.add(operation_id)
      expected_markdown = render_report(report).encode("utf-8")
      markdown_path = path.with_name("report.md")
      if not markdown_path.is_file() or markdown_path.read_bytes() != expected_markdown:
        errors.append(f"Markdown replay mismatch: {markdown_path}")
      if report["api_reference_estimate"].get("actual_charge") is not False:
        errors.append(f"actual_charge must be false: {path}")
      if report["billing"].get("actual_charge_observed") is not False:
        errors.append(f"actual_charge_observed must be false: {path}")
    except (OSError, ValueError, KeyError) as error:
      errors.append(str(error))
  _validate_archive_paths(archive_root, errors)
  _validate_sensitive_content(archive_root, errors)
  expected_manifest = build_manifest(archive_root)
  _check_json_bytes(archive_root / "manifest.json", expected_manifest, errors)
  expected_manifest_md = render_manifest(expected_manifest).encode("utf-8")
  manifest_md = archive_root / "manifest.md"
  if not manifest_md.is_file() or manifest_md.read_bytes() != expected_manifest_md:
    errors.append(f"Manifest Markdown mismatch: {manifest_md}")
  for comparison in config.get("comparisons", []):
    paths = [
      archive_root
      / comparison["skill"]
      / "operations"
      / operation_id
      / "report.json"
      for operation_id in comparison["operation_ids"]
    ]
    try:
      expected = compare_report_paths(paths)
      output = (
        archive_root
        / comparison["skill"]
        / "comparisons"
        / comparison["id"]
      )
      _check_json_bytes(output / "comparison.json", expected, errors)
      expected_md = render_comparison(expected).encode("utf-8")
      markdown = output / "comparison.md"
      if not markdown.is_file() or markdown.read_bytes() != expected_md:
        errors.append(f"Comparison Markdown mismatch: {markdown}")
    except (OSError, ValueError, KeyError) as error:
      errors.append(str(error))
  if errors:
    raise ValueError("Archive validation failed:\n" + "\n".join(f"- {item}" for item in errors))
  return {
    "status": "PASS",
    "reports": len(report_paths),
    "comparisons": len(config.get("comparisons", [])),
    "pricing_file": (
      pricing_path.relative_to(archive_root).as_posix()
      if pricing_path is not None
      else None
    ),
  }


def _check_json_bytes(
  path: Path,
  expected: dict[str, Any],
  errors: list[str],
) -> None:
  expected_bytes = (
    json.dumps(expected, indent=2, ensure_ascii=False) + "\n"
  ).encode("utf-8")
  if not path.is_file() or path.read_bytes() != expected_bytes:
    errors.append(f"JSON replay mismatch: {path}")


def _validate_archive_paths(archive_root: Path, errors: list[str]) -> None:
  for path in sorted(archive_root.rglob("*")):
    relative = path.relative_to(archive_root)
    if path.is_file() and (
      path.suffix in FORBIDDEN_SUFFIXES
      or path.name in FORBIDDEN_NAMES
      or any(part in FORBIDDEN_PARTS for part in relative.parts)
      or any(part.startswith(".eval-") for part in relative.parts)
    ):
      errors.append(f"forbidden archived path: {relative.as_posix()}")


def _validate_sensitive_content(archive_root: Path, errors: list[str]) -> None:
  for path in sorted(archive_root.rglob("*")):
    if not path.is_file():
      continue
    try:
      text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
      errors.append(f"non UTF-8 archive file: {path.relative_to(archive_root)}")
      continue
    for pattern in SECRET_PATTERNS:
      match = pattern.search(text)
      if match and "[REDACTED]" not in match.group(0):
        errors.append(
          f"credential pattern in {path.relative_to(archive_root).as_posix()}"
        )
        break


def _display(value: Any) -> str:
  return "unknown" if value is None else str(value)
