# Evaluation evidence: 20260727T121835.379099Z-1076d0881b03

- Operation: `validate-change`
- Status: `FAIL`
- Provenance: `executed`
- Started: `2026-07-27T12:18:35.379099Z`
- Finished: `2026-07-27T12:23:28.180021Z`
- Duration: `293107 ms`
- Executor model: `gpt-5.6-sol`
- Executor effort: `medium`
- Codex CLI: `codex-cli 0.145.0`
- Authentication: `chatgpt`
- Runner SHA-256: `30f579584ba4eb2c9d21a68786aaae41f336a012c01cad35f4079e72a1e640e5`

## Consumption

- Tokens: input `792336`, cached input `687104`, output `12132`, reasoning output `1911`
- Normalized usage events: `2`, complete `true`, scopes `turn`
- Sessions: planned `16`, executed `2`

## API reference estimate

- Reference amount: unavailable
- This is not an actual charge.
- Base-rate amount: `1.233672000000 USD`
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
- Duration: `143155 ms`
- Workspace retention: `retained`
- Tokens: input `490147`, cached input `429312`, output `6076`, reasoning output `1097`
- Normalized usage events: `1`, complete `true`, scopes `turn`

### Executor account

Diagnosis:

Approach:
- None recorded.

Decisions:
- Used `gpt-5.6-terra` with low effort for the economical plan.
- Preserved `gpt-5.6-sol` with medium effort for the user specified plan.

Rejected Alternatives:
- None recorded.

Key Changes:
- Saved complete plans with four executor sessions and zero judge sessions each.

Validation:
- JSON parsing passed.
- Schema validation passed.
- Candidate and baseline source fingerprints remained unchanged.

### Mechanical facts

- Mechanical result: `PASS`
- Oracle result: `FAIL`
- Judge verdict: `PASS`
- `executor exit code`: `PASS`
- `executor response schema`: `PASS`
- `required path: plan-economical.json`: `PASS`
- `required path: plan-user-sol.json`: `PASS`
- `forbidden changed path: .agents/skills/**`: `PASS`
- `forbidden changed path: candidate-skill/**`: `PASS`
- `forbidden changed path: baseline-skill/**`: `PASS`
- `evaluated skill remained unchanged`: `PASS`

### Changed files

- `plan-economical.json`
- `plan-user-sol.json`

### Sanitized diff

