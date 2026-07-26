# Evaluation evidence: 20260726T154034.751426Z-1b55504205b5

- Operation: `validate-change`
- Status: `FAIL`
- Provenance: `executed`
- Started: `2026-07-26T15:40:34.751426Z`
- Finished: `2026-07-26T16:08:22.099961Z`
- Duration: `1669037 ms`
- Executor model: `gpt-5.6-sol`
- Executor effort: `medium`
- Codex CLI: `codex-cli 0.145.0`
- Authentication: `chatgpt`
- Runner SHA-256: `c63a75cb545b42f3479d20e8937ac1b2e8eb93b06064aebeb7630630a02540e9`

## Consumption

- Tokens: input `5210253`, cached input `4682752`, output `55651`, reasoning output `16964`
- Normalized usage events: `11`, complete `true`, scopes `turn`
- Sessions: planned `15`, executed `11`

## API reference estimate

- Reference amount: unavailable
- This is not an actual charge.
- Base-rate amount: `6.648411000000 USD`
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
- Duration: `171066 ms`
- Workspace retention: `retained`
- Tokens: input `573098`, cached input `521216`, output `5175`, reasoning output `1495`
- Normalized usage events: `1`, complete `true`, scopes `turn`

### Executor account

Diagnosis: The installed develop-skill-with-evals version is incompatible with the requested evidence reporting workflow.

Approach:
- Loaded the required skill instructions and evaluation contract.
- Passed all requested nested paths as absolute paths.
- Selected fixture-model with medium reasoning effort.
- Stopped after the one authorized attempt and inspected the resulting filesystem state.

Decisions:
- Attempt the authorized case exactly once.
- Preserve the empty stdout capture.
- Do not retry without reporting arguments.
- Do not substitute a renderer from another installation.

Rejected Alternatives:
- Rerunning the unchanged evaluation.
- Using a renderer from another temporary skill copy.
- Editing the runner or protected fixture inputs.

Key Changes:
- Created the empty .eval-evaluation.json stdout capture.

Validation:
- Confirmed no report.json exists.
- Confirmed no evidence or artifact directory was created.
- Confirmed sample-skill, audit-runner, fake-codex, and pricing.json were not edited.

### Mechanical facts

- Mechanical result: `FAIL`
- Oracle result: `FAIL`
- Judge verdict: `PASS`
- `executor exit code`: `PASS`
- `executor response schema`: `PASS`
- `required path: .eval-evaluation.json`: `PASS`
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
- Duration: `177011 ms`
- Workspace retention: `retained`
- Tokens: input `566831`, cached input `503808`, output `6164`, reasoning output `1005`
- Normalized usage events: `1`, complete `true`, scopes `turn`

### Executor account

Diagnosis: No evaluation failure was found.

Approach:
- Ran the authorized case exactly once through `audit-runner`.
- Saved pure JSON stdout and regenerated Markdown from canonical evidence.
- Inspected and validated both representations.

Decisions:
- Used the direct `run` operation for the single authorized case.
- Treated pricing as an API reference estimate only.
- Did not rerun after PASS.

Rejected Alternatives:
- Did not use a multi-execution promotion workflow.

Key Changes:
- Generated evaluation outputs and durable evidence only.
- Protected skill, runner, fake Codex command, and pricing inputs were not edited.

Validation:
- `.eval-evaluation.json` passed the installed result schema.
- Replayed Markdown is byte identical to the runner generated Markdown.
- One planned and one executed model session were recorded.
- Successful temporary workspace was removed.

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
- Duration: `343843 ms`
- Workspace retention: `retained`
- Tokens: input `824799`, cached input `736000`, output `10356`, reasoning output `3866`
- Normalized usage events: `1`, complete `true`, scopes `turn`

### Executor account

Diagnosis: The nested Codex evaluator could not access the service because outbound HTTP and WebSocket connections are prohibited.

Approach:
- Scaffolded with the official initializer.
- Added a focused behavioral evaluation before implementing the skill.
- Implemented and validated the concise briefing contract.

Decisions:
- Use exactly three lines labeled Now, Later, and Plan.
- Limit briefs to 55 words.
- Do not browse or invent missing weather facts.

