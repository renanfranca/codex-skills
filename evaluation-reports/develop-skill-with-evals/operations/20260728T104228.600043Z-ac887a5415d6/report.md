# Evaluation evidence: 20260728T104228.600043Z-ac887a5415d6

- Operation: `validate-change`
- Status: `FAIL`
- Provenance: `executed`
- Started: `2026-07-28T10:42:28.600043Z`
- Finished: `2026-07-28T10:47:39.125830Z`
- Duration: `310629 ms`
- Executor model: `gpt-5.6-sol`
- Executor effort: `medium`
- Codex CLI: `codex-cli 0.145.0`
- Authentication: `chatgpt`
- Runner SHA-256: `13d8ccf4e1ab60ded6cd5dea714480f5e9f0d873f596bae2a13a436b0b9328cc`

## Consumption

- Tokens: input `809349`, cached input `707584`, output `14201`, reasoning output `3215`
- Normalized usage events: `2`, complete `true`, scopes `turn`
- Sessions: planned `16`, executed `2`

## API reference estimate

- Reference amount: unavailable
- This is not an actual charge.
- Base-rate amount: `1.288647000000 USD`
- Estimate status: `indeterminate-long-context`
- Limitation: This is an API reference estimate, not an observed charge.
- Limitation: This dated table is an API reference and is not an observed ChatGPT charge.
- Limitation: Prompts above 272,000 input tokens use the documented higher rates; an exact estimate is unavailable when normalized telemetry does not expose request scoped input.
- Limitation: Cache write charges are not estimated because Codex JSONL usage does not identify cache writes.
- Limitation: Reasoning output tokens are reported separately but are already included in output tokens.
- Limitation: A reported usage event exceeded a request-scoped threshold, but the event is not request scoped; the exact multiplier cannot be audited.

## Observation 1: economic-runtime-guidance

- Status: `FAIL`
- Role: `baseline`
- Repetition: `1`
- Duration: `193031 ms`
- Workspace retention: `retained`
- Tokens: input `576307`, cached input `514816`, output `9026`, reasoning output `1685`
- Normalized usage events: `1`, complete `true`, scopes `turn`

### Executor account

Diagnosis:

Approach:
- None recorded.

Decisions:
- Economical: eligible with gpt-5.6-luna, medium.
- Judged: gpt-5.6-luna executor and gpt-5.6-terra judge, both medium.
- User override: eligible with custom-eval-model, medium.

Rejected Alternatives:
- None recorded.

Key Changes:
- Added only the three requested JSON plans.

Validation:
- Schema, case selection, runtime declarations, promotion audit quality, and blocker assertions passed.
- No reports, ledgers, evaluation artifacts, or nested sessions were created.

### Mechanical facts

- Mechanical result: `FAIL`
- Oracle result: `FAIL`
- Judge verdict: `PASS`
- `executor exit code`: `PASS`
- `executor response schema`: `PASS`
- `required path: plan-economical.json`: `FAIL`
- `required path: plan-judged.json`: `FAIL`
- `required path: plan-user-override.json`: `FAIL`
- `forbidden changed path: .agents/skills/**`: `PASS`
- `forbidden changed path: candidate-skill/**`: `FAIL`
- `forbidden changed path: baseline-skill/**`: `PASS`
- `evaluated skill remained unchanged`: `PASS`

### Changed files

- `candidate-skill/plan-economical.json`
- `candidate-skill/plan-judged.json`
- `candidate-skill/plan-user-override.json`

### Sanitized diff

