# Evaluation evidence: 20260726T151204.350808Z-4a0eb0057728

- Operation: `run`
- Status: `PASS`
- Provenance: `executed`
- Started: `2026-07-26T15:12:04.350808Z`
- Finished: `2026-07-26T15:14:48.650286Z`
- Duration: `164653 ms`
- Executor model: `gpt-5.6-sol`
- Executor effort: `medium`
- Codex CLI: `codex-cli 0.145.0`
- Authentication: `chatgpt`
- Runner SHA-256: `c63a75cb545b42f3479d20e8937ac1b2e8eb93b06064aebeb7630630a02540e9`

## Consumption

- Tokens: input `678628`, cached input `622336`, output `5981`, reasoning output `1628`
- Normalized usage events: `1`, complete `true`, scopes `turn`
- Sessions: planned `1`, executed `1`

## API reference estimate

- Reference amount: unavailable
- This is not an actual charge.
- Base-rate amount: `0.772058000000 USD`
- Estimate status: `indeterminate-long-context`
- Limitation: This is an API reference estimate, not an observed charge.
- Limitation: This dated table is an API reference and is not an observed ChatGPT charge.
- Limitation: Prompts above 272,000 input tokens use the documented higher rates; an exact estimate is unavailable when normalized telemetry does not expose request scoped input.
- Limitation: Cache write charges are not estimated because Codex JSONL usage does not identify cache writes.
- Limitation: Reasoning output tokens are reported separately but are already included in output tokens.
- Limitation: A reported usage event exceeded a request-scoped threshold, but the event is not request scoped; the exact multiplier cannot be audited.

## Observation 1: explicit-runtime-promotion-workflow

- Status: `PASS`
- Role: `observation`
- Repetition: `1`
- Duration: `164531 ms`
- Workspace retention: `removed`
- Tokens: input `678628`, cached input `622336`, output `5981`, reasoning output `1628`
- Normalized usage events: `1`, complete `true`, scopes `turn`

### Executor account

Diagnosis: The renderer uppercased input without first removing surrounding whitespace.

Approach:
- Planned and ran the diagnostic workflow.
- Planned and ran the promotion workflow.
- Performed schema, structural, and scope validation.

Decisions:
- Classified the change as deterministic.
- Authorized zero model sessions, matching both displayed plans.

Rejected Alternatives:
- None recorded.

Key Changes:
- Changed rendering to `sys.argv[1].strip().upper()`.
- Kept `sample-baseline` unchanged.

Validation:
- Diagnostic: PASS, baseline FAIL and candidate PASS.
- Promotion: PASS and promotion eligible.
- Candidate passed three stable repetitions.
- Executor and judge declarations matched the requested models and medium reasoning effort.
- Skill structural validation passed.

### Mechanical facts

- Mechanical result: `PASS`
- Oracle result: `PASS`
- Judge verdict: `PASS`
- `executor exit code`: `PASS`
- `executor response schema`: `PASS`
- `required path: diagnostic-plan.json`: `PASS`
- `required path: diagnostic.json`: `PASS`
- `required path: promotion-plan.json`: `PASS`
- `required path: validation.json`: `PASS`
- `forbidden changed path: .agents/skills/**`: `PASS`
- `forbidden changed path: sample-skill/SKILL.md`: `PASS`
- `forbidden changed path: sample-baseline/**`: `PASS`
- `forbidden changed path: audit-runner`: `PASS`
- `forbidden changed path: fake-codex`: `PASS`
- `forbidden changed path: check_workflow.py`: `PASS`
- `evaluated skill remained unchanged`: `PASS`

### Changed files

- `diagnostic-plan.json`
- `diagnostic.json`
- `promotion-plan.json`
- `runner-invocations.jsonl`
- `sample-skill/scripts/render.py`
- `validation.json`

### Sanitized diff