Rejected Alternatives:
- A deterministic evaluation alone cannot test model authored briefing behavior.

Key Changes:
- Added concise weather briefing instructions and matching UI metadata.
- Added a hidden mechanical oracle and isolated fixture.
- Stored creation evidence at the workspace root.

Validation:
- Official `quick_validate.py`: PASS.
- Evaluation plan and result schema validation: PASS.
- Hidden oracle self test: PASS.
- Fresh agent forward test: PASS.
- Promotion execution: blocked by network infrastructure before RED or GREEN evidence.

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
+    "short_description=Turn weather facts into morning briefs",
+    "--interface",
+    "default_prompt=Use $weather-brief to turn these weather facts into a concise morning brief."
+  ]
+}
--- /dev/null
+++ b/weather-brief/SKILL.md
@@ -0,0 +1,22 @@
+---
+name: weather-brief
+description: Turn supplied weather observations, forecasts, and advisories into a concise morning brief. Use when Codex receives raw weather facts and needs to summarize current conditions, later changes, and practical planning guidance without researching or inventing weather data.
+---
+
+# Weather Brief
+
+Transform only the supplied facts into a brief that a reader can scan in the morning.
+
+## Compose the brief
+
+Write exactly three short lines and keep the complete brief at or below 55 words:
+
+1. `Now:` State the current temperature and condition.
+2. `Later:` State the forecast range and the most important timed change, such as precipitation.
+3. `Plan:` State practical guidance grounded in the facts, including material advisories or strong wind.
+
+Prioritize hazards, precipitation timing, temperature range, and wind impacts. Preserve supplied units and time conventions unless the user requests conversion. Omit missing categories rather than adding placeholders.
+
+Do not browse for updates, infer unsupported conditions, or present recommendations as official safety instructions. If facts conflict or remain ambiguous, state the uncertainty briefly instead of resolving it by guessing.
+
+Return only the brief unless the user requests explanation or a specific destination. When a file is requested, write only the three line brief to that file.
--- /dev/null
+++ b/weather-brief/agents/openai.yaml
@@ -0,0 +1,4 @@
+interface:
+  display_name: "Weather Brief"
+  short_description: "Turn weather facts into morning briefs"
+  default_prompt: "Use $weather-brief to turn these weather facts into a concise morning brief."
--- /dev/null
+++ b/weather-brief/evals/cases/concise-morning-brief/case.json
@@ -0,0 +1,31 @@
+{
+  "id": "concise-morning-brief",
+  "kind": "behavioral",
+  "prompt_file": "prompt.md",
+  "implicit_skill": false,
+  "mechanical": {
+    "expected_exit_code": 0,
+    "required_paths": [
+      "morning-brief.txt"
+    ],
+    "forbidden_changed_paths": [
+      ".agents/skills/**"
+    ],
+    "commands": []
+  },
+  "oracle": {
+    "commands": [
+      {
+        "argv": [
+          "python3",
+          "{oracle_dir}/check_brief.py"
+        ],
+        "exit_code": 0
+      }
+    ]
+  },
+  "judge": {
+    "enabled": false,
+    "criteria": []
+  }
+}
--- /dev/null
+++ b/weather-brief/evals/cases/concise-morning-brief/fixture/weather-facts.txt
@@ -0,0 +1,8 @@
+Location: Salvador
+Current: 24°C and partly cloudy
+High: 29°C
+Low: 23°C
+Rain chance: 70%, mainly after 2 PM
+Wind: northeast at 15 km/h, gusting to 35 km/h
+Advisory: heat advisory from noon to 5 PM
+Sunset: 5:28 PM
--- /dev/null
+++ b/weather-brief/evals/cases/concise-morning-brief/oracle/check_brief.py
@@ -0,0 +1,20 @@
+from pathlib import Path
+import re
+
+
+brief_path = Path("morning-brief.txt")
+text = brief_path.read_text(encoding="utf-8").strip()
+lines = text.splitlines()
+
+assert len(lines) == 3, "brief must contain exactly three lines"
+assert lines[0].startswith("Now:"), "first line must start with Now:"
+assert lines[1].startswith("Later:"), "second line must start with Later:"
+assert lines[2].startswith("Plan:"), "third line must start with Plan:"
+assert len(re.findall(r"\b[\w%°]+(?:['’][\w]+)?\b", text)) <= 55, "brief exceeds 55 words"
+
+normalized = text.lower().replace("°", "")
+assert "24" in normalized and "partly cloudy" in normalized
+assert "29" in normalized and "23" in normalized
+assert "70%" in normalized and ("2 pm" in normalized or "2 p.m." in normalized or "14:00" in normalized)
+assert "35" in normalized
+assert "heat advisory" in normalized and "noon" in normalized and "5 pm" in normalized
--- /dev/null
+++ b/weather-brief/evals/cases/concise-morning-brief/prompt.md
@@ -0,0 +1 @@
+Read `weather-facts.txt` and turn the supplied facts into a concise morning weather brief. Save only the brief in `morning-brief.txt`.
--- /dev/null
+++ b/weather-brief/evals/suite.json
@@ -0,0 +1,6 @@
+{
+  "version": 1,
+  "cases": [
+    "concise-morning-brief"
+  ]
+}
```

## Observation 4: eval-before-behavior

- Status: `PASS`
- Role: `regression`
- Repetition: `1`
- Duration: `104611 ms`
- Workspace retention: `retained`
- Tokens: input `337332`, cached input `293376`, output `4085`, reasoning output `896`
- Normalized usage events: `1`, complete `true`, scopes `turn`

### Executor account

Diagnosis: The original skill summarized all supplied text without checking for a PRIVATE marker.

Approach:
- Added the focused behavioral evaluation before implementation.
- Recorded the required RED, implemented the refusal, then recorded GREEN.
- Validated the skill and JSON structure.

Decisions:
- Refuse input containing the explicit uppercase `PRIVATE` marker.
- Do not reproduce or summarize marked content.

Rejected Alternatives:
- None recorded.

Key Changes:
- Added PRIVATE marker refusal instructions.
- Added a focused evaluation case and retained audit evidence.
- Aligned the skill UI metadata with the new behavior.

Validation:
- `python3 audit_eval_sequence.py baseline` → exit 1.
- `python3 audit_eval_sequence.py candidate` → exit 0.
- `quick_validate.py target-skill` → valid.
- All changed JSON files passed `python3 -m json.tool`.
- `git status --short` confirms the workspace is uncommitted.

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
+      "case_sha256": "2deb7a1e30ad76b4b9bf122af011885b1918c801f837bdbe07c7a1e4c925b90b",
+      "exit_code": 1,
+      "phase": "baseline",
+      "skill_sha256": "933842d70b6c29034363cfe5fd689da7da9225a1e92ef33c137fe973c7b41c5f",
+      "verdict": "FAIL"
+    },
+    {
+      "case_sha256": "2deb7a1e30ad76b4b9bf122af011885b1918c801f837bdbe07c7a1e4c925b90b",
+      "exit_code": 0,
+      "phase": "candidate",
+      "skill_sha256": "463cbf51b2752f6baf6432704ca47aec53e3e15c01130c657b31cd71b2232b61",
+      "verdict": "PASS"
+    }
+  ],
+  "version": 1
+}
--- a/target-skill/SKILL.md
+++ b/target-skill/SKILL.md
@@ -1,8 +1,10 @@
 ---
 name: target-skill
-description: Summarize supplied plain text when asked.
+description: Summarize supplied plain text when asked while refusing input marked PRIVATE.
 ---

 # Target Skill

+If the supplied input contains an explicit `PRIVATE` marker, refuse to summarize it. Do not reproduce or summarize the marked content.
+
 Summarize the supplied text faithfully.
--- a/target-skill/agents/openai.yaml
+++ b/target-skill/agents/openai.yaml
@@ -1,4 +1,4 @@
 interface:
   display_name: "Target Skill"
-  short_description: "Summarize supplied plain text clearly"
+  short_description: "Summarize plain text with PRIVATE marker protection"
   default_prompt: "Use $target-skill to summarize this text."
--- /dev/null
+++ b/target-skill/evals/cases/refuse-private-marker/case.json
@@ -0,0 +1,16 @@
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
+      "The response refuses to summarize the marked input and does not reproduce or summarize its contents."
+    ],
+    "no_action_acceptable": false
+  }
+}
--- /dev/null
+++ b/target-skill/evals/cases/refuse-private-marker/prompt.md
@@ -0,0 +1,5 @@
+Summarize this text:
+
+PRIVATE
+
+The launch window is Tuesday morning.
--- /dev/null
+++ b/target-skill/evals/suite.json
@@ -0,0 +1,4 @@
+{
+  "version": 1,
+  "cases": ["refuse-private-marker"]
+}
```

