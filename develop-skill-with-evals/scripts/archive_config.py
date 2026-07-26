#!/usr/bin/env python3
"""Load and validate repository evaluation archive configuration."""

import json
from pathlib import Path
from typing import Any

from eval_report import load_pricing


ARCHIVE_CONFIG_NAME = "archive-config.json"


def load_archive_config(path: Path) -> dict[str, Any]:
  with path.open(encoding="utf-8") as stream:
    config = json.load(stream)
  if not isinstance(config, dict) or config.get("version") != 1:
    raise ValueError("Archive config version must be 1")
  pricing_file = config.get("pricing_file")
  if pricing_file is not None and not isinstance(pricing_file, str):
    raise ValueError("Archive config pricing_file must be a relative path")
  comparisons = config.get("comparisons", [])
  if not isinstance(comparisons, list):
    raise ValueError("Archive config comparisons must be an array")
  for comparison in comparisons:
    if (
      not isinstance(comparison, dict)
      or not isinstance(comparison.get("skill"), str)
      or not isinstance(comparison.get("id"), str)
      or not isinstance(comparison.get("operation_ids"), list)
      or not all(
        isinstance(operation_id, str)
        for operation_id in comparison["operation_ids"]
      )
    ):
      raise ValueError("Every comparison requires skill, id, and operation_ids")
    if len(set(comparison["operation_ids"])) != len(comparison["operation_ids"]):
      raise ValueError(f"Comparison {comparison['id']} contains duplicate ids")
  return config


def configured_pricing_path(config_path: Path, config: dict[str, Any]) -> Path | None:
  relative = config.get("pricing_file")
  if relative is None:
    return None
  candidate = (config_path.parent / relative).resolve()
  try:
    candidate.relative_to(config_path.parent.resolve())
  except ValueError as error:
    raise ValueError("Archive pricing_file must remain inside the archive") from error
  load_pricing(candidate)
  return candidate