```diff
--- /dev/null
+++ b/plan-economical.json
@@ -0,0 +1,96 @@
+{
+  "operation": "plan",
+  "workflow": "promotion",
+  "promotion_eligible": true,
+  "skill": "/tmp/promote-economic-runtime.acJDsi/promotion-third-artifacts/validate-change-rttqjg7l/economic-runtime-guidance-o02kdiu5/candidate-skill",
+  "baseline": "/tmp/promote-economic-runtime.acJDsi/promotion-third-artifacts/validate-change-rttqjg7l/economic-runtime-guidance-o02kdiu5/baseline-skill",
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
+    "python3 /tmp/promote-economic-runtime.acJDsi/promotion-third-artifacts/validate-change-rttqjg7l/economic-runtime-guidance-o02kdiu5/.agents/skills/develop-skill-with-evals/scripts/run_skill_evals.py validate-change --skill /tmp/promote-economic-runtime.acJDsi/promotion-third-artifacts/validate-change-rttqjg7l/economic-runtime-guidance-o02kdiu5/candidate-skill --baseline /tmp/promote-economic-runtime.acJDsi/promotion-third-artifacts/validate-change-rttqjg7l/economic-runtime-guidance-o02kdiu5/baseline-skill --impact scoped --case eligible --model gpt-5.6-terra --reasoning-effort low --approved-model-sessions 8",
+    "python3 .system/skill-creator/scripts/quick_validate.py /tmp/promote-economic-runtime.acJDsi/promotion-third-artifacts/validate-change-rttqjg7l/economic-runtime-guidance-o02kdiu5/candidate-skill"
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
+  "manifest_fingerprint": "2dd07a6bb6771e7f5f0df53b89b218c7e921c3c708d264a2dac0d9938d17d73d",
+  "case_fingerprints": {
+    "eligible": "fee17fd722d5619c75560e7b14c09d3fdf46054a857093ba910a0a18df8a9c72"
+  },
+  "source_fingerprints": {
+    "baseline": "e2f8a7728b96087d47983ccb03f0c4b18580d0346dfa7c958010ebbda972503a",
+    "candidate": "e2f8a7728b96087d47983ccb03f0c4b18580d0346dfa7c958010ebbda972503a"
+  },
+  "runtime": {
+    "required": true,
+    "complete": true,
+    "audit_quality": "promotion",
+    "executor": {
+      "required": true,
+      "model": "gpt-5.6-terra",
+      "model_source": "cli",
+      "reasoning_effort": "low",
+      "reasoning_effort_source": "cli"
+    },
+    "judge": {
+      "required": false,
+      "model": "gpt-5.6-terra",
+      "model_source": "executor",
+      "reasoning_effort": "low",
+      "reasoning_effort_source": "executor"
+    }
+  },
+  "runtime_fingerprint": "c4d0bed7fb3af0b954348b9f7cf9451bf1531a653ac2e1945f086c7236ca159d",
+  "campaign": {
+    "ledger": null,
+    "approved_cumulative_model_sessions": null,
+    "consumed_before": 0,
+    "reserved_before": 0,
+    "planned_maximum": 4,
+    "projected_maximum": 4
+  },
+  "execution_blockers": [],
+  "evaluation_fingerprint": "9c7a4c5f91bf931b45b71be08ef65cce7a13b70aa4ee85d0ca31707190783f0d"
+}
--- /dev/null
+++ b/plan-user-sol.json
@@ -0,0 +1,96 @@
+{
+  "operation": "plan",
+  "workflow": "promotion",
+  "promotion_eligible": true,
+  "skill": "/tmp/promote-economic-runtime.acJDsi/promotion-third-artifacts/validate-change-rttqjg7l/economic-runtime-guidance-o02kdiu5/candidate-skill",
+  "baseline": "/tmp/promote-economic-runtime.acJDsi/promotion-third-artifacts/validate-change-rttqjg7l/economic-runtime-guidance-o02kdiu5/baseline-skill",
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
+    "python3 /tmp/promote-economic-runtime.acJDsi/promotion-third-artifacts/validate-change-rttqjg7l/economic-runtime-guidance-o02kdiu5/.agents/skills/develop-skill-with-evals/scripts/run_skill_evals.py validate-change --skill /tmp/promote-economic-runtime.acJDsi/promotion-third-artifacts/validate-change-rttqjg7l/economic-runtime-guidance-o02kdiu5/candidate-skill --baseline /tmp/promote-economic-runtime.acJDsi/promotion-third-artifacts/validate-change-rttqjg7l/economic-runtime-guidance-o02kdiu5/baseline-skill --impact scoped --case eligible --model gpt-5.6-sol --reasoning-effort medium --approved-model-sessions 8",
+    "python3 .system/skill-creator/scripts/quick_validate.py /tmp/promote-economic-runtime.acJDsi/promotion-third-artifacts/validate-change-rttqjg7l/economic-runtime-guidance-o02kdiu5/candidate-skill"
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
+  "manifest_fingerprint": "2dd07a6bb6771e7f5f0df53b89b218c7e921c3c708d264a2dac0d9938d17d73d",
+  "case_fingerprints": {
+    "eligible": "fee17fd722d5619c75560e7b14c09d3fdf46054a857093ba910a0a18df8a9c72"
+  },
+  "source_fingerprints": {
+    "baseline": "e2f8a7728b96087d47983ccb03f0c4b18580d0346dfa7c958010ebbda972503a",
+    "candidate": "e2f8a7728b96087d47983ccb03f0c4b18580d0346dfa7c958010ebbda972503a"
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
+  "runtime_fingerprint": "c14a0f868736e18522ab09e078a7a58af1ae08f15b4b0d7a1bda13bbeb2aaaee",
+  "campaign": {
+    "ledger": null,
+    "approved_cumulative_model_sessions": null,
+    "consumed_before": 0,
+    "reserved_before": 0,
+    "planned_maximum": 4,
+    "projected_maximum": 4
+  },
+  "execution_blockers": [],
+  "evaluation_fingerprint": "afab08fe72040b7e6e0c2aeb6f21d6e94935e3d96a9cd75167b0e1eca69684cd"
+}
```