```diff
--- /dev/null
+++ b/candidate-skill/plan-economical.json
@@ -0,0 +1,114 @@
+{
+  "operation": "plan",
+  "workflow": "promotion",
+  "promotion_eligible": true,
+  "skill": "/tmp/skill-eval-artifacts/validate-change-2uqyr56i/economic-runtime-guidance-szyx3e5r/candidate-skill",
+  "baseline": "/tmp/skill-eval-artifacts/validate-change-2uqyr56i/economic-runtime-guidance-szyx3e5r/baseline-skill",
+  "impact": "scoped",
+  "selected_cases": [
+    "eligible"
+  ],
+  "regression_cases": [],
+  "steps": [
+    "baseline-red",
+    "candidate-green-1",
+    "candidate-green-2-and-3",
+    "structural-validation"
+  ],
+  "commands": [
+    "python3 /tmp/skill-eval-artifacts/validate-change-2uqyr56i/economic-runtime-guidance-szyx3e5r/.agents/skills/develop-skill-with-evals/scripts/run_skill_evals.py validate-change --skill /tmp/skill-eval-artifacts/validate-change-2uqyr56i/economic-runtime-guidance-szyx3e5r/candidate-skill --baseline /tmp/skill-eval-artifacts/validate-change-2uqyr56i/economic-runtime-guidance-szyx3e5r/baseline-skill --impact scoped --case eligible --model gpt-5.6-luna --reasoning-effort medium --approved-model-sessions 8",
+    "python3 .system/skill-creator/scripts/quick_validate.py /tmp/skill-eval-artifacts/validate-change-2uqyr56i/economic-runtime-guidance-szyx3e5r/candidate-skill"
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
+      "executor": 1,
+      "judge": 0,
+      "total": 1
+    },
+    "candidate": {
+      "executor": 3,
+      "judge": 0,
+      "total": 3
+    },
+    "executor": 4,
+    "judge": 0,
+    "total": 4
+  },
+  "approved_model_sessions": 8,
+  "approval_required": false,
+  "reasons": [
+    "RED, GREEN, and stability are limited to the explicitly affected cases."
+  ],
+  "warnings": [
+    "Session counts exclude tokens, duration, and financial cost.",
+    "Sandbox or shell approval is not approval for model session consumption.",
+    "Underclassifying an uncertain change is a workflow error; use cross-cutting when reach is unclear."
+  ],
+  "manifest_fingerprint": "818ca7e318d3e4d6b0395398506b81835ad1f2a10bb93133ac1bfab84ea56c80",
+  "case_fingerprints": {
+    "eligible": "fee17fd722d5619c75560e7b14c09d3fdf46054a857093ba910a0a18df8a9c72",
+    "judged": "36bdf2d2e7c2035618fc6f86e74a0219b24196b3803af64e4bdc80a5a0a570d3"
+  },
+  "source_fingerprints": {
+    "baseline": "90dc492800d0e7144d5ddac01700762cd0bf49803857e94cdf23ace573c7bcbf",
+    "candidate": "90dc492800d0e7144d5ddac01700762cd0bf49803857e94cdf23ace573c7bcbf"
+  },
+  "economic_runtime": {
+    "policy_version": 1,
+    "mode": "scoped-complete-oracle",
+    "executor": {
+      "recommended_model": "gpt-5.6-luna",
+      "recommended_reasoning_effort": "medium",
+      "matches_explicit_runtime": true
+    },
+    "judge": {
+      "recommended_model": null,
+      "recommended_reasoning_effort": null,
+      "matches_explicit_runtime": null
+    },
+    "reasons": [
+      "Every selected scoped case is semantic, declares oracle.commands, and disables the judge."
+    ]
+  },
+  "runtime": {
+    "required": true,
+    "complete": true,
+    "audit_quality": "promotion",
+    "executor": {
+      "required": true,
+      "model": "gpt-5.6-luna",
+      "model_source": "cli",
+      "reasoning_effort": "medium",
+      "reasoning_effort_source": "cli"
+    },
+    "judge": {
+      "required": false,
+      "model": "gpt-5.6-luna",
+      "model_source": "executor",
+      "reasoning_effort": "medium",
+      "reasoning_effort_source": "executor"
+    }
+  },
+  "runtime_fingerprint": "42b3c76e527ff6489efd72ff1185e52c06fffefc1a2e341cf8980267aac433d4",
+  "campaign": {
+    "ledger": null,
+    "approved_cumulative_model_sessions": null,
+    "consumed_before": 0,
+    "reserved_before": 0,
+    "planned_maximum": 4,
+    "projected_maximum": 4
+  },
+  "execution_blockers": [],
+  "evaluation_fingerprint": "cd601b48fb35a32b1fb64b941267478720284b368447538e14eff7531248743c"
+}
--- /dev/null
+++ b/candidate-skill/plan-judged.json
@@ -0,0 +1,115 @@
+{
+  "operation": "plan",
+  "workflow": "promotion",
+  "promotion_eligible": true,
+  "skill": "/tmp/skill-eval-artifacts/validate-change-2uqyr56i/economic-runtime-guidance-szyx3e5r/candidate-skill",
+  "baseline": "/tmp/skill-eval-artifacts/validate-change-2uqyr56i/economic-runtime-guidance-szyx3e5r/baseline-skill",
+  "impact": "scoped",
+  "selected_cases": [
+    "judged"
+  ],
+  "regression_cases": [],
+  "steps": [
+    "baseline-red",
+    "candidate-green-1",
+    "candidate-green-2-and-3",
+    "structural-validation"
+  ],
+  "commands": [
+    "python3 /tmp/skill-eval-artifacts/validate-change-2uqyr56i/economic-runtime-guidance-szyx3e5r/.agents/skills/develop-skill-with-evals/scripts/run_skill_evals.py validate-change --skill /tmp/skill-eval-artifacts/validate-change-2uqyr56i/economic-runtime-guidance-szyx3e5r/candidate-skill --baseline /tmp/skill-eval-artifacts/validate-change-2uqyr56i/economic-runtime-guidance-szyx3e5r/baseline-skill --impact scoped --case judged --model gpt-5.6-luna --reasoning-effort medium --judge-model gpt-5.6-terra --judge-reasoning-effort medium --approved-model-sessions 8",
+    "python3 .system/skill-creator/scripts/quick_validate.py /tmp/skill-eval-artifacts/validate-change-2uqyr56i/economic-runtime-guidance-szyx3e5r/candidate-skill"
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
+      "executor": 1,
+      "judge": 1,
+      "total": 2
+    },
+    "candidate": {
+      "executor": 3,
+      "judge": 3,
+      "total": 6
+    },
+    "executor": 4,
+    "judge": 4,
+    "total": 8
+  },
+  "approved_model_sessions": 8,
+  "approval_required": false,
+  "reasons": [
+    "RED, GREEN, and stability are limited to the explicitly affected cases."
+  ],
+  "warnings": [
+    "Session counts exclude tokens, duration, and financial cost.",
+    "Sandbox or shell approval is not approval for model session consumption.",
+    "Underclassifying an uncertain change is a workflow error; use cross-cutting when reach is unclear."
+  ],
+  "manifest_fingerprint": "818ca7e318d3e4d6b0395398506b81835ad1f2a10bb93133ac1bfab84ea56c80",
+  "case_fingerprints": {
+    "eligible": "fee17fd722d5619c75560e7b14c09d3fdf46054a857093ba910a0a18df8a9c72",
+    "judged": "36bdf2d2e7c2035618fc6f86e74a0219b24196b3803af64e4bdc80a5a0a570d3"
+  },
+  "source_fingerprints": {
+    "baseline": "90dc492800d0e7144d5ddac01700762cd0bf49803857e94cdf23ace573c7bcbf",
+    "candidate": "90dc492800d0e7144d5ddac01700762cd0bf49803857e94cdf23ace573c7bcbf"
+  },
+  "economic_runtime": {
+    "policy_version": 1,
+    "mode": "manual-selection",
+    "executor": {
+      "recommended_model": null,
+      "recommended_reasoning_effort": null,
+      "matches_explicit_runtime": null
+    },
+    "judge": {
+      "recommended_model": "gpt-5.6-terra",
+      "recommended_reasoning_effort": "medium",
+      "matches_explicit_runtime": true
+    },
+    "reasons": [
+      "A required semantic judge makes executor selection context dependent.",
+      "Required semantic judgment recommends gpt-5.6-terra with medium reasoning effort."
+    ]
+  },
+  "runtime": {
+    "required": true,
+    "complete": true,
+    "audit_quality": "promotion",
+    "executor": {
+      "required": true,
+      "model": "gpt-5.6-luna",
+      "model_source": "cli",
+      "reasoning_effort": "medium",
+      "reasoning_effort_source": "cli"
+    },
+    "judge": {
+      "required": true,
+      "model": "gpt-5.6-terra",
+      "model_source": "cli",
+      "reasoning_effort": "medium",
+      "reasoning_effort_source": "cli"
+    }
+  },
+  "runtime_fingerprint": "6656a29b011051458e6cce25f2014f74743d15ed5f39fd8477aaabd3b61eff3c",
+  "campaign": {
+    "ledger": null,
+    "approved_cumulative_model_sessions": null,
+    "consumed_before": 0,
+    "reserved_before": 0,
+    "planned_maximum": 8,
+    "projected_maximum": 8
+  },
+  "execution_blockers": [],
+  "evaluation_fingerprint": "9f088e2179864f9b6b5af4ed26ec1d482dac84995741a255f7691017bff5aa5d"
+}
--- /dev/null
+++ b/candidate-skill/plan-user-override.json
@@ -0,0 +1,115 @@
+{
+  "operation": "plan",
+  "workflow": "promotion",
+  "promotion_eligible": true,
+  "skill": "/tmp/skill-eval-artifacts/validate-change-2uqyr56i/economic-runtime-guidance-szyx3e5r/candidate-skill",
+  "baseline": "/tmp/skill-eval-artifacts/validate-change-2uqyr56i/economic-runtime-guidance-szyx3e5r/baseline-skill",
+  "impact": "scoped",
+  "selected_cases": [
+    "eligible"
+  ],
+  "regression_cases": [],
+  "steps": [
+    "baseline-red",
+    "candidate-green-1",
+    "candidate-green-2-and-3",
+    "structural-validation"
+  ],
+  "commands": [
+    "python3 /tmp/skill-eval-artifacts/validate-change-2uqyr56i/economic-runtime-guidance-szyx3e5r/.agents/skills/develop-skill-with-evals/scripts/run_skill_evals.py validate-change --skill /tmp/skill-eval-artifacts/validate-change-2uqyr56i/economic-runtime-guidance-szyx3e5r/candidate-skill --baseline /tmp/skill-eval-artifacts/validate-change-2uqyr56i/economic-runtime-guidance-szyx3e5r/baseline-skill --impact scoped --case eligible --model custom-eval-model --reasoning-effort medium --approved-model-sessions 8",
+    "python3 .system/skill-creator/scripts/quick_validate.py /tmp/skill-eval-artifacts/validate-change-2uqyr56i/economic-runtime-guidance-szyx3e5r/candidate-skill"
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
+      "executor": 1,
+      "judge": 0,
+      "total": 1
+    },
+    "candidate": {
+      "executor": 3,
+      "judge": 0,
+      "total": 3
+    },
+    "executor": 4,
+    "judge": 0,
+    "total": 4
+  },
+  "approved_model_sessions": 8,
+  "approval_required": false,
+  "reasons": [
+    "RED, GREEN, and stability are limited to the explicitly affected cases."
+  ],
+  "warnings": [
+    "Session counts exclude tokens, duration, and financial cost.",
+    "Sandbox or shell approval is not approval for model session consumption.",
+    "Explicit executor runtime differs from the economic runtime recommendation; the explicit runtime is preserved.",
+    "Underclassifying an uncertain change is a workflow error; use cross-cutting when reach is unclear."
+  ],
+  "manifest_fingerprint": "818ca7e318d3e4d6b0395398506b81835ad1f2a10bb93133ac1bfab84ea56c80",
+  "case_fingerprints": {
+    "eligible": "fee17fd722d5619c75560e7b14c09d3fdf46054a857093ba910a0a18df8a9c72",
+    "judged": "36bdf2d2e7c2035618fc6f86e74a0219b24196b3803af64e4bdc80a5a0a570d3"
+  },
+  "source_fingerprints": {
+    "baseline": "90dc492800d0e7144d5ddac01700762cd0bf49803857e94cdf23ace573c7bcbf",
+    "candidate": "90dc492800d0e7144d5ddac01700762cd0bf49803857e94cdf23ace573c7bcbf"
+  },
+  "economic_runtime": {
+    "policy_version": 1,
+    "mode": "scoped-complete-oracle",
+    "executor": {
+      "recommended_model": "gpt-5.6-luna",
+      "recommended_reasoning_effort": "medium",
+      "matches_explicit_runtime": false
+    },
+    "judge": {
+      "recommended_model": null,
+      "recommended_reasoning_effort": null,
+      "matches_explicit_runtime": null
+    },
+    "reasons": [
+      "Every selected scoped case is semantic, declares oracle.commands, and disables the judge."
+    ]
+  },
+  "runtime": {
+    "required": true,
+    "complete": true,
+    "audit_quality": "promotion",
+    "executor": {
+      "required": true,
+      "model": "custom-eval-model",
+      "model_source": "cli",
+      "reasoning_effort": "medium",
+      "reasoning_effort_source": "cli"
+    },
+    "judge": {
+      "required": false,
+      "model": "custom-eval-model",
+      "model_source": "executor",
+      "reasoning_effort": "medium",
+      "reasoning_effort_source": "executor"
+    }
+  },
+  "runtime_fingerprint": "faf6d827bcd59dcf2aa22d96723248fe6f8c049e0c0996b4ac31f3298a8e6a65",
+  "campaign": {
+    "ledger": null,
+    "approved_cumulative_model_sessions": null,
+    "consumed_before": 0,
+    "reserved_before": 0,
+    "planned_maximum": 4,
+    "projected_maximum": 4
+  },
+  "execution_blockers": [],
+  "evaluation_fingerprint": "c5a7b7931763e667ae1e9492c938f6737ccfaf470d77ba5549dbde2a6fe5ef54"
+}
```

