# Evaluation evidence: 20260726T142523.377510Z-706003141596

- Operation: `run`
- Status: `PASS`
- Provenance: `executed`
- Started: `2026-07-26T14:25:23.377510Z`
- Finished: `2026-07-26T14:31:08.480376Z`
- Duration: `345221 ms`
- Executor model: `gpt-5.6-sol`
- Executor effort: `medium`
- Codex CLI: `codex-cli 0.145.0`
- Authentication: `chatgpt`
- Runner SHA-256: `c63a75cb545b42f3479d20e8937ac1b2e8eb93b06064aebeb7630630a02540e9`

## Consumption

- Tokens: input `831401`, cached input `760064`, output `10775`, reasoning output `2542`
- Normalized usage events: `1`, complete `true`, scopes `turn`
- Sessions: planned `1`, executed `1`

## API reference estimate

- Reference amount: unavailable
- This is not an actual charge.
- Base-rate amount: `1.059967000000 USD`
- Estimate status: `indeterminate-long-context`
- Limitation: This is an API reference estimate, not an observed charge.
- Limitation: This dated table is an API reference and is not an observed ChatGPT charge.
- Limitation: Prompts above 272,000 input tokens use the documented higher rates; an exact estimate is unavailable when normalized telemetry does not expose request scoped input.
- Limitation: Cache write charges are not estimated because Codex JSONL usage does not identify cache writes.
- Limitation: Reasoning output tokens are reported separately but are already included in output tokens.
- Limitation: A reported usage event exceeded a request-scoped threshold, but the event is not request scoped; the exact multiplier cannot be audited.

## Observation 1: load-skill-creator-first

- Status: `PASS`
- Role: `observation`
- Repetition: `1`
- Duration: `345072 ms`
- Workspace retention: `removed`
- Tokens: input `831401`, cached input `760064`, output `10775`, reasoning output `2542`
- Normalized usage events: `1`, complete `true`, scopes `turn`

### Executor account

Diagnosis: Model backed promotion evaluation was blocked because subprocess network access to the Codex service is prohibited. Both attempts are preserved as infrastructure ERROR reports, so promotion readiness is not claimed.

Approach:
- Initialized with the official scaffold before manual edits.
- Preserved the untouched scaffold as the evaluation baseline.
- Added one focused behavioral case and performed offline and fresh agent validation.

Decisions:
- Default to two compact prose sentences, with a maximum of three.
- Preserve supplied facts, units, place names, and language without guessing.
- Keep creation evidence outside the skill directory.

Rejected Alternatives:
- None recorded.

Key Changes:
- Added practical, facts only morning brief instructions.
- Added matching UI metadata and a focused evaluation suite.
- Persisted both blocked evaluation reports outside the skill.

Validation:
- Official `quick_validate.py`: PASS.
- Creation evidence, JSON syntax, metadata, and evidence placement checks: PASS.
- Evaluation reports rendered deterministically and matched persisted Markdown: PASS.
- Fresh agent forward test: PASS.
- Model backed promotion gate: BLOCKED by infrastructure before behavioral evaluation.
- `git diff --check`: PASS.

### Mechanical facts

- Mechanical result: `PASS`
- Oracle result: `PASS`
- Judge verdict: `PASS`
- `executor exit code`: `PASS`
- `executor response schema`: `PASS`
- `required path: weather-brief/SKILL.md`: `PASS`
- `required path: creation-evidence.json`: `PASS`
- `forbidden changed path: .agents/skills/**`: `PASS`
- `forbidden changed path: weather-brief/creation-evidence.json`: `PASS`
- `evaluated skill remained unchanged`: `PASS`

### Changed files

- `creation-evidence.json`
- `eval-reports/20260726T142757.646355Z-c44029f668a4/report.json`
- `eval-reports/20260726T142757.646355Z-c44029f668a4/report.md`
- `eval-reports/20260726T142904.900915Z-2f99549ca8a9/report.json`
- `eval-reports/20260726T142904.900915Z-2f99549ca8a9/report.md`
- `weather-brief/SKILL.md`
- `weather-brief/agents/openai.yaml`
- `weather-brief/evals/cases/concise-morning-brief/case.json`
- `weather-brief/evals/cases/concise-morning-brief/prompt.md`
- `weather-brief/evals/suite.json`

### Sanitized diff