## Observation 2: cost-efficient-runtime-contract

- Status: `FAIL`
- Role: `baseline`
- Repetition: `1`
- Duration: `111 ms`
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

## Observation 3: nested-codex-outer-sandbox-contract

- Status: `FAIL`
- Role: `baseline`
- Repetition: `1`
- Duration: `59 ms`
- Workspace retention: `retained`
- Tokens: input `unknown`, cached input `unknown`, output `unknown`, reasoning output `unknown`
- Normalized usage events: `0`, complete `false`, scopes `none`

### Executor account

Executor did not provide a structured response.

### Mechanical facts

- Mechanical result: `FAIL`
- Oracle result: `PASS`
- Judge verdict: `PASS`
- `command: python3 check_nested_codex_outer_sandbox.py`: `FAIL`
- `evaluated skill remained unchanged`: `PASS`

### Changed files

- None.

### Sanitized diff

```diff

```

## Observation 4: economic-runtime-guidance

- Status: `FAIL`
- Role: `candidate`
- Repetition: `1`
- Duration: `149638 ms`
- Workspace retention: `retained`
- Tokens: input `302189`, cached input `257792`, output `6056`, reasoning output `814`
- Normalized usage events: `1`, complete `true`, scopes `turn`

### Executor account

Diagnosis:

Approach:
- Generated promotion plans with the repository scoped runner.
- Validated both plans against `eval-plan.schema.json` and regenerated output.

Decisions:
- Selected `gpt-5.6-luna` with `medium` effort for the economical plan.
- Preserved `gpt-5.6-sol` with `medium` effort for the user specified plan.

Rejected Alternatives:
- None recorded.

Key Changes:
- Saved the economical plan as `plan-economical.json`.
- Saved the user selected Sol plan as `plan-user-sol.json`.

Validation:
- Both JSON documents are schema valid.
- Both files exactly match fresh side effect free runner output.
- No reports, ledgers, artifacts, or skill tree changes were created.

### Mechanical facts

- Mechanical result: `PASS`
- Oracle result: `FAIL`
- Judge verdict: `PASS`
- `executor exit code`: `PASS`
- `executor response schema`: `PASS`
- `required path: plan-economical.json`: `PASS`
- `required path: plan-user-sol.json`: `PASS`
- `forbidden changed path: .agents/skills/**`: `PASS`
- `forbidden changed path: candidate-skill/**`: `PASS`
- `forbidden changed path: baseline-skill/**`: `PASS`
- `evaluated skill remained unchanged`: `PASS`

### Changed files

- `plan-economical.json`
- `plan-user-sol.json`

### Sanitized diff