```diff
--- /dev/null
+++ b/diagnostic-plan.json
@@ -0,0 +1,95 @@
+{
+  "operation": "plan",
+  "workflow": "diagnostic",
+  "promotion_eligible": false,
+  "skill": "/tmp/persist-eval-evidence.auoqZx/pilot-v2-artifacts/run-v2-14/run-4qadsd5x/explicit-runtime-promotion-workflow-sr9ky1_y/sample-skill",
+  "baseline": "/tmp/persist-eval-evidence.auoqZx/pilot-v2-artifacts/run-v2-14/run-4qadsd5x/explicit-runtime-promotion-workflow-sr9ky1_y/sample-baseline",
+  "impact": "deterministic",
+  "selected_cases": [
+    "trim-uppercase"
+  ],
+  "regression_cases": [],
+  "steps": [
+    "baseline-red",
+    "candidate-observation",
+    "structural-validation"
+  ],
+  "commands": [
+    "python3 /tmp/persist-eval-evidence.auoqZx/pilot-v2-artifacts/run-v2-14/run-4qadsd5x/explicit-runtime-promotion-workflow-sr9ky1_y/.agents/skills/develop-skill-with-evals/scripts/run_skill_evals.py probe-change --skill /tmp/persist-eval-evidence.auoqZx/pilot-v2-artifacts/run-v2-14/run-4qadsd5x/explicit-runtime-promotion-workflow-sr9ky1_y/sample-skill --baseline /tmp/persist-eval-evidence.auoqZx/pilot-v2-artifacts/run-v2-14/run-4qadsd5x/explicit-runtime-promotion-workflow-sr9ky1_y/sample-baseline --impact deterministic --case trim-uppercase --model gpt-5.6-sol --reasoning-effort medium --judge-model gpt-5.6-terra --judge-reasoning-effort medium --approved-model-sessions 8",
+    "python3 .system/skill-creator/scripts/quick_validate.py /tmp/persist-eval-evidence.auoqZx/pilot-v2-artifacts/run-v2-14/run-4qadsd5x/explicit-runtime-promotion-workflow-sr9ky1_y/sample-skill"
+  ],
+  "executions": {
+    "baseline": {
+      "affected": 1,
+      "total": 1
+    },
+    "candidate": {
+      "affected": 1,
+      "regression": 0,
+      "total": 1
+    }
+  },
+  "sessions": {
+    "baseline": {
+      "executor": 0,
+      "judge": 0,
+      "total": 0
+    },
+    "candidate": {
+      "executor": 0,
+      "judge": 0,
+      "total": 0
+    },
+    "executor": 0,
+    "judge": 0,
+    "total": 0
+  },
+  "approved_model_sessions": 8,
+  "approval_required": false,
+  "reasons": [
+    "Selected behavior is fully observable by direct mechanical checks."
+  ],
+  "warnings": [
+    "Session counts exclude tokens, duration, and financial cost.",
+    "Sandbox or shell approval is not approval for model session consumption.",
+    "Underclassifying an uncertain change is a workflow error; use cross-cutting when reach is unclear."
+  ],
+  "manifest_fingerprint": "9944b7cfcb48a401a87f7ecb3faee55502adedba9e86a5bf9c33bf191b382f83",
+  "case_fingerprints": {
+    "trim-uppercase": "ed8aaccfcd341190faed528ab0da71afe2d811ffa42c6883aad12ff9eb3debb6"
+  },
+  "source_fingerprints": {
+    "baseline": "10f3af4aa42ea3f4e3262cdcbb18366e13c0b74af9f757e482741c8486c3425a",
+    "candidate": "b930099eb6c128e2527615c9dbf7ff2c3f61b8a04a52395835cb95e546a53049"
+  },
+  "runtime": {
+    "required": false,
+    "complete": true,
+    "audit_quality": "not_applicable",
+    "executor": {
+      "required": false,
+      "model": "gpt-5.6-sol",
+      "model_source": "cli",
+      "reasoning_effort": "medium",
+      "reasoning_effort_source": "cli"
+    },
+    "judge": {
+      "required": false,
+      "model": "gpt-5.6-terra",
+      "model_source": "cli",
+      "reasoning_effort": "medium",
+      "reasoning_effort_source": "cli"
+    }
+  },
+  "runtime_fingerprint": "b7ec6ffb777fd6feb2240c4ebc33c20dd3b87fd0e176325a6a2fac7751221590",
+  "campaign": {
+    "ledger": null,
+    "approved_cumulative_model_sessions": null,
+    "consumed_before": 0,
+    "reserved_before": 0,
+    "planned_maximum": 0,
+    "projected_maximum": 0
+  },
+  "execution_blockers": [],
+  "evaluation_fingerprint": "de76ee6594a7654b32272cacfdd2af2f030e260ee7500a205e85b2e64a8894c0"
+}
--- /dev/null
+++ b/diagnostic.json
@@ -0,0 +1,350 @@
+{
+  "operation": "probe-change",
+  "status": "PASS",
+  "workflow": "diagnostic",
+  "promotion_eligible": false,
+  "failure_category": null,
+  "skill": "/tmp/persist-eval-evidence.auoqZx/pilot-v2-artifacts/run-v2-14/run-4qadsd5x/explicit-runtime-promotion-workflow-sr9ky1_y/sample-skill",
+  "model": "gpt-5.6-sol",
+  "runtime": {
+    "required": false,
+    "complete": true,
+    "audit_quality": "not_applicable",
+    "executor": {
+      "required": false,
+      "model": "gpt-5.6-sol",
+      "model_source": "cli",
+      "reasoning_effort": "medium",
+      "reasoning_effort_source": "cli"
+    },
+    "judge": {
+      "required": false,
+      "model": "gpt-5.6-terra",
+      "model_source": "cli",
+      "reasoning_effort": "medium",
+      "reasoning_effort_source": "cli"
+    }
+  },
+  "model_sessions": {
+    "executor": 0,
+    "judge": 0,
+    "total": 0
+  },
+  "usage": {
+    "input_tokens": null,
+    "cached_input_tokens": null,
+    "output_tokens": null,
+    "reasoning_output_tokens": null,
+    "total_tokens": null,
+    "complete": false,
+    "reasoning_output_tokens_complete": false,
+    "events": [],
+    "event_count": 0,
+    "events_complete": false
+  },
+  "campaign": {
+    "ledger": null,
+    "approved_cumulative_model_sessions": null,
+    "consumed_before": 0,
+    "reserved_before": 0,
+    "planned_maximum": 0,
+    "projected_maximum": 0,
+    "consumed_operation": 0,
+    "consumed_after": null
+  },
+  "plan": {
+    "operation": "plan",
+    "workflow": "diagnostic",
+    "promotion_eligible": false,
+    "skill": "/tmp/persist-eval-evidence.auoqZx/pilot-v2-artifacts/run-v2-14/run-4qadsd5x/explicit-runtime-promotion-workflow-sr9ky1_y/sample-skill",
+    "baseline": "/tmp/persist-eval-evidence.auoqZx/pilot-v2-artifacts/run-v2-14/run-4qadsd5x/explicit-runtime-promotion-workflow-sr9ky1_y/sample-baseline",
+    "impact": "deterministic",
+    "selected_cases": [
+      "trim-uppercase"
+    ],
+    "regression_cases": [],
+    "steps": [
+      "baseline-red",
+      "candidate-observation",
+      "structural-validation"
+    ],
+    "commands": [
+      "python3 /tmp/persist-eval-evidence.auoqZx/pilot-v2-artifacts/run-v2-14/run-4qadsd5x/explicit-runtime-promotion-workflow-sr9ky1_y/.agents/skills/develop-skill-with-evals/scripts/run_skill_evals.py probe-change --skill /tmp/persist-eval-evidence.auoqZx/pilot-v2-artifacts/run-v2-14/run-4qadsd5x/explicit-runtime-promotion-workflow-sr9ky1_y/sample-skill --baseline /tmp/persist-eval-evidence.auoqZx/pilot-v2-artifacts/run-v2-14/run-4qadsd5x/explicit-runtime-promotion-workflow-sr9ky1_y/sample-baseline --impact deterministic --case trim-uppercase --model gpt-5.6-sol --reasoning-effort medium --judge-model gpt-5.6-terra --judge-reasoning-effort medium --approved-model-sessions 0",
+      "python3 .system/skill-creator/scripts/quick_validate.py /tmp/persist-eval-evidence.auoqZx/pilot-v2-artifacts/run-v2-14/run-4qadsd5x/explicit-runtime-promotion-workflow-sr9ky1_y/sample-skill"
+    ],
+    "executions": {
+      "baseline": {
+        "affected": 1,
+        "total": 1
+      },
+      "candidate": {
+        "affected": 1,
+        "regression": 0,
+        "total": 1
+      }
+    },
+    "sessions": {
+      "baseline": {
+        "executor": 0,
+        "judge": 0,
+        "total": 0
+      },
+      "candidate": {
+        "executor": 0,
+        "judge": 0,
+        "total": 0
+      },
+      "executor": 0,
+      "judge": 0,
+      "total": 0
+    },
+    "approved_model_sessions": 0,
+    "approval_required": false,
+    "reasons": [
+      "Selected behavior is fully observable by direct mechanical checks."
+    ],
+    "warnings": [
+      "Session counts exclude tokens, duration, and financial cost.",
+      "Sandbox or shell approval is not approval for model session consumption.",
+      "Underclassifying an uncertain change is a workflow error; use cross-cutting when reach is unclear."
+    ],
+    "manifest_fingerprint": "9944b7cfcb48a401a87f7ecb3faee55502adedba9e86a5bf9c33bf191b382f83",
+    "case_fingerprints": {
+      "trim-uppercase": "ed8aaccfcd341190faed528ab0da71afe2d811ffa42c6883aad12ff9eb3debb6"
+    },
+    "source_fingerprints": {
+      "baseline": "10f3af4aa42ea3f4e3262cdcbb18366e13c0b74af9f757e482741c8486c3425a",
+      "candidate": "b930099eb6c128e2527615c9dbf7ff2c3f61b8a04a52395835cb95e546a53049"
+    },
+    "runtime": {
+      "required": false,
+      "complete": true,
+      "audit_quality": "not_applicable",
+      "executor": {
+        "required": false,
+        "model": "gpt-5.6-sol",
+        "model_source": "cli",
+        "reasoning_effort": "medium",
+        "reasoning_effort_source": "cli"
+      },
+      "judge": {
+        "required": false,
+        "model": "gpt-5.6-terra",
+        "model_source": "cli",
+        "reasoning_effort": "medium",
+        "reasoning_effort_source": "cli"
+      }
+    },
+    "runtime_fingerprint": "b7ec6ffb777fd6feb2240c4ebc33c20dd3b87fd0e176325a6a2fac7751221590",
+    "campaign": {
+      "ledger": null,
+      "approved_cumulative_model_sessions": null,
+      "consumed_before": 0,
+      "reserved_before": 0,
+      "planned_maximum": 0,
+      "projected_maximum": 0
+    },
+    "execution_blockers": [],
+    "evaluation_fingerprint": "de76ee6594a7654b32272cacfdd2af2f030e260ee7500a205e85b2e64a8894c0"
+  },
+  "results": [
+    {
+      "case_id": "trim-uppercase",
+      "status": "FAIL",
+      "kind": "deterministic",
+      "executor": {
+        "enabled": false,
+        "executed": false,
+        "exit_code": null,
+        "response": null,
+        "stderr": "",
+        "usage": {
+          "input_tokens": null,
+          "cached_input_tokens": null,
+          "output_tokens": null,
+          "reasoning_output_tokens": null,
+          "total_tokens": null,
+          "complete": false,
+          "reasoning_output_tokens_complete": false,
+          "events": [],
+          "event_count": 0,
+          "events_complete": false
+        },
+        "duration_ms": 0
+      },
+      "mechanical": {
+        "passed": false,
+        "checks": [
+          {
+            "name": "command: python3 check_trim.py",
+            "passed": false,
+            "detail": "expected 0, got 1"
+          },
+          {
+            "name": "evaluated skill remained unchanged",
+            "passed": true,
+            "detail": "evaluated skill hash comparison"
+          }
+        ],
+        "commands": [
+          {
+            "argv": [
+              "python3",
+              "check_trim.py"
+            ],
+            "exit_code": 1,
+            "stdout": "",
+            "stderr": "Traceback (most recent call last):\n  File \"/tmp/skill-eval-artifacts/probe-change-po5a2ojz/trim-uppercase-1onvpe7j/check_trim.py\", line 16, in <module>\n    assert completed.stdout == \"HELLO\\n\"\nAssertionError\n"
+          }
+        ]
+      },
+      "oracle": {
+        "enabled": false,
+        "passed": true,
+        "commands": []
+      },
+      "judge": {
+        "enabled": false,
+        "executed": false,
+        "verdict": "PASS",
+        "rationale": "Deterministic cases do not use a semantic judge.",
+        "evidence": [],
+        "usage": {
+          "input_tokens": null,
+          "cached_input_tokens": null,
+          "output_tokens": null,
+          "reasoning_output_tokens": null,
+          "total_tokens": null,
+          "complete": false,
+          "reasoning_output_tokens_complete": false,
+          "events": [],
+          "event_count": 0,
+          "events_complete": false
+        },
+        "duration_ms": 0,
+        "failure_category": null
+      },
+      "changed_paths": [],
+      "workspace": null,
+      "model_sessions": {
+        "executor": 0,
+        "judge": 0,
+        "total": 0
+      },
+      "usage": {
+        "input_tokens": null,
+        "cached_input_tokens": null,
+        "output_tokens": null,
+        "reasoning_output_tokens": null,
+        "total_tokens": null,
+        "complete": false,
+        "reasoning_output_tokens_complete": false,
+        "events": [],
+        "event_count": 0,
+        "events_complete": false
+      },
+      "failure_category": "contract",
+      "role": "baseline"
+    },
+    {
+      "case_id": "trim-uppercase",
+      "status": "PASS",
+      "kind": "deterministic",
+      "executor": {
+        "enabled": false,
+        "executed": false,
+        "exit_code": null,
+        "response": null,
+        "stderr": "",
+        "usage": {
+          "input_tokens": null,
+          "cached_input_tokens": null,
+          "output_tokens": null,
+          "reasoning_output_tokens": null,
+          "total_tokens": null,
+          "complete": false,
+          "reasoning_output_tokens_complete": false,
+          "events": [],
+          "event_count": 0,
+          "events_complete": false
+        },
+        "duration_ms": 0
+      },
+      "mechanical": {
+        "passed": true,
+        "checks": [
+          {
+            "name": "command: python3 check_trim.py",
+            "passed": true,
+            "detail": "expected 0, got 0"
+          },
+          {
+            "name": "evaluated skill remained unchanged",
+            "passed": true,
+            "detail": "evaluated skill hash comparison"
+          }
+        ],
+        "commands": [
+          {
+            "argv": [
+              "python3",
+              "check_trim.py"
+            ],
+            "exit_code": 0,
+            "stdout": "",
+            "stderr": ""
+          }
+        ]
+      },
+      "oracle": {
+        "enabled": false,
+        "passed": true,
+        "commands": []
+      },
+      "judge": {
+        "enabled": false,
+        "executed": false,
+        "verdict": "PASS",
+        "rationale": "Deterministic cases do not use a semantic judge.",
+        "evidence": [],
+        "usage": {
+          "input_tokens": null,
+          "cached_input_tokens": null,
+          "output_tokens": null,
+          "reasoning_output_tokens": null,
+          "total_tokens": null,
+          "complete": false,
+          "reasoning_output_tokens_complete": false,
+          "events": [],
+          "event_count": 0,
+          "events_complete": false
+        },
+        "duration_ms": 0,
+        "failure_category": null
+      },
+      "changed_paths": [],
+      "workspace": null,
+      "model_sessions": {
+        "executor": 0,
+        "judge": 0,
+        "total": 0
+      },
+      "usage": {
+        "input_tokens": null,
+        "cached_input_tokens": null,
+        "output_tokens": null,
+        "reasoning_output_tokens": null,
+        "total_tokens": null,
+        "complete": false,
+        "reasoning_output_tokens_complete": false,
+        "events": [],
+        "event_count": 0,
+        "events_complete": false
+      },
+      "failure_category": null,
+      "role": "candidate",
+      "repetition": 1
+    }
+  ],
+  "artifacts": null
+}
--- /dev/null
+++ b/promotion-plan.json
@@ -0,0 +1,96 @@
+{
+  "operation": "plan",
+  "workflow": "promotion",
+  "promotion_eligible": true,
+  "skill": "/tmp/persist-eval-evidence.auoqZx/pilot-v2-artifacts/run-v2-14/run-4qadsd5x/explicit-runtime-promotion-workflow-sr9ky1_y/sample-skill",
+  "baseline": "/tmp/persist-eval-evidence.auoqZx/pilot-v2-artifacts/run-v2-14/run-4qadsd5x/explicit-runtime-promotion-workflow-sr9ky1_y/sample-baseline",
+  "impact": "deterministic",
+  "selected_cases": [
+    "trim-uppercase"
+  ],
+  "regression_cases": [],
+  "steps": [
+    "baseline-red",
+    "candidate-green-1",
+    "candidate-green-2-and-3",
+    "structural-validation"
+  ],
+  "commands": [
+    "python3 /tmp/persist-eval-evidence.auoqZx/pilot-v2-artifacts/run-v2-14/run-4qadsd5x/explicit-runtime-promotion-workflow-sr9ky1_y/.agents/skills/develop-skill-with-evals/scripts/run_skill_evals.py validate-change --skill /tmp/persist-eval-evidence.auoqZx/pilot-v2-artifacts/run-v2-14/run-4qadsd5x/explicit-runtime-promotion-workflow-sr9ky1_y/sample-skill --baseline /tmp/persist-eval-evidence.auoqZx/pilot-v2-artifacts/run-v2-14/run-4qadsd5x/explicit-runtime-promotion-workflow-sr9ky1_y/sample-baseline --impact deterministic --case trim-uppercase --model gpt-5.6-sol --reasoning-effort medium --judge-model gpt-5.6-terra --judge-reasoning-effort medium --approved-model-sessions 8",
+    "python3 .system/skill-creator/scripts/quick_validate.py /tmp/persist-eval-evidence.auoqZx/pilot-v2-artifacts/run-v2-14/run-4qadsd5x/explicit-runtime-promotion-workflow-sr9ky1_y/sample-skill"
+  ],
+  "executions": {
+    "baseline": {
+      "affected": 1,
+      "total": 1
+    },
+    "candidate": {
+      "affected": 3,
+      "regression": 0,
+      "total": 3
+    }
+  },
+  "sessions": {
+    "baseline": {
+      "executor": 0,
+      "judge": 0,
+      "total": 0
+    },
+    "candidate": {
+      "executor": 0,
+      "judge": 0,
+      "total": 0
+    },
+    "executor": 0,
+    "judge": 0,
+    "total": 0
+  },
+  "approved_model_sessions": 8,
+  "approval_required": false,
+  "reasons": [
+    "Selected behavior is fully observable by direct mechanical checks."
+  ],
+  "warnings": [
+    "Session counts exclude tokens, duration, and financial cost.",
+    "Sandbox or shell approval is not approval for model session consumption.",
+    "Underclassifying an uncertain change is a workflow error; use cross-cutting when reach is unclear."
+  ],
+  "manifest_fingerprint": "9944b7cfcb48a401a87f7ecb3faee55502adedba9e86a5bf9c33bf191b382f83",
+  "case_fingerprints": {
+    "trim-uppercase": "ed8aaccfcd341190faed528ab0da71afe2d811ffa42c6883aad12ff9eb3debb6"
+  },
+  "source_fingerprints": {
+    "baseline": "10f3af4aa42ea3f4e3262cdcbb18366e13c0b74af9f757e482741c8486c3425a",
+    "candidate": "b930099eb6c128e2527615c9dbf7ff2c3f61b8a04a52395835cb95e546a53049"
+  },
+  "runtime": {
+    "required": false,
+    "complete": true,
+    "audit_quality": "not_applicable",
+    "executor": {
+      "required": false,
+      "model": "gpt-5.6-sol",
+      "model_source": "cli",
+      "reasoning_effort": "medium",
+      "reasoning_effort_source": "cli"
+    },
+    "judge": {
+      "required": false,
+      "model": "gpt-5.6-terra",
+      "model_source": "cli",
+      "reasoning_effort": "medium",
+      "reasoning_effort_source": "cli"
+    }
+  },
+  "runtime_fingerprint": "b7ec6ffb777fd6feb2240c4ebc33c20dd3b87fd0e176325a6a2fac7751221590",
+  "campaign": {
+    "ledger": null,
+    "approved_cumulative_model_sessions": null,
+    "consumed_before": 0,
+    "reserved_before": 0,
+    "planned_maximum": 0,
+    "projected_maximum": 0
+  },
+  "execution_blockers": [],
+  "evaluation_fingerprint": "179af861007b5e1c7f60c7237730b83b392056ae350796cdb02f928a999bb6de"
+}
--- /dev/null
+++ b/runner-invocations.jsonl
@@ -0,0 +1,8 @@
+["--help"]
+["plan", "--help"]
+["probe-change", "--help"]
+["validate-change", "--help"]
+["plan", "--skill", "sample-skill", "--baseline", "sample-baseline", "--impact", "deterministic", "--workflow", "diagnostic", "--model", "gpt-5.6-sol", "--reasoning-effort", "medium", "--judge-model", "gpt-5.6-terra", "--judge-reasoning-effort", "medium"]
+["probe-change", "--skill", "sample-skill", "--baseline", "sample-baseline", "--impact", "deterministic", "--approved-model-sessions", "0", "--model", "gpt-5.6-sol", "--reasoning-effort", "medium", "--judge-model", "gpt-5.6-terra", "--judge-reasoning-effort", "medium", "--codex-command", "./fake-codex", "--quiet"]
+["plan", "--skill", "sample-skill", "--baseline", "sample-baseline", "--impact", "deterministic", "--workflow", "promotion", "--model", "gpt-5.6-sol", "--reasoning-effort", "medium", "--judge-model", "gpt-5.6-terra", "--judge-reasoning-effort", "medium"]
+["validate-change", "--skill", "sample-skill", "--baseline", "sample-baseline", "--impact", "deterministic", "--approved-model-sessions", "0", "--model", "gpt-5.6-sol", "--reasoning-effort", "medium", "--judge-model", "gpt-5.6-terra", "--judge-reasoning-effort", "medium", "--codex-command", "./fake-codex", "--quiet"]
--- a/sample-skill/scripts/render.py
+++ b/sample-skill/scripts/render.py
@@ -2,4 +2,4 @@
 import sys


-print(sys.argv[1].upper())
+print(sys.argv[1].strip().upper())
--- /dev/null
+++ b/validation.json
@@ -0,0 +1,549 @@
+{
+  "operation": "validate-change",
+  "status": "PASS",
+  "workflow": "promotion",
+  "promotion_eligible": true,
+  "failure_category": null,
+  "skill": "/tmp/persist-eval-evidence.auoqZx/pilot-v2-artifacts/run-v2-14/run-4qadsd5x/explicit-runtime-promotion-workflow-sr9ky1_y/sample-skill",
+  "model": "gpt-5.6-sol",
+  "runtime": {
+    "required": false,
+    "complete": true,
+    "audit_quality": "not_applicable",
+    "executor": {
+      "required": false,
+      "model": "gpt-5.6-sol",
+      "model_source": "cli",
+      "reasoning_effort": "medium",
+      "reasoning_effort_source": "cli"
+    },
+    "judge": {
+      "required": false,
+      "model": "gpt-5.6-terra",
+      "model_source": "cli",
+      "reasoning_effort": "medium",
+      "reasoning_effort_source": "cli"
+    }
+  },
+  "model_sessions": {
+    "executor": 0,
+    "judge": 0,
+    "total": 0
+  },
+  "usage": {
+    "input_tokens": null,
+    "cached_input_tokens": null,
+    "output_tokens": null,
+    "reasoning_output_tokens": null,
+    "total_tokens": null,
+    "complete": false,
+    "reasoning_output_tokens_complete": false,
+    "events": [],
+    "event_count": 0,
+    "events_complete": false
+  },
+  "campaign": {
+    "ledger": null,
+    "approved_cumulative_model_sessions": null,
+    "consumed_before": 0,
+    "reserved_before": 0,
+    "planned_maximum": 0,
+    "projected_maximum": 0,
+    "consumed_operation": 0,
+    "consumed_after": null
+  },
+  "plan": {
+    "operation": "plan",
+    "workflow": "promotion",
+    "promotion_eligible": true,
+    "skill": "/tmp/persist-eval-evidence.auoqZx/pilot-v2-artifacts/run-v2-14/run-4qadsd5x/explicit-runtime-promotion-workflow-sr9ky1_y/sample-skill",
+    "baseline": "/tmp/persist-eval-evidence.auoqZx/pilot-v2-artifacts/run-v2-14/run-4qadsd5x/explicit-runtime-promotion-workflow-sr9ky1_y/sample-baseline",
+    "impact": "deterministic",
+    "selected_cases": [
+      "trim-uppercase"
+    ],
+    "regression_cases": [],
+    "steps": [
+      "baseline-red",
+      "candidate-green-1",
+      "candidate-green-2-and-3",
+      "structural-validation"
+    ],
+    "commands": [
+      "python3 /tmp/persist-eval-evidence.auoqZx/pilot-v2-artifacts/run-v2-14/run-4qadsd5x/explicit-runtime-promotion-workflow-sr9ky1_y/.agents/skills/develop-skill-with-evals/scripts/run_skill_evals.py validate-change --skill /tmp/persist-eval-evidence.auoqZx/pilot-v2-artifacts/run-v2-14/run-4qadsd5x/explicit-runtime-promotion-workflow-sr9ky1_y/sample-skill --baseline /tmp/persist-eval-evidence.auoqZx/pilot-v2-artifacts/run-v2-14/run-4qadsd5x/explicit-runtime-promotion-workflow-sr9ky1_y/sample-baseline --impact deterministic --case trim-uppercase --model gpt-5.6-sol --reasoning-effort medium --judge-model gpt-5.6-terra --judge-reasoning-effort medium --approved-model-sessions 0",
+      "python3 .system/skill-creator/scripts/quick_validate.py /tmp/persist-eval-evidence.auoqZx/pilot-v2-artifacts/run-v2-14/run-4qadsd5x/explicit-runtime-promotion-workflow-sr9ky1_y/sample-skill"
+    ],
+    "executions": {
+      "baseline": {
+        "affected": 1,
+        "total": 1
+      },
+      "candidate": {
+        "affected": 3,
+        "regression": 0,
+        "total": 3
+      }
+    },
+    "sessions": {
+      "baseline": {
+        "executor": 0,
+        "judge": 0,
+        "total": 0
+      },
+      "candidate": {
+        "executor": 0,
+        "judge": 0,
+        "total": 0
+      },
+      "executor": 0,
+      "judge": 0,
+      "total": 0
+    },
+    "approved_model_sessions": 0,
+    "approval_required": false,
+    "reasons": [
+      "Selected behavior is fully observable by direct mechanical checks."
+    ],
+    "warnings": [
+      "Session counts exclude tokens, duration, and financial cost.",
+      "Sandbox or shell approval is not approval for model session consumption.",
+      "Underclassifying an uncertain change is a workflow error; use cross-cutting when reach is unclear."
+    ],
+    "manifest_fingerprint": "9944b7cfcb48a401a87f7ecb3faee55502adedba9e86a5bf9c33bf191b382f83",
+    "case_fingerprints": {
+      "trim-uppercase": "ed8aaccfcd341190faed528ab0da71afe2d811ffa42c6883aad12ff9eb3debb6"
+    },
+    "source_fingerprints": {
+      "baseline": "10f3af4aa42ea3f4e3262cdcbb18366e13c0b74af9f757e482741c8486c3425a",
+      "candidate": "b930099eb6c128e2527615c9dbf7ff2c3f61b8a04a52395835cb95e546a53049"
+    },
+    "runtime": {
+      "required": false,
+      "complete": true,
+      "audit_quality": "not_applicable",
+      "executor": {
+        "required": false,
+        "model": "gpt-5.6-sol",
+        "model_source": "cli",
+        "reasoning_effort": "medium",
+        "reasoning_effort_source": "cli"
+      },
+      "judge": {
+        "required": false,
+        "model": "gpt-5.6-terra",
+        "model_source": "cli",
+        "reasoning_effort": "medium",
+        "reasoning_effort_source": "cli"
+      }
+    },
+    "runtime_fingerprint": "b7ec6ffb777fd6feb2240c4ebc33c20dd3b87fd0e176325a6a2fac7751221590",
+    "campaign": {
+      "ledger": null,
+      "approved_cumulative_model_sessions": null,
+      "consumed_before": 0,
+      "reserved_before": 0,
+      "planned_maximum": 0,
+      "projected_maximum": 0
+    },
+    "execution_blockers": [],
+    "evaluation_fingerprint": "179af861007b5e1c7f60c7237730b83b392056ae350796cdb02f928a999bb6de"
+  },
+  "results": [
+    {
+      "case_id": "trim-uppercase",
+      "status": "FAIL",
+      "kind": "deterministic",
+      "executor": {
+        "enabled": false,
+        "executed": false,
+        "exit_code": null,
+        "response": null,
+        "stderr": "",
+        "usage": {
+          "input_tokens": null,
+          "cached_input_tokens": null,
+          "output_tokens": null,
+          "reasoning_output_tokens": null,
+          "total_tokens": null,
+          "complete": false,
+          "reasoning_output_tokens_complete": false,
+          "events": [],
+          "event_count": 0,
+          "events_complete": false
+        },
+        "duration_ms": 0
+      },
+      "mechanical": {
+        "passed": false,
+        "checks": [
+          {
+            "name": "command: python3 check_trim.py",
+            "passed": false,
+            "detail": "expected 0, got 1"
+          },
+          {
+            "name": "evaluated skill remained unchanged",
+            "passed": true,
+            "detail": "evaluated skill hash comparison"
+          }
+        ],
+        "commands": [
+          {
+            "argv": [
+              "python3",
+              "check_trim.py"
+            ],
+            "exit_code": 1,
+            "stdout": "",
+            "stderr": "Traceback (most recent call last):\n  File \"/tmp/skill-eval-artifacts/validate-change-ox73ozcl/trim-uppercase-kzgsedxq/check_trim.py\", line 16, in <module>\n    assert completed.stdout == \"HELLO\\n\"\nAssertionError\n"
+          }
+        ]
+      },
+      "oracle": {
+        "enabled": false,
+        "passed": true,
+        "commands": []
+      },
+      "judge": {
+        "enabled": false,
+        "executed": false,
+        "verdict": "PASS",
+        "rationale": "Deterministic cases do not use a semantic judge.",
+        "evidence": [],
+        "usage": {
+          "input_tokens": null,
+          "cached_input_tokens": null,
+          "output_tokens": null,
+          "reasoning_output_tokens": null,
+          "total_tokens": null,
+          "complete": false,
+          "reasoning_output_tokens_complete": false,
+          "events": [],
+          "event_count": 0,
+          "events_complete": false
+        },
+        "duration_ms": 0,
+        "failure_category": null
+      },
+      "changed_paths": [],
+      "workspace": null,
+      "model_sessions": {
+        "executor": 0,
+        "judge": 0,
+        "total": 0
+      },
+      "usage": {
+        "input_tokens": null,
+        "cached_input_tokens": null,
+        "output_tokens": null,
+        "reasoning_output_tokens": null,
+        "total_tokens": null,
+        "complete": false,
+        "reasoning_output_tokens_complete": false,
+        "events": [],
+        "event_count": 0,
+        "events_complete": false
+      },
+      "failure_category": "contract",
+      "role": "baseline"
+    },
+    {
+      "case_id": "trim-uppercase",
+      "status": "PASS",
+      "kind": "deterministic",
+      "executor": {
+        "enabled": false,
+        "executed": false,
+        "exit_code": null,
+        "response": null,
+        "stderr": "",
+        "usage": {
+          "input_tokens": null,
+          "cached_input_tokens": null,
+          "output_tokens": null,
+          "reasoning_output_tokens": null,
+          "total_tokens": null,
+          "complete": false,
+          "reasoning_output_tokens_complete": false,
+          "events": [],
+          "event_count": 0,
+          "events_complete": false
+        },
+        "duration_ms": 0
+      },
+      "mechanical": {
+        "passed": true,
+        "checks": [
+          {
+            "name": "command: python3 check_trim.py",
+            "passed": true,
+            "detail": "expected 0, got 0"
+          },
+          {
+            "name": "evaluated skill remained unchanged",
+            "passed": true,
+            "detail": "evaluated skill hash comparison"
+          }
+        ],
+        "commands": [
+          {
+            "argv": [
+              "python3",
+              "check_trim.py"
+            ],
+            "exit_code": 0,
+            "stdout": "",
+            "stderr": ""
+          }
+        ]
+      },
+      "oracle": {
+        "enabled": false,
+        "passed": true,
+        "commands": []
+      },
+      "judge": {
+        "enabled": false,
+        "executed": false,
+        "verdict": "PASS",
+        "rationale": "Deterministic cases do not use a semantic judge.",
+        "evidence": [],
+        "usage": {
+          "input_tokens": null,
+          "cached_input_tokens": null,
+          "output_tokens": null,
+          "reasoning_output_tokens": null,
+          "total_tokens": null,
+          "complete": false,
+          "reasoning_output_tokens_complete": false,
+          "events": [],
+          "event_count": 0,
+          "events_complete": false
+        },
+        "duration_ms": 0,
+        "failure_category": null
+      },
+      "changed_paths": [],
+      "workspace": null,
+      "model_sessions": {
+        "executor": 0,
+        "judge": 0,
+        "total": 0
+      },
+      "usage": {
+        "input_tokens": null,
+        "cached_input_tokens": null,
+        "output_tokens": null,
+        "reasoning_output_tokens": null,
+        "total_tokens": null,
+        "complete": false,
+        "reasoning_output_tokens_complete": false,
+        "events": [],
+        "event_count": 0,
+        "events_complete": false
+      },
+      "failure_category": null,
+      "role": "candidate",
+      "repetition": 1
+    },
+    {
+      "case_id": "trim-uppercase",
+      "status": "PASS",
+      "kind": "deterministic",
+      "executor": {
+        "enabled": false,
+        "executed": false,
+        "exit_code": null,
+        "response": null,
+        "stderr": "",
+        "usage": {
+          "input_tokens": null,
+          "cached_input_tokens": null,
+          "output_tokens": null,
+          "reasoning_output_tokens": null,
+          "total_tokens": null,
+          "complete": false,
+          "reasoning_output_tokens_complete": false,
+          "events": [],
+          "event_count": 0,
+          "events_complete": false
+        },
+        "duration_ms": 0
+      },
+      "mechanical": {
+        "passed": true,
+        "checks": [
+          {
+            "name": "command: python3 check_trim.py",
+            "passed": true,
+            "detail": "expected 0, got
```

Truncations:
- `validation.json`: per file diff limit

## Integrity

- Report digest: `sha256:1d71ed7e32c8ad92254c47bdfd75e1964b869fcb31950c71ac4fe91cc5637df8`