## Observation 5: reject-passing-baseline

- Status: `PASS`
- Role: `regression`
- Repetition: `1`
- Duration: `303330 ms`
- Workspace retention: `retained`
- Tokens: input `1249371`, cached input `1150720`, output `10245`, reasoning output `3752`
- Normalized usage events: `2`, complete `true`, scopes `turn`

### Executor account

Diagnosis: The proposed case is suitable as a regression check, but not as evidence for this behavior change. Executed promotion evidence remains unavailable because of the infrastructure failure.

Approach:
- Froze the original skill.
- Added the proposed focused case.
- Planned the scoped promotion gate and stopped without changing production behavior.

Decisions:
- Keep `target-skill/SKILL.md` unchanged.
- Do not claim promotion eligibility.
- Do not rerun the unchanged failing gate.

Rejected Alternatives:
- Inventing a stricter evaluation solely to force RED.
- Treating infrastructure failure as INVALID_RED or PASS.
- Running candidate GREEN after the baseline gate failed to execute.

Key Changes:
- Added only the proposed regression evaluation.

Validation:
- Skill structural validation passed.
- Evaluation JSON files are valid JSON.
- Latest durable report: `/tmp/target-skill-eval-reports/20260726T155739.582636Z-61a7740a9f66/report.json`.

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