```diff
--- /dev/null
+++ b/creation-evidence.json
@@ -0,0 +1,16 @@
+{
+  "skill_creator_path": "/home/renanfranca/.codex/skills/.system/skill-creator/SKILL.md",
+  "scaffold_argv": [
+    "python3",
+    "/home/renanfranca/.codex/skills/.system/skill-creator/scripts/init_skill.py",
+    "weather-brief",
+    "--path",
+    ".",
+    "--interface",
+    "display_name=Weather Brief",
+    "--interface",
+    "short_description=Turn weather facts into a concise morning brief",
+    "--interface",
+    "default_prompt=Use $weather-brief to turn these weather facts into a concise morning brief."
+  ]
+}
--- /dev/null
+++ b/eval-reports/20260726T142757.646355Z-c44029f668a4/report.json
@@ -0,0 +1,243 @@
+{
+  "schema_version": 1,
+  "operation": {
+    "id": "20260726T142757.646355Z-c44029f668a4",
+    "type": "validate-change",
+    "status": "ERROR",
+    "workflow": "promotion",
+    "promotion_eligible": false,
+    "failure_category": "infrastructure"
+  },
+  "provenance": "executed",
+  "started_at": "2026-07-26T14:27:57.646355Z",
+  "finished_at": "2026-07-26T14:27:57.801126Z",
+  "duration_ms": 254,
+  "skill": {
+    "path": "/tmp/persist-eval-evidence.auoqZx/pilot-v2-artifacts/run-v2-01r/run-g0c4eaz0/load-skill-creator-first-nr7l5uf8/weather-brief",
+    "name": "weather-brief"
+  },
+  "fingerprints": {
+    "manifest": "47a931c78f042da8e21b181a6d9824f551b5953bd1c47fa99d20c514d1ad2caa",
+    "cases": {
+      "concise-morning-brief": "01de4bdd5a6aa773b38cb619fc7b0afa9a28dac9e56a8ecbe5da84a5e477cb13"
+    },
+    "sources": {
+      "baseline": "45c38a4e4fe703171990403339def44f97053bb9d0a2c65da31442c76a4fe1e9",
+      "candidate": "764b3dfce939ff251023b42d7ac45a9065c5663ec4ff87fd78b7b470d85b08dd"
+    },
+    "runtime": "6147b3d5a9fe78fbe0be5889e85fb547d12e605816b7ff4876d3a397e4440e91",
+    "evaluation": "db176db81da96f659c921d882f321f722f47f03543bd074f59f2a1e2547370a7"
+  },
+  "environment": {
+    "codex_cli": {
+      "status": "available",
+      "version": "codex-cli 0.145.0"
+    },
+    "authentication": {
+      "status": "available",
+      "mode": "unknown"
+    },
+    "runner": {
+      "path": "/tmp/persist-eval-evidence.auoqZx/pilot-v2-artifacts/run-v2-01r/run-g0c4eaz0/load-skill-creator-first-nr7l5uf8/.agents/skills/develop-skill-with-evals/scripts/run_skill_evals.py",
+      "sha256": "c63a75cb545b42f3479d20e8937ac1b2e8eb93b06064aebeb7630630a02540e9"
+    }
+  },
+  "billing": {
+    "mode": "chatgpt-plan-or-unknown",
+    "actual_charge_observed": false
+  },
+  "runtime": {
+    "required": true,
+    "complete": true,
+    "audit_quality": "promotion",
+    "executor": {
+      "required": true,
+      "model": "gpt-5.4-mini",
+      "model_source": "cli",
+      "reasoning_effort": "medium",
+      "reasoning_effort_source": "cli"
+    },
+    "judge": {
+      "required": true,
+      "model": "gpt-5.4-mini",
+      "model_source": "cli",
+      "reasoning_effort": "medium",
+      "reasoning_effort_source": "cli"
+    }
+  },
+  "sessions": {
+    "planned": {
+      "executor": 4,
+      "judge": 4,
+      "total": 8
+    },
+    "executed": {
+      "executor": 1,
+      "judge": 0,
+      "total": 1
+    },
+    "provenance": "executed"
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
+  "pricing": {
+    "applied": false,
+    "snapshot": null,
+    "limitations": [
+      "No explicit pricing file was supplied."
+    ]
+  },
+  "api_reference_estimate": {
+    "available": false,
+    "status": "unavailable",
+    "currency": null,
+    "amount": null,
+    "base_rate_amount": null,
+    "actual_charge": false,
+    "billing_mode": "chatgpt-plan-or-unknown",
+    "calculation": null,
+    "long_context_assessment": null,
+    "limitations": [
+      "This is an API reference estimate, not an observed charge.",
+      "No explicit pricing file was supplied."
+    ]
+  },
+  "observations": [
+    {
+      "case_id": "concise-morning-brief",
+      "status": "ERROR",
+      "kind": "behavioral",
+      "role": "baseline",
+      "repetition": 1,
+      "provenance": "executed",
+      "started_at": "2026-07-26T14:27:57.651278Z",
+      "finished_at": "2026-07-26T14:27:57.800909Z",
+      "duration_ms": 150,
+      "prompt": "Use $weather-brief with these facts:\n\nLocation: Porto\nNow: cloudy, 14°C\nHigh: 19°C\nRain: 70% chance after 15:00\nWind: southwest 25 km/h, gusts to 40 km/h\n",
+      "executor": {
+        "enabled": true,
+        "executed": true,
+        "exit_code": 1,
+        "duration_ms": 143,
+        "response": null,
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
+        }
+      },
+      "mechanical": {
+        "passed": false,
+        "checks": [
+          {
+            "name": "executor exit code",
+            "passed": false,
+            "detail": "expected 0, got 1"
+          },
+          {
+            "name": "executor response schema",
+            "passed": false,
+            "detail": "structured response present and valid"
+          },
+          {
+            "name": "forbidden changed path: **",
+            "passed": false,
+            "detail": ".eval-executor-schema.json"
+          },
+          {
+            "name": "evaluated skill remained unchanged",
+            "passed": true,
+            "detail": "repository-scoped skill hash comparison"
+          }
+        ],
+        "commands": []
+      },
+      "oracle": {
+        "enabled": false,
+        "passed": true,
+        "commands": []
+      },
+      "judge": {
+        "enabled": true,
+        "executed": false,
+        "verdict": "SKIPPED",
+        "rationale": "Semantic judge skipped because executor infrastructure failed.",
+        "evidence": [],
+        "duration_ms": 0,
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
+        "failure_category": "infrastructure"
+      },
+      "sessions": {
+        "executor": 1,
+        "judge": 0,
+        "total": 1
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
+      "evidence": {
+        "changed_files": [],
+        "diff": "",
+        "fragments": [],
+        "truncated": false,
+        "truncations": [],
+        "limits": {
+          "capture_bytes_per_file": 32768,
+          "diff_bytes_per_file": 12000,
+          "diff_bytes_per_report": 64000,
+          "fragment_bytes": 2000
+        }
+      },
+      "workspace": {
+        "original_path": "/tmp/skill-eval-artifacts/validate-change-doj3u21y/concise-morning-brief-46a4qnyo",
+        "retention": "retained"
+      }
+    }
+  ],
+  "limitations": [
+    "No raw Codex JSONL or complete transcript is persisted.",
+    "Structured executor fields record concise declared decisions, not private reasoning.",
+    "Diffs and text fragments are sanitized and bounded."
+  ],
+  "report_digest": {
+    "algorithm": "sha256",
+    "value": "5a924cf33eb80376c495bdd243eacb3751f977852316fff31090869d3a7b9be2"
+  }
+}
--- /dev/null
+++ b/eval-reports/20260726T142757.646355Z-c44029f668a4/report.md
@@ -0,0 +1,65 @@
+# Evaluation evidence: 20260726T142757.646355Z-c44029f668a4
+
+- Operation: `validate-change`
+- Status: `ERROR`
+- Provenance: `executed`
+- Started: `2026-07-26T14:27:57.646355Z`
+- Finished: `2026-07-26T14:27:57.801126Z`
+- Duration: `254 ms`
+- Executor model: `gpt-5.4-mini`
+- Executor effort: `medium`
+- Codex CLI: `codex-cli 0.145.0`
+- Authentication: `unknown`
+- Runner SHA-256: `c63a75cb545b42f3479d20e8937ac1b2e8eb93b06064aebeb7630630a02540e9`
+
+## Consumption
+
+- Tokens: input `unknown`, cached input `unknown`, output `unknown`, reasoning output `unknown`
+- Normalized usage events: `0`, complete `false`, scopes `none`
+- Sessions: planned `8`, executed `1`
+
+## API reference estimate
+
+- Reference amount: unavailable
+- This is not an actual charge.
+- Estimate status: `unavailable`
+- Limitation: This is an API reference estimate, not an observed charge.
+- Limitation: No explicit pricing file was supplied.
+
+## Observation 1: concise-morning-brief
+
+- Status: `ERROR`
+- Role: `baseline`
+- Repetition: `1`
+- Duration: `150 ms`
+- Workspace retention: `retained`
+- Tokens: input `unknown`, cached input `unknown`, output `unknown`, reasoning output `unknown`
+- Normalized usage events: `0`, complete `false`, scopes `none`
+
+### Executor account
+
+Executor did not provide a structured response.
+
+### Mechanical facts
+
+- Mechanical result: `FAIL`
+- Oracle result: `PASS`
+- Judge verdict: `SKIPPED`
+- `executor exit code`: `FAIL`
+- `executor response schema`: `FAIL`
+- `forbidden changed path: **`: `FAIL`
+- `evaluated skill remained unchanged`: `PASS`
+
+### Changed files
+
+- None.
+
+### Sanitized diff
+
+```diff
+
+```
+
+## Integrity
+
+- Report digest: `sha256:5a924cf33eb80376c495bdd243eacb3751f977852316fff31090869d3a7b9be2`
--- /dev/null
+++ b/eval-reports/20260726T142904.900915Z-2f99549ca8a9/report.json
@@ -0,0 +1,238 @@
+{
+  "schema_version": 1,
+  "operation": {
+    "id": "20260726T142904.900915Z-2f99549ca8a9",
+    "type": "validate-change",
+    "status": "ERROR",
+    "workflow": "promotion",
+    "promotion_eligible": false,
+    "failure_category": "infrastructure"
+  },
+  "provenance": "executed",
+  "started_at": "2026-07-26T14:29:04.900915Z",
+  "finished_at": "2026-07-26T14:29:40.443493Z",
+  "duration_ms": 35630,
+  "skill": {
+    "path": "/tmp/persist-eval-evidence.auoqZx/pilot-v2-artifacts/run-v2-01r/run-g0c4eaz0/load-skill-creator-first-nr7l5uf8/weather-brief",
+    "name": "weather-brief"
+  },
+  "fingerprints": {
+    "manifest": "2cb7067b0f31008c2192f83b0c8f03adb691e04ab554d2c759fdc503c88d4274",
+    "cases": {
+      "concise-morning-brief": "ff4b0bc614e614568d910a037a28b162e57afdff5af35744b0c6518317c9e1f2"
+    },
+    "sources": {
+      "baseline": "45c38a4e4fe703171990403339def44f97053bb9d0a2c65da31442c76a4fe1e9",
+      "candidate": "29b26682ddb08183e24855f53616a6341980f72aff91adc5812bf9f2a6d6cc9b"
+    },
+    "runtime": "9f82232c6ead4cef277fc2b2ce5cf000680e74a6b929f381720ad0d453050f68",
+    "evaluation": "1f3f62f3b218574855a3fe2ece103c7dec8c72b055038c85cc991327246be813"
+  },
+  "environment": {
+    "codex_cli": {
+      "status": "available",
+      "version": "codex-cli 0.145.0"
+    },
+    "authentication": {
+      "status": "available",
+      "mode": "unknown"
+    },
+    "runner": {
+      "path": "/tmp/persist-eval-evidence.auoqZx/pilot-v2-artifacts/run-v2-01r/run-g0c4eaz0/load-skill-creator-first-nr7l5uf8/.agents/skills/develop-skill-with-evals/scripts/run_skill_evals.py",
+      "sha256": "c63a75cb545b42f3479d20e8937ac1b2e8eb93b06064aebeb7630630a02540e9"
+    }
+  },
+  "billing": {
+    "mode": "chatgpt-plan-or-unknown",
+    "actual_charge_observed": false
+  },
+  "runtime": {
+    "required": true,
+    "complete": true,
+    "audit_quality": "promotion",
+    "executor": {
+      "required": true,
+      "model": "gpt-5.4-mini",
+      "model_source": "cli",
+      "reasoning_effort": "medium",
+      "reasoning_effort_source": "cli"
+    },
+    "judge": {
+      "required": true,
+      "model": "gpt-5.4-mini",
+      "model_source": "cli",
+      "reasoning_effort": "medium",
+      "reasoning_effort_source": "cli"
+    }
+  },
+  "sessions": {
+    "planned": {
+      "executor": 4,
+      "judge": 4,
+      "total": 8
+    },
+    "executed": {
+      "executor": 1,
+      "judge": 0,
+      "total": 1
+    },
+    "provenance": "executed"
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
+  "pricing": {
+    "applied": false,
+    "snapshot": null,
+    "limitations": [
+      "No explicit pricing file was supplied."
+    ]
+  },
+  "api_reference_estimate": {
+    "available": false,
+    "status": "unavailable",
+    "currency": null,
+    "amount": null,
+    "base_rate_amount": null,
+    "actual_charge": false,
+    "billing_mode": "chatgpt-plan-or-unknown",
+    "calculation": null,
+    "long_context_assessment": null,
+    "limitations": [
+      "This is an API reference estimate, not an observed charge.",
+      "No explicit pricing file was supplied."
+    ]
+  },
+  "observations": [
+    {
+      "case_id": "concise-morning-brief",
+      "status": "ERROR",
+      "kind": "behavioral",
+      "role": "baseline",
+      "repetition": 1,
+      "provenance": "executed",
+      "started_at": "2026-07-26T14:29:04.904031Z",
+      "finished_at": "2026-07-26T14:29:40.443314Z",
+      "duration_ms": 35528,
+      "prompt": "Use $weather-brief with these facts:\n\nLocation: Porto\nNow: cloudy, 14°C\nHigh: 19°C\nRain: 70% chance after 15:00\nWind: southwest 25 km/h, gusts to 40 km/h\n",
+      "executor": {
+        "enabled": true,
+        "executed": true,
+        "exit_code": 1,
+        "duration_ms": 35522,
+        "response": null,
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
+        }
+      },
+      "mechanical": {
+        "passed": false,
+        "checks": [
+          {
+            "name": "executor exit code",
+            "passed": false,
+            "detail": "expected 0, got 1"
+          },
+          {
+            "name": "executor response schema",
+            "passed": false,
+            "detail": "structured response present and valid"
+          },
+          {
+            "name": "evaluated skill remained unchanged",
+            "passed": true,
+            "detail": "repository-scoped skill hash comparison"
+          }
+        ],
+        "commands": []
+      },
+      "oracle": {
+        "enabled": false,
+        "passed": true,
+        "commands": []
+      },
+      "judge": {
+        "enabled": true,
+        "executed": false,
+        "verdict": "SKIPPED",
+        "rationale": "Semantic judge skipped because executor infrastructure failed.",
+        "evidence": [],
+        "duration_ms": 0,
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
+        "failure_category": "infrastructure"
+      },
+      "sessions": {
+        "executor": 1,
+        "judge": 0,
+        "total": 1
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
+      "evidence": {
+        "changed_files": [],
+        "diff": "",
+        "fragments": [],
+        "truncated": false,
+        "truncations": [],
+        "limits": {
+          "capture_bytes_per_file": 32768,
+          "diff_bytes_per_file": 12000,
+          "diff_bytes_per_report": 64000,
+          "fragment_bytes": 2000
+        }
+      },
+      "workspace": {
+        "original_path": "/tmp/skill-eval-artifacts/validate-change-5uzj9fom/concise-morning-brief-st9ltzul",
+        "retention": "retained"
+      }
+    }
+  ],
+  "limitations": [
+    "No raw Codex JSONL or complete transcript is persisted.",
+    "Structured executor fields record concise declared decisions, not private reasoning.",
+    "Diffs and text fragments are sanitized and bounded."
+  ],
+  "report_digest": {
+    "algorithm": "sha256",
+    "value": "e1e8769f9f15e0c33ef5a91a9cfc2e389fbc7d924c229c9b2a55e2e2bc1712ba"
+  }
+}
--- /dev/null
+++ b/eval-reports/20260726T142904.900915Z-2f99549ca8a9/report.md
@@ -0,0 +1,64 @@
+# Evaluation evidence: 20260726T142904.900915Z-2f99549ca8a9
+
+- Operation: `validate-change`
+- Status: `ERROR`
+- Provenance: `executed`
+- Started: `2026-07-26T14:29:04.900915Z`
+- Finished: `2026-07-26T14:29:40.443493Z`
+- Duration: `35630 ms`
+- Executor model: `gpt-5.4-mini`
+- Executor effort: `medium`
+- Codex CLI: `codex-cli 0.145.0`
+- Authentication: `unknown`
+- Runner SHA-256: `c63a75cb545b42f3479d20e8937ac1b2e8eb93b06064aebeb7630630a02540e9`
+
+## Consumption
+
+- Tokens: input `unknown`, cached input `unknown`, output `unknown`, reasoning output `unknown`
+- Normalized usage events: `0`, complete `false`, scopes `none`
+- Sessions: planned `8`, executed `1`
+
+## API reference estimate
+
+- Reference amount: unavailable
+- This is not an actual charge.
+- Estimate status: `unavailable`
+- Limitation: This is an API reference estimate, not an observed charge.
+- Limitation: No explicit pricing file was supplied.
+
+## Observation 1: concise-morning-brief
+
+- Status: `ERROR`
+- Role: `baseline`
+- Repetition: `1`
+- Duration: `35528 ms`
+- Workspace retention: `retained`
+- Tokens: input `unknown`, cached input `unknown`, output `unknown`, reasoning output `unknown`
+- Normalized usage events: `0`, complete `false`, scopes `none`
+
+### Executor account
+
+Executor did not provide a structured response.
+
+### Mechanical facts
+
+- Mechanical result: `FAIL`
+- Oracle result: `PASS`
+- Judge verdict: `SKIPPED`
+- `executor exit code`: `FAIL`
+- `executor response schema`: `FAIL`
+- `evaluated skill remained unchanged`: `PASS`
+
+### Changed files
+
+- None.
+
+### Sanitized diff
+
+```diff
+
+```
+
+## Integrity
+
+- Report digest: `sha256:e1e8769f9f15e0c33ef5a91a9cfc2e389fbc7d924c229c9b2a55e2e2bc1712ba`
--- /dev/null
+++ b/weather-brief/SKILL.md
@@ -0,0 +1,24 @@
+---
+name: weather-brief
+description: Turn supplied weather facts into a concise, practical morning brief. Use when the user provides current conditions, temperatures, precipitation, wind, alerts, or similar forecast facts and wants a morning weather summary or quick daily outlook.
+---
+
+# Weather Brief
+
+Create a compact morning update from only the facts the user supplies.
+
+## Compose the brief
+
+1. Identify the location, current conditions, current temperature, expected high or low, precipitation timing and probability, wind, and alerts when supplied.
+2. Lead with the current condition and temperature, then state the most useful change or risk for the day.
+3. Add practical guidance only when it follows directly from the facts, such as carrying rain protection or allowing for strong gusts.
+4. Preserve the supplied units and place names. Match the user's language.
+5. Omit missing fields without calling attention to them. Resolve no gaps by guessing.
+
+## Output rules
+
+- Write two compact sentences by default and never more than three.
+- Use plain prose without a heading, preamble, or bullet list.
+- Prefer specific timing and probabilities over vague language.
+- Mention alerts or hazardous conditions before routine details.
+- Do not add forecasts, advice, or certainty unsupported by the supplied facts.
--- /dev/null
+++ b/weather-brief/agents/openai.yaml
@@ -0,0 +1,4 @@
+interface:
+  display_name: "Weather Brief"
+  short_description: "Turn weather facts into a concise morning brief"
+  default_prompt: "Use $weather-brief to turn these weather facts into a concise morning brief."
--- /dev/null
+++ b/weather-brief/evals/cases/concise-morning-brief/case.json
@@ -0,0 +1,18 @@
+{
+  "id": "concise-morning-brief",
+  "kind": "behavioral",
+  "prompt_file": "prompt.md",
+  "implicit_skill": false,
+  "mechanical": {
+    "expected_exit_code": 0
+  },
+  "judge": {
+    "enabled": true,
+    "criteria": [
+      "The response is a morning brief of no more than three short sentences and has no heading or bullet list.",
+      "It accurately includes the current condition, temperature, expected high, rain timing and chance, and wind information.",
+      "It prioritizes practical morning guidance derived only from the supplied facts and does not invent weather details."
+    ],
+    "no_action_acceptable": true
+  }
+}
--- /dev/null
+++ b/weather-brief/evals/cases/concise-morning-brief/prompt.md
@@ -0,0 +1,7 @@
+Use $weather-brief with these facts:
+
+Location: Porto
+Now: cloudy, 14°C
+High: 19°C
+Rain: 70% chance after 15:00
+Wind: southwest 25 km/h, gusts to 40 km/h
--- /dev/null
+++ b/weather-brief/evals/suite.json
@@ -0,0 +1,4 @@
+{
+  "version": 1,
+  "cases": ["concise-morning-brief"]
+}
```

## Integrity

- Report digest: `sha256:3fc77f5548e51a7471a225c8e7ec4190de369981272ef031974b0883694fc883`