```diff
--- /dev/null
+++ b/plan-economical.json
@@ -0,0 +1,113 @@
+{
+  "operation": "plan",
+  "workflow": "promotion",
+  "promotion_eligible": true,
+  "skill": "/tmp/promote-economic-runtime.acJDsi/promotion-third-artifacts/validate-change-rttqjg7l/economic-runtime-guidance-5k8wwwrr/candidate-skill",
+  "baseline": "/tmp/promote-economic-runtime.acJDsi/promotion-third-artifacts/validate-change-rttqjg7l/economic-runtime-guidance-5k8wwwrr/baseline-skill",
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
+    "python3 /tmp/promote-economic-runtime.acJDsi/promotion-third-artifacts/validate-change-rttqjg7l/economic-runtime-guidance-5k8wwwrr/.agents/skills/develop-skill-with-evals/scripts/run_skill_evals.py validate-change --skill /tmp/promote-economic-runtime.acJDsi/promotion-third-artifacts/validate-change-rttqjg7l/economic-runtime-guidance-5k8wwwrr/candidate-skill --baseline /tmp/promote-economic-runtime.acJDsi/promotion-third-artifacts/validate-change-rttqjg7l/economic-runtime-guidance-5k8wwwrr/baseline-skill --impact scoped --case eligible --model gpt-5.6-luna --reasoning-effort medium --approved-model-sessions 8",
+    "python3 .system/skill-creator/scripts/quick_validate.py /tmp/promote-economic-runtime.acJDsi/promotion-third-artifacts/validate-change-rttqjg7l/economic-runtime-guidance-5k8wwwrr/candidate-skill"
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
+  "manifest_fingerprint": "2dd07a6bb6771e7f5f0df53b89b218c7e921c3c708d264a2dac0d9938d17d73d",
+  "case_fingerprints": {
+    "eligible": "fee17fd722d5619c75560e7b14c09d3fdf46054a857093ba910a0a18df8a9c72"
+  },
+  "source_fingerprints": {
+    "baseline": "e2f8a7728b96087d47983ccb03f0c4b18580d0346dfa7c958010ebbda972503a",
+    "candidate": "e2f8a7728b96087d47983ccb03f0c4b18580d0346dfa7c958010ebbda972503a"
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
+  "runtime_fingerprint": "9786ee1cf01fef0d47e885b5105bbad5f227b8ad0921b5b9644f671a901f3e27",
+  "campaign": {
+    "ledger": null,
+    "approved_cumulative_model_sessions": null,
+    "consumed_before": 0,
+    "reserved_before": 0,
+    "planned_maximum": 4,
+    "projected_maximum": 4
+  },
+  "execution_blockers": [],
+  "evaluation_fingerprint": "1a3c1b6025c9034168bbcb460fb9f6985772148bf2b47b75fc5215c753669762"
+}
--- /dev/null
+++ b/plan-user-sol.json
@@ -0,0 +1,114 @@
+{
+  "operation": "plan",
+  "workflow": "promotion",
+  "promotion_eligible": true,
+  "skill": "/tmp/promote-economic-runtime.acJDsi/promotion-third-artifacts/validate-change-rttqjg7l/economic-runtime-guidance-5k8wwwrr/candidate-skill",
+  "baseline": "/tmp/promote-economic-runtime.acJDsi/promotion-third-artifacts/validate-change-rttqjg7l/economic-runtime-guidance-5k8wwwrr/baseline-skill",
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
+    "python3 /tmp/promote-economic-runtime.acJDsi/promotion-third-artifacts/validate-change-rttqjg7l/economic-runtime-guidance-5k8wwwrr/.agents/skills/develop-skill-with-evals/scripts/run_skill_evals.py validate-change --skill /tmp/promote-economic-runtime.acJDsi/promotion-third-artifacts/validate-change-rttqjg7l/economic-runtime-guidance-5k8wwwrr/candidate-skill --baseline /tmp/promote-economic-runtime.acJDsi/promotion-third-artifacts/validate-change-rttqjg7l/economic-runtime-guidance-5k8wwwrr/baseline-skill --impact scoped --case eligible --model gpt-5.6-sol --reasoning-effort medium --approved-model-sessions 8",
+    "python3 .system/skill-creator/scripts/quick_validate.py /tmp/promote-economic-runtime.acJDsi/promotion-third-artifacts/validate-change-rttqjg7l/economic-runtime-guidance-5k8wwwrr/candidate-skill"
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
+  "manifest_fingerprint": "2dd07a6bb6771e7f5f0df53b89b218c7e921c3c708d264a2dac0d9938d17d73d",
+  "case_fingerprints": {
+    "eligible": "fee17fd722d5619c75560e7b14c09d3fdf46054a857093ba910a0a18df8a9c72"
+  },
+  "source_fingerprints": {
+    "baseline": "e2f8a7728b96087d47983ccb03f0c4b18580d0346dfa7c958010ebbda972503a",
+    "candidate": "e2f8a7728b96087d47983ccb03f0c4b18580d0346dfa7c958010ebbda972503a"
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
+  "runtime_fingerprint": "c14a0f868736e18522ab09e078a7a58af1ae08f15b4b0d7a1bda13bbeb2aaaee",
+  "campaign": {
+    "ledger": null,
+    "approved_cumulative_model_sessions": null,
+    "consumed_before": 0,
+    "reserved_before": 0,
+    "planned_maximum": 4,
+    "projected_maximum": 4
+  },
+  "execution_blockers": [],
+  "evaluation_fingerprint": "c7460c8ab00bbabcbfe793da20408effc8bfa727e8d6c2e299e54392347bfb8a"
+}
```

## Integrity

- Report digest: `sha256:a047f7ef6757a2fb47f3dc28e9166b5cecac99198a586b4ab2121fdd9bd796b9`