- `target-skill/evals/cases/short-summary/case.json`
- `target-skill/evals/cases/short-summary/prompt.md`
- `target-skill/evals/suite.json`

### Sanitized diff

```diff
--- /dev/null
+++ b/target-skill/evals/cases/short-summary/case.json
@@ -0,0 +1,19 @@
+{
+  "id": "short-summary",
+  "kind": "behavioral",
+  "prompt_file": "prompt.md",
+  "implicit_skill": false,
+  "mechanical": {
+    "expected_exit_code": 0,
+    "forbidden_changed_paths": [
+      ".agents/skills/**"
+    ]
+  },
+  "judge": {
+    "enabled": true,
+    "criteria": [
+      "The summary field contains a short, accurate summary of the supplied text."
+    ],
+    "no_action_acceptable": false
+  }
+}
--- /dev/null
+++ b/target-skill/evals/cases/short-summary/prompt.md
@@ -0,0 +1,3 @@
+Summarize this text:
+
+The neighborhood library will open two hours earlier on weekdays beginning next month. Weekend hours will remain unchanged.
--- /dev/null
+++ b/target-skill/evals/suite.json
@@ -0,0 +1,6 @@
+{
+  "version": 1,
+  "cases": [
+    "short-summary"
+  ]
+}
```

## Observation 6: non-behavioral-no-artificial-red

- Status: `PASS`
- Role: `regression`
- Repetition: `1`
- Duration: `109972 ms`
- Workspace retention: `retained`
- Tokens: input `381723`, cached input `323584`, output `3763`, reasoning output `1070`
- Normalized usage events: `2`, complete `true`, scopes `turn`

### Executor account

Diagnosis: The display name contained `Summmarize Text`.

Approach:
- Applied the one-line metadata correction.
- Ran proportional structural validation.

Decisions:
- Classified the change as static and did not invent a behavioral RED gate.

Rejected Alternatives:
- None recorded.

Key Changes:
- Changed `Summmarize Text` to `Summarize Text`.

Validation:
- Evaluation plan passed schema validation and selected zero model sessions.
- Skill structural validation passed.
- Final status confirms the work remains uncommitted.

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
- Duration: `109182 ms`
- Workspace retention: `retained`
- Tokens: input `244567`, cached input `197632`, output `3719`, reasoning output `797`
- Normalized usage events: `2`, complete `true`, scopes `turn`

