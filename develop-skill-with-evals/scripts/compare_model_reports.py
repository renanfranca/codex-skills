#!/usr/bin/env python3
"""Compare canonical skill evaluation evidence reports by executor model."""

import argparse
from collections import defaultdict
import json
from pathlib import Path
import statistics
from typing import Any

from eval_report import api_reference_estimate, atomic_write_text, load_report


TOKEN_FIELDS = (
  "input_tokens",
  "cached_input_tokens",
  "output_tokens",
  "reasoning_output_tokens",
)


def compare_reports(reports_root: Path) -> dict[str, Any]:
  report_paths = sorted(reports_root.rglob("report.json"))
  return compare_report_paths(report_paths)


def compare_report_paths(report_paths: list[Path]) -> dict[str, Any]:
  observations: list[dict[str, Any]] = []
  operation_ids: set[str] = set()
  skill_names: set[str] = set()
  for path in report_paths:
    report = load_report(path)
    operation_id = report["operation"]["id"]
    if operation_id in operation_ids:
      raise ValueError(f"Duplicate operation id: {operation_id}")
    operation_ids.add(operation_id)
    skill_names.add(report["skill"]["name"])
    model = report["runtime"]["executor"]["model"] or "configured-default"
    for observation in report["observations"]:
      observations.append({
        **observation,
        "_model": model,
        "_estimate": _observation_estimate(report, observation),
        "_operation_id": operation_id,
      })
  if len(skill_names) > 1:
    raise ValueError(
      "Reports from different skills cannot be compared together: "
      + ", ".join(sorted(skill_names))
    )

  grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
  for observation in observations:
    grouped[observation["_model"]].append(observation)
  models = [
    _model_summary(model, grouped[model])
    for model in sorted(grouped)
  ]
  return {
    "version": 1,
    "report_count": len(report_paths),
    "observation_count": len(observations),
    "executed_observation_count": sum(
      observation.get("provenance") == "executed"
      for observation in observations
    ),
    "models": models,
    "directional_pilot": True,
    "limitations": [
      "The comparison is directional and is not statistical proof.",
      "API reference estimates are not observed ChatGPT charges.",
      "A model qualifies only with at least three stable PASS observations in every represented case.",
    ],
  }


def render_comparison(comparison: dict[str, Any]) -> str:
  lines = [
    "# Model evaluation comparison",
    "",
    f"- Reports: `{comparison['report_count']}`",
    f"- Observations: `{comparison['observation_count']}`",
    f"- Executed observations: `{comparison['executed_observation_count']}`",
    "- Interpretation: directional pilot, not statistical proof.",
    "",
    "| Model | PASS | Observations | Qualifies | Input tokens | Output tokens | Reasoning output | Duration ms | API reference |",
    "| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: |",
  ]
  for model in comparison["models"]:
    lines.append(
      "| "
      + " | ".join([
        model["model"],
        str(model["pass_count"]),
        str(model["observation_count"]),
        "yes" if model["qualifies"] else "no",
        str(model["tokens"]["input"]["total"]),
        str(model["tokens"]["output"]["total"]),
        str(model["tokens"]["reasoning_output"]["total"]),
        str(model["duration_ms"]["total"]),
        _display(model["api_reference_cost"]["total"]),
      ])
      + " |"
    )
    lines.extend(["", f"## {model['model']}", ""])
    for case in model["cases"]:
      lines.append(
        f"- `{case['case_id']}`: {case['pass_count']}/{case['observation_count']} PASS, "
        f"stable `{str(case['stable']).lower()}`"
      )
    lines.append(
      f"- Explanation complete ratio: `{model['explanation']['complete_ratio']}`"
    )
    lines.append(
      f"- Explanation coherent ratio: `{model['explanation']['coherent_ratio']}`"
    )
    lines.append(
      f"- Base-rate API reference: "
      f"`{_display(model['api_reference_cost']['base_rate_total'])}`"
    )
    lines.append(
      f"- Long context indeterminate observations: "
      f"`{model['api_reference_cost']['indeterminate_long_context_count']}`"
    )
  lines.append("")
  return "\n".join(lines)