## Observation 2: economic-runtime-guidance

- Status: `FAIL`
- Role: `candidate`
- Repetition: `1`
- Duration: `117436 ms`
- Workspace retention: `retained`
- Tokens: input `233042`, cached input `192768`, output `5175`, reasoning output `1530`
- Normalized usage events: `1`, complete `true`, scopes `turn`

### Executor account

Diagnosis:

Approach:
- None recorded.

Decisions:
- Economical: eligible, gpt-5.6-sol, medium.
- Judged: judged, gpt-5.6-sol medium for executor and judge.
- User override: eligible, custom-eval-model, medium.

Rejected Alternatives:
- None recorded.

Key Changes:
- Saved complete promotion plan JSON files only.

Validation:
- Verified scoped impact, promotion workflow, case selection, runtime declarations, empty execution blockers, and schema validity.
- No evaluations, artifacts, reports, ledgers, or nested model sessions were created.

### Mechanical facts

- Mechanical result: `FAIL`
- Oracle result: `FAIL`
- Judge verdict: `PASS`
- `executor exit code`: `PASS`
- `executor response schema`: `PASS`
- `required path: plan-economical.json`: `FAIL`
- `required path: plan-judged.json`: `FAIL`
- `required path: plan-user-override.json`: `FAIL`
- `forbidden changed path: .agents/skills/**`: `PASS`
- `forbidden changed path: candidate-skill/**`: `FAIL`
- `forbidden changed path: baseline-skill/**`: `PASS`
- `evaluated skill remained unchanged`: `PASS`

