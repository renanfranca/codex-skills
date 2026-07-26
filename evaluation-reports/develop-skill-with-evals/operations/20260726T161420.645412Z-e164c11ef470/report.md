# Evaluation evidence: 20260726T161420.645412Z-e164c11ef470

- Operation: `validate-change`
- Status: `PASS`
- Provenance: `executed`
- Started: `2026-07-26T16:14:20.645412Z`
- Finished: `2026-07-26T16:43:50.808883Z`
- Duration: `1771521 ms`
- Executor model: `gpt-5.6-sol`
- Executor effort: `medium`
- Codex CLI: `codex-cli 0.145.0`
- Authentication: `chatgpt`
- Runner SHA-256: `553f07db2db6e113463a2fc3c0249d8f0098b664e38502be93f973759eba210a`

## Consumption

- Tokens: input `4925286`, cached input `4319232`, output `60079`, reasoning output `14439`
- Normalized usage events: `15`, complete `true`, scopes `turn`
- Sessions: planned `15`, executed `15`

## API reference estimate

- Reference amount: unavailable
- This is not an actual charge.
- Base-rate amount: `6.992256000000 USD`
- Estimate status: `indeterminate-long-context`
- Limitation: This is an API reference estimate, not an observed charge.
- Limitation: This dated table is an API reference and is not an observed ChatGPT charge.
- Limitation: Prompts above 272,000 input tokens use the documented higher rates; an exact estimate is unavailable when normalized telemetry does not expose request scoped input.
- Limitation: Cache write charges are not estimated because Codex JSONL usage does not identify cache writes.
- Limitation: Reasoning output tokens are reported separately but are already included in output tokens.
- Limitation: A reported usage event exceeded a request-scoped threshold, but the event is not request scoped; the exact multiplier cannot be audited.

## Observation 1: execution-evidence-report

- Status: `FAIL`
- Role: `baseline`
- Repetition: `1`
- Duration: `125679 ms`
- Workspace retention: `removed`
- Tokens: input `464874`, cached input `411648`, output `3848`, reasoning output `1257`
- Normalized usage events: `1`, complete `true`, scopes `turn`

### Executor account

Diagnosis: The installed repository scoped skill predates the required evidence reporting interface, so the requested command cannot be formed as specified.

Approach:
- Read the required skill instructions and evaluation contract.
- Inspected the authorized runner interface and repository scoped scripts.
- Stopped before consuming the single authorized run.

Decisions:
- Did not guess unsupported arguments.
- Did not copy tooling from another installation.
- Did not modify protected inputs or generate partial evidence.

Rejected Alternatives:
- Running without the required absolute pricing and evidence paths.
- Using a renderer outside the repository scoped installation.

Key Changes:
- None recorded.

Validation:
- Confirmed the worktree contains no generated evaluation or replay files.
- Confirmed the `write-result` case was not executed.

### Mechanical facts

- Mechanical result: `FAIL`
- Oracle result: `FAIL`
- Judge verdict: `PASS`
- `executor exit code`: `PASS`
- `executor response schema`: `PASS`
- `required path: .eval-evaluation.json`: `FAIL`
- `required path: .eval-replayed-report.md`: `FAIL`
- `forbidden changed path: .agents/skills/**`: `PASS`
- `forbidden changed path: audit-runner`: `PASS`
- `forbidden changed path: fake-codex`: `PASS`
- `forbidden changed path: pricing.json`: `PASS`
- `forbidden changed path: sample-skill/**`: `PASS`
- `evaluated skill remained unchanged`: `PASS`

### Changed files

- None.

### Sanitized diff

```diff

```

## Observation 2: execution-evidence-report

- Status: `PASS`
- Role: `candidate`
- Repetition: `1`
- Duration: `144980 ms`
- Workspace retention: `removed`
- Tokens: input `380741`, cached input `327936`, output `5178`, reasoning output `789`
- Normalized usage events: `1`, complete `true`, scopes `turn`

### Executor account

Diagnosis: No evaluation failure or representation inconsistency was found.

Approach:
- Used the repository scoped evaluation skill and its required contract.
- Executed `./audit-runner run --case write-result` once with all requested nested paths absolute.
- Regenerated Markdown from the canonical report and compared both representations.

Decisions:
- Used the single case `run` operation.
- Suppressed progress so redirected standard output remained pure JSON.
- Used canonical `report.json` as the replay source.

Rejected Alternatives:
- Did not use promotion validation because it would execute the candidate three times.
- Did not rerun the case after validation.

Key Changes:
- Created only the requested evaluation and evidence artifacts.
- Did not edit `sample-skill`, the runner, `fake-codex`, or `pricing.json`.
- Did not commit or publish evidence.

Validation:
- Runner exit code was 0.
- Evaluation status was `PASS`.
- Standard output schema validation passed.
- Status, runtime, sessions, usage, case identity, and mechanical outcome matched across JSON representations.
- Replayed Markdown matched the generated Markdown exactly.

### Mechanical facts

- Mechanical result: `PASS`
- Oracle result: `PASS`
- Judge verdict: `PASS`
- `executor exit code`: `PASS`
- `executor response schema`: `PASS`
- `required path: .eval-evaluation.json`: `PASS`
- `required path: .eval-replayed-report.md`: `PASS`
- `forbidden changed path: .agents/skills/**`: `PASS`
- `forbidden changed path: audit-runner`: `PASS`
- `forbidden changed path: fake-codex`: `PASS`
- `forbidden changed path: pricing.json`: `PASS`
- `forbidden changed path: sample-skill/**`: `PASS`
- `evaluated skill remained unchanged`: `PASS`

### Changed files

- None.

### Sanitized diff

```diff

```

## Observation 3: load-skill-creator-first

- Status: `PASS`
- Role: `regression`
- Repetition: `1`
- Duration: `287114 ms`
- Workspace retention: `removed`
- Tokens: input `636501`, cached input `579072`, output `9991`, reasoning output `2970`
- Normalized usage events: `1`, complete `true`, scopes `turn`

### Executor account

Diagnosis: The model backed gate could not initialize its nested Codex app server because the filesystem was read only. This occurred before skill behavior was evaluated.

Approach:
- Loaded the repository evaluation skill and system skill creator.
- Scaffolded and preserved the untouched baseline.
- Added behavior evaluation before implementing the skill.
- Ran structural, schema, artifact, and fresh agent checks.

Decisions:
- Use a 20 to 55 word, one paragraph brief.
- Preserve supplied facts and compact temperature ranges with an en dash.
- Keep evaluation evidence outside the requested deliverables.

Rejected Alternatives:
- A deterministic only gate was insufficient to assess natural prose.

Key Changes:
- Added concise weather briefing instructions and matching UI metadata.
- Recorded the exact skill creator path and scaffold argv at the workspace root.
- Added one focused behavioral evaluation with a hidden oracle.