def _model_summary(model: str, observations: list[dict[str, Any]]) -> dict[str, Any]:
  by_case: dict[str, list[dict[str, Any]]] = defaultdict(list)
  for observation in observations:
    by_case[observation["case_id"]].append(observation)
  cases = []
  for case_id in sorted(by_case):
    case_observations = by_case[case_id]
    signatures = {_signature(item) for item in case_observations}
    cases.append({
      "case_id": case_id,
      "observation_count": len(case_observations),
      "pass_count": sum(item["status"] == "PASS" for item in case_observations),
      "stable": len(signatures) == 1,
      "signature_count": len(signatures),
    })
  token_summary = {}
  for field, label in (
    ("input_tokens", "input"),
    ("cached_input_tokens", "cached_input"),
    ("output_tokens", "output"),
    ("reasoning_output_tokens", "reasoning_output"),
  ):
    values = [
      item["usage"].get(field)
      for item in observations
      if isinstance(item["usage"].get(field), int)
    ]
    token_summary[label] = _numeric_summary(values, len(observations))
  input_total = token_summary["input"]["total"]
  cached_total = token_summary["cached_input"]["total"]
  cache_ratio = (
    round(cached_total / input_total, 6)
    if input_total
    else None
  )
  durations = [
    item["duration_ms"]
    for item in observations
    if isinstance(item.get("duration_ms"), int)
  ]
  estimates = [
    item["_estimate"]["amount"]
    for item in observations
    if item["_estimate"]["available"]
  ]
  base_rate_estimates = [
    item["_estimate"]["base_rate_amount"]
    for item in observations
    if isinstance(item["_estimate"].get("base_rate_amount"), (int, float))
  ]
  stable_valid_gates = sum(
    case["observation_count"]
    for case in cases
    if case["stable"] and case["pass_count"] == case["observation_count"]
  )
  estimates_complete = len(estimates) == len(observations)
  estimate_total = (
    round(sum(estimates), 12)
    if estimates_complete and estimates
    else None
  )
  base_rate_total = (
    round(sum(base_rate_estimates), 12)
    if len(base_rate_estimates) == len(observations) and base_rate_estimates
    else None
  )
  complete = [_explanation_complete(item) for item in observations]
  coherent = [_explanation_coherent(item) for item in observations]
  return {
    "model": model,
    "observation_count": len(observations),
    "pass_count": sum(item["status"] == "PASS" for item in observations),
    "cases": cases,
    "qualifies": bool(cases) and all(
      case["observation_count"] >= 3
      and case["pass_count"] == case["observation_count"]
      and case["stable"]
      for case in cases
    ),
    "tokens": token_summary,
    "cache_ratio": cache_ratio,
    "duration_ms": _numeric_summary(durations, len(observations)),
    "api_reference_cost": {
      "total": estimate_total,
      "complete": estimates_complete,
      "base_rate_total": base_rate_total,
      "indeterminate_long_context_count": sum(
        item["_estimate"].get("status") == "indeterminate-long-context"
        for item in observations
      ),
      "effective_per_stable_gate": (
        round(estimate_total / stable_valid_gates, 12)
        if estimate_total is not None and stable_valid_gates
        else None
      ),
      "base_rate_per_stable_gate": (
        round(base_rate_total / stable_valid_gates, 12)
        if base_rate_total is not None and stable_valid_gates
        else None
      ),
      "actual_charge": False,
    },
    "explanation": {
      "complete_count": sum(complete),
      "complete_ratio": round(sum(complete) / len(complete), 6) if complete else None,
      "coherent_count": sum(coherent),
      "coherent_ratio": round(sum(coherent) / len(coherent), 6) if coherent else None,
    },
  }


def _numeric_summary(values: list[int], expected: int) -> dict[str, Any]:
  return {
    "total": sum(values),
    "median": statistics.median(values) if values else None,
    "complete": len(values) == expected,
  }


def _signature(observation: dict[str, Any]) -> str:
  value = {
    "status": observation["status"],
    "mechanical": [
      [check["name"], check["passed"]]
      for check in observation["mechanical"].get("checks", [])
    ],
    "oracle": observation["oracle"].get("passed"),
    "judge": observation["judge"].get("verdict"),
    "changed_files": observation["evidence"].get("changed_files", []),
  }
  return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _explanation_complete(observation: dict[str, Any]) -> bool:
  response = observation["executor"].get("response")
  if not isinstance(response, dict):
    return False
  return (
    isinstance(response.get("diagnosis"), str)
    and all(
      isinstance(response.get(field), list)
      for field in (
        "approach",
        "decisions",
        "rejected_alternatives",
        "key_changes",
        "validation",
      )
    )
  )


def _explanation_coherent(observation: dict[str, Any]) -> bool:
  response = observation["executor"].get("response")
  if not _explanation_complete(observation):
    return False
  declared = set(response.get("files_changed", []))
  changed = set(observation["evidence"].get("changed_files", []))
  return declared.issubset(changed) and bool(response.get("validation"))


def _observation_estimate(
  report: dict[str, Any],
  observation: dict[str, Any],
) -> dict[str, Any]:
  pricing = report.get("pricing", {})
  model = report["runtime"]["executor"]["model"]
  return api_reference_estimate(
    pricing,
    observation.get("usage", {}),
    model,
    report.get("billing", {}).get("mode", "unknown"),
  )


def _display(value: Any) -> str:
  return "unavailable" if value is None else str(value)


def main() -> int:
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("--reports", type=Path, required=True)
  parser.add_argument("--output-dir", type=Path, required=True)
  args = parser.parse_args()
  comparison = compare_reports(args.reports)
  args.output_dir.mkdir(parents=True, exist_ok=True)
  atomic_write_text(
    args.output_dir / "comparison.json",
    json.dumps(comparison, indent=2, ensure_ascii=False) + "\n",
  )
  atomic_write_text(
    args.output_dir / "comparison.md",
    render_comparison(comparison),
  )
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
