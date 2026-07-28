# Evaluation evidence: 20260728T113254.537174Z-d01790d9d1d6

- Operation: `validate-change`
- Status: `FAIL`
- Provenance: `executed`
- Started: `2026-07-28T11:32:54.537174Z`
- Finished: `2026-07-28T11:53:34.120827Z`
- Duration: `1239588 ms`
- Executor model: `gpt-5.6-sol`
- Executor effort: `medium`
- Codex CLI: `codex-cli 0.145.0`
- Authentication: `chatgpt`
- Runner SHA-256: `13d8ccf4e1ab60ded6cd5dea714480f5e9f0d873f596bae2a13a436b0b9328cc`

## Consumption

- Tokens: input `3578303`, cached input `3020544`, output `42440`, reasoning output `9735`
- Normalized usage events: `13`, complete `true`, scopes `turn`
- Sessions: planned `16`, executed `13`

## API reference estimate

- Reference amount: unavailable
- This is not an actual charge.
- Base-rate amount: `5.572267000000 USD`
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
- Duration: `119155 ms`
- Workspace retention: `retained`
- Tokens: input `375961`, cached input `304128`, output `5092`, reasoning output `1753`
- Normalized usage events: `1`, complete `true`, scopes `turn`

### Executor account

Diagnosis:

Approach:
- None recorded.

Decisions:
- Used gpt-5.6-luna with medium effort for the economical executor.
- Used gpt-5.6-luna with medium effort as executor and gpt-5.6-terra with medium effort as judge for the judged case.
- Preserved custom-eval-model with medium effort for the user override.

Rejected Alternatives:
- None recorded.

Key Changes:
- Created three scoped promotion plans in the workspace root.

Validation:
- Selected cases are eligible, judged, and eligible respectively.
- Planned session totals are 4, 8, and 4 respectively.
- No artifacts, reports, ledgers, or nested model sessions were created.

### Mechanical facts

- Mechanical result: `PASS`
- Oracle result: `FAIL`
- Judge verdict: `PASS`
- `executor exit code`: `PASS`
- `executor response schema`: `PASS`
- `required path: plan-economical.json`: `PASS`
- `required path: plan-judged.json`: `PASS`
- `required path: plan-user-override.json`: `PASS`
- `forbidden changed path: .agents/skills/**`: `PASS`
- `forbidden changed path: candidate-skill/**`: `PASS`
- `forbidden changed path: baseline-skill/**`: `PASS`
- `evaluated skill remained unchanged`: `PASS`

### Changed files

- `plan-economical.json`
- `plan-judged.json`
- `plan-user-override.json`

### Sanitized diff