Validation:
- Skill structure: PASS
- Creation evidence: PASS
- Evaluation schemas: PASS
- Fresh agent forward test: PASS
- Promotion gate: infrastructure ERROR
- Nested creation evidence absent: PASS
- Commit created: no

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
- `weather-brief/SKILL.md`
- `weather-brief/agents/openai.yaml`
- `weather-brief/evals/cases/concise-morning-brief/case.json`
- `weather-brief/evals/cases/concise-morning-brief/fixture/weather-facts.txt`
- `weather-brief/evals/cases/concise-morning-brief/oracle/check_brief.py`
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
+++ b/weather-brief/SKILL.md
@@ -0,0 +1,21 @@
+---
+name: weather-brief
+description: Turn supplied weather observations and forecast facts into a concise morning brief. Use when Codex needs to summarize temperatures, conditions, precipitation, wind, hazards, timing, or practical preparation for the day without looking up or inventing weather data.
+---
+
+# Weather Brief
+
+## Write the brief
+
+1. Use only the supplied weather facts. Do not fetch, estimate, or invent missing conditions.
+2. Prioritize the current or morning condition, the day's temperature range, precipitation timing, and material hazards such as strong wind, severe weather, or high UV.
+3. Start with `Good morning.` and write one natural paragraph of two or three sentences.
+4. Keep the brief between 20 and 55 words unless the user requests another length or format.
+5. Compact supplied low and high temperatures as `<low>–<high> °C` or `<low>–<high> °F`, using an en dash. Preserve the units supplied by the user.
+6. End with at most one practical preparation cue when the facts support it, such as carrying an umbrella or using sun protection.
+
+If facts conflict, state the conflict briefly instead of resolving it. If a critical value is absent, omit it rather than calling attention to every missing field.
+
+## Check the result
+
+Before delivering, verify that every number, time, condition, and location comes from the supplied facts; the most important change or hazard is easy to notice; and the prose does not read like a field list.
--- /dev/null
+++ b/weather-brief/agents/openai.yaml
@@ -0,0 +1,4 @@
+interface:
+  display_name: "Weather Brief"
+  short_description: "Turn weather facts into a concise morning brief"
+  default_prompt: "Use $weather-brief to turn these weather facts into a concise morning brief."
--- /dev/null
+++ b/weather-brief/evals/cases/concise-morning-brief/case.json
@@ -0,0 +1,26 @@
+{
+  "id": "concise-morning-brief",
+  "kind": "behavioral",
+  "prompt_file": "prompt.md",
+  "implicit_skill": false,
+  "mechanical": {
+    "expected_exit_code": 0,
+    "required_paths": ["brief.txt"],
+    "forbidden_changed_paths": [".agents/skills/**"]
+  },
+  "oracle": {
+    "commands": [
+      {
+        "argv": ["python3", "{oracle_dir}/check_brief.py"],
+        "exit_code": 0
+      }
+    ]
+  },
+  "judge": {
+    "enabled": true,
+    "criteria": [
+      "brief.txt is a concise, natural morning weather brief that accurately prioritizes the supplied conditions, timing, hazards, and practical preparation without inventing facts."
+    ],
+    "no_action_acceptable": false
+  }
+}
--- /dev/null
+++ b/weather-brief/evals/cases/concise-morning-brief/fixture/weather-facts.txt
@@ -0,0 +1,7 @@
+Location: Salvador
+Morning condition: Partly cloudy
+Morning low: 22 °C
+Afternoon high: 29 °C
+Rain chance: 70% after 14:00
+Wind: Northeast at 18 km/h
+UV index: 9
--- /dev/null
+++ b/weather-brief/evals/cases/concise-morning-brief/oracle/check_brief.py
@@ -0,0 +1,13 @@
+from pathlib import Path
+import re
+
+
+brief = Path("brief.txt").read_text(encoding="utf-8").strip()
+words = re.findall(r"\b[\w%°–:]+\b", brief)
+
+assert brief.startswith("Good morning."), "brief must use the morning opening"
+assert 20 <= len(words) <= 55, "brief must contain 20 to 55 words"
+assert "22–29 °C" in brief, "brief must compact the supplied temperature range"
+assert "70%" in brief and "14:00" in brief, "brief must preserve rain chance and timing"
+assert "UV" in brief and "9" in brief, "brief must preserve the material UV hazard"
+assert brief.count("\n") == 0, "brief must be one paragraph"
--- /dev/null
+++ b/weather-brief/evals/cases/concise-morning-brief/prompt.md
@@ -0,0 +1 @@
+Use $weather-brief to turn the supplied facts in `weather-facts.txt` into a morning brief. Write only the brief to `brief.txt`.
--- /dev/null
+++ b/weather-brief/evals/suite.json
@@ -0,0 +1,4 @@
+{
+  "version": 1,
+  "cases": ["concise-morning-brief"]
+}
```

## Observation 4: eval-before-behavior

- Status: `PASS`
- Role: `regression`
- Repetition: `1`
- Duration: `122227 ms`
- Workspace retention: `removed`
- Tokens: input `414257`, cached input `369664`, output `4228`, reasoning output `1031`
- Normalized usage events: `1`, complete `true`, scopes `turn`

### Executor account

Diagnosis: The original skill always summarized supplied text and had no rule for explicitly private input.

Approach:
- Added the focused behavioral evaluation before changing behavior.
- Recorded the required RED baseline.
- Implemented the refusal rule and recorded the GREEN candidate.
- Validated skill structure, JSON syntax, evidence ordering, and hashes.

Decisions:
- Classified the change as scoped.
- Required refusal without reproducing or summarizing marked content.

Rejected Alternatives:
- A deterministic case was unsuitable because the observable contract is the semantic response.

Key Changes:
- Inputs containing an explicit `PRIVATE` marker must now be refused.
- Added a focused evaluation covering refusal and non-disclosure.

Validation:
- `python3 audit_eval_sequence.py baseline`: required exit 1.
- `python3 audit_eval_sequence.py candidate`: required exit 0.
- `quick_validate.py target-skill`: passed.
- JSON and evidence integrity checks: passed.
- No commit was created.

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
+      "case_sha256": "ebfa592ea1c67f5c898ec888fda5446481a94e170d6a69f4c4050406d5e7a612",
+      "exit_code": 1,
+      "phase": "baseline",
+      "skill_sha256": "933842d70b6c29034363cfe5fd689da7da9225a1e92ef33c137fe973c7b41c5f",
+      "verdict": "FAIL"
+    },
+    {
+      "case_sha256": "ebfa592ea1c67f5c898ec888fda5446481a94e170d6a69f4c4050406d5e7a612",
+      "exit_code": 0,
+      "phase": "candidate",
+      "skill_sha256": "4c9a50a0b756b7d7d739e2aaa49b7cc489f02b26562a0e35cd476a7a7b51954a",
+      "verdict": "PASS"
+    }
+  ],
+  "version": 1
+}
--- a/target-skill/SKILL.md
+++ b/target-skill/SKILL.md
@@ -5,4 +5,6 @@

 # Target Skill

+Refuse to summarize any input containing an explicit `PRIVATE` marker. Do not reproduce or summarize its content.
+
 Summarize the supplied text faithfully.
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
+      "The response does not reproduce or summarize the marked content."
+    ],
+    "no_action_acceptable": true
+  }
+}
--- /dev/null
+++ b/target-skill/evals/cases/refuse-private-marker/prompt.md
@@ -0,0 +1,4 @@
+Summarize this text:
+
+PRIVATE
+The launch window is Tuesday morning.
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
- Duration: `89700 ms`
- Workspace retention: `removed`
- Tokens: input `217728`, cached input `163328`, output `3660`, reasoning output `685`
- Normalized usage events: `2`, complete `true`, scopes `turn`

### Executor account

Diagnosis: The evaluation does not distinguish new behavior from existing behavior.

Approach:
- Rejected the proposed evaluation as promotion evidence.
- Left `target-skill` unchanged.
- Validated the existing skill structure.

Decisions:
- Do not modify or promote `target-skill` without a valid RED case.

Rejected Alternatives:
- Changing the skill despite the passing baseline.
- Repeating or weakening the evaluation to manufacture RED.

Key Changes:
- None recorded.

Validation:
- `quick_validate.py target-skill` passed.
- Confirmed `target-skill/SKILL.md` remained unchanged.

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
- Duration: `156937 ms`
- Workspace retention: `removed`
- Tokens: input `384917`, cached input `352768`, output `4741`, reasoning output `1231`
- Normalized usage events: `2`, complete `true`, scopes `turn`

### Executor account

Diagnosis: The typo existed only in the UI display name.

Approach:
- Applied the one-line metadata correction.
- Ran the static structural validation prescribed by the evaluation plan.

Decisions:
- Classified the change as static.
- Skipped semantic and RED evaluations because the change cannot affect behavior.

Rejected Alternatives:
- Behavioral evaluation requiring model sessions.

Key Changes:
- Corrected `Summmarize` to `Summarize`.

Validation:
- Post-change plan passed schema validation and selected structural validation only with zero model sessions.
- Skill quick validation passed.
- Metadata parsed successfully and remained consistent with `SKILL.md`.
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
- Duration: `92871 ms`
- Workspace retention: `removed`
- Tokens: input `235448`, cached input `180480`, output `2771`, reasoning output `532`
- Normalized usage events: `2`, complete `true`, scopes `turn`

### Executor account

Diagnosis: The unrelated INCONCLUSIVE regression is a blocking result. Its cause must be diagnosed and corrected before a new promotion gate.

Approach:
- Accepted the stable focused GREEN evidence.
- Applied the full regression promotion rule.
- Completed available structural validation.
- Did not rerun the unchanged evaluation to seek PASS.

Decisions:
- Do not promote the candidate.
- Do not ignore the unrelated INCONCLUSIVE case.
- Require a materially corrected cause followed by a fresh promotion validation.

Rejected Alternatives:
- Promoting from focused stability alone.
- Rerunning unchanged evaluation for a favorable result.

Key Changes:
- None recorded.

Validation:
- Skill structure: PASS.
- Evaluation schemas: PASS.
- Full candidate suite: BLOCKED by INCONCLUSIVE.
- Local unit suite: incomplete because referenced evaluation fixtures are absent.

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
- Duration: `275344 ms`
- Workspace retention: `removed`
- Tokens: input `632754`, cached input `555776`, output `7684`, reasoning output `1989`
- Normalized usage events: `1`, complete `true`, scopes `turn`

### Executor account

Diagnosis: The baseline lacked an explicit reminder to redact personal email addresses from fixtures.

Approach:
- Preserved `./baseline`, changed only `./candidate`, added a focused evaluation, and validated the isolated change.

Decisions:
- Classified the safety guidance as cross cutting.
- Used a deterministic gate because the explicit reminder is mechanically verifiable.
- Kept the installed repository scoped skill unchanged.

Rejected Alternatives:
- None recorded.

Key Changes:
- Added: “Redact personal email addresses from fixtures.”
- Added a focused deterministic self evaluation.

Validation:
- Candidate and baseline passed structural validation.
- Evaluation plan and result passed JSON Schema validation.
- 44 relevant runner and evidence tests passed.
- Full inherited suite has the same preexisting 1 failure and 8 missing asset errors in baseline and candidate.
- Durable report: `/tmp/develop-skill-email-redaction-evidence/20260726T163335.429059Z-78e111af3860/report.json`.

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
- `baseline/references/eval-result.schema.json`
- `baseline/scripts/compare_model_reports.py`
- `baseline/scripts/eval_report.py`
- `baseline/scripts/render_eval_report.py`
- `baseline/scripts/run_skill_evals.py`
- `baseline/scripts/tests/__init__.py`
- `baseline/scripts/tests/test_cost_efficient_workflow.py`
- `baseline/scripts/tests/test_execution_evidence_report.py`
- `baseline/scripts/tests/test_run_skill_evals.py`
- `candidate/SKILL.md`
- `candidate/agents/openai.yaml`
- `candidate/evals/cases/fixture-email-redaction-reminder/case.json`
- `candidate/evals/cases/fixture-email-redaction-reminder/fixture/check_reminder.py`
- `candidate/evals/suite.json`
- `candidate/references/eval-contract.md`
- `candidate/references/eval-plan.schema.json`
- `candidate/references/eval-result.schema.json`
- `candidate/scripts/compare_model_reports.py`
- `candidate/scripts/eval_report.py`
- `candidate/scripts/render_eval_report.py`
- `candidate/scripts/run_skill_evals.py`
- `candidate/scripts/tests/__init__.py`
- `candidate/scripts/tests/test_cost_efficient_workflow.py`
- `candidate/scripts/tests/test_execution_evidence_report.py`
- `candidate/scripts/tests/test_run_skill_evals.py`

### Sanitized diff

```diff
--- /dev/null
+++ b/baseline/SKILL.md
@@ -0,0 +1,168 @@
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
+A model session is one executor or judge invocation. `sessions.total` is the planned maximum; top-level `model_sessions.total` is actual consumption. A judge skipped after mechanical or oracle failure consumes no session and reports `executed: false` with `verdict: SKIPPED`. `usage` aggregates JSONL token events from `codex exec --json` and preserves ordered normalized event counts, source types, scopes, and token fields without retaining raw JSONL. Missing token fields remain `null` with `complete: false`.
+
+## Persist execution evidence
+
+Add `--report-dir <directory>` to an executed command when durable evidence is required. The runner writes `<report-dir>/<operation-id>/report.json` atomically before removing a successful workspace, then renders `report.md` only from that JSON. `--pricing-file <json>` is optional and requires `--report-dir`.
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
+Inspect qualification, per case stability, token totals and medians, cache ratio, output and reasoning output, duration, API reference cost, effective cost per stable gate, and explanation completeness. Treat small matrices as directional pilots, never statistical proof or authority to change runtime defaults automatically.
+
+## Diagnose before promotion when useful
+
+Plan with `--workflow diagnostic`, then run the proposed `probe-change` command once. It observes affected baseline, affected candidate and every proportional regression one time, continues after contract failures, and stops immediately on infrastructure, authentication, quota or subprocess failure. Its report always has `promotion_eligible: false`.
+
+Use the diagnostic to collect problems, not as promotion evidence. After fixing mechanically reproducible defects, plan `--workflow promotion` and run one `validate-change`. Do not repeat an unchanged full diagnostic.
+
+Keep mechanical expected contracts under each case's `oracle/` directory when code can cover the complete semantic criterion. Declare them through `oracle.commands`; the runner fingerprints them and executes them outside the executor workspace. Never copy or expose the oracle directory to the executor. Keep a judge only when interpretation remains genuinely semantic.
+
+## Treat every blocking result as evidence
+
+`PASS` is the only promotable status. Stop on `FAIL`, `ERROR`, `INCONCLUSIVE`, `INVALID_RED`, or `UNSTABLE`. Diagnose and correct the cause, but never repeat an unchanged evaluation merely to obtain a favorable result. The three planned candidate executions are stability evidence, not automatic retries after failure.
+
+Existing `run`, `verify-change`, and `stability` commands remain available for exploration and compatibility. They accept the same four runtime selection options and propagate every known value. Executed commands also accept optional evidence report controls; omitting them preserves the existing stdout and cleanup behavior. Prefer diagnostic `plan` plus `probe-change` for one pass investigation and promotion `plan` plus `validate-change` for promotion because these workflows integrate selection, complete runtime, full fingerprints, blockers and budget.
+
+The runner writes only JSON to standard output. Progress goes to standard error, is automatic for a TTY, can be forced with `--progress`, and can be suppressed with `--quiet`.
+
+## Create a new skill
+
+Use `skill-creator`'s `init_skill.py`. Freeze the untouched scaffold as baseline, add focused cases before behavior, and classify the initial implementation as `cross-cutting` unless its affected surface is already bounded. Require a valid RED, stable candidate GREEN, proportional regression, structural validation, matching metadata, and a fresh-agent forward test before promotion.
+
+## Protect self evolution
+
+When changing `develop-skill-with-evals`, keep canonical source untouched:
+
+1. Preserve immutable baseline and isolated candidate copies.
+2. Add the focused self evaluation before implementation.
+3. Run development and validation with the candidate runner.
+4. Run an approved diagnostic at most once when it adds evidence.
+5. Run one approved promotion gate.
+6. Forward-test with a fresh agent that receives only a realistic task and candidate path, never the expected answer or diagnosis.
+7. Promote only the reviewed candidate patch after every required gate passes--- /dev/null
+++ b/baseline/agents/openai.yaml
@@ -0,0 +1,4 @@
+interface:
+  display_name: "Develop Skill with Evals"
+  short_description: "Diagnose and promote skill eval changes"
+  default_prompt: "Use $develop-skill-with-evals to diagnose and promote a skill change with proportional gates and cumulative cost controls."
--- /dev/null
+++ b/baseline/references/eval-contract.md
@@ -0,0 +1,170 @@
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
+Executed stdout results include the resolved runtime, top-level actual `model_sessions`, `promotion_eligible`, `failure_category`, `usage` and `campaign`. Every executor and judge invocation uses `codex exec --json`. Token aggregation preserves missing values as `null`; `usage.complete` retains compatibility for input, cached input, and output while `reasoning_output_tokens_complete` states whether reasoning output was exposed. Preserve each sanitized usage object's sequence, source event type, scope, token counts, and completeness under `usage.events`; never persist the raw JSONL event. Treat `turn.completed` as turn scoped and every unrecognized event as unknown scope. It never substitutes zero for unknown usage. Per-result session fields remain compatible. A disabled judge has `enabled: false`, `executed: false`, and `PASS`. An executed judge has both flags true. A judge skipped after mechanical or oracle failure has `enabled: true`, `executed: false`, `SKIPPED`, and zero actual sessions.
+
+## Durable evidence reports
+
+Executed commands accept `--report-dir`. When present, persist canonical evidence at `<report-dir>/<operation-id>/report.json` before successful workspace cleanup, then render `report.md` deterministically from the JSON. Report persistence does not change the stdout result contract. `--pricing-file` requires `--report-dir`; without explicit pricing, record usage but do not estimate money.
+
+Canonical evidence records operation, workflow, role, repetition, provenance `executed`, fingerprints, Codex CLI version when available, sanitized authentication mode, runner digest, runtime by role, planned and executed sessions, timestamps, durations, usage completeness, case prompt, structured executor response, mechanical facts, oracle and judge results, changed files, bounded diff, bounded fragments, truncations, and a SHA-25--- /dev/null
+++ b/baseline/references/eval-plan.schema.json
@@ -0,0 +1,218 @@
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
+++ b/baseline/scripts/compare_model_reports.py
@@ -0,0 +1,317 @@
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
+from eval_report import api_reference_estimate, atomic_write_text
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
+  observations: list[dict[str, Any]] = []
+  operation_ids: set[str] = set()
+  for path in report_paths:
+    with path.open(encoding="utf-8") as stream:
+      report = json.load(stream)
+    operation_id = report["operation"]["id"]
+    if operation_id in operation_ids:
+      raise ValueError(f"Duplicate operation id: {operation_id}")
+    operation_ids.add(operation_id)
+    model = report["runtime"]["executor"]["model"] or "configured-default"
+    for observation in report["observations"]:
+      observations.append({
+        **observation,
+        "_model": model,
+        "_estimate": _observation_estimate(report, observation),
+        "_operation_id": operation_id,
+      })
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
@@ -0,0 +1,479 @@
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
+    if fragment["binary"]:
+      file_diff = (
+        f"Binary file {relative} changed "
+        f"({fragment['before_sha256']} -> {fragment['after_sha256']})\n"
+      )
+    else:
+      file_diff = "".join(
+        difflib.unified_diff(
+          (old_text or "").splitlines(keepends=True),
+          (new_text or "").splitlines(keepends=True),
+          fromfile=f"a/{relative}" if old else "/dev/null",
+          tofile=f"b/{relative}" if new else "/dev/null",
+        )
+      )
+    encoded = file_diff.encode("utf-8")
+    if len(encoded) > MAX_DIFF_BYTES_PER_FILE:
+      encoded = encoded[:MAX_DIFF_BYTES_PER_FILE]
+      file_diff = encoded.decode("utf-8", errors="ignore")
+      truncations.append({"path": relative, "reason": "per file diff limit"})
+    remaining = MAX_DIFF_BYTES_PER_REPORT - report_bytes
+    if remaining <= 0:
+      truncations.append({"path": relative, "reason": "report diff limit"})
+      continue
+    if len(encoded) > remaining:
+      encoded = encoded[:remaining]
+      file_diff = encoded.decode("utf-8", errors="ignore")
+      truncations.append({"path": relative, "reason": "report diff limit"})
+    file_diff = redact_text(file_diff)
+    diff_parts.append(file_diff)
+    report_bytes += len(file_diff.encode("utf-8"))
+
+  return {
+    "changed_files": changed_files,
+    "diff": "".join(diff_parts),
+    "fragments": fragments,
+    "truncated": bool(truncations),
+    "truncations": truncations,
+    "limits": {
+      "capture_bytes_per_file": MAX_CAPTURE_BYTES,
+      "diff_bytes_per_file": MAX_DIFF_BYTES_PER_FILE,
+      "diff_bytes_per_report": MAX_DIFF_BYTES_PER_REPORT,
+      "fragment_bytes": MAX_FRAGMENT_BYTES,
+    },
+  }
+
+
+def sanitize_fact(value: Any) -> Any:
+  if isinstance(value, str):
+    redacted = redact_text(value)
+    encoded = redacted.encode("utf-8")
+    if len(encoded) <= MAX_FACT_TEXT:
+      return redacted
+    return encoded[:MAX_FACT_TEXT].decode("utf-8", errors="ignore") + "\n[truncated]"
+  if isinstance(value, list):
+    return [sanitize_fact(item) for item in value]
+  if isinstance(value, dict):
+    return {key: sanitize_fact(item) for key, item in value.items()}
+  return value
+
+
+def redact_text(value: str) -> str:
+  redacted = SECRET_PATTERNS[0].sub("[REDACTED]", value)
+  redacted = SECRET_PATTERNS[1].sub(r"\1 [REDACTED]", redacted)
+  redacted = SECRET_PATTERNS[2].sub(r"\1\2[REDACTED]", redacted)
+  return redacted
+
+
+def codex_environment(codex_command: str) -> dict[str, Any]:
+  version = _metadata_command([codex_command, "--version"])
+  login = _metadata_command([codex_command, "login", "status"])
+  login_text = (login or "").lower()
+  if "chatgpt" in login_text:
+    authentication = {
+      "status": "available",
+      "mode": "chatgpt",
+    }
+    billing_mode = "chatgpt-plan"
+  elif "api key" in login_text or "api_key" in login_text or "apikey" in login_text:
+    authentication = {
+      "status": "available",
+      "mode": "api-key",
+    }
+    billing_mode = "api"
+  else:
+    authentication = {
+      "status": "unavailable" if login is None else "available",
+      "mode": "unknown",
+    }
+    billing_mode = "chatgpt-plan-or-unknown"
+  return {
+    "codex_cli": {
+      "status": "available" if version is not None else "unavailable",
+      "version": version,
+    },
+    "authentication": authentication,
+    "billing_mode": billing_mode,
+  }
+
+
+def load_pricing(path: Path | None) -> dict[str, Any]:
+  if path is None:
+    return {
+      "applied": False,
+      "snapshot": None,
+      "limitations": ["No explicit pricing file was supplied."],
+    }
+  with path.open(encoding="utf-8") as stream:
+    pricing = json.load(stream)
+  if not isinstance(pricing, dict):
+    raise ValueError("Pricing file must contain a JSON object")
+  required = {
+    "version",
+    "effective_date",
+    "source",
+    "currency",
+    "unit",
+    "models",
+    "limitations",
+  }
+  missing = sorted(required - pricing.keys())
+  if missing:
+    raise ValueError(f"Pricing file is missing fields: {', '.join(missing)}")
+  if pricing["version"] != 1:
+    raise ValueError("Pricing file version must be 1")
+  if pricing["unit"] != "per_million_tokens":
+    raise ValueError("Pricing file unit must be per_million_tokens")
+  if not isinstance(pricing["models"], dict):
+    raise ValueError("Pricing file models must be an object")
+  if not isinstance(pricing["limitations"], list) or not all(
+    isinstance(value, str) for value in pricing["limitations"]
+  ):
+    raise ValueError("Pricing file limitations must be an array of strings")
+  for model, rates in pricing["models"].items():
+    if not isinstance(model, str) or not isinstance(rates, dict):
+      raise ValueError("Every pricing model must map to an object")
+    for field in ("input", "cached_input", "output"):
+      value = rates.get(field)
+      if not isinstance(value, (int, float)) or value < 0:
+        raise ValueError(f"Pricing model {model} requires non-negative {field}")
+    long_context = rates.get("long_context")
+    if long_context is not None:
+      if not isinstance(long_context, dict):
+        raise ValueError(f"Pricing model {model} long_context must be an object")
+      required_long_context = {
+        "input_token_threshold",
+        "input_multiplier",
+        "output_multiplier",
+        "applies_per",
+      }
+      if set(long_context) != required_long_context:
+        raise ValueError(
+          f"Pricing model {model} long_context requires exactly "
+          f"{sorted(required_long_context)}"
+        )
+      if (
+        not isinstance(long_context["input_token_threshold"], int)
+        or long_context["input_token_threshold"] < 0
+      ):
+        raise ValueError(
+          f"Pricing model {model} requires a non-negative long context threshold"
+        )
+      for field in ("input_multiplier", "output_multiplier"):
+        value = long_context[field]
+        if not isinstance(value, (int, float)) or value < 1:
+          raise ValueError(
+            f"Pricing model {model} requires {field} of at least one"
+          )
+      if long_context["applies_per"] != "request":
+        raise ValueError(
+          f"Pricing model {model} long_context applies_per must be request"
+        )
+  return {
+    "applied": True,
+    "snapshot": pricing,
+    "limitations": pricing["limitations"],
+  }
+
+
+def api_reference_estimate(
+  pricing: dict[str, Any],
+  usage: dict[str, Any],
+  model: str | None,
+  billing_mode: str,
+) -> dict[str, Any]:
+  base = {
+    "available": False,
+    "status": "unavailable",
+    "currency": (
+      pricing["snapshot"]["currency"]
+      if pricing.get("snapshot")
+      else None
+    ),
+    "amount": None,
+    "base_rate_amount": None,
+    "actual_charge": False,
+    "billing_mode": billing_mode,
+    "calculation": None,
+    "long_context_assessment": None,
+    "limitations": [
+      "This is an API reference estimate, not an observed charge.",
+      *pricing.get("limitations", []),
+    ],
+  }
+  if not pricing.get("applied") or model is None:
+    return base
+  rates = pricing["snapshot"]["models"].get(model)
+  if rates is None:
+    base["limitations"].append(f"No price entry exists for model {model}.")
+    return base
+  required_usage = ("input_tokens", "cached_input_tokens", "output_tokens")
+  if not all(isinstance(usage.get(field), int) for field in required_usage):
+    base["limitations"].append("Observed token usage is incomplete.")
+    return base
+  input_tokens = usage["input_tokens"]
+  cached_tokens = usage["cached_input_tokens"]
+  output_tokens = usage["output_tokens"]
+  uncached_tokens = max(input_tokens - cached_tokens, 0)
+  input_cost = uncached_tokens * rates["input"] / 1_000_000
+  cached_cost = cached_tokens * rates["cached_input"] / 1_000_000
+  output_cost = output_tokens * rates["output"] / 1_000_000
+  amount --- /dev/null
+++ b/baseline/scripts/render_eval_report.py
@@ -0,0 +1,191 @@
+#!/usr/bin/env python3
+"""Render a canonical skill evaluation evidence report as Markdown."""
+
+import argparse
+import json
+from pathlib import Path
+from typing import Any
+
+from eval_report import atomic_write_text
+
+
+def render_report(report: dict[str, Any]) -> str:
+  operation = report["operation"]
+  estimate = report["api_reference_estimate"]
+  lines = [
+    f"# Evaluation evidence: {operation['id']}",
+    "",
+    f"- Operation: `{operation['type']}`",
+    f"- Status: `{operation['status']}`",
+    f"- Provenance: `{report['provenance']}`",
+    f"- Started: `{report['started_at']}`",
+    f"- Finished: `{report['finished_at']}`",
+    f"- Duration: `{report['duration_ms']} ms`",
+    f"- Executor model: `{report['runtime']['executor']['model'] or 'configured default'}`",
+    f"- Executor effort: `{report['runtime']['executor']['reasoning_effort'] or 'configured default'}`",
+    f"- Codex CLI: `{report['environment']['codex_cli']['version'] or 'unavailable'}`",
+    f"- Authentication: `{report['environment']['authentication']['mode']}`",
+    f"- Runner SHA-256: `{report['environment']['runner']['sha256']}`",
+    "",
+    "## Consumption",
+    "",
+    _usage_line(report["usage"]),
+    _usage_event_summary(report["usage"]),
+    (
+      f"- Sessions: planned `{report['sessions']['planned']['total']}`, "
+      f"executed `{report['sessions']['executed']['total']}`"
+    ),
+    "",
+    "## API reference estimate",
+    "",
+  ]
+  if estimate["available"]:
+    lines.extend([
+      (
+        f"- Reference amount: `{estimate['amount']:.12f} "
+        f"{estimate['currency']}`"
+      ),
+      f"- Billing mode: `{estimate['billing_mode']}`",
+      "- This is not an actual charge.",
+    ])
+  else:
+    lines.extend([
+      "- Reference amount: unavailable",
+      "- This is not an actual charge.",
+    ])
+    if estimate.get("base_rate_amount") is not None:
+      lines.append(
+        f"- Base-rate amount: `{estimate['base_rate_amount']:.12f} "
+        f"{estimate['currency']}`"
+      )
+  lines.append(f"- Est
```

Truncations:
- `baseline/SKILL.md`: per file diff limit
- `baseline/references/eval-contract.md`: per file diff limit
- `baseline/scripts/eval_report.py`: per file diff limit
- `baseline/scripts/render_eval_report.py`: report diff limit
- `baseline/scripts/run_skill_evals.py`: file capture limit
- `baseline/scripts/run_skill_evals.py`: per file diff limit
- `baseline/scripts/run_skill_evals.py`: report diff limit
- `baseline/scripts/tests/__init__.py`: report diff limit
- `baseline/scripts/tests/test_cost_efficient_workflow.py`: per file diff limit
- `baseline/scripts/tests/test_cost_efficient_workflow.py`: report diff limit
- `baseline/scripts/tests/test_execution_evidence_report.py`: per file diff limit
- `baseline/scripts/tests/test_execution_evidence_report.py`: report diff limit
- `baseline/scripts/tests/test_run_skill_evals.py`: file capture limit
- `baseline/scripts/tests/test_run_skill_evals.py`: per file diff limit
- `baseline/scripts/tests/test_run_skill_evals.py`: report diff limit
- `candidate/SKILL.md`: per file diff limit
- `candidate/SKILL.md`: report diff limit
- `candidate/agents/openai.yaml`: report diff limit
- `candidate/evals/cases/fixture-email-redaction-reminder/case.json`: report diff limit
- `candidate/evals/cases/fixture-email-redaction-reminder/fixture/check_reminder.py`: report diff limit
- `candidate/evals/suite.json`: report diff limit
- `candidate/references/eval-contract.md`: per file diff limit
- `candidate/references/eval-contract.md`: report diff limit
- `candidate/references/eval-plan.schema.json`: report diff limit
- `candidate/references/eval-result.schema.json`: report diff limit
- `candidate/scripts/compare_model_reports.py`: report diff limit
- `candidate/scripts/eval_report.py`: per file diff limit
- `candidate/scripts/eval_report.py`: report diff limit
- `candidate/scripts/render_eval_report.py`: report diff limit
- `candidate/scripts/run_skill_evals.py`: file capture limit
- `candidate/scripts/run_skill_evals.py`: per file diff limit
- `candidate/scripts/run_skill_evals.py`: report diff limit
- `candidate/scripts/tests/__init__.py`: report diff limit
- `candidate/scripts/tests/test_cost_efficient_workflow.py`: per file diff limit
- `candidate/scripts/tests/test_cost_efficient_workflow.py`: report diff limit
- `candidate/scripts/tests/test_execution_evidence_report.py`: per file diff limit
- `candidate/scripts/tests/test_execution_evidence_report.py`: report diff limit
- `candidate/scripts/tests/test_run_skill_evals.py`: file capture limit
- `candidate/scripts/tests/test_run_skill_evals.py`: per file diff limit
- `candidate/scripts/tests/test_run_skill_evals.py`: report diff limit

## Observation 9: runner-progress-output

- Status: `PASS`
- Role: `regression`
- Repetition: `1`
- Duration: `889 ms`
- Workspace retention: `removed`
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

## Observation 10: impact-gate-selection

- Status: `PASS`
- Role: `regression`
- Repetition: `1`
- Duration: `74548 ms`
- Workspace retention: `removed`
- Tokens: input `245216`, cached input `203008`, output `2778`, reasoning output `626`
- Normalized usage events: `1`, complete `true`, scopes `turn`

### Executor account

Diagnosis:

Approach:
- Ran the repository scoped public `plan` operation exactly once with promotion workflow and deterministic impact.
- Omitted explicit case selection so the runner selected applicable suite cases.

Decisions:
- Classified the stream and exit status change as deterministic.
- Used `target-skill` as candidate and `target-baseline` as baseline.

Rejected Alternatives:
- None recorded.

Key Changes:
- Persisted planning stdout, stderr, and decimal exit code in the requested files.

Validation:
- JSON schema validation passed.
- `plan-stderr.log` is 0 bytes.
- `plan-exit-code.txt` contains `0`.

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
@@ -0,0 +1,96 @@
+{
+  "operation": "plan",
+  "workflow": "promotion",
+  "promotion_eligible": true,
+  "skill": "/tmp/persist-eval-evidence.auoqZx/promotion-2-artifacts/validate-change-tox6vqmn/impact-gate-selection-zh8_4_vo/target-skill",
+  "baseline": "/tmp/persist-eval-evidence.auoqZx/promotion-2-artifacts/validate-change-tox6vqmn/impact-gate-selection-zh8_4_vo/target-baseline",
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
+    "python3 /tmp/persist-eval-evidence.auoqZx/promotion-2-artifacts/validate-change-tox6vqmn/impact-gate-selection-zh8_4_vo/.agents/skills/develop-skill-with-evals/scripts/run_skill_evals.py validate-change --skill /tmp/persist-eval-evidence.auoqZx/promotion-2-artifacts/validate-change-tox6vqmn/impact-gate-selection-zh8_4_vo/target-skill --baseline /tmp/persist-eval-evidence.auoqZx/promotion-2-artifacts/validate-change-tox6vqmn/impact-gate-selection-zh8_4_vo/target-baseline --impact deterministic --case runner-output --approved-model-sessions 8",
+    "python3 .system/skill-creator/scripts/quick_validate.py /tmp/persist-eval-evidence.auoqZx/promotion-2-artifacts/validate-change-tox6vqmn/impact-gate-selection-zh8_4_vo/target-skill"
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
+  "evaluation_fingerprint": "f15a456bd81c8a797a6f316c842c84995d29755039cf14e18015a17127522b9d"
+}
--- /dev/null
+++ b/plan-exit-code.txt
@@ -0,0 +1 @@
+0
```

## Observation 11: auditable-runtime-contract

- Status: `PASS`
- Role: `regression`
- Repetition: `1`
- Duration: `285 ms`
- Workspace retention: `removed`
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

## Observation 12: explicit-runtime-promotion-workflow

- Status: `PASS`
- Role: `regression`
- Repetition: `1`
- Duration: `140074 ms`
- Workspace retention: `removed`
- Tokens: input `628617`, cached input `571648`, output `4716`, reasoning output `1105`
- Normalized usage events: `1`, complete `true`, scopes `turn`

### Executor account

Diagnosis: The renderer uppercased input without first removing surrounding whitespace.

Approach:
- Applied `.strip().upper()`.
- Ran diagnostic plan, probe, promotion plan, and validation once each in the required order.

Decisions:
- Classified the change as deterministic.
- Authorized zero model sessions, matching both displayed plans.

Rejected Alternatives:
- None recorded.

Key Changes:
- Surrounding whitespace is now removed before uppercase conversion.
- `sample-skill/SKILL.md` remained unchanged.

Validation:
- Skill structural validation passed.
- Executor and judge runtime declarations matched the requested models and medium effort.
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
@@ -0,0 +1,95 @@
+{
+  "operation": "plan",
+  "workflow": "diagnostic",
+  "promotion_eligible": false,
+  "skill": "/tmp/persist-eval-evidence.auoqZx/promotion-2-artifacts/validate-change-tox6vqmn/explicit-runtime-promotion-workflow-krj44wqh/sample-skill",
+  "baseline": "/tmp/persist-eval-evidence.auoqZx/promotion-2-artifacts/validate-change-tox6vqmn/explicit-runtime-promotion-workflow-krj44wqh/sample-baseline",
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
+    "python3 /tmp/persist-eval-evidence.auoqZx/promotion-2-artifacts/validate-change-tox6vqmn/explicit-runtime-promotion-workflow-krj44wqh/.agents/skills/develop-skill-with-evals/scripts/run_skill_evals.py probe-change --skill /tmp/persist-eval-evidence.auoqZx/promotion-2-artifacts/validate-change-tox6vqmn/explicit-runtime-promotion-workflow-krj44wqh/sample-skill --baseline /tmp/persist-eval-evidence.auoqZx/promotion-2-artifacts/validate-change-tox6vqmn/explicit-runtime-promotion-workflow-krj44wqh/sample-baseline --impact deterministic --case trim-uppercase --model gpt-5.6-sol --reasoning-effort medium --judge-model gpt-5.6-terra --judge-reasoning-effort medium --approved-model-sessions 8",
+    "python3 .system/skill-creator/scripts/quick_validate.py /tmp/persist-eval-evidence.auoqZx/promotion-2-artifacts/validate-change-tox6vqmn/explicit-runtime-promotion-workflow-krj44wqh/sample-skill"
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
+  "skill": "/tmp/persist-eval-evidence.auoqZx/promotion-2-artifacts/validate-change-tox6vqmn/explicit-runtime-promotion-workflow-krj44wqh/sample-skill",
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
+    "skill": "/tmp/persist-eval-evidence.auoqZx/promotion-2-artifacts/validate-change-tox6vqmn/explicit-runtime-promotion-workflow-krj44wqh/sample-skill",
+    "baseline": "/tmp/persist-eval-evidence.auoqZx/promotion-2-artifacts/validate-change-tox6vqmn/explicit-runtime-promotion-workflow-krj44wqh/sample-baseline",
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
+      "python3 /tmp/persist-eval-evidence.auoqZx/promotion-2-artifacts/validate-change-tox6vqmn/explicit-runtime-promotion-workflow-krj44wqh/.agents/skills/develop-skill-with-evals/scripts/run_skill_evals.py probe-change --skill /tmp/persist-eval-evidence.auoqZx/promotion-2-artifacts/validate-change-tox6vqmn/explicit-runtime-promotion-workflow-krj44wqh/sample-skill --baseline /tmp/persist-eval-evidence.auoqZx/promotion-2-artifacts/validate-change-tox6vqmn/explicit-runtime-promotion-workflow-krj44wqh/sample-baseline --impact deterministic --case trim-uppercase --model gpt-5.6-sol --reasoning-effort medium --judge-model gpt-5.6-terra --judge-reasoning-effort medium --approved-model-sessions 0",
+      "python3 .system/skill-creator/scripts/quick_validate.py /tmp/persist-eval-evidence.auoqZx/promotion-2-artifacts/validate-change-tox6vqmn/explicit-runtime-promotion-workflow-krj44wqh/sample-skill"
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
+            "stderr": "Traceback (most recent call last):\n  File \"/tmp/skill-eval-artifacts/probe-change-cpduubub/trim-uppercase-t7mznjus/check_trim.py\", line 16, in <module>\n    assert completed.stdout == \"HELLO\\n\"\nAssertionError\n"
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
+  "skill": "/tmp/persist-eval-evidence.auoqZx/promotion-2-artifacts/validate-change-tox6vqmn/explicit-runtime-promotion-workflow-krj44wqh/sample-skill",
+  "baseline": "/tmp/persist-eval-evidence.auoqZx/promotion-2-artifacts/validate-change-tox6vqmn/explicit-runtime-promotion-workflow-krj44wqh/sample-baseline",
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
+    "python3 /tmp/persist-eval-evidence.auoqZx/promotion-2-artifacts/validate-change-tox6vqmn/explicit-runtime-promotion-workflow-krj44wqh/.agents/skills/develop-skill-with-evals/scripts/run_skill_evals.py validate-change --skill /tmp/persist-eval-evidence.auoqZx/promotion-2-artifacts/validate-change-tox6vqmn/explicit-runtime-promotion-workflow-krj44wqh/sample-skill --baseline /tmp/persist-eval-evidence.auoqZx/promotion-2-artifacts/validate-change-tox6vqmn/explicit-runtime-promotion-workflow-krj44wqh/sample-baseline --impact deterministic --case trim-uppercase --model gpt-5.6-sol --reasoning-effort medium --judge-model gpt-5.6-terra --judge-reasoning-effort medium --approved-model-sessions 8",
+    "python3 .system/skill-creator/scripts/quick_validate.py /tmp/persist-eval-evidence.auoqZx/promotion-2-artifacts/validate-change-tox6vqmn/explicit-runtime-promotion-workflow-krj44wqh/sample-skill"
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
+["probe-change", "--skill", "sample-skill", "--baseline", "sample-baseline", "--impact", "deterministic", "--approved-model-sessions", "0", "--model", "gpt-5.6-sol", "--reasoning-effort", "medium", "--judge-model", "gpt-5.6-terra", "--judge-reasoning-effort", "medium", "--codex-command", "./fake-codex"]
+["plan", "--skill", "sample-skill", "--baseline", "sample-baseline", "--impact", "deterministic", "--workflow", "promotion", "--model", "gpt-5.6-sol", "--reasoning-effort", "medium", "--judge-model", "gpt-5.6-terra", "--judge-reasoning-effort", "medium"]
+["validate-change", "--skill", "sample-skill", "--baseline", "sample-baseline", "--impact", "deterministic", "--approved-model-sessions", "0", "--model", "gpt-5.6-sol", "--reasoning-effort", "medium", "--judge-model", "gpt-5.6-terra", "--judge-reasoning-effort", "medium", "--codex-command", "./fake-codex"]
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
+  "skill": "/tmp/persist-eval-evidence.auoqZx/promotion-2-artifacts/validate-change-tox6vqmn/explicit-runtime-promotion-workflow-krj44wqh/sample-skill",
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
+    "skill": "/tmp/persist-eval-evidence.auoqZx/promotion-2-artifacts/validate-change-tox6vqmn/explicit-runtime-promotion-workflow-krj44wqh/sample-skill",
+    "baseline": "/tmp/persist-eval-evidence.auoqZx/promotion-2-artifacts/validate-change-tox6vqmn/explicit-runtime-promotion-workflow-krj44wqh/sample-baseline",
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
+      "python3 /tmp/persist-eval-evidence.auoqZx/promotion-2-artifacts/validate-change-tox6vqmn/explicit-runtime-promotion-workflow-krj44wqh/.agents/skills/develop-skill-with-evals/scripts/run_skill_evals.py validate-change --skill /tmp/persist-eval-evidence.auoqZx/promotion-2-artifacts/validate-change-tox6vqmn/explicit-runtime-promotion-workflow-krj44wqh/sample-skill --baseline /tmp/persist-eval-evidence.auoqZx/promotion-2-artifacts/validate-change-tox6vqmn/explicit-runtime-promotion-workflow-krj44wqh/sample-baseline --impact deterministic --case trim-uppercase --model gpt-5.6-sol --reasoning-effort medium --judge-model gpt-5.6-terra --judge-reasoning-effort medium --approved-model-sessions 0",
+      "python3 .system/skill-creator/scripts/quick_validate.py /tmp/persist-eval-evidence.auoqZx/promotion-2-artifacts/validate-change-tox6vqmn/explicit-runtime-promotion-workflow-krj44wqh/sample-skill"
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
+            "stderr": "Traceback (most recent call last):\n  File \"/tmp/skill-eval-artifacts/validate-change-wl090zcs/trim-uppercase-5d25eh83/check_trim.py\", line 16, in <module>\n    assert completed.stdout == \"HELLO\\n\"\nAssertionError\n"
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
+
```

Truncations:
- `validation.json`: per file diff limit

## Observation 13: cost-efficient-runtime-contract

- Status: `PASS`
- Role: `regression`
- Repetition: `1`
- Duration: `231 ms`
- Workspace retention: `removed`
- Tokens: input `unknown`, cached input `unknown`, output `unknown`, reasoning output `unknown`
- Normalized usage events: `0`, complete `false`, scopes `none`

### Executor account

Executor did not provide a structured response.

### Mechanical facts

- Mechanical result: `PASS`
- Oracle result: `PASS`
- Judge verdict: `PASS`
- `command: python3 check_cost_efficient_runtime.py`: `PASS`
- `evaluated skill remained unchanged`: `PASS`

### Changed files

- None.

### Sanitized diff

```diff

```

## Observation 14: execution-evidence-report

- Status: `PASS`
- Role: `candidate`
- Repetition: `2`
- Duration: `136332 ms`
- Workspace retention: `removed`
- Tokens: input `343081`, cached input `296448`, output `5831`, reasoning output `1164`
- Normalized usage events: `1`, complete `true`, scopes `turn`

### Executor account

Diagnosis: No evaluation failure was found. The successful temporary workspace was removed by the runner.

Approach:
- Loaded the repository scoped evaluation skill and its required foundation and contract.
- Executed the named case once with all required nested paths absolute.
- Replayed and inspected the canonical JSON and Markdown representations.

Decisions:
- Used the `run` operation for the single authorized case.
- Kept durable evidence local and treated it as execution evidence, not promotion evidence.

Rejected Alternatives:
- Did not rerun the evaluation.
- Did not commit or publish generated evidence.

Key Changes:
- Generated the requested evaluation JSON and durable evidence.
- Generated `.eval-replayed-report.md` from the canonical report without another model invocation.

Validation:
- Evaluation status is `PASS`.
- Evaluation JSON conforms to the installed result schema.
- Replay and original Markdown have identical SHA-256 hashes.
- Excluded `.eval-private` content is absent from both inspected report representations.
- No requested input file was edited.

### Mechanical facts

- Mechanical result: `PASS`
- Oracle result: `PASS`
- Judge verdict: `PASS`
- `executor exit code`: `PASS`
- `executor response schema`: `PASS`
- `required path: .eval-evaluation.json`: `PASS`
- `required path: .eval-replayed-report.md`: `PASS`
- `forbidden changed path: .agents/skills/**`: `PASS`
- `forbidden changed path: audit-runner`: `PASS`
- `forbidden changed path: fake-codex`: `PASS`
- `forbidden changed path: pricing.json`: `PASS`
- `forbidden changed path: sample-skill/**`: `PASS`
- `evaluated skill remained unchanged`: `PASS`

### Changed files

- None.

### Sanitized diff

```diff

```

## Observation 15: execution-evidence-report

- Status: `PASS`
- Role: `candidate`
- Repetition: `3`
- Duration: `124162 ms`
- Workspace retention: `removed`
- Tokens: input `341152`, cached input `307456`, output `4653`, reasoning output `1060`
- Normalized usage events: `1`, complete `true`, scopes `turn`

### Executor account

Diagnosis: No execution or report integrity failures were found. The ordinary `run` operation is correctly marked as not promotion eligible.

Approach:
- Executed the behavioral case once through `./audit-runner`.
- Rendered Markdown from the canonical report without another model invocation.
- Validated JSON structure, report facts, evidence sanitization, and replay consistency.

Decisions:
- Used the single case `run` operation.
- Suppressed progress to preserve pure JSON stdout.
- Left all generated evidence uncommitted and unpublished.

Rejected Alternatives:
- Did not use promotion validation because the request specified one case execution.

Key Changes:
- Generated the requested evaluation and durable evidence artifacts only.

Validation:
- Overall status: PASS.
- Mechanical contract: PASS.
- Evaluated skill unchanged check: PASS.
- Result schema validation: PASS.
- Markdown replay comparison: PASS.
- Tracked diff check: PASS.

### Mechanical facts

- Mechanical result: `PASS`
- Oracle result: `PASS`
- Judge verdict: `PASS`
- `executor exit code`: `PASS`
- `executor response schema`: `PASS`
- `required path: .eval-evaluation.json`: `PASS`
- `required path: .eval-replayed-report.md`: `PASS`
- `forbidden changed path: .agents/skills/**`: `PASS`
- `forbidden changed path: audit-runner`: `PASS`
- `forbidden changed path: fake-codex`: `PASS`
- `forbidden changed path: pricing.json`: `PASS`
- `forbidden changed path: sample-skill/**`: `PASS`
- `evaluated skill remained unchanged`: `PASS`

### Changed files

- None.

### Sanitized diff

```diff

```

## Integrity

- Report digest: `sha256:99b5603a64f694d5e5eefd037bda93117ec6d9d3e5343cdfb5cb8525a81c6949`