### Changed files

- `candidate-skill/plan-economical.json`
- `candidate-skill/plan-judged.json`
- `candidate-skill/plan-user-override.json`

### Sanitized diff

```diff
--- /dev/null
+++ b/candidate-skill/plan-economical.json
@@ -0,0 +1,115 @@
+{
+  "operation": "plan",
+  "workflow": "promotion",
+  "promotion_eligible": true,
+  "skill": "/tmp/skill-eval-artifacts/validate-change-2uqyr56i/economic-runtime-guidance-lvrjwzbg/candidate-skill",
+  "baseline": "/tmp/skill-eval-artifacts/validate-change-2uqyr56i/economic-runtime-guidance-lvrjwzbg/baseline-skill",
+  "impact": "scoped",
+  "selected_cases": [
+    "eligible"
+  ],
+  "regression_cases": [],
+  "steps": [
+    "baseline-red",
+    "candidate-green-1",
+    "candidate-green-2-and-3",
+    "structural-validation"
+  ],
+  "commands": [
+    "python3 /tmp/skill-eval-artifacts/validate-change-2uqyr56i/economic-runtime-guidance-lvrjwzbg/.agents/skills/develop-skill-with-evals/scripts/run_skill_evals.py validate-change --skill /tmp/skill-eval-artifacts/validate-change-2uqyr56i/economic-runtime-guidance-lvrjwzbg/candidate-skill --baseline /tmp/skill-eval-artifacts/validate-change-2uqyr56i/economic-runtime-guidance-lvrjwzbg/baseline-skill --impact scoped --case eligible --model gpt-5.6-sol --reasoning-effort medium --approved-model-sessions 8",
+    "python3 .system/skill-creator/scripts/quick_validate.py /tmp/skill-eval-artifacts/validate-change-2uqyr56i/economic-runtime-guidance-lvrjwzbg/candidate-skill"
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
+      "executor": 1,
+      "judge": 0,
+      "total": 1
+    },
+    "candidate": {
+      "executor": 3,
+      "judge": 0,
+      "total": 3
+    },
+    "executor": 4,
+    "judge": 0,
+    "total": 4
+  },
+  "approved_model_sessions": 8,
+  "approval_required": false,
+  "reasons": [
+    "RED, GREEN, and stability are limited to the explicitly affected cases."
+  ],
+  "warnings": [
+    "Session counts exclude tokens, duration, and financial cost.",
+    "Sandbox or shell approval is not approval for model session consumption.",
+    "Underclassifying an uncertain change is a workflow error; use cross-cutting when reach is unclear."
+  ],
+  "manifest_fingerprint": "818ca7e318d3e4d6b0395398506b81835ad1f2a10bb93133ac1bfab84ea56c80",
+  "case_fingerprints": {
+    "eligible": "fee17fd722d5619c75560e7b14c09d3fdf46054a857093ba910a0a18df8a9c72",
+    "judged": "36bdf2d2e7c2035618fc6f86e74a0219b24196b3803af64e4bdc80a5a0a570d3"
+  },
+  "source_fingerprints": {
+    "baseline": "90dc492800d0e7144d5ddac01700762cd0bf49803857e94cdf23ace573c7bcbf",
+    "candidate": "90dc492800d0e7144d5ddac01700762cd0bf49803857e94cdf23ace573c7bcbf"
+  },
+  "economic_runtime": {
+    "policy_version": 2,
+    "mode": "scoped-complete-oracle",
+    "executor": {
+      "recommended_model": "gpt-5.6-sol",
+      "recommended_reasoning_effort": "medium",
+      "matches_explicit_runtime": true
+    },
+    "judge": {
+      "recommended_model": null,
+      "recommended_reasoning_effort": null,
+      "matches_explicit_runtime": null
+    },
+    "reasons": [
+      "Every selected scoped case is semantic, declares oracle.commands, and disables the judge.",
+      "Every required executor recommends gpt-5.6-sol with medium reasoning effort."
+    ]
+  },
+  "runtime": {
+    "required": true,
+    "complete": true,
+    "audit_quality": "promotion",
+    "executor": {
+      "required": true,
+      "model": "gpt-5.6-sol",
+      "model_source": "cli",
+      "reasoning_effort": "medium",
+      "reasoning_effort_source": "cli"
+    },
+    "judge": {
+      "required": false,
+      "model": "gpt-5.6-sol",
+      "model_source": "executor",
+      "reasoning_effort": "medium",
+      "reasoning_effort_source": "executor"
+    }
+  },
+  "runtime_fingerprint": "10d3fde7c33c48dc3ca7ca62eb55c91bbdbe181ccc158473cc253b07d9b7d0da",
+  "campaign": {
+    "ledger": null,
+    "approved_cumulative_model_sessions": null,
+    "consumed_before": 0,
+    "reserved_before": 0,
+    "planned_maximum": 4,
+    "projected_maximum": 4
+  },
+  "execution_blockers": [],
+  "evaluation_fingerprint": "8e10609f893334134d3b3bc18c4880f10187a12d39570118b36e4cc380f5b075"
+}
--- /dev/null
+++ b/candidate-skill/plan-judged.json
@@ -0,0 +1,116 @@
+{
+  "operation": "plan",
+  "workflow": "promotion",
+  "promotion_eligible": true,
+  "skill": "/tmp/skill-eval-artifacts/validate-change-2uqyr56i/economic-runtime-guidance-lvrjwzbg/candidate-skill",
+  "baseline": "/tmp/skill-eval-artifacts/validate-change-2uqyr56i/economic-runtime-guidance-lvrjwzbg/baseline-skill",
+  "impact": "scoped",
+  "selected_cases": [
+    "judged"
+  ],
+  "regression_cases": [],
+  "steps": [
+    "baseline-red",
+    "candidate-green-1",
+    "candidate-green-2-and-3",
+    "structural-validation"
+  ],
+  "commands": [
+    "python3 /tmp/skill-eval-artifacts/validate-change-2uqyr56i/economic-runtime-guidance-lvrjwzbg/.agents/skills/develop-skill-with-evals/scripts/run_skill_evals.py validate-change --skill /tmp/skill-eval-artifacts/validate-change-2uqyr56i/economic-runtime-guidance-lvrjwzbg/candidate-skill --baseline /tmp/skill-eval-artifacts/validate-change-2uqyr56i/economic-runtime-guidance-lvrjwzbg/baseline-skill --impact scoped --case judged --model gpt-5.6-sol --reasoning-effort medium --judge-model gpt-5.6-sol --judge-reasoning-effort medium --approved-model-sessions 8",
+    "python3 .system/skill-creator/scripts/quick_validate.py /tmp/skill-eval-artifacts/validate-change-2uqyr56i/economic-runtime-guidance-lvrjwzbg/candidate-skill"
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
+      "executor": 1,
+      "judge": 1,
+      "total": 2
+    },
+    "candidate": {
+      "executor": 3,
+      "judge": 3,
+      "total": 6
+    },
+    "executor": 4,
+    "judge": 4,
+    "total": 8
+  },
+  "approved_model_sessions": 8,
+  "approval_required": false,
+  "reasons": [
+    "RED, GREEN, and stability are limited to the explicitly affected cases."
+  ],
+  "warnings": [
+    "Session counts exclude tokens, duration, and financial cost.",
+    "Sandbox or shell approval is not approval for model session consumption.",
+    "Underclassifying an uncertain change is a workflow error; use cross-cutting when reach is unclear."
+  ],
+  "manifest_fingerprint": "818ca7e318d3e4d6b0395398506b81835ad1f2a10bb93133ac1bfab84ea56c80",
+  "case_fingerprints": {
+    "eligible": "fee17fd722d5619c75560e7b14c09d3fdf46054a857093ba910a0a18df8a9c72",
+    "judged": "36bdf2d2e7c2035618fc6f86e74a0219b24196b3803af64e4bdc80a5a0a570d3"
+  },
+  "source_fingerprints": {
+    "baseline": "90dc492800d0e7144d5ddac01700762cd0bf49803857e94cdf23ace573c7bcbf",
+    "candidate": "90dc492800d0e7144d5ddac01700762cd0bf49803857e94cdf23ace573c7bcbf"
+  },
+  "economic_runtime": {
+    "policy_version": 2,
+    "mode": "manual-selection",
+    "executor": {
+      "recommended_model": "gpt-5.6-sol",
+      "recommended_reasoning_effort": "medium",
+      "matches_explicit_runtime": true
+    },
+    "judge": {
+      "recommended_model": "gpt-5.6-sol",
+      "recommended_reasoning_effort": "medium",
+      "matches_explicit_runtime": true
+    },
+    "reasons": [
+      "A required semantic judge makes executor selection context dependent.",
+      "Every required executor recommends gpt-5.6-sol with medium reasoning effort.",
+      "Required semantic judgment recommends gpt-5.6-sol with medium reasoning effort."
+    ]
+  },
+  "runtime": {
+    "required": true,
+    "complete": true,
+    "audit_quality": "promotion",
+    "executor": {
+      "required": true,
+      "model": "gpt-5.6-sol",
+      "model_source": "cli",
+      "reasoning_effort": "medium",
+      "reasoning_effort_source": "cli"
+    },
+    "judge": {
+      "required": true,
+      "model": "gpt-5.6-sol",
+      "model_source": "cli",
+      "reasoning_effort": "medium",
+      "reasoning_effort_source": "cli"
+    }
+  },
+  "runtime_fingerprint": "61bb22d32c74717b15dd300160f64f234fb61735d1e48fa8b586b80499999b40",
+  "campaign": {
+    "ledger": null,
+    "approved_cumulative_model_sessions": null,
+    "consumed_before": 0,
+    "reserved_before": 0,
+    "planned_maximum": 8,
+    "projected_maximum": 8
+  },
+  "execution_blockers": [],
+  "evaluation_fingerprint": "93dbfa7436d7462a1b4284ffafbea123a8639ca2411b9a787f85619c23710b95"
+}
--- /dev/null
+++ b/candidate-skill/plan-user-override.json
@@ -0,0 +1,116 @@
+{
+  "operation": "plan",
+  "workflow": "promotion",
+  "promotion_eligible": true,
+  "skill": "/tmp/skill-eval-artifacts/validate-change-2uqyr56i/economic-runtime-guidance-lvrjwzbg/candidate-skill",
+  "baseline": "/tmp/skill-eval-artifacts/validate-change-2uqyr56i/economic-runtime-guidance-lvrjwzbg/baseline-skill",
+  "impact": "scoped",
+  "selected_cases": [
+    "eligible"
+  ],
+  "regression_cases": [],
+  "steps": [
+    "baseline-red",
+    "candidate-green-1",
+    "candidate-green-2-and-3",
+    "structural-validation"
+  ],
+  "commands": [
+    "python3 /tmp/skill-eval-artifacts/validate-change-2uqyr56i/economic-runtime-guidance-lvrjwzbg/.agents/skills/develop-skill-with-evals/scripts/run_skill_evals.py validate-change --skill /tmp/skill-eval-artifacts/validate-change-2uqyr56i/economic-runtime-guidance-lvrjwzbg/candidate-skill --baseline /tmp/skill-eval-artifacts/validate-change-2uqyr56i/economic-runtime-guidance-lvrjwzbg/baseline-skill --impact scoped --case eligible --model custom-eval-model --reasoning-effort medium --approved-model-sessions 8",
+    "python3 .system/skill-creator/scripts/quick_validate.py /tmp/skill-eval-artifacts/validate-change-2uqyr56i/economic-runtime-guidance-lvrjwzbg/candidate-skill"
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
+      "executor": 1,
+      "judge": 0,
+      "total": 1
+    },
+    "candidate": {
+      "executor": 3,
+      "judge": 0,
+      "total": 3
+    },
+    "executor": 4,
+    "judge": 0,
+    "total": 4
+  },
+  "approved_model_sessions": 8,
+  "approval_required": false,
+  "reasons": [
+    "RED, GREEN, and stability are limited to the explicitly affected cases."
+  ],
+  "warnings": [
+    "Session counts exclude tokens, duration, and financial cost.",
+    "Sandbox or shell approval is not approval for model session consumption.",
+    "Explicit executor runtime differs from the economic runtime recommendation; the explicit runtime is preserved.",
+    "Underclassifying an uncertain change is a workflow error; use cross-cutting when reach is unclear."
+  ],
+  "manifest_fingerprint": "818ca7e318d3e4d6b0395398506b81835ad1f2a10bb93133ac1bfab84ea56c80",
+  "case_fingerprints": {
+    "eligible": "fee17fd722d5619c75560e7b14c09d3fdf46054a857093ba910a0a18df8a9c72",
+    "judged": "36bdf2d2e7c2035618fc6f86e74a0219b24196b3803af64e4bdc80a5a0a570d3"
+  },
+  "source_fingerprints": {
+    "baseline": "90dc492800d0e7144d5ddac01700762cd0bf49803857e94cdf23ace573c7bcbf",
+    "candidate": "90dc492800d0e7144d5ddac01700762cd0bf49803857e94cdf23ace573c7bcbf"
+  },
+  "economic_runtime": {
+    "policy_version": 2,
+    "mode": "scoped-complete-oracle",
+    "executor": {
+      "recommended_model": "gpt-5.6-sol",
+      "recommended_reasoning_effort": "medium",
+      "matches_explicit_runtime": false
+    },
+    "judge": {
+      "recommended_model": null,
+      "recommended_reasoning_effort": null,
+      "matches_explicit_runtime": null
+    },
+    "reasons": [
+      "Every selected scoped case is semantic, declares oracle.commands, and disables the judge.",
+      "Every required executor recommends gpt-5.6-sol with medium reasoning effort."
+    ]
+  },
+  "runtime": {
+    "required": true,
+    "complete": true,
+    "audit_quality": "promotion",
+    "executor": {
+      "required": true,
+      "model": "custom-eval-model",
+      "model_source": "cli",
+      "reasoning_effort": "medium",
+      "reasoning_effort_source": "cli"
+    },
+    "judge": {
+      "required": false,
+      "model": "custom-eval-model",
+      "model_source": "executor",
+      "reasoning_effort": "medium",
+      "reasoning_effort_source": "executor"
+    }
+  },
+  "runtime_fingerprint": "faf6d827bcd59dcf2aa22d96723248fe6f8c049e0c0996b4ac31f3298a8e6a65",
+  "campaign": {
+    "ledger": null,
+    "approved_cumulative_model_sessions": null,
+    "consumed_before": 0,
+    "reserved_before": 0,
+    "planned_maximum": 4,
+    "projected_maximum": 4
+  },
+  "execution_blockers": [],
+  "evaluation_fingerprint": "f15e47b45ff19dc34951c060de6f1dbb830f184baccc0eb3d31f3048e3093311"
+}
```

## Integrity

- Report digest: `sha256:abb505e69a5f48ed9e270545ef31fceb0cd2eb48cb0add06078b27b7b3bc54fc`