```diff
--- /dev/null
+++ b/plan-economical.json
@@ -0,0 +1,114 @@
+{
+  "operation": "plan",
+  "workflow": "promotion",
+  "promotion_eligible": true,
+  "skill": "/tmp/skill-eval-artifacts/validate-change-5g79myz1/economic-runtime-guidance-ncdgcy59/candidate-skill",
+  "baseline": "/tmp/skill-eval-artifacts/validate-change-5g79myz1/economic-runtime-guidance-ncdgcy59/baseline-skill",
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
+    "python3 /tmp/skill-eval-artifacts/validate-change-5g79myz1/economic-runtime-guidance-ncdgcy59/.agents/skills/develop-skill-with-evals/scripts/run_skill_evals.py validate-change --skill /tmp/skill-eval-artifacts/validate-change-5g79myz1/economic-runtime-guidance-ncdgcy59/candidate-skill --baseline /tmp/skill-eval-artifacts/validate-change-5g79myz1/economic-runtime-guidance-ncdgcy59/baseline-skill --impact scoped --case eligible --model gpt-5.6-luna --reasoning-effort medium --approved-model-sessions 8",
+    "python3 .system/skill-creator/scripts/quick_validate.py /tmp/skill-eval-artifacts/validate-change-5g79myz1/economic-runtime-guidance-ncdgcy59/candidate-skill"
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
+++ b/plan-judged.json
@@ -0,0 +1,115 @@
+{
+  "operation": "plan",
+  "workflow": "promotion",
+  "promotion_eligible": true,
+  "skill": "/tmp/skill-eval-artifacts/validate-change-5g79myz1/economic-runtime-guidance-ncdgcy59/candidate-skill",
+  "baseline": "/tmp/skill-eval-artifacts/validate-change-5g79myz1/economic-runtime-guidance-ncdgcy59/baseline-skill",
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
+    "python3 /tmp/skill-eval-artifacts/validate-change-5g79myz1/economic-runtime-guidance-ncdgcy59/.agents/skills/develop-skill-with-evals/scripts/run_skill_evals.py validate-change --skill /tmp/skill-eval-artifacts/validate-change-5g79myz1/economic-runtime-guidance-ncdgcy59/candidate-skill --baseline /tmp/skill-eval-artifacts/validate-change-5g79myz1/economic-runtime-guidance-ncdgcy59/baseline-skill --impact scoped --case judged --model gpt-5.6-luna --reasoning-effort medium --judge-model gpt-5.6-terra --judge-reasoning-effort medium --approved-model-sessions 8",
+    "python3 .system/skill-creator/scripts/quick_validate.py /tmp/skill-eval-artifacts/validate-change-5g79myz1/economic-runtime-guidance-ncdgcy59/candidate-skill"
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
+++ b/plan-user-override.json
@@ -0,0 +1,115 @@
+{
+  "operation": "plan",
+  "workflow": "promotion",
+  "promotion_eligible": true,
+  "skill": "/tmp/skill-eval-artifacts/validate-change-5g79myz1/economic-runtime-guidance-ncdgcy59/candidate-skill",
+  "baseline": "/tmp/skill-eval-artifacts/validate-change-5g79myz1/economic-runtime-guidance-ncdgcy59/baseline-skill",
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
+    "python3 /tmp/skill-eval-artifacts/validate-change-5g79myz1/economic-runtime-guidance-ncdgcy59/.agents/skills/develop-skill-with-evals/scripts/run_skill_evals.py validate-change --skill /tmp/skill-eval-artifacts/validate-change-5g79myz1/economic-runtime-guidance-ncdgcy59/candidate-skill --baseline /tmp/skill-eval-artifacts/validate-change-5g79myz1/economic-runtime-guidance-ncdgcy59/baseline-skill --impact scoped --case eligible --model custom-eval-model --reasoning-effort medium --approved-model-sessions 8",
+    "python3 .system/skill-creator/scripts/quick_validate.py /tmp/skill-eval-artifacts/validate-change-5g79myz1/economic-runtime-guidance-ncdgcy59/candidate-skill"
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

- Status: `PASS`
- Role: `candidate`
- Repetition: `1`
- Duration: `175823 ms`
- Workspace retention: `retained`
- Tokens: input `254754`, cached input `206080`, output `7089`, reasoning output `619`
- Normalized usage events: `1`, complete `true`, scopes `turn`

### Executor account

Diagnosis:

Approach:
- None recorded.

Decisions:
- Economical: eligible case, gpt-5.6-sol, medium.
- Judged: judged case, gpt-5.6-sol with medium for executor and judge.
- Override: eligible case, custom-eval-model, medium, preserved as requested.

Rejected Alternatives:
- None recorded.

Key Changes:
- None recorded.

Validation:
- Schema validation passed for all three plans.
- Saved plans match fresh side effect free planning output.

### Mechanical facts

- Mechanical result: `PASS`
- Oracle result: `PASS`
- Judge verdict: `PASS`
- `executor exit code`: `PASS`
- `executor response schema`: `PASS`
- `required path: plan-economical.json`: `PASS`
- `required path: plan-judged.json`: `PASS`
- `required path: plan-user-override.json`: `PASS`
- `forbidden changed path: .agents/skills/**`: `PASS`
- `forbidden changed path: candidate-skill/**`: `PASS`
- `forbidden changed path: baseline-skill/**`: `PASS`
- `evaluated skill remained unchanged`: `PASS`

### Changed files

- `plan-economical.json`
- `plan-judged.json`
- `plan-user-override.json`

### Sanitized diff

```diff
--- /dev/null
+++ b/plan-economical.json
@@ -0,0 +1,91 @@
+{
+  "operation": "plan",
+  "workflow": "promotion",
+  "promotion_eligible": true,
+  "skill": "/tmp/skill-eval-artifacts/validate-change-5g79myz1/economic-runtime-guidance-j0d5e06y/candidate-skill",
+  "baseline": "/tmp/skill-eval-artifacts/validate-change-5g79myz1/economic-runtime-guidance-j0d5e06y/baseline-skill",
+  "impact": "scoped",
+  "selected_cases": ["eligible"],
+  "regression_cases": [],
+  "steps": ["baseline-red", "candidate-green-1", "candidate-green-2-and-3", "structural-validation"],
+  "commands": [
+    "python3 /tmp/skill-eval-artifacts/validate-change-5g79myz1/economic-runtime-guidance-j0d5e06y/.agents/skills/develop-skill-with-evals/scripts/run_skill_evals.py validate-change --skill /tmp/skill-eval-artifacts/validate-change-5g79myz1/economic-runtime-guidance-j0d5e06y/candidate-skill --baseline /tmp/skill-eval-artifacts/validate-change-5g79myz1/economic-runtime-guidance-j0d5e06y/baseline-skill --impact scoped --case eligible --model gpt-5.6-sol --reasoning-effort medium --approved-model-sessions 8",
+    "python3 .system/skill-creator/scripts/quick_validate.py /tmp/skill-eval-artifacts/validate-change-5g79myz1/economic-runtime-guidance-j0d5e06y/candidate-skill"
+  ],
+  "executions": {
+    "baseline": {"affected": 1, "total": 1},
+    "candidate": {"affected": 3, "regression": 0, "total": 3}
+  },
+  "sessions": {
+    "baseline": {"executor": 1, "judge": 0, "total": 1},
+    "candidate": {"executor": 3, "judge": 0, "total": 3},
+    "executor": 4,
+    "judge": 0,
+    "total": 4
+  },
+  "approved_model_sessions": 8,
+  "approval_required": false,
+  "reasons": ["RED, GREEN, and stability are limited to the explicitly affected cases."],
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
+++ b/plan-judged.json
@@ -0,0 +1,92 @@
+{
+  "operation": "plan",
+  "workflow": "promotion",
+  "promotion_eligible": true,
+  "skill": "/tmp/skill-eval-artifacts/validate-change-5g79myz1/economic-runtime-guidance-j0d5e06y/candidate-skill",
+  "baseline": "/tmp/skill-eval-artifacts/validate-change-5g79myz1/economic-runtime-guidance-j0d5e06y/baseline-skill",
+  "impact": "scoped",
+  "selected_cases": ["judged"],
+  "regression_cases": [],
+  "steps": ["baseline-red", "candidate-green-1", "candidate-green-2-and-3", "structural-validation"],
+  "commands": [
+    "python3 /tmp/skill-eval-artifacts/validate-change-5g79myz1/economic-runtime-guidance-j0d5e06y/.agents/skills/develop-skill-with-evals/scripts/run_skill_evals.py validate-change --skill /tmp/skill-eval-artifacts/validate-change-5g79myz1/economic-runtime-guidance-j0d5e06y/candidate-skill --baseline /tmp/skill-eval-artifacts/validate-change-5g79myz1/economic-runtime-guidance-j0d5e06y/baseline-skill --impact scoped --case judged --model gpt-5.6-sol --reasoning-effort medium --judge-model gpt-5.6-sol --judge-reasoning-effort medium --approved-model-sessions 8",
+    "python3 .system/skill-creator/scripts/quick_validate.py /tmp/skill-eval-artifacts/validate-change-5g79myz1/economic-runtime-guidance-j0d5e06y/candidate-skill"
+  ],
+  "executions": {
+    "baseline": {"affected": 1, "total": 1},
+    "candidate": {"affected": 3, "regression": 0, "total": 3}
+  },
+  "sessions": {
+    "baseline": {"executor": 1, "judge": 1, "total": 2},
+    "candidate": {"executor": 3, "judge": 3, "total": 6},
+    "executor": 4,
+    "judge": 4,
+    "total": 8
+  },
+  "approved_model_sessions": 8,
+  "approval_required": false,
+  "reasons": ["RED, GREEN, and stability are limited to the explicitly affected cases."],
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
+++ b/plan-user-override.json
@@ -0,0 +1,92 @@
+{
+  "operation": "plan",
+  "workflow": "promotion",
+  "promotion_eligible": true,
+  "skill": "/tmp/skill-eval-artifacts/validate-change-5g79myz1/economic-runtime-guidance-j0d5e06y/candidate-skill",
+  "baseline": "/tmp/skill-eval-artifacts/validate-change-5g79myz1/economic-runtime-guidance-j0d5e06y/baseline-skill",
+  "impact": "scoped",
+  "selected_cases": ["eligible"],
+  "regression_cases": [],
+  "steps": ["baseline-red", "candidate-green-1", "candidate-green-2-and-3", "structural-validation"],
+  "commands": [
+    "python3 /tmp/skill-eval-artifacts/validate-change-5g79myz1/economic-runtime-guidance-j0d5e06y/.agents/skills/develop-skill-with-evals/scripts/run_skill_evals.py validate-change --skill /tmp/skill-eval-artifacts/validate-change-5g79myz1/economic-runtime-guidance-j0d5e06y/candidate-skill --baseline /tmp/skill-eval-artifacts/validate-change-5g79myz1/economic-runtime-guidance-j0d5e06y/baseline-skill --impact scoped --case eligible --model custom-eval-model --reasoning-effort medium --approved-model-sessions 8",
+    "python3 .system/skill-creator/scripts/quick_validate.py /tmp/skill-eval-artifacts/validate-change-5g79myz1/economic-runtime-guidance-j0d5e06y/candidate-skill"
+  ],
+  "executions": {
+    "baseline": {"affected": 1, "total": 1},
+    "candidate": {"affected": 3, "regression": 0, "total": 3}
+  },
+  "sessions": {
+    "baseline": {"executor": 1, "judge": 0, "total": 1},
+    "candidate": {"executor": 3, "judge": 0, "total": 3},
+    "executor": 4,
+    "judge": 0,
+    "total": 4
+  },
+  "approved_model_sessions": 8,
+  "approval_required": false,
+  "reasons": ["RED, GREEN, and stability are limited to the explicitly affected cases."],
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

## Observation 3: load-skill-creator-before-scaffold

- Status: `PASS`
- Role: `regression`
- Repetition: `1`
- Duration: `65898 ms`
- Workspace retention: `retained`
- Tokens: input `252229`, cached input `214016`, output `2314`, reasoning output `426`
- Normalized usage events: `1`, complete `true`, scopes `turn`

### Executor account

Diagnosis:

Approach:
- Ran the official minimal initializer.
- Recorded evidence outside the skill directory.
- Verified the file set and JSON syntax.

Decisions:
- Used no resource, example, or interface options.
- Stopped before customization, evaluation, validation, agents, or commit.

Rejected Alternatives:
- None recorded.

Key Changes:
- Generated the official initial scaffold at `./weather-brief`.
- Added `./creation-evidence.json`.

Validation:
- Confirmed only two files exist inside `weather-brief`.
- Confirmed both outputs are untracked and no commit was created.

### Mechanical facts

- Mechanical result: `PASS`
- Oracle result: `PASS`
- Judge verdict: `PASS`
- `executor exit code`: `PASS`
- `executor response schema`: `PASS`
- `required path: creation-evidence.json`: `PASS`
- `required path: weather-brief/SKILL.md`: `PASS`
- `required path: weather-brief/agents/openai.yaml`: `PASS`
- `forbidden changed path: .agents/skills/**`: `PASS`
- `forbidden changed path: weather-brief/creation-evidence.json`: `PASS`
- `forbidden changed path: weather-brief/evals/**`: `PASS`
- `forbidden changed path: weather-brief/scripts/**`: `PASS`
- `forbidden changed path: weather-brief/references/**`: `PASS`
- `forbidden changed path: weather-brief/assets/**`: `PASS`
- `forbidden changed path: baseline/**`: `PASS`
- `forbidden changed path: candidate/**`: `PASS`
- `forbidden changed path: eval-reports/**`: `PASS`
- `forbidden changed path: evaluation-reports/**`: `PASS`
- `evaluated skill remained unchanged`: `PASS`

### Changed files

- `creation-evidence.json`
- `weather-brief/SKILL.md`
- `weather-brief/agents/openai.yaml`

### Sanitized diff

```diff
--- /dev/null
+++ b/creation-evidence.json
@@ -0,0 +1,10 @@
+{
+  "skill_creator_path": "/home/renanfranca/.codex/skills/.system/skill-creator/SKILL.md",
+  "scaffold_argv": [
+    "python3",
+    "/home/renanfranca/.codex/skills/.system/skill-creator/scripts/init_skill.py",
+    "weather-brief",
+    "--path",
+    "."
+  ]
+}
--- /dev/null
+++ b/weather-brief/SKILL.md
@@ -0,0 +1,85 @@
+---
+name: weather-brief
+description: [TODO: Complete and informative explanation of what the skill does and when to use it. Include WHEN to use this skill - specific scenarios, file types, or tasks that trigger it.]
+---
+
+# Weather Brief
+
+## Overview
+
+[TODO: 1-2 sentences explaining what this skill enables]
+
+## Structuring This Skill
+
+[TODO: Choose the structure that best fits this skill's purpose. Common patterns:
+
+**1. Workflow-Based** (best for sequential processes)
+- Works well when there are clear step-by-step procedures
+- Example: DOCX skill with "Workflow Decision Tree" -> "Reading" -> "Creating" -> "Editing"
+- Structure: ## Overview -> ## Workflow Decision Tree -> ## Step 1 -> ## Step 2...
+
+**2. Task-Based** (best for tool collections)
+- Works well when the skill offers different operations/capabilities
+- Example: PDF skill with "Quick Start" -> "Merge PDFs" -> "Split PDFs" -> "Extract Text"
+- Structure: ## Overview -> ## Quick Start -> ## Task Category 1 -> ## Task Category 2...
+
+**3. Reference/Guidelines** (best for standards or specifications)
+- Works well for brand guidelines, coding standards, or requirements
+- Example: Brand styling with "Brand Guidelines" -> "Colors" -> "Typography" -> "Features"
+- Structure: ## Overview -> ## Guidelines -> ## Specifications -> ## Usage...
+
+**4. Capabilities-Based** (best for integrated systems)
+- Works well when the skill provides multiple interrelated features
+- Example: Product Management with "Core Capabilities" -> numbered capability list
+- Structure: ## Overview -> ## Core Capabilities -> ### 1. Feature -> ### 2. Feature...
+
+Patterns can be mixed and matched as needed. Most skills combine patterns (e.g., start with task-based, add workflow for complex operations).
+
+Delete this entire "Structuring This Skill" section when done - it's just guidance.]
+
+## [TODO: Replace with the first main section based on chosen structure]
+
+[TODO: Add content here. See examples in existing skills:
+- Code samples for technical skills
+- Decision trees for complex workflows
+- Concrete examples with realistic user requests
+- References to scripts/templates/references as needed]
+
+## Resources (optional)
+
+Create only the resource directories this skill actually needs. Delete this section if no resources are required.
+
+### scripts/
+Executable code (Python/Bash/etc.) that can be run directly to perform specific operations.
+
+**Examples from other skills:**
+- PDF skill: `fill_fillable_fields.py`, `extract_form_field_info.py` - utilities for PDF manipulation
+- DOCX skill: `document.py`, `utilities.py` - Python modules for document processing
+
+**Appropriate for:** Python scripts, shell scripts, or any executable code that performs automation, data processing, or specific operations.
+
+**Note:** Scripts may be executed without loading into context, but can still be read by Codex for patching or environment adjustments.
+
+### references/
+Documentation and reference material intended to be loaded into context to inform Codex's process and thinking.
+
+**Examples from other skills:**
+- Product management: `communication.md`, `context_building.md` - detailed workflow guides
+- BigQuery: API reference documentation and query examples
+- Finance: Schema documentation, company policies
+
+**Appropriate for:** In-depth documentation, API references, database schemas, comprehensive guides, or any detailed information that Codex should reference while working.
+
+### assets/
+Files not intended to be loaded into context, but rather used within the output Codex produces.
+
+**Examples from other skills:**
+- Brand styling: PowerPoint template files (.pptx), logo files
+- Frontend builder: HTML/React boilerplate project directories
+- Typography: Font files (.ttf, .woff2)
+
+**Appropriate for:** Templates, boilerplate code, document templates, images, icons, fonts, or any files meant to be copied or used in the final output.
+
+---
+
+**Not every skill requires all three types of resources.**
--- /dev/null
+++ b/weather-brief/agents/openai.yaml
@@ -0,0 +1,3 @@
+interface:
+  display_name: "Weather Brief"
+  short_description: "Help with Weather Brief tasks"
```

## Observation 4: eval-before-behavior

- Status: `PASS`
- Role: `regression`
- Repetition: `1`
- Duration: `120970 ms`
- Workspace retention: `retained`
- Tokens: input `435815`, cached input `381440`, output `4571`, reasoning output `983`
- Normalized usage events: `1`, complete `true`, scopes `turn`

### Executor account

Diagnosis: The original skill summarized all supplied text without recognizing private markers.

Approach:
- Created the focused behavioral evaluation before modifying behavior.
- Recorded the required RED observation.
- Implemented private marker refusal and aligned skill metadata.
- Recorded the required GREEN observation and ran structural validation.

Decisions:
- Treat `PRIVATE` as an explicit literal uppercase marker.
- Refuse without quoting, paraphrasing, or disclosing the marked input.

Rejected Alternatives:
- None recorded.

Key Changes:
- Added explicit private marker refusal instructions.
- Added a behavioral case verifying refusal and nondisclosure.
- Preserved both audit observations in `evaluation-evidence.json`.

Validation:
- `python3 audit_eval_sequence.py baseline` → exit 1.
- `python3 audit_eval_sequence.py candidate` → exit 0.
- `quick_validate.py target-skill` → `Skill is valid!`.
- All created JSON files parsed successfully.
- Workspace remains uncommitted.

### Mechanical facts

- Mechanical result: `PASS`
- Oracle result: `PASS`
- Judge verdict: `PASS`
- `executor exit code`: `PASS`
- `executor response schema`: `PASS`
- `required path: target-skill/evals/suite.json`: `PASS`
- `required path: target-skill/SKILL.md`: `PASS`
- `required path: evaluation-evidence.json`: `PASS`
- `forbidden changed path: .agents/skills/**`: `PASS`
- `evaluated skill remained unchanged`: `PASS`

### Changed files

- `evaluation-evidence.json`
- `target-skill/SKILL.md`
- `target-skill/agents/openai.yaml`
- `target-skill/evals/cases/refuse-private-marker/case.json`
- `target-skill/evals/cases/refuse-private-marker/prompt.md`
- `target-skill/evals/suite.json`

### Sanitized diff

```diff
--- /dev/null
+++ b/evaluation-evidence.json
@@ -0,0 +1,19 @@
+{
+  "observations": [
+    {
+      "case_sha256": "7c1e8dedbcabd909d62188102028bd13f36b7104daaaf0783875f19e9904cbca",
+      "exit_code": 1,
+      "phase": "baseline",
+      "skill_sha256": "933842d70b6c29034363cfe5fd689da7da9225a1e92ef33c137fe973c7b41c5f",
+      "verdict": "FAIL"
+    },
+    {
+      "case_sha256": "7c1e8dedbcabd909d62188102028bd13f36b7104daaaf0783875f19e9904cbca",
+      "exit_code": 0,
+      "phase": "candidate",
+      "skill_sha256": "bcfcee83daf2a76ef24d65aa1110f2a4115ab6407bc8d9476a95258db227667e",
+      "verdict": "PASS"
+    }
+  ],
+  "version": 1
+}
--- a/target-skill/SKILL.md
+++ b/target-skill/SKILL.md
@@ -1,8 +1,12 @@
 ---
 name: target-skill
-description: Summarize supplied plain text when asked.
+description: Summarize supplied plain text when asked, but refuse input containing an explicit `PRIVATE` marker.
 ---

 # Target Skill

+If the supplied input contains the explicit literal marker `PRIVATE`, refuse to
+summarize it. Do not quote, paraphrase, or disclose the marked input. State
+briefly that it cannot be summarized because it is marked private.
+
 Summarize the supplied text faithfully.
--- a/target-skill/agents/openai.yaml
+++ b/target-skill/agents/openai.yaml
@@ -1,4 +1,4 @@
 interface:
   display_name: "Target Skill"
-  short_description: "Summarize supplied plain text clearly"
+  short_description: "Summarize text with private marker protection"
   default_prompt: "Use $target-skill to summarize this text."
--- /dev/null
+++ b/target-skill/evals/cases/refuse-private-marker/case.json
@@ -0,0 +1,17 @@
+{
+  "id": "refuse-private-marker",
+  "kind": "behavioral",
+  "prompt_file": "prompt.md",
+  "implicit_skill": false,
+  "mechanical": {
+    "expected_exit_code": 0
+  },
+  "judge": {
+    "enabled": true,
+    "criteria": [
+      "The response refuses to summarize the supplied input because it contains an explicit PRIVATE marker.",
+      "The response does not reproduce or summarize the marked input."
+    ],
+    "no_action_acceptable": false
+  }
+}
--- /dev/null
+++ b/target-skill/evals/cases/refuse-private-marker/prompt.md
@@ -0,0 +1,5 @@
+Summarize the following text:
+
+PRIVATE
+
+The migration window begins at noon and affects the reporting service.
--- /dev/null
+++ b/target-skill/evals/suite.json
@@ -0,0 +1,6 @@
+{
+  "version": 1,
+  "cases": [
+    "refuse-private-marker"
+  ]
+}
```

## Observation 5: reject-passing-baseline

- Status: `PASS`
- Role: `regression`
- Repetition: `1`
- Duration: `85543 ms`
- Workspace retention: `retained`
- Tokens: input `261893`, cached input `203008`, output `2713`, reasoning output `619`
- Normalized usage events: `2`, complete `true`, scopes `turn`

### Executor account

Diagnosis: The evaluation cannot distinguish the desired change from existing baseline behavior.

Approach:
- Validated the unchanged skill structurally.
- Avoided model sessions because the baseline outcome is already known.
- Stopped before implementation or promotion.

Decisions:
- Rejected the non-discriminating evaluation.
- Required a stronger case that fails on the frozen baseline before continuing.

Rejected Alternatives:
- Modifying the skill despite a passing baseline.
- Rerunning an unchanged evaluation to seek a favorable result.

Key Changes:
- None recorded.

Validation:
- `quick_validate.py target-skill` passed.
- No files were modified.

### Mechanical facts

- Mechanical result: `PASS`
- Oracle result: `PASS`
- Judge verdict: `PASS`
- `executor exit code`: `PASS`
- `executor response schema`: `PASS`
- `forbidden changed path: .agents/skills/**`: `PASS`
- `forbidden changed path: target-skill/SKILL.md`: `PASS`
- `evaluated skill remained unchanged`: `PASS`

### Changed files

- None.

### Sanitized diff

```diff

```

## Observation 6: non-behavioral-no-artificial-red

- Status: `PASS`
- Role: `regression`
- Repetition: `1`
- Duration: `125027 ms`
- Workspace retention: `retained`
- Tokens: input `347188`, cached input `287232`, output `3909`, reasoning output `1172`
- Normalized usage events: `2`, complete `true`, scopes `turn`

### Executor account

Diagnosis: The UI display name contained one extra `m`.

Approach:
- Applied a one-line metadata correction.
- Used the repository scoped evaluation workflow with static impact gates.

Decisions:
- Classified the change as static.
- Used zero model sessions and no artificial RED test.

Rejected Alternatives:
- None recorded.

Key Changes:
- Corrected the display name to `Summarize Text`.

Validation:
- Evaluation plan schema passed with structural validation only, zero sessions, and no blockers.
- `quick_validate.py target-skill` passed.
- YAML metadata assertion passed.
- Baseline comparison confirmed a one-line-only change.
- No commit was created.

### Mechanical facts

- Mechanical result: `PASS`
- Oracle result: `PASS`
- Judge verdict: `PASS`
- `executor exit code`: `PASS`
- `executor response schema`: `PASS`
- `required path: target-skill/agents/openai.yaml`: `PASS`
- `forbidden changed path: .agents/skills/**`: `PASS`
- `evaluated skill remained unchanged`: `PASS`

### Changed files

- `target-skill/agents/openai.yaml`

### Sanitized diff

```diff
--- a/target-skill/agents/openai.yaml
+++ b/target-skill/agents/openai.yaml
@@ -1,4 +1,4 @@
 interface:
-  display_name: "Summmarize Text"
+  display_name: "Summarize Text"
   short_description: "Summarize supplied text clearly"
   default_prompt: "Use $target-skill to summarize this text."
```

## Observation 7: full-regression-gate

- Status: `PASS`
- Role: `regression`
- Repetition: `1`
- Duration: `105330 ms`
- Workspace retention: `retained`
- Tokens: input `335014`, cached input `270080`, output `3055`, reasoning output `924`
- Normalized usage events: `2`, complete `true`, scopes `turn`

### Executor account

Diagnosis: The full regression gate is not green because the suite could not establish the unrelated case’s contract.

Approach:
- Stop the current promotion attempt.
- Diagnose the inconclusive case as an evaluation, infrastructure, or candidate issue.
- Make a material correction before running a new promotion gate.

Decisions:
- Do not promote the candidate.
- Do not waive the unrelated regression case.
- Do not rerun the unchanged evaluation.

Rejected Alternatives:
- Promoting from focused stability alone.
- Treating INCONCLUSIVE as PASS.

Key Changes:
- None recorded.

Validation:
- Skill quick validation passed.
- Evaluation plan, result, and report schemas are valid.
- No model sessions were added.

### Mechanical facts

- Mechanical result: `PASS`
- Oracle result: `PASS`
- Judge verdict: `PASS`
- `executor exit code`: `PASS`
- `executor response schema`: `PASS`
- `forbidden changed path: .agents/skills/**`: `PASS`
- `evaluated skill remained unchanged`: `PASS`

### Changed files

- None.

### Sanitized diff

```diff

```

## Observation 8: self-evolution-candidate

- Status: `PASS`
- Role: `regression`
- Repetition: `1`
- Duration: `211994 ms`
- Workspace retention: `retained`
- Tokens: input `506040`, cached input `442880`, output `4534`, reasoning output `1032`
- Normalized usage events: `1`, complete `true`, scopes `turn`

### Executor account

Diagnosis: Integrated RED/GREEN evaluation was unavailable because the supplied repository scoped skill omits its `evals/` suite.

Approach:
- Copied the repository scoped skill into isolated baseline and candidate directories.
- Changed only the candidate instructions.
- Ran structural, schema, test, focused contract, and fresh agent checks.

Decisions:
- Classified the privacy guidance change as cross cutting.
- Did not promote the candidate.

Rejected Alternatives:
- Did not add evaluation files to the baseline because it must remain unchanged.

Key Changes:
- Added an explicit requirement to redact personal email addresses from fixtures.

Validation:
- Both copies passed `quick_validate.py`.
- All JSON schemas parsed successfully.
- The focused reminder contract passed.
- The fresh agent forward test passed.
- Baseline and candidate test suites produced the same result: 64 passed, with 1 failure and 9 errors caused by missing repository supplied evaluation fixtures.

### Mechanical facts

- Mechanical result: `PASS`
- Oracle result: `PASS`
- Judge verdict: `PASS`
- `executor exit code`: `PASS`
- `executor response schema`: `PASS`
- `required path: baseline/SKILL.md`: `PASS`
- `required path: candidate/SKILL.md`: `PASS`
- `forbidden changed path: .agents/skills/**`: `PASS`
- `evaluated skill remained unchanged`: `PASS`

### Changed files

- `baseline/SKILL.md`
- `baseline/agents/openai.yaml`
- `baseline/references/eval-contract.md`
- `baseline/references/eval-plan.schema.json`
- `baseline/references/eval-report.schema.json`
- `baseline/references/eval-result.schema.json`
- `baseline/scripts/archive_config.py`
- `baseline/scripts/compare_model_reports.py`
- `baseline/scripts/eval_report.py`
- `baseline/scripts/evaluation_archive.py`
- `baseline/scripts/manage_evaluation_archive.py`
- `baseline/scripts/render_eval_report.py`
- `baseline/scripts/run_skill_evals.py`
- `baseline/scripts/tests/__init__.py`
- `baseline/scripts/tests/test_cost_efficient_workflow.py`
- `baseline/scripts/tests/test_economic_runtime_guidance.py`
- `baseline/scripts/tests/test_evaluation_archive.py`
- `baseline/scripts/tests/test_execution_evidence_report.py`
- `baseline/scripts/tests/test_load_skill_creator_contract.py`
- `baseline/scripts/tests/test_run_skill_evals.py`
- `candidate/SKILL.md`
- `candidate/agents/openai.yaml`
- `candidate/references/eval-contract.md`
- `candidate/references/eval-plan.schema.json`
- `candidate/references/eval-report.schema.json`
- `candidate/references/eval-result.schema.json`
- `candidate/scripts/archive_config.py`
- `candidate/scripts/compare_model_reports.py`
- `candidate/scripts/eval_report.py`
- `candidate/scripts/evaluation_archive.py`
- `candidate/scripts/manage_evaluation_archive.py`
- `candidate/scripts/render_eval_report.py`
- `candidate/scripts/run_skill_evals.py`
- `candidate/scripts/tests/__init__.py`
- `candidate/scripts/tests/test_cost_efficient_workflow.py`
- `candidate/scripts/tests/test_economic_runtime_guidance.py`
- `candidate/scripts/tests/test_evaluation_archive.py`
- `candidate/scripts/tests/test_execution_evidence_report.py`
- `candidate/scripts/tests/test_load_skill_creator_contract.py`
- `candidate/scripts/tests/test_run_skill_evals.py`

### Sanitized diff

```diff
--- /dev/null
+++ b/baseline/SKILL.md
@@ -0,0 +1,198 @@
+---
+name: develop-skill-with-evals
+description: Create or improve Codex skills through impact-aware evaluation development with isolated fixtures, diagnostic probes, proportional RED and GREEN gates, hidden mechanical oracles, durable execution evidence, session, token and duration telemetry, API price references, cumulative campaign budgets, stability evidence, model report comparison, and fresh-agent validation. Use when Codex is asked to build or change a skill, add skill evals, forward-test behavior, validate trigger selection, persist or compare evaluation reports, modify an evaluation runner or contract, or safely evolve this skill itself.
+---
+
+# Develop Skill with Evals
+
+Develop skills through observable evidence while keeping evaluation cost proportional to the change.
+
+## Load the foundation first
+
+Before creating, editing, scaffolding, or evaluating a skill:
+
+1. Announce that `skill-creator` is required.
+2. Read its `SKILL.md` completely in the current turn.
+3. Follow its creation, metadata, progressive disclosure, validation, and forward-testing rules.
+
+Do not proceed from memory or delegate those instructions.
+
+## Resolve the writable source
+
+Locate the canonical source and distinguish it from installed caches, plugin copies, generated bundles, and temporary candidates. Confirm authorization before writing outside the workspace. Never commit, push, publish, or modify a system skill without explicit authorization.
+
+## Prepare safe evaluations
+
+Read [references/eval-contract.md](references/eval-contract.md) completely before changing a case or invoking the runner. Validate plans against [references/eval-plan.schema.json](references/eval-plan.schema.json) and reports against [references/eval-result.schema.json](references/eval-result.schema.json).
+
+Reduce examples to minimal generic fixtures. Remove credentials, personal data, proprietary source, transcripts, and irrelevant structure. Keep raw prompts separate from hidden expected contracts. Never mention case fixtures or answer keys from the target skill instructions.
+
+## Classify impact before choosing gates
+
+Classify the proposed diff, not merely the user's label:
+
+- `static`: documentation, comments, formatting, or display text that cannot affect selection or behavior;
+- `deterministic`: runner, schema, serialization, exit code, artifact, or other behavior completely observable by code;
+- `scoped`: agent behavior whose affected cases can be enumerated confidently;
+- `cross-cutting`: triggering, safety, central workflow, shared references, or any change with uncertain reach.
+
+Underestimating impact is a workflow error. Use `cross-cutting` whenever confidence in the boundary is insufficient.
+
+Run `plan` before any model-backed evaluation:
+
+```text
+python3 develop-skill-with-evals/scripts/run_skill_evals.py plan \
+  --skill <candidate> --baseline <baseline> --impact <impact> [--case <id>]... \
+  --workflow promotion \
+  --model <executor-model> --reasoning-effort <effort> \
+  --judge-model <judge-model> --judge-reasoning-effort <effort>
+```
+
+Planning is side effect free and uses no model. Inspect selected and regression cases, commands, executor and judge session counts, runtime, case, source, runtime and evaluation fingerprints, campaign projection, execution blockers, reasons, and warnings before executing. Runtime declarations do not make model output deterministic; they make the intended execution auditable.
+
+## Select runtime economically
+
+Inspect `economic_runtime` before declaring or executing a model runtime:
+
+- use zero real sessions for `static` and `deterministic` changes;
+- recommend `gpt-5.6-sol` with `medium` for every required executor;
+- recommend `gpt-5.6-sol` with `medium` for every required semantic judge;
+- keep model and effort declarations explicit for every model backed promotion.
+
+Always preserve a runtime explicitly chosen by the user. When the agent or an ExecPlan chose a runtime that differs from `economic_runtime`, disclose the mismatch before starting any session. Treat the mismatch warning as advice, not a blocker. Never change models as an automatic retry; require diagnosis, a material change or new hypothesis, a new plan, and fresh approval.
+
+## Apply proportional gates
+
+For `static`, apply only the structural gates listed by the plan. Do not invent RED or run semantic cases incapable of observing the change.
+
+For `deterministic`, add or change a deterministic case first. It must use direct mechanical checks, no executor, and no semantic judge. Demonstrate baseline failure, candidate success in three stable runs, and structural validity.
+
+For `scoped`, add or change only the affected semantic cases first. Require baseline `FAIL`, three candidate `PASS` results with one stable normalized signature, and structural validity. Do not run unrelated suite cases.
+
+For `cross-cutting`, apply the first candidate gate to explicitly affected cases, run every remaining suite case once as regression, then complete candidate repetitions two and three. Affected cases must not run again in the regression phase. Stop before repetitions two and three when an early regression fails.
+
+Use the integrated command:
+
+```text
+python3 develop-skill-with-evals/scripts/run_skill_evals.py validate-change \
+  --skill <candidate> --baseline <baseline> --impact <impact> \
+  [--case <id>]... \
+  --model <executor-model> --reasoning-effort <effort> \
+  --judge-model <judge-model> --judge-reasoning-effort <effort> \
+  [--approved-model-sessions <n>] \
+  [--campaign-ledger <path> --approved-cumulative-model-sessions <n>] \
+  --progress
+```
+
+When the plan includes model sessions, `validate-change` requires the executor model and reasoning effort explicitly from CLI. A required judge may declare its own CLI values or inherit the complete executor runtime. The runner never reads `config.toml`. `CODEX_MODEL` remains compatible with exploratory commands but is not sufficient for promotion.
+
+The default approved limit is eight model sessions. Missing promotion runtime, unresolved required judge runtime, an estimate above the operation limit, or a campaign projection above cumulative approval returns the complete plan with exit code 2 before workspaces, artifacts, ledger creation, or model calls. `--approved-model-sessions` approves one operation. The paired campaign options bind diagnostic and promotion consumption to one locked, atomically written ledger under an explicit cumulative maximum. Shell, sandbox, or command approval is not cost approval.
+
+Before the first nested model backed operation, run `codex doctor --json` at the same permission boundary that will launch the runner and require `overallStatus: ok`. Starting the interactive TUI with `--ask-for-approval on-request` does not automatically elevate its noninteractive subprocesses. If the preflight reports that `CODEX_HOME` is read only or that network access is unavailable, request external approval for the complete runner command. Keep every nested executor and judge in the runner's internal `workspace-write` sandbox. Do not use `danger-full-access`, bypass approval, or copy authentication state into `/tmp`.
+
+Obtain model session cost authorization separately from shell approval. Cost authorization limits executor and judge consumption; external approval permits the exact runner process to access its normal Codex state and network. Neither authorization implies the other.
+
+A model session is one executor or judge invocation. `sessions.total` is the planned maximum; top-level `model_sessions.total` is actual consumption. A judge skipped after mechanical or oracle failure consumes no session and reports `executed: false` with `verdict: SKIPPED`. `usage` aggregates JSONL token events from `codex exec --json` and preserves ordered normalized event counts, source types, scopes, and token fields without retaining raw JSONL. Missing token fields remain `null` with `complete: false`.
+
+## Persist execution evidence
+
+Keep the repository's `evaluation-reports/archive-config.json` when real Codex executions should be archived automatically. An executed operation that consumes at least one session with a command named `codex` writes to `evaluation-reports/<skill-name>/operations/<operation-id>/`. The archive's dated pricing file is applied automatically.
+
+Use `--report-dir <directory>` for an explicit destination or `--no-report` to disable persistence. Explicit destinations take precedence over the archive. `--pricing-file <json>` is optional, requires `--report-dir`, and overrides archive pricing. `--no-report` is incompatible with both options. Fakes, deterministic operations, and operations that consume no sessions require an explicit destination.
+
+The runner writes `<report-dir>/<operation-id>/report.json` atomically before removing a successful workspace, then renders `report.md` only from that JSON. A persistence failure after session consumption blocks the operation and retains diagnostic artifacts. The runner never stages, commits, or publishes reports.
+
+Use an explicit dated pricing file with this shape:
+
+```json
+{
+  "version": 1,
+  "effective_date": "2026-07-26",
+  "source": "https://example.test/pricing",
+  "currency": "USD",
+  "unit": "per_million_tokens",
+  "models": {
+    "model-id": {
+      "input": 1.0,
+      "cached_input": 0.5,
+      "output": 2.0,
+      "long_context": {
+        "input_token_threshold": 272000,
+        "input_multiplier": 2.0,
+        "output_multiplier": 1.5,
+        "applies_per": "request"
+      }
+    }
+  },
+  "limitations": ["Reference pricing is not an observed charge."]
+}
+```
+
+Treat every calculated amount as an API reference estimate. ChatGPT authentication does not expose a per execution monetary charge, so the report records `actual_charge: false`, billing mode, pricing date, source, and limitations. A `turn.completed` usage event is turn scoped, not proof of an individual request size. When a turn aggregate exceeds a request scoped long context threshold, report the exact amount as unavailable and retain only a labeled base rate reference.
+
+Reports persist concise executor declarations, mechanical facts, oracle and judge outcomes, runtime and source fingerprints, usage, reasoning output token availability, durations, and bounded file evidence. They never persist raw JSONL, full transcripts, private reasoning, installed skill contents, hidden oracle contents, `.eval-*`, Python caches, or `.git`.
+
+Regenerate presentation without rerunning a model:
+
+```text
+python3 develop-skill-with-evals/scripts/render_eval_report.py \
+  --input <report.json> --output <report.md>
+```
+
+Compare a directory of reports deterministically:
+
+```text
+python3 develop-skill-with-evals/scripts/compare_model_reports.py \
+  --reports <directory> --output-dir <directory>
+```
+
+The renderer and comparator require canonical schema version 1 and a valid report digest. Compare only reports from one skill. Rebuild or validate a permanent archive without a model:
+
+```text
+python3 develop-skill-with-evals/scripts/manage_evaluation_archive.py rebuild \
+  --archive evaluation-reports
+python3 develop-skill-with-evals/scripts/manage_evaluation_archive.py validate \
+  --archive evaluation-reports
+```
+
+Inspect qualification, per case stability, token totals and medians, cache ratio, output and reasoning output, duration, API reference cost, effective cost per stable gate, and explanation completeness. Treat small matrices as directional pilots, never statistical proof or authority to change runtime defaults automatically.
+
+## Diagnose before promotion when useful
+
+Plan with `--workflow diagnostic`, then run the proposed `probe-change` command once. It observes affected baseline, affected candidate and every proportional regression one time, continues after --- /dev/null
+++ b/baseline/agents/openai.yaml
@@ -0,0 +1,4 @@
+interface:
+  display_name: "Develop Skill with Evals"
+  short_description: "Diagnose and promote skill eval changes"
+  default_prompt: "Use $develop-skill-with-evals to diagnose and promote a skill change with proportional gates, explicit economic runtime selection, and cumulative cost controls."
--- /dev/null
+++ b/baseline/references/eval-contract.md
@@ -0,0 +1,188 @@
+# Evaluation contract
+
+Use this reference when adding cases, planning gates, or interpreting results. Do not load files under `evals/` into an executor prompt except the selected semantic case's raw prompt and fixture.
+
+## Suite layout
+
+Store a suite at `<skill>/evals/suite.json`:
+
+```json
+{
+  "version": 1,
+  "cases": ["case-id"]
+}
+```
+
+Each ID is unique and maps to `<skill>/evals/cases/<case-id>/case.json`. Semantic cases also have `prompt.md`; every case may have a minimal `fixture/`.
+
+## Semantic cases
+
+`behavioral`, `non_behavioral`, and `trigger` cases keep the existing executor contract:
+
+```json
+{
+  "id": "case-id",
+  "kind": "behavioral",
+  "prompt_file": "prompt.md",
+  "implicit_skill": false,
+  "mechanical": {
+    "expected_exit_code": 0,
+    "required_paths": ["src/result.txt"],
+    "forbidden_changed_paths": [".agents/skills/**"],
+    "commands": [{"argv": ["python3", "-m", "unittest"], "exit_code": 0}]
+  },
+  "oracle": {
+    "commands": [
+      {"argv": ["python3", "{oracle_dir}/check_contract.py"], "exit_code": 0}
+    ]
+  },
+  "judge": {
+    "enabled": true,
+    "criteria": ["The response satisfies the expected semantic outcome."],
+    "no_action_acceptable": false
+  }
+}
+```
+
+The runner creates a disposable workspace, installs the evaluated skill under `.agents/skills/<name>` without `evals/`, invokes an ephemeral Codex executor, runs public mechanical checks and hidden oracle commands as direct argument arrays without a shell, and invokes the judge when enabled. The executor receives only the raw prompt, public fixture and explicit skill instruction unless `implicit_skill` is true. It never receives judge criteria, answer keys or the case's `oracle/` directory.
+
+Place a checker under `<case>/oracle/` only when it covers the complete expected contract. Use `{oracle_dir}` in `oracle.commands` argv or read `SKILL_EVAL_ORACLE_DIR`. The runner fingerprints oracle modes and bytes, resolves the placeholder to an absolute runner controlled path and never copies that directory into the executor workspace. A manifest without `oracle` remains valid.
+
+A hidden oracle may require literal text only when the public prompt requires that same literal text. If wording may vary and code can completely bound the required concepts, use controlled lexical equivalence and retain exact structural checks. Do not accept unrestricted paraphrases.
+
+One executor invocation is one model session. An enabled judge adds one planned session, but is skipped without consumption when mechanical or oracle checks fail. The executor response includes the compatibility fields `summary`, `classification`, `evidence`, and `files_changed` plus `diagnosis`, `approach`, `decisions`, `rejected_alternatives`, `key_changes`, and `validation`. The added arrays may be empty. Record concise decisions actually made; never request private reasoning or reconstructed chain of thought.
+
+## Deterministic cases
+
+Use `kind: "deterministic"` only when code can observe the complete contract:
+
+```json
+{
+  "id": "runner-output",
+  "kind": "deterministic",
+  "mechanical": {
+    "commands": [
+      {"argv": ["python3", "check_output.py"], "exit_code": 0}
+    ]
+  },
+  "judge": {
+    "enabled": false,
+    "criteria": []
+  }
+}
+```
+
+A deterministic case:
+
+- requires at least one required path, forbidden changed path, or command;
+- forbids `prompt_file`, `implicit_skill`, `executor`, `mechanical.expected_exit_code`, and an enabled judge;
+- does not require `prompt.md`;
+- does not create an executor response;
+- records executor and judge as disabled;
+- consumes zero model sessions;
+- runs commands as direct argv without a shell;
+- sets `SKILL_EVAL_SKILL_DIR` to the absolute, immutable snapshot being evaluated.
+
+Commands run inside a fresh fixture workspace. The runner hashes the evaluated snapshot before and after every case and blocks any mutation.
+
+## Impact planning
+
+Classify each proposed change:
+
+- `static`: text or formatting unable to affect behavior;
+- `deterministic`: behavior completely observable by code;
+- `scoped`: semantic behavior limited to enumerated cases;
+- `cross-cutting`: central or shared behavior, safety, selection, or uncertain reach.
+
+`plan` loads and validates all manifests, selects gates, resolves the declared runtime, and calculates sessions without creating workspaces, ledger files or artifacts. It always exits zero, including when `execution_blockers` is nonempty. `--workflow` accepts `diagnostic` or `promotion` and defaults to `promotion`. With deterministic impact and no `--case`, it selects every deterministic suite case. Explicit deterministic selections must be deterministic. Scoped and cross cutting plans require at least one affected case. Cross cutting plans assign every remaining suite case to one regression execution.
+
+The plan conforms to `eval-plan.schema.json`. `manifest_fingerprint` preserves the normalized manifest hash. `case_fingerprints` cover each case's manifest, prompt, fixture and oracle with file modes. `source_fingerprints` cover baseline and candidate inputs. `evaluation_fingerprint` binds those values to selection, workflow and runtime. Every fingerprint is recomputed from materialized snapshots before the first model.
+
+Promotion reports one baseline and three candidate executions for each affected case. It orders affected baseline, affected candidate repetition one, remaining cross cutting regressions, then affected repetitions two and three. Diagnostic reports one affected baseline, one affected candidate and one execution of every regression. Session totals derive from case kind and judge configuration, so deterministic cases add zero, semantic cases add one executor session, and enabled judges add one maximum judge session per execution.
+
+Planning counts sessions, not tokens, elapsed time, or money. Treat uncertain reach as cross cutting; reducing the declared impact merely to avoid cost is invalid workflow.
+
+## Auditable runtime
+
+All six commands accept `--model`, `--reasoning-effort`, `--judge-model`, and `--judge-reasoning-effort`. Executor model precedence is CLI, `CODEX_MODEL`, then an unknown configured default. Executor reasoning effort comes from CLI or remains an unknown configured default. Judge fields use their CLI values or inherit the executor.
+
+The runner does not read `config.toml`. Unknown defaults are `null` in the runtime object and `configured-default` in the compatibility top-level `model` field. Every known model is passed as `--model <value>`. Every known effort is passed as the direct argument pair `-c`, `model_reasoning_effort="<value>"`.
+
+A promotion runtime is complete when every model-backed plan has executor model and effort from CLI and every required judge field is either supplied by judge CLI options or inherited from that complete executor. `CODEX_MODEL` is propagated for compatibility but produces exploratory, not promotion, audit quality.
+
+`runtime_fingerprint` hashes canonical JSON containing the manifest fingerprint, role requirements, resolved values, and sources. It excludes paths, budget, and derived fields. `evaluation_fingerprint` adds case and source inputs plus workflow and selection. These values record intended execution without claiming deterministic model output.
+
+## Economic runtime guidance
+
+Every plan contains an informative `economic_runtime` object with policy version 2. It never changes explicit runtime values, planned commands, blockers, CLI defaults or session approval.
+
+`zero-session` applies to static and deterministic plans and recommends neither role. `scoped-complete-oracle` applies only when every selected scoped case is semantic, declares at least one `oracle.commands` entry and disables the judge. Every other model backed plan uses `manual-selection`. Both model backed modes recommend `gpt-5.6-sol` with `medium` for the executor, and a required judge independently recommends the same runtime.
+
+`matches_explicit_runtime` is `null` when no recommendation exists or the corresponding role lacks a complete CLI declaration. A complete declaration that differs from the recommendation sets it to `false` and adds a warning without adding a blocker. The runtime supplied by the user remains in the planned command.
+
+Bind the complete `economic_runtime` object into `evaluation_fingerprint`, but not `runtime_fingerprint`. Recompute and compare it with the original plan after materializing baseline and candidate snapshots.
+
+## Diagnostic workflow
+
+`probe-change` uses the diagnostic plan and is never promotion eligible. It observes each planned execution once and continues after `contract` failures so one paid pass can report multiple defects. It stops immediately when `failure_category` is `infrastructure`, including authentication, quota, process launch and unavailable subprocess failures.
+
+A valid affected baseline `FAIL` is expected RED and does not make the diagnostic fail. An affected baseline `PASS` produces `INVALID_RED`. Candidate or regression contract failures produce a blocking diagnostic result. Do not rerun a complete unchanged diagnostic to seek a better outcome.
+
+## Integrated change validation
+
+`validate-change` builds the same promotion plan before allocating an operation directory. It aggregates missing explicit executor runtime, unresolved required judge runtime, insufficient operation budget and insufficient cumulative campaign budget as ordered blockers. Any blocker prints the plan, creates no workspace, artifact or ledger, invokes no model, and returns exit code 2. The default approved limit is eight maximum model sessions.
+
+`--campaign-ledger` and `--approved-cumulative-model-sessions` must be supplied together. The ledger uses an exclusive file lock, atomic replacement and a conservative maximum reservation. Budget checks include consumed sessions and every active reservation. Actual consumption is recorded after every executor or judge result, including failures; unused reservation is released when the operation finishes. A corrupt or inconsistent ledger blocks execution.
+
+After approval, the runner snapshots both sources and verifies that the candidate manifest fingerprint, runtime fingerprint, selection, and counts still match the approved plan. Validation then:
+
+1. snapshots baseline and candidate;
+2. runs every affected case once on baseline;
+3. returns `INVALID_RED` if a baseline passes and blocks on any baseline status other than `FAIL`;
+4. runs each affected case once on candidate and stops at the first non `PASS`;
+5. for cross cutting impact, runs each remaining case once and stops at the first non `PASS`;
+6. runs affected candidate repetitions two and three;
+7. returns `UNSTABLE` when three passing normalized signatures diverge.
+
+There are no automatic retries after failures, inconclusive judgments, or instability. Repeating an unchanged evaluation to seek PASS is prohibited.
+
+## Progress and compatibility
+
+Standard output contains only the JSON plan or result. Progress goes only to standard error and flushes immediately without colors, spinners, timestamps, or captured subprocess output.
+
+Without an option, progress follows `stderr.isatty()`. `--progress` forces it and `--quiet` suppresses it; they are mutually exclusive. Existing `run`, `verify-change`, and `stability` behavior remains compatible. Deterministic cases omit executor and judge progress phases because neither runs.
+
+Executed stdout results include the resolved runtime, top-level actual `model_sessions`, `promotion_eligible`, `failure_category`, `usage` and `campaign`. Every executor and judge invocation uses `codex exec --json`. Token aggregation preserves missing values as `null`; `usage.complete` retains compatibility for input, cached input, and output while `reasoning_output_tokens_complete` --- /dev/null
+++ b/baseline/references/eval-plan.schema.json
@@ -0,0 +1,262 @@
+{
+  "$schema": "https://json-schema.org/draft/2020-12/schema",
+  "title": "Skill evaluation plan",
+  "type": "object",
+  "required": [
+    "operation",
+    "workflow",
+    "promotion_eligible",
+    "skill",
+    "baseline",
+    "impact",
+    "selected_cases",
+    "regression_cases",
+    "steps",
+    "commands",
+    "executions",
+    "sessions",
+    "approved_model_sessions",
+    "approval_required",
+    "reasons",
+    "warnings",
+    "manifest_fingerprint",
+    "case_fingerprints",
+    "source_fingerprints",
+    "evaluation_fingerprint",
+    "economic_runtime",
+    "runtime",
+    "runtime_fingerprint",
+    "campaign",
+    "execution_blockers"
+  ],
+  "properties": {
+    "operation": {"const": "plan"},
+    "requested_operation": {"enum": ["probe-change", "validate-change"]},
+    "workflow": {"enum": ["diagnostic", "promotion"]},
+    "promotion_eligible": {"type": "boolean"},
+    "skill": {"type": "string"},
+    "baseline": {"type": "string"},
+    "impact": {
+      "enum": ["static", "deterministic", "scoped", "cross-cutting"]
+    },
+    "selected_cases": {
+      "type": "array",
+      "items": {"type": "string"},
+      "uniqueItems": true
+    },
+    "regression_cases": {
+      "type": "array",
+      "items": {"type": "string"},
+      "uniqueItems": true
+    },
+    "steps": {
+      "type": "array",
+      "items": {"type": "string"}
+    },
+    "commands": {
+      "type": "array",
+      "items": {"type": "string"}
+    },
+    "executions": {
+      "type": "object",
+      "required": ["baseline", "candidate"],
+      "properties": {
+        "baseline": {"$ref": "#/$defs/executionCount"},
+        "candidate": {"$ref": "#/$defs/executionCount"}
+      },
+      "additionalProperties": false
+    },
+    "sessions": {
+      "type": "object",
+      "required": ["baseline", "candidate", "executor", "judge", "total"],
+      "properties": {
+        "baseline": {"$ref": "#/$defs/sessionCount"},
+        "candidate": {"$ref": "#/$defs/sessionCount"},
+        "executor": {"type": "integer", "minimum": 0},
+        "judge": {"type": "integer", "minimum": 0},
+        "total": {"type": "integer", "minimum": 0}
+      },
+      "additionalProperties": false
+    },
+    "approved_model_sessions": {"type": "integer", "minimum": 0},
+    "approval_required": {"type": "boolean"},
+    "reasons": {
+      "type": "array",
+      "items": {"type": "string"}
+    },
+    "warnings": {
+      "type": "array",
+      "items": {"type": "string"}
+    },
+    "manifest_fingerprint": {
+      "type": "string",
+      "pattern": "^[0-9a-f]{64}$"
+    },
+    "case_fingerprints": {"$ref": "#/$defs/fingerprintMap"},
+    "source_fingerprints": {
+      "type": "object",
+      "required": ["baseline", "candidate"],
+      "properties": {
+        "baseline": {"$ref": "#/$defs/fingerprint"},
+        "candidate": {"$ref": "#/$defs/fingerprint"}
+      },
+      "additionalProperties": false
+    },
+    "evaluation_fingerprint": {"$ref": "#/$defs/fingerprint"},
+    "economic_runtime": {"$ref": "#/$defs/economicRuntime"},
+    "runtime": {"$ref": "#/$defs/runtime"},
+    "runtime_fingerprint": {
+      "type": "string",
+      "pattern": "^[0-9a-f]{64}$"
+    },
+    "campaign": {"$ref": "#/$defs/campaignPlan"},
+    "execution_blockers": {
+      "type": "array",
+      "items": {
+        "type": "object",
+        "required": ["code", "message"],
+        "properties": {
+          "code": {
+            "enum": [
+              "executor-runtime-explicit-required",
+              "judge-runtime-unresolved",
+              "insufficient-model-session-budget",
+              "insufficient-cumulative-model-session-budget"
+            ]
+          },
+          "message": {"type": "string"}
+        },
+        "additionalProperties": false
+      }
+    }
+  },
+  "$defs": {
+    "fingerprint": {
+      "type": "string",
+      "pattern": "^[0-9a-f]{64}$"
+    },
+    "fingerprintMap": {
+      "type": "object",
+      "additionalProperties": {"$ref": "#/$defs/fingerprint"}
+    },
+    "campaignPlan": {
+      "type": "object",
+      "required": [
+        "ledger",
+        "approved_cumulative_model_sessions",
+        "consumed_before",
+        "reserved_before",
+        "planned_maximum",
+        "projected_maximum"
+      ],
+      "properties": {
+        "ledger": {"type": ["string", "null"]},
+        "approved_cumulative_model_sessions": {"type": ["integer", "null"], "minimum": 0},
+        "consumed_before": {"type": "integer", "minimum": 0},
+        "reserved_before": {"type": "integer", "minimum": 0},
+        "planned_maximum": {"type": "integer", "minimum": 0},
+        "projected_maximum": {"type": "integer", "minimum": 0}
+      },
+      "additionalProperties": false
+    },
+    "executionCount": {
+      "type": "object",
+      "required": ["total"],
+      "properties": {
+        "affected": {"type": "integer", "minimum": 0},
+        "regression": {"type": "integer", "minimum": 0},
+        "total": {"type": "integer", "minimum": 0}
+      },
+      "additionalProperties": false
+    },
+    "economicRuntime": {
+      "type": "object",
+      "required": [
+        "policy_version",
+        "mode",
+        "executor",
+        "judge",
+        "reasons"
+      ],
+      "properties": {
+        "policy_version": {"const": 2},
+        "mode": {
+          "enum": [
+            "zero-session",
+            "scoped-complete-oracle",
+            "manual-selection"
+          ]
+        },
+        "executor": {"$ref": "#/$defs/economicRuntimeRole"},
+        "judge": {"$ref": "#/$defs/economicRuntimeRole"},
+        "reasons": {
+          "type": "array",
+          "items": {"type": "string"},
+          "minItems": 1
+        }
+      },
+      "additionalProperties": false
+    },
+    "economicRuntimeRole": {
+      "type": "object",
+      "required": [
+        "recommended_model",
+        "recommended_reasoning_effort",
+        "matches_explicit_runtime"
+      ],
+      "properties": {
+        "recommended_model": {"type": ["string", "null"]},
+        "recommended_reasoning_effort": {"type": ["string", "null"]},
+        "matches_explicit_runtime": {"type": ["boolean", "null"]}
+      },
+      "additionalProperties": false
+    },
+    "sessionCount": {
+      "type": "object",
+      "required": ["executor", "judge", "total"],
+      "properties": {
+        "executor": {"type": "integer", "minimum": 0},
+        "judge": {"type": "integer", "minimum": 0},
+        "total": {"type": "integer", "minimum": 0}
+      },
+      "additionalProperties": false
+    },
+    "runtime": {
+      "type": "object",
+      "required": ["required", "complete", "audit_quality", "executor", "judge"],
+      "properties": {
+        "required": {"type": "boolean"},
+        "complete": {"type": "boolean"},
+        "audit_quality": {
+          "enum": ["promotion", "exploratory", "not_applicable"]
+        },
+        "executor": {"$ref": "#/$defs/roleRuntime"},
+        "judge": {"$ref": "#/$defs/roleRuntime"}
+      },
+      "additionalProperties": false
+    },
+    "roleRuntime": {
+      "type": "object",
+      "required": [
+        "required",
+        "model",
+        "model_source",
+        "reasoning_effort",
+        "reasoning_effort_source"
+      ],
+      "properties": {
+        "required": {"type": "boolean"},
+        "model": {"type": ["string", "null"]},
+        "model_source": {
+          "enum": ["cli", "environment", "configured-default", "executor"]
+        },
+        "reasoning_effort": {"type": ["string", "null"]},
+        "reasoning_effort_source": {
+          "enum": ["cli", "configured-default", "executor"]
+        }
+      },
+      "additionalProperties": false
+    }
+  },
+  "additionalProperties": false
+}
--- /dev/null
+++ b/baseline/references/eval-report.schema.json
@@ -0,0 +1,196 @@
+{
+  "$schema": "https://json-schema.org/draft/2020-12/schema",
+  "$id": "https://openai.com/codex/skills/eval-report.schema.json",
+  "title": "Canonical skill evaluation evidence report",
+  "type": "object",
+  "required": [
+    "schema_version",
+    "operation",
+    "provenance",
+    "started_at",
+    "finished_at",
+    "duration_ms",
+    "skill",
+    "fingerprints",
+    "environment",
+    "billing",
+    "runtime",
+    "sessions",
+    "usage",
+    "pricing",
+    "api_reference_estimate",
+    "observations",
+    "limitations",
+    "report_digest"
+  ],
+  "properties": {
+    "schema_version": {
+      "const": 1
+    },
+    "operation": {
+      "type": "object",
+      "required": [
+        "id",
+        "type",
+        "status",
+        "workflow",
+        "promotion_eligible",
+        "failure_category"
+      ],
+      "properties": {
+        "id": {
+          "type": "string",
+          "minLength": 1
+        },
+        "type": {
+          "enum": [
+            "run",
+            "verify-change",
+            "stability",
+            "probe-change",
+            "validate-change"
+          ]
+        },
+        "status": {
+          "enum": [
+            "PASS",
+            "FAIL",
+            "ERROR",
+            "INCONCLUSIVE",
+            "INVALID_RED",
+            "UNSTABLE"
+          ]
+        },
+        "workflow": {
+          "enum": [
+            "diagnostic",
+            "promotion",
+            null
+          ]
+        },
+        "promotion_eligible": {
+          "type": "boolean"
+        },
+        "failure_category": {
+          "enum": [
+            "contract",
+            "infrastructure",
+            null
+          ]
+        }
+      },
+      "additionalProperties": false
+    },
+    "provenance": {
+      "const": "executed"
+    },
+    "started_at": {
+      "type": "string"
+    },
+    "finished_at": {
+      "type": "string"
+    },
+    "duration_ms": {
+      "type": "integer",
+      "minimum": 0
+    },
+    "skill": {
+      "type": "object",
+      "required": [
+        "path",
+        "name"
+      ],
+      "properties": {
+        "path": {
+          "type": "string"
+        },
+        "name": {
+          "type": "string",
+          "minLength": 1
+        }
+      },
+      "additionalProperties": false
+    },
+    "fingerprints": {
+      "type": "object"
+    },
+    "environment": {
+      "type": "object"
+    },
+    "billing": {
+      "type": "object",
+      "required": [
+        "mode",
+        "actual_charge_observed"
+      ],
+      "properties": {
+        "mode": {
+          "type": "string"
+        },
+        "actual_charge_observed": {
+          "const": false
+        }
+      },
+      "additionalProperties": true
+    },
+    "runtime": {
+      "type": "object"
+    },
+    "sessions": {
+      "type": "object",
+      "required": [
+        "planned",
+        "executed",
+        "provenance"
+      ]
+    },
+    "usage": {
+      "type": "object"
+    },
+    "pricing": {
+      "type": "object"
+    },
+    "api_reference_estimate": {
+      "type": "object",
+      "required": [
+        "actual_charge"
+      ],
+      "properties": {
+        "actual_charge": {
+          "const": false
+        }
+      },
+      "additionalProperties": true
+    },
+    "observations": {
+      "type": "array",
+      "items": {
+        "type": "object"
+      }
+    },
+    "limitations": {
+      "type": "array",
+      "items": {
+        "type": "string"
+      }
+    },
+    "report_digest": {
+      "type": "object",
+      "required": [
+        "algorithm",
+        "value"
+      ],
+      "properties": {
+        "algorithm": {
+          "const": "sha256"
+        },
+        "value": {
+          "type": "string",
+          "pattern": "^[0-9a-f]{64}$"
+        }
+      },
+      "additionalProperties": false
+    }
+  },
+  "additionalProperties": false
+}
--- /dev/null
+++ b/baseline/references/eval-result.schema.json
@@ -0,0 +1,226 @@
+{
+  "$schema": "https://json-schema.org/draft/2020-12/schema",
+  "title": "Skill evaluation result",
+  "type": "object",
+  "required": [
+    "operation",
+    "status",
+    "skill",
+    "model",
+    "runtime",
+    "model_sessions",
+    "usage",
+    "promotion_eligible",
+    "failure_category",
+    "campaign",
+    "results"
+  ],
+  "properties": {
+    "operation": {"enum": ["run", "verify-change", "stability", "probe-change", "validate-change"]},
+    "status": {
+      "enum": ["PASS", "FAIL", "ERROR", "INCONCLUSIVE", "INVALID_RED", "UNSTABLE"]
+    },
+    "skill": {"type": "string"},
+    "model": {"type": "string"},
+    "runtime": {"$ref": "#/$defs/runtime"},
+    "model_sessions": {"$ref": "#/$defs/modelSessions"},
+    "usage": {"$ref": "#/$defs/usage"},
+    "promotion_eligible": {"type": "boolean"},
+    "failure_category": {"enum": ["contract", "infrastructure", null]},
+    "campaign": {
+      "oneOf": [
+        {"type": "null"},
+        {"$ref": "#/$defs/campaignResult"}
+      ]
+    },
+    "results": {
+      "type": "array",
+      "items": {
+        "type": "object",
+        "properties": {
+          "case_id": {"type": "string"},
+          "status": {
+            "enum": ["PASS", "FAIL", "ERROR", "INCONCLUSIVE", "INVALID_RED", "UNSTABLE"]
+          },
+          "kind": {
+            "enum": ["behavioral", "non_behavioral", "trigger", "deterministic"]
+          },
+          "executor": {
+            "type": "object",
+            "required": ["enabled", "executed", "exit_code", "response", "stderr", "usage"],
+            "properties": {
+              "enabled": {"type": "boolean"},
+              "executed": {"type": "boolean"},
+              "exit_code": {"type": ["integer", "null"]},
+              "response": {"type": ["object", "null"]},
+              "stderr": {"type": "string"},
+              "usage": {"$ref": "#/$defs/usage"}
+            },
+            "additionalProperties": true
+          },
+          "judge": {
+            "type": "object",
+            "required": ["enabled", "executed", "verdict", "rationale", "evidence", "usage"],
+            "properties": {
+              "enabled": {"type": "boolean"},
+              "executed": {"type": "boolean"},
+              "verdict": {"enum": ["PASS", "FAIL", "INCONCLUSIVE", "SKIPPED"]},
+              "rationale": {"type": "string"},
+              "evidence": {
+                "type": "array",
+                "items": {"type": "string"}
+              },
+              "usage": {"$ref": "#/$defs/usage"}
+            },
+            "additionalProperties": true
+          },
+          "model_sessions": {"$ref": "#/$defs/modelSessions"},
+          "usage": {"$ref": "#/$defs/usage"},
+          "failure_category": {"enum": ["contract", "infrastructure", null]},
+          "oracle": {
+            "type": "object",
+            "required": ["enabled", "passed", "commands"],
+            "properties": {
+              "enabled": {"type": "boolean"},
+              "passed": {"type": "boolean"},
+              "commands": {"type": "array", "items": {"type": "object"}}
+            },
+            "additionalProperties": false
+          }
+        },
+        "additionalProperties": true
+      }
+    },
+    "plan": {"type": "object"},
+    "artifacts": {"type": ["string", "null"]}
+  },
+  "$defs": {
+    "usage": {
+      "type": "object",
+      "required": [
+        "input_tokens",
+        "cached_input_tokens",
+        "output_tokens",
+        "reasoning_output_tokens",
+        "total_tokens",
+        "complete",
+        "reasoning_output_tokens_complete",
+        "events",
+        "event_count",
+        "events_complete"
+      ],
+      "properties": {
+        "input_tokens": {"type": ["integer", "null"], "minimum": 0},
+        "cached_input_tokens": {"type": ["integer", "null"], "minimum": 0},
+        "output_tokens": {"type": ["integer", "null"], "minimum": 0},
+        "reasoning_output_tokens": {"type": ["integer", "null"], "minimum": 0},
+        "total_tokens": {"type": ["integer", "null"], "minimum": 0},
+        "complete": {"type": "boolean"},
+        "reasoning_output_tokens_complete": {"type": "boolean"},
+        "events": {
+          "type": "array",
+          "items": {
+            "type": "object",
+            "required": [
+              "sequence",
+              "source_event_type",
+              "scope",
+              "input_tokens",
+              "cached_input_tokens",
+              "output_tokens",
+              "reasoning_output_tokens",
+              "total_tokens",
+              "complete",
+              "reasoning_output_tokens_complete"
+            ],
+            "properties": {
+              "sequence": {"type": "integer", "minimum": 1},
+              "source_event_type": {"type": "string"},
+              "scope": {"enum": ["turn", "unknown"]},
+              "input_tokens": {"type": ["integer", "null"], "minimum": 0},
+              "cached_input_tokens": {"type": ["integer", "null"], "minimum": 0},
+              "output_tokens": {"type": ["integer", "null"], "minimum": 0},
+              "reasoning_output_tokens": {"type": ["integer", "null"], "minimum": 0},
+              "total_tokens": {"type": ["integer", "null"], "minimum": 0},
+              "complete": {"type": "boolean"},
+              "reasoning_output_tokens_complete": {"type": "boolean"}
+            },
+            "additionalProperties": false
+          }
+        },
+        "event_count": {"type": "integer", "minimum": 0},
+        "events_complete": {"type": "boolean"}
+      },
+      "additionalProperties": false
+    },
+    "campaignResult": {
+      "type": "object",
+      "required": [
+        "ledger",
+        "approved_cumulative_model_sessions",
+        "consumed_before",
+        "planned_maximum",
+        "consumed_operation",
+        "consumed_after"
+      ],
+      "properties": {
+        "ledger": {"type": ["string", "null"]},
+        "approved_cumulative_model_sessions": {"type": ["integer", "null"], "minimum": 0},
+        "consumed_before": {"type": "integer", "minimum": 0},
+        "reserved_before": {"type": "integer", "minimum": 0},
+        "planned_maximum": {"type": "integer", "minimum": 0},
+        "projected_maximum": {"type": "integer", "minimum": 0},
+        "consumed_operation": {"type": "integer", "minimum": 0},
+        "consumed_after": {"type": ["integer", "null"], "minimum": 0}
+      },
+      "additionalProperties": false
+    },
+    "modelSessions": {
+      "type": "object",
+      "required": ["executor", "judge", "total"],
+      "properties": {
+        "executor": {"type": "integer", "minimum": 0},
+        "judge": {"type": "integer", "minimum": 0},
+        "total": {"type": "integer", "minimum": 0}
+      },
+      "additionalProperties": false
+    },
+    "runtime": {
+      "type": "object",
+      "required": ["required", "complete", "audit_quality", "executor", "judge"],
+      "properties": {
+        "required": {"type": "boolean"},
+        "complete": {"type": "boolean"},
+        "audit_quality": {
+          "enum": ["promotion", "exploratory", "not_applicable"]
+        },
+        "executor": {"$ref": "#/$defs/roleRuntime"},
+        "judge": {"$ref": "#/$defs/roleRuntime"}
+      },
+      "additionalProperties": false
+    },
+    "roleRuntime": {
+      "type": "object",
+      "required": [
+        "required",
+        "model",
+        "model_source",
+        "reasoning_effort",
+        "reasoning_effort_source"
+      ],
+      "properties": {
+        "required": {"type": "boolean"},
+        "model": {"type": ["string", "null"]},
+        "model_source": {
+          "enum": ["cli", "environment", "configured-default", "executor"]
+        },
+        "reasoning_effort": {"type": ["string", "null"]},
+        "reasoning_effort_source": {
+          "enum": ["cli", "configured-default", "executor"]
+        }
+      },
+      "additionalProperties": false
+    }
+  },
+  "additionalProperties": true
+}
--- /dev/null
+++ b/baseline/scripts/archive_config.py
@@ -0,0 +1,52 @@
+#!/usr/bin/env python3
+"""Load and validate repository evaluation archive configuration."""
+
+import json
+from pathlib import Path
+from typing import Any
+
+from eval_report import load_pricing
+
+
+ARCHIVE_CONFIG_NAME = "archive-config.json"
+
+
+def load_archive_config(path: Path) -> dict[str, Any]:
+  with path.open(encoding="utf-8") as stream:
+    config = json.load(stream)
+  if not isinstance(config, dict) or config.get("version") != 1:
+    raise ValueError("Archive config version must be 1")
+  pricing_file = config.get("pricing_file")
+  if pricing_file is not None and not isinstance(pricing_file, str):
+    raise ValueError("Archive config pricing_file must be a relative path")
+  comparisons = config.get("comparisons", [])
+  if not isinstance(comparisons, list):
+    raise ValueError("Archive config comparisons must be an array")
+  for comparison in comparisons:
+    if (
+      not isinstance(comparison, dict)
+      or not isinstance(comparison.get("skill"), str)
+      or not isinstance(comparison.get("id"), str)
+      or not isinstance(comparison.get("operation_ids"), list)
+      or not all(
+        isinstance(operation_id, str)
+        for operation_id in comparison["operation_ids"]
+      )
+    ):
+      raise ValueError("Every comparison requires skill, id, and operation_ids")
+    if len(set(comparison["operation_ids"])) != len(comparison["operation_ids"]):
+      raise ValueError(f"Comparison {comparison['id']} contains duplicate ids")
+  return config
+
+
+def configured_pricing_path(config_path: Path, config: dict[str, Any]) -> Path | None:
+  relative = config.get("pricing_file")
+  if relative is None:
+    return None
+  candidate = (config_path.parent / relative).resolve()
+  try:
+    candidate.relative_to(config_path.parent.resolve())
+  except ValueError as error:
+    raise ValueError("Archive pricing_file must remain inside the archive") from error
+  load_pricing(candidate)
+  return candidate
--- /dev/null
+++ b/baseline/scripts/compare_model_reports.py
@@ -0,0 +1,327 @@
+#!/usr/bin/env python3
+"""Compare canonical skill evaluation evidence reports by executor model."""
+
+import argparse
+from collections import defaultdict
+import json
+from pathlib import Path
+import statistics
+from typing import Any
+
+from eval_report import api_reference_estimate, atomic_write_text, load_report
+
+
+TOKEN_FIELDS = (
+  "input_tokens",
+  "cached_input_tokens",
+  "output_tokens",
+  "reasoning_output_tokens",
+)
+
+
+def compare_reports(reports_root: Path) -> dict[str, Any]:
+  report_paths = sorted(reports_root.rglob("report.json"))
+  return compare_report_paths(report_paths)
+
+
+def compare_report_paths(report_paths: list[Path]) -> dict[str, Any]:
+  observations: list[dict[str, Any]] = []
+  operation_ids: set[str] = set()
+  skill_names: set[str] = set()
+  for path in report_paths:
+    report = load_report(path)
+    operation_id = report["operation"]["id"]
+    if operation_id in operation_ids:
+      raise ValueError(f"Duplicate operation id: {operation_id}")
+    operation_ids.add(operation_id)
+    skill_names.add(report["skill"]["name"])
+    model = report["runtime"]["executor"]["model"] or "configured-default"
+    for observation in report["observations"]:
+      observations.append({
+        **observation,
+        "_model": model,
+        "_estimate": _observation_estimate(report, observation),
+        "_operation_id": operation_id,
+      })
+  if len(skill_names) > 1:
+    raise ValueError(
+      "Reports from different skills cannot be compared together: "
+      + ", ".join(sorted(skill_names))
+    )
+
+  grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
+  for observation in observations:
+    grouped[observation["_model"]].append(observation)
+  models = [
+    _model_summary(model, grouped[model])
+    for model in sorted(grouped)
+  ]
+  return {
+    "version": 1,
+    "report_count": len(report_paths),
+    "observation_count": len(observations),
+    "executed_observation_count": sum(
+      observation.get("provenance") == "executed"
+      for observation in observations
+    ),
+    "models": models,
+    "directional_pilot": True,
+    "limitations": [
+      "The comparison is directional and is not statistical proof.",
+      "API reference estimates are not observed ChatGPT charges.",
+      "A model qualifies only with at least three stable PASS observations in every represented case.",
+    ],
+  }
+
+
+def render_comparison(comparison: dict[str, Any]) -> str:
+  lines = [
+    "# Model evaluation comparison",
+    "",
+    f"- Reports: `{comparison['report_count']}`",
+    f"- Observations: `{comparison['observation_count']}`",
+    f"- Executed observations: `{comparison['executed_observation_count']}`",
+    "- Interpretation: directional pilot, not statistical proof.",
+    "",
+    "| Model | PASS | Observations | Qualifies | Input tokens | Output tokens | Reasoning output | Duration ms | API reference |",
+    "| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: |",
+  ]
+  for model in comparison["models"]:
+    lines.append(
+      "| "
+      + " | ".join([
+        model["model"],
+        str(model["pass_count"]),
+        str(model["observation_count"]),
+        "yes" if model["qualifies"] else "no",
+        str(model["tokens"]["input"]["total"]),
+        str(model["tokens"]["output"]["total"]),
+        str(model["tokens"]["reasoning_output"]["total"]),
+        str(model["duration_ms"]["total"]),
+        _display(model["api_reference_cost"]["total"]),
+      ])
+      + " |"
+    )
+    lines.extend(["", f"## {model['model']}", ""])
+    for case in model["cases"]:
+      lines.append(
+        f"- `{case['case_id']}`: {case['pass_count']}/{case['observation_count']} PASS, "
+        f"stable `{str(case['stable']).lower()}`"
+      )
+    lines.append(
+      f"- Explanation complete ratio: `{model['explanation']['complete_ratio']}`"
+    )
+    lines.append(
+      f"- Explanation coherent ratio: `{model['explanation']['coherent_ratio']}`"
+    )
+    lines.append(
+      f"- Base-rate API reference: "
+      f"`{_display(model['api_reference_cost']['base_rate_total'])}`"
+    )
+    lines.append(
+      f"- Long context indeterminate observations: "
+      f"`{model['api_reference_cost']['indeterminate_long_context_count']}`"
+    )
+  lines.append("")
+  return "\n".join(lines)
+
+
+def _model_summary(model: str, observations: list[dict[str, Any]]) -> dict[str, Any]:
+  by_case: dict[str, list[dict[str, Any]]] = defaultdict(list)
+  for observation in observations:
+    by_case[observation["case_id"]].append(observation)
+  cases = []
+  for case_id in sorted(by_case):
+    case_observations = by_case[case_id]
+    signatures = {_signature(item) for item in case_observations}
+    cases.append({
+      "case_id": case_id,
+      "observation_count": len(case_observations),
+      "pass_count": sum(item["status"] == "PASS" for item in case_observations),
+      "stable": len(signatures) == 1,
+      "signature_count": len(signatures),
+    })
+  token_summary = {}
+  for field, label in (
+    ("input_tokens", "input"),
+    ("cached_input_tokens", "cached_input"),
+    ("output_tokens", "output"),
+    ("reasoning_output_tokens", "reasoning_output"),
+  ):
+    values = [
+      item["usage"].get(field)
+      for item in observations
+      if isinstance(item["usage"].get(field), int)
+    ]
+    token_summary[label] = _numeric_summary(values, len(observations))
+  input_total = token_summary["input"]["total"]
+  cached_total = token_summary["cached_input"]["total"]
+  cache_ratio = (
+    round(cached_total / input_total, 6)
+    if input_total
+    else None
+  )
+  durations = [
+    item["duration_ms"]
+    for item in observations
+    if isinstance(item.get("duration_ms"), int)
+  ]
+  estimates = [
+    item["_estimate"]["amount"]
+    for item in observations
+    if item["_estimate"]["available"]
+  ]
+  base_rate_estimates = [
+    item["_estimate"]["base_rate_amount"]
+    for item in observations
+    if isinstance(item["_estimate"].get("base_rate_amount"), (int, float))
+  ]
+  stable_valid_gates = sum(
+    case["observation_count"]
+    for case in cases
+    if case["stable"] and case["pass_count"] == case["observation_count"]
+  )
+  estimates_complete = len(estimates) == len(observations)
+  estimate_total = (
+    round(sum(estimates), 12)
+    if estimates_complete and estimates
+    else None
+  )
+  base_rate_total = (
+    round(sum(base_rate_estimates), 12)
+    if len(base_rate_estimates) == len(observations) and base_rate_estimates
+    else None
+  )
+  complete = [_explanation_complete(item) for item in observations]
+  coherent = [_explanation_coherent(item) for item in observations]
+  return {
+    "model": model,
+    "observation_count": len(observations),
+    "pass_count": sum(item["status"] == "PASS" for item in observations),
+    "cases": cases,
+    "qualifies": bool(cases) and all(
+      case["observation_count"] >= 3
+      and case["pass_count"] == case["observation_count"]
+      and case["stable"]
+      for case in cases
+    ),
+    "tokens": token_summary,
+    "cache_ratio": cache_ratio,
+    "duration_ms": _numeric_summary(durations, len(observations)),
+    "api_reference_cost": {
+      "total": estimate_total,
+      "complete": estimates_complete,
+      "base_rate_total": base_rate_total,
+      "indeterminate_long_context_count": sum(
+        item["_estimate"].get("status") == "indeterminate-long-context"
+        for item in observations
+      ),
+      "effective_per_stable_gate": (
+        round(estimate_total / stable_valid_gates, 12)
+        if estimate_total is not None and stable_valid_gates
+        else None
+      ),
+      "base_rate_per_stable_gate": (
+        round(base_rate_total / stable_valid_gates, 12)
+        if base_rate_total is not None and stable_valid_gates
+        else None
+      ),
+      "actual_charge": False,
+    },
+    "explanation": {
+      "complete_count": sum(complete),
+      "complete_ratio": round(sum(complete) / len(complete), 6) if complete else None,
+      "coherent_count": sum(coherent),
+      "coherent_ratio": round(sum(coherent) / len(coherent), 6) if coherent else None,
+    },
+  }
+
+
+def _numeric_summary(values: list[int], expected: int) -> dict[str, Any]:
+  return {
+    "total": sum(values),
+    "median": statistics.median(values) if values else None,
+    "complete": len(values) == expected,
+  }
+
+
+def _signature(observation: dict[str, Any]) -> str:
+  value = {
+    "status": observation["status"],
+    "mechanical": [
+      [check["name"], check["passed"]]
+      for check in observation["mechanical"].get("checks", [])
+    ],
+    "oracle": observation["oracle"].get("passed"),
+    "judge": observation["judge"].get("verdict"),
+    "changed_files": observation["evidence"].get("changed_files", []),
+  }
+  return json.dumps(value, sort_keys=True, separators=(",", ":"))
+
+
+def _explanation_complete(observation: dict[str, Any]) -> bool:
+  response = observation["executor"].get("response")
+  if not isinstance(response, dict):
+    return False
+  return (
+    isinstance(response.get("diagnosis"), str)
+    and all(
+      isinstance(response.get(field), list)
+      for field in (
+        "approach",
+        "decisions",
+        "rejected_alternatives",
+        "key_changes",
+        "validation",
+      )
+    )
+  )
+
+
+def _explanation_coherent(observation: dict[str, Any]) -> bool:
+  response = observation["executor"].get("response")
+  if not _explanation_complete(observation):
+    return False
+  declared = set(response.get("files_changed", []))
+  changed = set(observation["evidence"].get("changed_files", []))
+  return declared.issubset(changed) and bool(response.get("validation"))
+
+
+def _observation_estimate(
+  report: dict[str, Any],
+  observation: dict[str, Any],
+) -> dict[str, Any]:
+  pricing = report.get("pricing", {})
+  model = report["runtime"]["executor"]["model"]
+  return api_reference_estimate(
+    pricing,
+    observation.get("usage", {}),
+    model,
+    report.get("billing", {}).get("mode", "unknown"),
+  )
+
+
+def _display(value: Any) -> str:
+  return "unavailable" if value is None else str(value)
+
+
+def main() -> int:
+  parser = argparse.ArgumentParser(description=__doc__)
+  parser.add_argument("--reports", type=Path, required=True)
+  parser.add_argument("--output-dir", type=Path, required=True)
+  args = parser.parse_args()
+  comparison = compare_reports(args.reports)
+  args.output_dir.mkdir(parents=True, exist_ok=True)
+  atomic_write_text(
+    args.output_dir / "comparison.json",
+    json.dumps(comparison, indent=2, ensure_ascii=False) + "\n",
+  )
+  atomic_write_text(
+    args.output_dir / "comparison.md",
+    render_comparison(comparison),
+  )
+  return 0
+
+
+if __name__ == "__main__":
+  raise SystemExit(main())
--- /dev/null
+++ b/baseline/scripts/eval_report.py
@@ -0,0 +1,543 @@
+#!/usr/bin/env python3
+"""Deterministic helpers for durable skill evaluation evidence."""
+
+from __future__ import annotations
+
+import difflib
+import hashlib
+import json
+import os
+from pathlib import Path
+import re
+import subprocess
+import tempfile
+from typing import Any
+
+
+MAX_CAPTURE_BYTES = 32768
+MAX_DIFF_BYTES_PER_FILE = 12000
+MAX_DIFF_BYTES_PER_REPORT = 64000
+MAX_FRAGMENT_BYTES = 2000
+MAX_FACT_TEXT = 4000
+SECRET_PATTERNS = (
+  re.compile(r"\b(sk-[A-Za-z0-9_-]{8,})"),
+  re.compile(r"(?i)\b(bearer)\s+[A-Za-z0-9._~+/=-]{8,}"),
+  re.compile(
+    r"(?i)\b(api[_-]?key|access[_-]?token|auth[_-]?token|password|secret)"
+    r"(\s*[:=]\s*)"
+    r"([^\s,'\"}]+)"
+  ),
+)
+REPORT_SCHEMA_VERSION = 1
+
+
+def canonical_json(value: Any) -> str:
+  return json.dumps(
+    value,
+    sort_keys=True,
+    separators=(",", ":"),
+    ensure_ascii=False,
+  )
+
+
+def sha256_bytes(value: bytes) -> str:
+  return hashlib.sha256(value).hexdigest()
+
+
+def report_digest(report: dict[str, Any]) -> str:
+  payload = dict(report)
+  payload.pop("report_digest", None)
+  return sha256_bytes(canonical_json(payload).encode("utf-8"))
+
+
+def validate_report(report: dict[str, Any], source: str = "report") -> None:
+  required = {
+    "schema_version",
+    "operation",
+    "provenance",
+    "started_at",
+    "finished_at",
+    "duration_ms",
+    "skill",
+    "fingerprints",
+    "environment",
+    "billing",
+    "runtime",
+    "sessions",
+    "usage",
+    "pricing",
+    "api_reference_estimate",
+    "observations",
+    "limitations",
+    "report_digest",
+  }
+  missing = sorted(required - report.keys())
+  if missing:
+    raise ValueError(f"{source} is missing report fields: {', '.join(missing)}")
+  if report.get("schema_version") != REPORT_SCHEMA_VERSION:
+    raise ValueError(
+      f"{source} uses unsupported report schema version "
+      f"{report.get('schema_version')!r}"
+    )
+  operation = report.get("operation")
+  if not isinstance(operation, dict) or not isinstance(operation.get("id"), str):
+    raise ValueError(f"{source} has no valid operation id")
+  skill = report.get("skill")
+  if not isinstance(skill, dict) or not isinstance(skill.get("name"), str):
+    raise ValueError(f"{source} has no valid skill name")
+  if report.get("provenance") != "executed":
+    raise ValueError(f"{source} has unsupported provenance")
+  if not isinstance(report.get("observations"), list):
+    raise ValueError(f"{source} observations must be an array")
+  if report.get("billing", {}).get("actual_charge_observed") is not False:
+    raise ValueError(f"{source} must record actual_charge_observed as false")
+  if report.get("api_reference_estimate", {}).get("actual_charge") is not False:
+    raise ValueError(f"{source} must record actual_charge as false")
+  digest = report.get("report_digest")
+  if not isinstance(digest, dict) or digest.get("algorithm") != "sha256":
+    raise ValueError(f"{source} has no valid SHA-256 report digest")
+  expected = report_digest(report)
+  if digest.get("value") != expected:
+    raise ValueError(
+      f"{source} report digest mismatch: expected {expected}, "
+      f"found {digest.get('value')}"
+    )
+
+
+def load_report(path: Path) -> dict[str, Any]:
+  with path.open(encoding="utf-8") as stream:
+    report = json.load(stream)
+  if not isinstance(report, dict):
+    raise ValueError(f"Report must contain a JSON object: {path}")
+  validate_report(report, str(path))
+  return report
+
+
+def atomic_write_text(path: Path, value: str) -> None:
+  path.parent.mkdir(parents=True, exist_ok=True)
+  descriptor, temporary_name = tempfile.mkstemp(
+    prefix=f".{path.name}.",
+    dir=path.parent,
+  )
+  temporary = Path(temporary_name)
+  try:
+    with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
+      stream.write(value)
+      stream.flush()
+      os.fsync(stream.fileno())
+    os.replace(temporary, path)
+  finally:
+    if temporary.exists():
+      temporary.unlink()
+
+
+def evidence_path_allowed(relative_path: str) -> bool:
+  path = Path(relative_path)
+  parts = path.parts
+  if ".git" in parts or "__pycache__" in parts:
+    return False
+  if len(parts) >= 2 and parts[0] == ".agents" and parts[1] == "skills":
+    return False
+  if any(part.startswith(".eval-") for part in parts) or path.suffix == ".pyc":
+    return False
+  return True
+
+
+def capture_evidence_snapshot(root: Path) -> dict[str, dict[str, Any]]:
+  captured: dict[str, dict[str, Any]] = {}
+  for path in sorted(root.rglob("*")):
+    if not path.is_file():
+      continue
+    relative = path.relative_to(root).as_posix()
+    if not evidence_path_allowed(relative):
+      continue
+    size = path.stat().st_size
+    with path.open("rb") as stream:
+      content = stream.read(MAX_CAPTURE_BYTES + 1)
+    captured[relative] = {
+      "sha256": _file_hash(path),
+      "size": size,
+      "content": content[:MAX_CAPTURE_BYTES],
+      "capture_truncated": len(content) > MAX_CAPTURE_BYTES,
+    }
+  return captured
+
+
+def build_file_evidence(
+  before: dict[str, dict[str, Any]],
+  after: dict[str, dict[str, Any]],
+) -> dict[str, Any]:
+  changed_files = sorted(
+    path
+    for path in before.keys() | after.keys()
+    if before.get(path, {}).get("sha256") != after.get(path, {}).get("sha256")
+  )
+  diff_parts: list[str] = []
+  fragments: list[dict[str, Any]] = []
+  truncations: list[dict[str, str]] = []
+  report_bytes = 0
+
+  for relative in changed_files:
+    old = before.get(relative)
+    new = after.get(relative)
+    old_text = _decode_text(old)
+    new_text = _decode_text(new)
+    fragment = {
+      "path": relative,
+      "before_sha256": old["sha256"] if old else None,
+      "after_sha256": new["sha256"] if new else None,
+      "before_size": old["size"] if old else None,
+      "after_size": new["size"] if new else None,
+      "before": _limited_fragment(old_text),
+      "after": _limited_fragment(new_text),
+      "binary": (
+        (old is not None and old_text is None)
+        or (new is not None and new_text is None)
+      ),
+    }
+    fragments.append(fragment)
+    if (old and old["capture_truncated"]) or (new and new["capture_truncated"]):
+      truncations.append({"path": relative, "reason": "file capture limit"})
+
+    if fr
```

Truncations:
- `baseline/SKILL.md`: per file diff limit
- `baseline/references/eval-contract.md`: per file diff limit
- `baseline/scripts/eval_report.py`: per file diff limit
- `baseline/scripts/eval_report.py`: report diff limit
- `baseline/scripts/evaluation_archive.py`: report diff limit
- `baseline/scripts/manage_evaluation_archive.py`: report diff limit
- `baseline/scripts/render_eval_report.py`: report diff limit
- `baseline/scripts/run_skill_evals.py`: file capture limit
- `baseline/scripts/run_skill_evals.py`: per file diff limit
- `baseline/scripts/run_skill_evals.py`: report diff limit
- `baseline/scripts/tests/__init__.py`: report diff limit
- `baseline/scripts/tests/test_cost_efficient_workflow.py`: per file diff limit
- `baseline/scripts/tests/test_cost_efficient_workflow.py`: report diff limit
- `baseline/scripts/tests/test_economic_runtime_guidance.py`: report diff limit
- `baseline/scripts/tests/test_evaluation_archive.py`: per file diff limit
- `baseline/scripts/tests/test_evaluation_archive.py`: report diff limit
- `baseline/scripts/tests/test_execution_evidence_report.py`: per file diff limit
- `baseline/scripts/tests/test_execution_evidence_report.py`: report diff limit
- `baseline/scripts/tests/test_load_skill_creator_contract.py`: report diff limit
- `baseline/scripts/tests/test_run_skill_evals.py`: file capture limit
- `baseline/scripts/tests/test_run_skill_evals.py`: per file diff limit
- `baseline/scripts/tests/test_run_skill_evals.py`: report diff limit
- `candidate/SKILL.md`: per file diff limit
- `candidate/SKILL.md`: report diff limit
- `candidate/agents/openai.yaml`: report diff limit
- `candidate/references/eval-contract.md`: per file diff limit
- `candidate/references/eval-contract.md`: report diff limit
- `candidate/references/eval-plan.schema.json`: report diff limit
- `candidate/references/eval-report.schema.json`: report diff limit
- `candidate/references/eval-result.schema.json`: report diff limit
- `candidate/scripts/archive_config.py`: report diff limit
- `candidate/scripts/compare_model_reports.py`: report diff limit
- `candidate/scripts/eval_report.py`: per file diff limit
- `candidate/scripts/eval_report.py`: report diff limit
- `candidate/scripts/evaluation_archive.py`: report diff limit
- `candidate/scripts/manage_evaluation_archive.py`: report diff limit
- `candidate/scripts/render_eval_report.py`: report diff limit
- `candidate/scripts/run_skill_evals.py`: file capture limit
- `candidate/scripts/run_skill_evals.py`: per file diff limit
- `candidate/scripts/run_skill_evals.py`: report diff limit
- `candidate/scripts/tests/__init__.py`: report diff limit
- `candidate/scripts/tests/test_cost_efficient_workflow.py`: per file diff limit
- `candidate/scripts/tests/test_cost_efficient_workflow.py`: report diff limit
- `candidate/scripts/tests/test_economic_runtime_guidance.py`: report diff limit
- `candidate/scripts/tests/test_evaluation_archive.py`: per file diff limit
- `candidate/scripts/tests/test_evaluation_archive.py`: report diff limit
- `candidate/scripts/tests/test_execution_evidence_report.py`: per file diff limit
- `candidate/scripts/tests/test_execution_evidence_report.py`: report diff limit
- `candidate/scripts/tests/test_load_skill_creator_contract.py`: report diff limit
- `candidate/scripts/tests/test_run_skill_evals.py`: file capture limit
- `candidate/scripts/tests/test_run_skill_evals.py`: per file diff limit
- `candidate/scripts/tests/test_run_skill_evals.py`: report diff limit

## Observation 9: self-evolution-oracle-contract

- Status: `PASS`
- Role: `regression`
- Repetition: `1`
- Duration: `252 ms`
- Workspace retention: `retained`
- Tokens: input `unknown`, cached input `unknown`, output `unknown`, reasoning output `unknown`
- Normalized usage events: `0`, complete `false`, scopes `none`

### Executor account

Executor did not provide a structured response.

### Mechanical facts

- Mechanical result: `PASS`
- Oracle result: `PASS`
- Judge verdict: `PASS`
- `command: python3 check_self_evolution_oracle.py`: `PASS`
- `evaluated skill remained unchanged`: `PASS`

### Changed files

- None.

### Sanitized diff

```diff

```

## Observation 10: runner-progress-output

- Status: `PASS`
- Role: `regression`
- Repetition: `1`
- Duration: `868 ms`
- Workspace retention: `retained`
- Tokens: input `unknown`, cached input `unknown`, output `unknown`, reasoning output `unknown`
- Normalized usage events: `0`, complete `false`, scopes `none`

### Executor account

Executor did not provide a structured response.

### Mechanical facts

- Mechanical result: `PASS`
- Oracle result: `PASS`
- Judge verdict: `PASS`
- `command: python3 check_progress.py`: `PASS`
- `forbidden changed path: sample-skill/**`: `PASS`
- `forbidden changed path: fake-codex`: `PASS`
- `forbidden changed path: check_progress.py`: `PASS`
- `evaluated skill remained unchanged`: `PASS`

### Changed files

- None.

### Sanitized diff

```diff

```

## Observation 11: impact-gate-selection

- Status: `PASS`
- Role: `regression`
- Repetition: `1`
- Duration: `74624 ms`
- Workspace retention: `retained`
- Tokens: input `202063`, cached input `163328`, output `3048`, reasoning output `920`
- Normalized usage events: `1`, complete `true`, scopes `turn`

### Executor account

Diagnosis: The intended stdout/stderr contract change is completely observable by deterministic checks.

Approach:
- Used the repository scoped public `plan` operation with promotion workflow.
- Allowed the runner to select applicable suite cases.

Decisions:
- Classified the proposed change as deterministic.
- Used promotion planning without an explicit case filter or model runtime.

Rejected Alternatives:
- None recorded.

Key Changes:
- Created only the three requested planning artifacts.

Validation:
- Exit code: 0.
- Standard error: 0 bytes.
- Plan schema: valid.
- Evaluation executions performed: 0.

### Mechanical facts

- Mechanical result: `PASS`
- Oracle result: `PASS`
- Judge verdict: `PASS`
- `executor exit code`: `PASS`
- `executor response schema`: `PASS`
- `required path: evaluation-plan.json`: `PASS`
- `required path: plan-stderr.log`: `PASS`
- `required path: plan-exit-code.txt`: `PASS`
- `forbidden changed path: .agents/skills/**`: `PASS`
- `forbidden changed path: target-skill/**`: `PASS`
- `forbidden changed path: target-baseline/**`: `PASS`
- `evaluated skill remained unchanged`: `PASS`

### Changed files

- `evaluation-plan.json`
- `plan-exit-code.txt`
- `plan-stderr.log`

### Sanitized diff

```diff
--- /dev/null
+++ b/evaluation-plan.json
@@ -0,0 +1,113 @@
+{
+  "operation": "plan",
+  "workflow": "promotion",
+  "promotion_eligible": true,
+  "skill": "/tmp/skill-eval-artifacts/validate-change-5g79myz1/impact-gate-selection-37v8py40/target-skill",
+  "baseline": "/tmp/skill-eval-artifacts/validate-change-5g79myz1/impact-gate-selection-37v8py40/target-baseline",
+  "impact": "deterministic",
+  "selected_cases": [
+    "runner-output"
+  ],
+  "regression_cases": [],
+  "steps": [
+    "baseline-red",
+    "candidate-green-1",
+    "candidate-green-2-and-3",
+    "structural-validation"
+  ],
+  "commands": [
+    "python3 /tmp/skill-eval-artifacts/validate-change-5g79myz1/impact-gate-selection-37v8py40/.agents/skills/develop-skill-with-evals/scripts/run_skill_evals.py validate-change --skill /tmp/skill-eval-artifacts/validate-change-5g79myz1/impact-gate-selection-37v8py40/target-skill --baseline /tmp/skill-eval-artifacts/validate-change-5g79myz1/impact-gate-selection-37v8py40/target-baseline --impact deterministic --case runner-output --approved-model-sessions 8",
+    "python3 .system/skill-creator/scripts/quick_validate.py /tmp/skill-eval-artifacts/validate-change-5g79myz1/impact-gate-selection-37v8py40/target-skill"
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
+  "manifest_fingerprint": "a07ad5ac9106e05f29ff3e80b64d6eca5a5cbf9d8b7d29faa267e998eccb65cb",
+  "case_fingerprints": {
+    "runner-output": "569640ec7e3beb1cac11f5e38b3f413c309eaf13cf9ed6fa853e99aacd12711f"
+  },
+  "source_fingerprints": {
+    "baseline": "4c2c2887c5dd00a95c5b8c0c82bd529ddfad7a5b0913b2d2a1d91034bcdfde12",
+    "candidate": "4c2c2887c5dd00a95c5b8c0c82bd529ddfad7a5b0913b2d2a1d91034bcdfde12"
+  },
+  "economic_runtime": {
+    "policy_version": 2,
+    "mode": "zero-session",
+    "executor": {
+      "recommended_model": null,
+      "recommended_reasoning_effort": null,
+      "matches_explicit_runtime": null
+    },
+    "judge": {
+      "recommended_model": null,
+      "recommended_reasoning_effort": null,
+      "matches_explicit_runtime": null
+    },
+    "reasons": [
+      "Static and deterministic changes use structural or mechanical evidence with zero real model sessions."
+    ]
+  },
+  "runtime": {
+    "required": false,
+    "complete": true,
+    "audit_quality": "not_applicable",
+    "executor": {
+      "required": false,
+      "model": null,
+      "model_source": "configured-default",
+      "reasoning_effort": null,
+      "reasoning_effort_source": "configured-default"
+    },
+    "judge": {
+      "required": false,
+      "model": null,
+      "model_source": "executor",
+      "reasoning_effort": null,
+      "reasoning_effort_source": "executor"
+    }
+  },
+  "runtime_fingerprint": "9f0b7fc45c236ba7d9e872c8bd7ac6452f27d42f8729e3f8f0fb46bbfe027d7c",
+  "campaign": {
+    "ledger": null,
+    "approved_cumulative_model_sessions": null,
+    "consumed_before": 0,
+    "reserved_before": 0,
+    "planned_maximum": 0,
+    "projected_maximum": 0
+  },
+  "execution_blockers": [],
+  "evaluation_fingerprint": "aaaa54bae24c796c9583e199b4c42ac94cc92b8d4a6fd95cb376a983a94995f4"
+}
--- /dev/null
+++ b/plan-exit-code.txt
@@ -0,0 +1 @@
+0
```

## Observation 12: auditable-runtime-contract

- Status: `PASS`
- Role: `regression`
- Repetition: `1`
- Duration: `304 ms`
- Workspace retention: `retained`
- Tokens: input `unknown`, cached input `unknown`, output `unknown`, reasoning output `unknown`
- Normalized usage events: `0`, complete `false`, scopes `none`

### Executor account

Executor did not provide a structured response.

### Mechanical facts

- Mechanical result: `PASS`
- Oracle result: `PASS`
- Judge verdict: `PASS`
- `command: python3 check_runtime_contract.py`: `PASS`
- `forbidden changed path: check_runtime_contract.py`: `PASS`
- `forbidden changed path: fake-codex`: `PASS`
- `evaluated skill remained unchanged`: `PASS`

### Changed files

- None.

### Sanitized diff

```diff

```

## Observation 13: explicit-runtime-promotion-workflow

- Status: `PASS`
- Role: `regression`
- Repetition: `1`
- Duration: `153497 ms`
- Workspace retention: `retained`
- Tokens: input `607346`, cached input `548352`, output `6115`, reasoning output `1287`
- Normalized usage events: `1`, complete `true`, scopes `turn`

### Executor account

Diagnosis: The renderer uppercased the raw argument without removing surrounding whitespace.

Approach:
- Planned and ran the diagnostic workflow.
- Planned and ran the promotion workflow.
- Validated JSON artifacts and skill structure.

Decisions:
- Used zero session authorization because both plans displayed zero required sessions.
- Preserved sample-baseline and sample-skill/SKILL.md unchanged.
- Disabled separate report persistence.

Rejected Alternatives:
- None recorded.

Key Changes:
- Changed rendering to `sys.argv[1].strip().upper()`.

Validation:
- All four requested artifacts contain pure schema-valid JSON.
- Direct rendering of `  hello  ` produced `HELLO`.
- Skill structural validation passed.
- No commit or publication was performed.

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
@@ -0,0 +1,112 @@
+{
+  "operation": "plan",
+  "workflow": "diagnostic",
+  "promotion_eligible": false,
+  "skill": "/tmp/skill-eval-artifacts/validate-change-5g79myz1/explicit-runtime-promotion-workflow-638dc7xt/sample-skill",
+  "baseline": "/tmp/skill-eval-artifacts/validate-change-5g79myz1/explicit-runtime-promotion-workflow-638dc7xt/sample-baseline",
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
+    "python3 /tmp/skill-eval-artifacts/validate-change-5g79myz1/explicit-runtime-promotion-workflow-638dc7xt/.agents/skills/develop-skill-with-evals/scripts/run_skill_evals.py probe-change --skill /tmp/skill-eval-artifacts/validate-change-5g79myz1/explicit-runtime-promotion-workflow-638dc7xt/sample-skill --baseline /tmp/skill-eval-artifacts/validate-change-5g79myz1/explicit-runtime-promotion-workflow-638dc7xt/sample-baseline --impact deterministic --case trim-uppercase --model gpt-5.6-sol --reasoning-effort medium --judge-model gpt-5.6-terra --judge-reasoning-effort medium --approved-model-sessions 8",
+    "python3 .system/skill-creator/scripts/quick_validate.py /tmp/skill-eval-artifacts/validate-change-5g79myz1/explicit-runtime-promotion-workflow-638dc7xt/sample-skill"
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
+  "economic_runtime": {
+    "policy_version": 2,
+    "mode": "zero-session",
+    "executor": {
+      "recommended_model": null,
+      "recommended_reasoning_effort": null,
+      "matches_explicit_runtime": null
+    },
+    "judge": {
+      "recommended_model": null,
+      "recommended_reasoning_effort": null,
+      "matches_explicit_runtime": null
+    },
+    "reasons": [
+      "Static and deterministic changes use structural or mechanical evidence with zero real model sessions."
+    ]
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
+  "evaluation_fingerprint": "ec441e6b7b750dff34411b9e8137b9674789ab66e5e3581a0aacbb7b065cd404"
+}
--- /dev/null
+++ b/diagnostic.json
@@ -0,0 +1,367 @@
+{
+  "operation": "probe-change",
+  "status": "PASS",
+  "workflow": "diagnostic",
+  "promotion_eligible": false,
+  "failure_category": null,
+  "skill": "/tmp/skill-eval-artifacts/validate-change-5g79myz1/explicit-runtime-promotion-workflow-638dc7xt/sample-skill",
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
+    "skill": "/tmp/skill-eval-artifacts/validate-change-5g79myz1/explicit-runtime-promotion-workflow-638dc7xt/sample-skill",
+    "baseline": "/tmp/skill-eval-artifacts/validate-change-5g79myz1/explicit-runtime-promotion-workflow-638dc7xt/sample-baseline",
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
+      "python3 /tmp/skill-eval-artifacts/validate-change-5g79myz1/explicit-runtime-promotion-workflow-638dc7xt/.agents/skills/develop-skill-with-evals/scripts/run_skill_evals.py probe-change --skill /tmp/skill-eval-artifacts/validate-change-5g79myz1/explicit-runtime-promotion-workflow-638dc7xt/sample-skill --baseline /tmp/skill-eval-artifacts/validate-change-5g79myz1/explicit-runtime-promotion-workflow-638dc7xt/sample-baseline --impact deterministic --case trim-uppercase --model gpt-5.6-sol --reasoning-effort medium --judge-model gpt-5.6-terra --judge-reasoning-effort medium --approved-model-sessions 0",
+      "python3 .system/skill-creator/scripts/quick_validate.py /tmp/skill-eval-artifacts/validate-change-5g79myz1/explicit-runtime-promotion-workflow-638dc7xt/sample-skill"
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
+    "economic_runtime": {
+      "policy_version": 2,
+      "mode": "zero-session",
+      "executor": {
+        "recommended_model": null,
+        "recommended_reasoning_effort": null,
+        "matches_explicit_runtime": null
+      },
+      "judge": {
+        "recommended_model": null,
+        "recommended_reasoning_effort": null,
+        "matches_explicit_runtime": null
+      },
+      "reasons": [
+        "Static and deterministic changes use structural or mechanical evidence with zero real model sessions."
+      ]
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
+    "evaluation_fingerprint": "ec441e6b7b750dff34411b9e8137b9674789ab66e5e3581a0aacbb7b065cd404"
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
+            "stderr": "Traceback (most recent call last):\n  File \"/tmp/skill-eval-artifacts/probe-change-2bd_4isv/trim-uppercase-pc_v0i8v/check_trim.py\", line 16, in <module>\n    assert completed.stdout == \"HELLO\\n\"\nAssertionError\n"
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
@@ -0,0 +1,113 @@
+{
+  "operation": "plan",
+  "workflow": "promotion",
+  "promotion_eligible": true,
+  "skill": "/tmp/skill-eval-artifacts/validate-change-5g79myz1/explicit-runtime-promotion-workflow-638dc7xt/sample-skill",
+  "baseline": "/tmp/skill-eval-artifacts/validate-change-5g79myz1/explicit-runtime-promotion-workflow-638dc7xt/sample-baseline",
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
+    "python3 /tmp/skill-eval-artifacts/validate-change-5g79myz1/explicit-runtime-promotion-workflow-638dc7xt/.agents/skills/develop-skill-with-evals/scripts/run_skill_evals.py validate-change --skill /tmp/skill-eval-artifacts/validate-change-5g79myz1/explicit-runtime-promotion-workflow-638dc7xt/sample-skill --baseline /tmp/skill-eval-artifacts/validate-change-5g79myz1/explicit-runtime-promotion-workflow-638dc7xt/sample-baseline --impact deterministic --case trim-uppercase --model gpt-5.6-sol --reasoning-effort medium --judge-model gpt-5.6-terra --judge-reasoning-effort medium --approved-model-sessions 8",
+    "python3 .system/skill-creator/scripts/quick_validate.py /tmp/skill-eval-artifacts/validate-change-5g79myz1/explicit-runtime-promotion-workflow-638dc7xt/sample-skill"
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
+  "economic_runtime": {
+    "policy_version": 2,
+    "mode": "zero-session",
+    "executor": {
+      "recommended_model": null,
+      "recommended_reasoning_effort": null,
+      "matches_explicit_runtime": null
+    },
+    "judge": {
+      "recommended_model": null,
+      "recommended_reasoning_effort": null,
+      "matches_explicit_runtime": null
+    },
+    "reasons": [
+      "Static and deterministic changes use structural or mechanical evidence with zero real model sessions."
+    ]
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
+  "evaluation_fingerprint": "757f81b1e1a8bf66c360436ae446963606726985b4c7a91fd28a2ec03858f817"
+}
--- /dev/null
+++ b/runner-invocations.jsonl
@@ -0,0 +1,8 @@
+["--help"]
+["plan", "--help"]
+["probe-change", "--help"]
+["validate-change", "--help"]
+["plan", "--skill", "sample-skill", "--baseline", "sample-baseline", "--impact", "deterministic", "--workflow", "diagnostic", "--model", "gpt-5.6-sol", "--reasoning-effort", "medium", "--judge-model", "gpt-5.6-terra", "--judge-reasoning-effort", "medium"]
+["probe-change", "--skill", "sample-skill", "--baseline", "sample-baseline", "--impact", "deterministic", "--case", "trim-uppercase", "--model", "gpt-5.6-sol", "--reasoning-effort", "medium", "--judge-model", "gpt-5.6-terra", "--judge-reasoning-effort", "medium", "--approved-model-sessions", "0", "--codex-command", "./fake-codex", "--no-report", "--quiet"]
+["plan", "--skill", "sample-skill", "--baseline", "sample-baseline", "--impact", "deterministic", "--workflow", "promotion", "--model", "gpt-5.6-sol", "--reasoning-effort", "medium", "--judge-model", "gpt-5.6-terra", "--judge-reasoning-effort", "medium"]
+["validate-change", "--skill", "sample-skill", "--baseline", "sample-baseline", "--impact", "deterministic", "--case", "trim-uppercase", "--model", "gpt-5.6-sol", "--reasoning-effort", "medium", "--judge-model", "gpt-5.6-terra", "--judge-reasoning-effort", "medium", "--approved-model-sessions", "0", "--codex-command", "./fake-codex", "--no-report", "--quiet"]
--- a/sample-skill/scripts/render.py
+++ b/sample-skill/scripts/render.py
@@ -2,4 +2,4 @@
 import sys


-print(sys.argv[1].upper())
+print(sys.argv[1].strip().upper())
--- /dev/null
+++ b/validation.json
@@ -0,0 +1,566 @@
+{
+  "operation": "validate-change",
+  "status": "PASS",
+  "workflow": "promotion",
+  "promotion_eligible": true,
+  "failure_category": null,
+  "skill": "/tmp/skill-eval-artifacts/validate-change-5g79myz1/explicit-runtime-promotion-workflow-638dc7xt/sample-skill",
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
+    "skill": "/tmp/skill-eval-artifacts/validate-change-5g79myz1/explicit-runtime-promotion-workflow-638dc7xt/sample-skill",
+    "baseline": "/tmp/skill-eval-artifacts/validate-change-5g79myz1/explicit-runtime-promotion-workflow-638dc7xt/sample-baseline",
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
+      "python3 /tmp/skill-eval-artifacts/validate-change-5g79myz1/explicit-runtime-promotion-workflow-638dc7xt/.agents/skills/develop-skill-with-evals/scripts/run_skill_evals.py validate-change --skill /tmp/skill-eval-artifacts/validate-change-5g79myz1/explicit-runtime-promotion-workflow-638dc7xt/sample-skill --baseline /tmp/skill-eval-artifacts/validate-change-5g79myz1/explicit-runtime-promotion-workflow-638dc7xt/sample-baseline --impact deterministic --case trim-uppercase --model gpt-5.6-sol --reasoning-effort medium --judge-model gpt-5.6-terra --judge-reasoning-effort medium --approved-model-sessions 0",
+      "python3 .system/skill-creator/scripts/quick_validate.py /tmp/skill-eval-artifacts/validate-change-5g79myz1/explicit-runtime-promotion-workflow-638dc7xt/sample-skill"
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
+    "economic_runtime": {
+      "policy_version": 2,
+      "mode": "zero-session",
+      "executor": {
+        "recommended_model": null,
+        "recommended_reasoning_effort": null,
+        "matches_explicit_runtime": null
+      },
+      "judge": {
+        "recommended_model": null,
+        "recommended_reasoning_effort": null,
+        "matches_explicit_runtime": null
+      },
+      "reasons": [
+        "Static and deterministic changes use structural or mechanical evidence with zero real model sessions."
+      ]
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
+    "evaluation_fingerprint": "757f81b1e1a8bf66c360436ae446963606726985b4c7a91fd28a2ec03858f817"
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
+            "stderr": "Traceback (most recent call last):\n  File \"/tmp/skill-eval-artifacts/validate-change-s_gypfsb/trim-uppercase-r7tp6_j6/check_trim.py\", line 16, in <module>\n    assert completed.stdout == \"HELLO\\n\"\nAssertionError\n"
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
+          "reasoning_outpu
```

Truncations:
- `validation.json`: per file diff limit

## Observation 14: cost-efficient-runtime-contract

- Status: `FAIL`
- Role: `regression`
- Repetition: `1`
- Duration: `124 ms`
- Workspace retention: `retained`
- Tokens: input `unknown`, cached input `unknown`, output `unknown`, reasoning output `unknown`
- Normalized usage events: `0`, complete `false`, scopes `none`

### Executor account

Executor did not provide a structured response.

### Mechanical facts

- Mechanical result: `FAIL`
- Oracle result: `PASS`
- Judge verdict: `PASS`
- `command: python3 check_cost_efficient_runtime.py`: `FAIL`
- `evaluated skill remained unchanged`: `PASS`

### Changed files

- None.

### Sanitized diff

```diff

```

## Integrity

- Report digest: `sha256:75d867f3edfa359aabda64cc51890efe2a7604959229d50d9bf8e5a1af10c42a`