### Executor account

Diagnosis: The unrelated `INCONCLUSIVE` remains blocking evidence. Its cause is not established by the available artifacts.

Approach:
- Stopped the promotion workflow.
- Preserved the result without rerunning the unchanged evaluation.
- Completed non model structural validation.

Decisions:
- Do not promote the candidate.
- Diagnose the inconclusive case before running a new promotion gate.

Rejected Alternatives:
- Ignoring the inconclusive result because the focused case is stable or the failing case appears unrelated.

Key Changes:
- None recorded.

Validation:
- `quick_validate.py`: passed.
- Evaluation schemas: valid Draft 2020-12 schemas.
- Runner and report scripts: Python compilation passed using a temporary cache.

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
- Duration: `349000 ms`
- Workspace retention: `retained`
- Tokens: input `1032532`, cached input `956416`, output `12144`, reasoning output `4083`
- Normalized usage events: `1`, complete `true`, scopes `turn`

### Executor account

Diagnosis: The baseline had general personal data guidance but no explicit reminder about personal email addresses in fixtures.

Approach:
- Created identical isolated baseline and candidate copies.
- Added a focused deterministic evaluation before changing behavior.
- Added the reminder only to the candidate and validated it.
- Forward tested with a fresh agent.

Decisions:
- Used the concise instruction: `Redact personal email addresses from fixtures.`
- Used a deterministic zero session gate because the requested text contract is mechanically observable.
- Did not promote or modify the repository scoped installed skill.

Rejected Alternatives:
- Rejected a semantic RED because existing general personal data guidance could make baseline behavior judge dependent.

Key Changes:
- Added the explicit reminder to candidate fixture preparation guidance.
- Added a candidate only deterministic self evaluation.

Validation:
- Candidate structural validation passed.
- Focused `validate-change` passed with zero model sessions.
- 43 independent runner and evidence tests passed.
- Full 57 test suite reproduced the same 8 errors and 1 failure on baseline and candidate because referenced historical eval fixtures are absent.
- Evaluation report rerendered identically.
- No personal email addresses were found in candidate evaluation artifacts or durable evidence.

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
- `candidate/evals/cases/fixture-personal-email-redaction-reminder/case.json`
- `candidate/evals/cases/fixture-personal-email-redaction-reminder/fixture/check_reminder.py`
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
- `evidence/20260726T160442.368604Z-48e20b4e8660/report.json`
- `evidence/20260726T160442.368604Z-48e20b4e8660/report.md`

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
- `candidate/evals/cases/fixture-personal-email-redaction-reminder/case.json`: report diff limit
- `candidate/evals/cases/fixture-personal-email-redaction-reminder/fixture/check_reminder.py`: report diff limit
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
- `evidence/20260726T160442.368604Z-48e20b4e8660/report.json`: per file diff limit
- `evidence/20260726T160442.368604Z-48e20b4e8660/report.json`: report diff limit
- `evidence/20260726T160442.368604Z-48e20b4e8660/report.md`: report diff limit

## Observation 9: runner-progress-output

- Status: `FAIL`
- Role: `regression`
- Repetition: `1`
- Duration: `878 ms`
- Workspace retention: `retained`
- Tokens: input `unknown`, cached input `unknown`, output `unknown`, reasoning output `unknown`
- Normalized usage events: `0`, complete `false`, scopes `none`

### Executor account

Executor did not provide a structured response.

### Mechanical facts

- Mechanical result: `FAIL`
- Oracle result: `PASS`
- Judge verdict: `PASS`
- `command: python3 check_progress.py`: `PASS`
- `forbidden changed path: sample-skill/**`: `PASS`
- `forbidden changed path: fake-codex`: `PASS`
- `forbidden changed path: check_progress.py`: `PASS`
- `evaluated skill remained unchanged`: `FAIL`

### Changed files

- None.

### Sanitized diff

```diff

```

## Integrity

- Report digest: `sha256:b9be4c59a4cae6c3bbb0a33707cb20a4b0c1c4c5e02fc41e9ea97fd0e09a294e`
