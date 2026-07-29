# Evaluation evidence: 20260729T184809.268321Z-a248a1eb23ca

- Operation: `validate-change`
- Status: `FAIL`
- Provenance: `executed`
- Started: `2026-07-29T18:48:09.268321Z`
- Finished: `2026-07-29T18:55:06.890067Z`
- Duration: `418090 ms`
- Executor model: `gpt-5.6-sol`
- Executor effort: `medium`
- Codex CLI: `codex-cli 0.146.0`
- Authentication: `chatgpt`
- Runner SHA-256: `64808412e5d77fbb0bac91a724053821acfe2fd4b38d05c2c92c657ec5065cd2`

## Consumption

- Tokens: input `327495`, cached input `244992`, output `14815`, reasoning output `2481`
- Normalized usage events: `2`, complete `true`, scopes `turn`
- Sessions: planned `4`, executed `2`

## API reference estimate

- Reference amount: `0.979461000000 USD`
- Billing mode: `chatgpt-plan`
- This is not an actual charge.
- Estimate status: `complete`
- Limitation: This is an API reference estimate, not an observed charge.
- Limitation: This dated table is an API reference and is not an observed ChatGPT charge.
- Limitation: Prompts above 272,000 input tokens use the documented higher rates; an exact estimate is unavailable when normalized telemetry does not expose request scoped input.
- Limitation: Cache write charges are not estimated because Codex JSONL usage does not identify cache writes.
- Limitation: Reasoning output tokens are reported separately but are already included in output tokens.

## Observation 1: documentation-impact-contract

- Status: `FAIL`
- Role: `baseline`
- Repetition: `1`
- Duration: `257571 ms`
- Workspace retention: `retained`
- Tokens: input `211368`, cached input `172288`, output `8091`, reasoning output `1129`
- Normalized usage events: `1`, complete `true`, scopes `turn`

### Executor account

Diagnosis: Planning task completed successfully.

Approach:
- Inspected the repository and canonical documentation sources.
- Created file scoped milestones, acceptance criteria, validation commands, and recovery guidance.
- Validated plan structure and existing Python and JSON behavior.

Decisions:
- Treat `timeout_seconds` as required while preserving `start(config)` return behavior.
- Update both canonical documentation sources for the public change.
- Rename `attempts` to `retry_count` with no documentation changes for the internal refactor.
- Use `python3` in validation commands.

Rejected Alternatives:
- None recorded.

Key Changes:
- The public plan coordinates `service.py`, `README.md`, and `config.json`.
- The internal plan requires `README.md` and `config.json` to remain byte identical.

Validation:
- Required section check passed for both plans.
- Checklist placement check passed.
- Existing service syntax, behavior, and JSON parsing checks passed.
- Confirmed no repository `__pycache__` artifact was created.

### Mechanical facts

- Mechanical result: `PASS`
- Oracle result: `FAIL`
- Judge verdict: `PASS`
- `executor exit code`: `PASS`
- `executor response schema`: `PASS`
- `required path: plans/public-change.md`: `PASS`
- `required path: plans/internal-change.md`: `PASS`
- `forbidden changed path: README.md`: `PASS`
- `forbidden changed path: config.json`: `PASS`
- `forbidden changed path: service.py`: `PASS`
- `forbidden changed path: .agents/skills/**`: `PASS`
- `evaluated skill remained unchanged`: `PASS`

### Changed files

- `plans/internal-change.md`
- `plans/public-change.md`

### Sanitized diff

```diff
--- /dev/null
+++ b/plans/internal-change.md
@@ -0,0 +1,160 @@
+# Rename the private retry local
+
+This ExecPlan is a living document. Keep `Progress`, `Decisions`, `Risks and Mitigations`, and `Lessons Learned` up to date as work advances.
+
+## Purpose / Big Picture
+
+Improve the internal clarity of `start(config)` by renaming its private local variable without changing anything a caller or configuration author can observe. After the refactor, the same input produces the same output, the same invalid input fails in the same way, and neither canonical documentation source changes.
+
+## Scope
+
+In scope is only the private local variable currently named `attempts` inside `service.py` and the references to that local within the same function. Focused behavior checks and explicit verification that `README.md` and `config.json` remain unchanged are also in scope.
+
+Out of scope are public function names or parameters, configuration keys or values, return behavior, error behavior, formatting unrelated code, and any edit to `README.md` or `config.json`. This plan describes future implementation only; creating the plan does not authorize implementation.
+
+## Definitions
+
+`start(config)` is the function in `service.py` that reads and returns the public `retries` setting. A private local variable exists only inside a function and is not part of the public API or configuration contract. Canonical means the authoritative repository source for a kind of public information: `README.md` is the canonical user documentation and `config.json` is the canonical public configuration reference.
+
+## Existing Context
+
+`service.py` contains one function. It reads `config["retries"]` into the private local `attempts` and immediately returns `attempts`. `README.md` says the service reads public settings from `config.json`; `config.json` contains `"retries": 3`. The repository has no test files, dependency manifest, or full validation script.
+
+The critical assumption is that the rename is purely internal. The dictionary key must remain exactly `"retries"`, the function must remain named `start` with the same parameter, and documentation must not change because no user facing contract changes.
+
+## Desired End State
+
+Within `service.py`, the local `attempts` is renamed to `retry_count` at both assignment and return. `start({"retries": 3})` still returns `3`, and missing `retries` still raises `KeyError("retries")`. `README.md` and `config.json` are byte for byte unchanged.
+
+## Milestones
+
+### Milestone 1: Record the unchanged contract
+
+#### Goal
+
+Capture the current behavior and canonical documentation fingerprints before editing so the refactor has a concrete comparison baseline.
+
+#### Changes
+
+Do not edit any file in this milestone. Run the current behavior checks and record the checksum output for `README.md` and `config.json` in this plan's `Lessons Learned` section before starting Milestone 2.
+
+#### Validation
+
+Run `python3 -c 'from service import start; assert start({"retries": 3}) == 3'`.
+
+Expected result: the command exits with status 0 and prints nothing.
+
+Run `python3 -c 'from service import start; start({})' 2>&1 | tail -n 1 | rg -x "KeyError: 'retries'"`.
+
+Expected result: the command exits with status 0, confirming the current missing key behavior.
+
+Run `sha256sum README.md config.json`.
+
+Expected result: the command prints one checksum for each canonical documentation file. Copy both exact lines into `Lessons Learned` before editing.
+
+#### Acceptance Criteria
+
+The success and failure behaviors are confirmed, and the plan contains the two prechange checksums needed to prove the public documentation remained untouched.
+
+### Milestone 2: Rename the private local
+
+#### Goal
+
+Improve the local name while producing no observable behavior, API, or configuration change.
+
+#### Changes
+
+Edit only `service.py`. Rename the local variable `attempts` to `retry_count` in its assignment and return statement. Leave the function name, parameter, dictionary key, indentation, control flow, and all other files unchanged.
+
+#### Validation
+
+Run `python3 -m py_compile service.py`.
+
+Expected result: the command exits with status 0.
+
+Run `python3 -c 'from service import start; assert start({"retries": 3}) == 3'`.
+
+Expected result: the command exits with status 0 and prints nothing.
+
+Run `python3 -c 'from service import start; start({})' 2>&1 | tail -n 1 | rg -x "KeyError: 'retries'"`.
+
+Expected result: the command exits with status 0, confirming unchanged error behavior.
+
+Run `rg -n 'attempts|retry_count|config\\[\"retries\"\\]' service.py`.
+
+Expected result: `retry_count` appears at assignment and return, the public key remains exactly `retries`, and `attempts` does not appear.
+
+#### Acceptance Criteria
+
+Only the private identifier changes. Both representative success and error scenarios behave exactly as they did before the edit.
+
+### Milestone 3: Prove documentation and public surfaces are unchanged
+
+#### Goal
+
+Finish with evidence that the internal refactor did not leak into public code or canonical documentation.
+
+#### Changes
+
+Do not make further edits unless validation exposes a discrepancy. If it does, restore the intended private only scope before rerunning all checks.
+
+#### Validation
+
+Run `sha256sum README.md config.json`.
+
+Expected result: both lines exactly match the prechange checksum lines recorded in `Lessons Learned`.
+
+Run `git diff --check`.
+
+Expected result: the command exits with status 0 and reports no whitespace errors.
+
+Run `git diff -- service.py README.md config.json`.
+
+Expected result: the only diff is the two occurrences of the private local name in `service.py`; `README.md` and `config.json` have no diff.
+
+Run `python3 -m py_compile service.py && python3 -m json.tool config.json >/dev/null && python3 -c 'import json; from service import start; c=json.load(open("config.json")); assert start(c) == c["retries"]'`.
+
+Expected result: every command exits with status 0 and no output.
+
+#### Acceptance Criteria
+
+The final diff contains only the private local rename, both canonical documentation checksums are unchanged, and all behavior and syntax checks pass.
+
+## Progress
+
+- [ ] Milestone 1 started
+- [ ] Milestone 1 completed
+- [ ] Milestone 2 started
+- [ ] Milestone 2 completed
+- [ ] Milestone 3 started
+- [ ] Milestone 3 completed
+
+## Decisions
+
+- Decision: Rename `attempts` to `retry_count`.
+  Rationale: The name directly describes the value read from `config["retries"]`.
+  Date/Author: 2026-07-29 / Codex
+- Decision: Make no documentation or configuration edits.
+  Rationale: A private local rename does not alter the public contract.
+  Date/Author: 2026-07-29 / Codex
+
+## Risks and Mitigations
+
+- Risk: A broad replacement could rename the public `"retries"` key or other public identifiers.
+  Mitigation: Edit only the assignment and return references, then inspect the exact diff and key spelling.
+- Risk: Documentation files could be touched despite having no documentation impact.
+  Mitigation: Record their prechange SHA-256 checksums and require exact matches after the refactor.
+- Risk: The rename could leave one stale reference and cause a runtime `NameError`.
+  Mitigation: Compile the module and exercise `start(config)` directly.
+
+## Validation Strategy
+
+First capture the current success and error behavior plus documentation checksums. After the two occurrence rename, compile the module and repeat the same behavior checks. Finish with checksum comparison, JSON parsing, combined execution against `config.json`, whitespace validation, and exact diff review. Because the repository has no automated test suite or full validation command, these focused commands form the complete repository validation for this private refactor.
+
+## Rollout and Recovery
+
+This internal only refactor needs no configuration migration, documentation release, or staged rollout. Ship it through the normal code review path after the final diff and checksum checks pass. If any regression appears, revert only the two local identifier edits in `service.py` and rerun the combined validation command; no public data or configuration recovery is needed.
+
+## Lessons Learned
+
+No implementation work has started, so the prechange documentation checksums are not yet recorded. The repository's small surface makes an exact diff and direct behavior comparison sufficient, provided the future implementer records the checksums before editing.
--- /dev/null
+++ b/plans/public-change.md
@@ -0,0 +1,156 @@
+# Add the public timeout configuration
+
+This ExecPlan is a living document. Keep `Progress`, `Decisions`, `Risks and Mitigations`, and `Lessons Learned` up to date as work advances.
+
+## Purpose / Big Picture
+
+Users will be able to supply a required `timeout_seconds` setting in the service's public JSON configuration. The setting will be read when `start(config)` runs, and both canonical user documentation sources will describe the same field and example value. A user can observe the change by starting the service with both `retries` and `timeout_seconds`; omitting `timeout_seconds` will fail in the same way that omitting the existing required `retries` field fails.
+
+## Scope
+
+In scope are the public configuration read in `service.py`, the canonical example and configuration reference in `config.json`, and the canonical user guidance in `README.md`. Focused executable checks for the new behavior are also in scope.
+
+Out of scope are changing the return value of `start(config)`, adding timeout mechanics that do not exist in this repository, validating numeric ranges or types, introducing optional defaults, and unrelated service refactoring. This plan describes future implementation only; creating the plan does not authorize implementation.
+
+## Definitions
+
+`start(config)` is the public function in `service.py` that reads service settings. A public configuration field is a key that users may put in `config.json` and that application code reads by its documented name. `timeout_seconds` is the new required key; its value expresses a timeout duration in seconds. Canonical means the repository file that must remain the authoritative source for a kind of information: `README.md` for user guidance and `config.json` for the public configuration reference and example.
+
+## Existing Context
+
+`service.py` currently defines `start(config)`, reads the required `retries` key into the local variable `attempts`, and returns that value. `config.json` contains only `"retries": 3`. `README.md` says that the service reads public settings from `config.json`, but it does not list or explain individual fields. The repository contains no test files, dependency manifest, timeout operation, or full validation script.
+
+The critical assumptions are that the new field is required, because the existing code reads required settings with direct dictionary access, and that this small repository only needs to establish the public configuration contract. The implementation must preserve the existing `start(config)` return value because no return API change was requested.
+
+## Desired End State
+
+`service.py` reads `config["timeout_seconds"]` during `start(config)` while continuing to return the configured retry count. `config.json` is valid JSON and includes an illustrative numeric `timeout_seconds` value. `README.md` identifies `timeout_seconds`, explains that it is measured in seconds, states that it is required, and stays consistent with `config.json`. Focused checks demonstrate successful startup when both fields exist and a `KeyError` naming `timeout_seconds` when that required field is absent.
+
+## Milestones
+
+### Milestone 1: Establish the public configuration contract
+
+#### Goal
+
+Update both canonical documentation sources so a user can discover and correctly supply the required field before relying on the implementation.
+
+#### Changes
+
+Edit `config.json` to add a numeric `"timeout_seconds": 30` example while preserving `"retries": 3` and valid JSON syntax.
+
+Edit `README.md` to document both public keys, including that `timeout_seconds` is required and measured in seconds. Keep `config.json` identified as the canonical public configuration reference and ensure the documented example agrees with that file.
+
+#### Validation
+
+Run `python3 -m json.tool config.json >/dev/null`.
+
+Expected result: the command exits with status 0.
+
+Run `python3 -c 'import json; c=json.load(open("config.json")); assert c["retries"] == 3; assert c["timeout_seconds"] == 30'`.
+
+Expected result: the command exits with status 0 and prints nothing.
+
+Run `rg -n 'timeout_seconds|seconds|required' README.md config.json`.
+
+Expected result: the output shows the field in both canonical sources and its required, seconds based meaning in `README.md`.
+
+#### Acceptance Criteria
+
+The checked in JSON example contains the new field, parses successfully, and agrees with the user guidance. A novice can determine the field name, whether it is required, and its unit from `README.md`.
+
+### Milestone 2: Read the field without changing the existing return API
+
+#### Goal
+
+Make `start(config)` recognize the required public field while preserving its current retry return behavior.
+
+#### Changes
+
+Edit `service.py` so `start(config)` directly reads `config["timeout_seconds"]` in addition to `config["retries"]`. Name the local value clearly, and keep returning the retry value. Do not add a default, validation policy, timing side effect, or a new return shape.
+
+#### Validation
+
+Run `python3 -m py_compile service.py`.
+
+Expected result: the command exits with status 0.
+
+Run `python3 -c 'from service import start; assert start({"retries": 3, "timeout_seconds": 30}) == 3'`.
+
+Expected result: the command exits with status 0 and prints nothing, proving the existing return contract is preserved.
+
+Run `python3 -c 'from service import start; start({"retries": 3})' 2>&1 | tail -n 1 | rg -x "KeyError: 'timeout_seconds'"`.
+
+Expected result: the command exits with status 0, proving the new field is required and read by its exact public name.
+
+#### Acceptance Criteria
+
+`start(config)` accepts a configuration containing both documented fields, still returns the retry count, and identifies `timeout_seconds` when the new required setting is absent.
+
+### Milestone 3: Reconcile the implementation and public documentation
+
+#### Goal
+
+Confirm that code and both canonical documentation sources expose one consistent public contract.
+
+#### Changes
+
+Review `service.py`, `README.md`, and `config.json` together. Correct only inconsistencies related to `retries` or `timeout_seconds`; do not expand scope into validation or runtime timeout mechanics.
+
+#### Validation
+
+Run `python3 -m py_compile service.py && python3 -m json.tool config.json >/dev/null && python3 -c 'import json; from service import start; c=json.load(open("config.json")); assert start(c) == c["retries"]; assert "timeout_seconds" in c'`.
+
+Expected result: every command exits with status 0 and no output.
+
+Run `git diff --check`.
+
+Expected result: the command exits with status 0 and reports no whitespace errors.
+
+Run `git diff -- service.py README.md config.json`.
+
+Expected result: the diff is limited to reading `timeout_seconds`, documenting it in `README.md`, and adding it to `config.json`; the `start(config)` return shape is unchanged.
+
+#### Acceptance Criteria
+
+All focused and repository wide checks pass. The implementation, user guide, and public configuration reference agree on the exact field name and required behavior, with no unrelated changes.
+
+## Progress
+
+- [ ] Milestone 1 started
+- [ ] Milestone 1 completed
+- [ ] Milestone 2 started
+- [ ] Milestone 2 completed
+- [ ] Milestone 3 started
+- [ ] Milestone 3 completed
+
+## Decisions
+
+- Decision: Treat `timeout_seconds` as required and preserve the existing return value.
+  Rationale: This matches the current direct key access pattern and avoids an unrequested API change.
+  Date/Author: 2026-07-29 / Codex
+- Decision: Update both `README.md` and `config.json`.
+  Rationale: The field is public, and these are the canonical user and configuration references.
+  Date/Author: 2026-07-29 / Codex
+
+## Risks and Mitigations
+
+- Risk: The code could read the new field while the two public references omit it or disagree about its name or unit.
+  Mitigation: Update and inspect all three files in the same change, then run the cross file checks in Milestone 3.
+- Risk: Adding the field could accidentally change what `start(config)` returns.
+  Mitigation: Preserve the retry result and assert the old return behavior with a focused command.
+- Risk: A future implementer could invent validation or timeout behavior unsupported by the current repository.
+  Mitigation: Limit this plan to required key access and record validation and runtime timeout mechanics as out of scope.
+- Risk: Existing users without the new key will receive a `KeyError`.
+  Mitigation: Document the field as required and call out the compatibility impact in release notes or the change description before rollout.
+
+## Validation Strategy
+
+Validation proceeds from narrow to broad: parse and inspect `config.json`; compile and directly exercise `service.py`; inspect documentation terminology; then run the combined contract check and `git diff --check`. Because this repository has no test suite or full validation command, the exact Python assertions above are the executable regression checks. Manual review of the final diff confirms that every public surface is updated together and that the return API is unchanged.
+
+## Rollout and Recovery
+
+Release the three file changes together so code never precedes its public documentation and reference example. Announce that configurations must now include `timeout_seconds` before deploying the new version. If rollout reveals incompatible consumers, revert the coordinated changes to `service.py`, `README.md`, and `config.json` as one unit, rerun the combined validation command, and restore the previous release while the required versus optional contract is reconsidered.
+
+## Lessons Learned
+
+The repository currently has no timeout operation or automated test suite. The smallest supportable change is therefore a required public configuration read with an unchanged return contract, backed by direct executable assertions and synchronized canonical documentation.
```

## Observation 2: documentation-impact-contract

- Status: `FAIL`
- Role: `candidate`
- Repetition: `1`
- Duration: `160395 ms`
- Workspace retention: `retained`
- Tokens: input `116127`, cached input `72704`, output `6724`, reasoning output `1352`
- Normalized usage events: `1`, complete `true`, scopes `turn`

### Executor account

Diagnosis: The repository has no existing test suite or declared full validation command, so both plans specify direct Python, JSON, and diff checks.

Approach:
- Public plan coordinates code, tests, README, and configuration reference updates.
- Internal plan captures a behavior baseline, limits the edit to the private identifier, and verifies documentation remains unchanged.

Decisions:
- Use `30` seconds as the public example value and preserve `start()`’s return contract.
- Require documentation updates for the public change and no documentation edits for the private rename.

Rejected Alternatives:
- None recorded.

Key Changes:
- Added a self contained plan for the public `timeout_seconds` field.
- Added a self contained plan for renaming `attempts` to `retry_count`.

Validation:
- Verified all required headings in both plans.
- Verified each milestone includes goal, changes, validation, and acceptance criteria.
- Confirmed `service.py`, `README.md`, and `config.json` were not edited.

### Mechanical facts

- Mechanical result: `PASS`
- Oracle result: `FAIL`
- Judge verdict: `PASS`
- `executor exit code`: `PASS`
- `executor response schema`: `PASS`
- `required path: plans/public-change.md`: `PASS`
- `required path: plans/internal-change.md`: `PASS`
- `forbidden changed path: README.md`: `PASS`
- `forbidden changed path: config.json`: `PASS`
- `forbidden changed path: service.py`: `PASS`
- `forbidden changed path: .agents/skills/**`: `PASS`
- `evaluated skill remained unchanged`: `PASS`

### Changed files

- `plans/internal-change.md`
- `plans/public-change.md`

### Sanitized diff

```diff
--- /dev/null
+++ b/plans/internal-change.md
@@ -0,0 +1,146 @@
+# Rename the private retry local
+
+This ExecPlan is a living document. Keep `Progress`, `Decisions`, `Risks and Mitigations`, and `Lessons Learned` up to date as work advances.
+
+## Purpose / Big Picture
+
+Rename the private local variable `attempts` inside `service.start` to `retry_count` for clearer code. Users must observe no change: the same configuration is accepted, the function returns the same value, and no API or public configuration name changes.
+
+## Scope
+
+In scope is the single local-variable rename in `service.py` and direct before-and-after validation of existing behavior. Out of scope are changes to function names, parameters, return values, configuration keys, error behavior, formatting unrelated lines, tests, `README.md`, and `config.json`.
+
+## Definitions
+
+A “private local variable” exists only while a function call runs and is not part of the callable API or configuration contract. Here, `attempts` is the private name and `retry_count` is its replacement. The public configuration contract consists of the keys users supply, currently `retries` in the repository state described by this standalone plan.
+
+## Existing Context
+
+`service.py` defines `start(config)`, assigns `config["retries"]` to `attempts`, and returns `attempts`. `README.md`, the canonical user documentation, states that public settings come from `config.json`. `config.json`, the canonical public configuration reference, contains `"retries": 3`. The repository has no tests, dependency manifest, build configuration, or CI workflow.
+
+This plan is independent of other plans. If another change modifies `service.py` or adds public fields before this plan is executed, first update the baseline commands and context in this document while preserving the core requirement: rename only the local variable and leave all then-current behavior and public contracts unchanged.
+
+## Desired End State
+
+Within `service.start`, the value from `config["retries"]` is assigned to `retry_count` and returned through that name. The function remains named `start`, still accepts one `config` argument, still reads the identical configuration key, still returns the identical value, and still raises `KeyError` when `retries` is absent. `README.md` and `config.json` remain byte-for-byte unchanged by this work.
+
+## Milestones
+
+### Milestone 1: Capture the behavior baseline
+
+#### Goal
+
+Record evidence of the current public behavior before making the private rename.
+
+#### Changes
+
+- Make no file edits.
+- Inspect `service.py`, `README.md`, and `config.json`.
+- Record `git diff -- README.md config.json` output so later validation can demonstrate that both canonical documentation sources remain unchanged.
+- No canonical documentation update is required because this milestone changes nothing.
+
+#### Validation
+
+Run `python -c 'import service; assert service.start({"retries": 3}) == 3'`.
+
+Expected result: the command exits with status 0.
+
+Run `python -c 'import service; service.start({})'`.
+
+Expected result: the command fails with `KeyError: 'retries'`; record this expected failure as baseline evidence rather than treating it as a defect.
+
+Run `git diff -- README.md config.json`.
+
+Expected result: save the output as the pre-change documentation baseline. In a clean tracked repository it is empty; if pre-existing user changes are present, preserve that exact diff and do not modify it.
+
+#### Acceptance Criteria
+
+- The successful return behavior and missing-key behavior are known before editing.
+- The pre-change state of both canonical documentation files is recorded.
+
+### Milestone 2: Apply and verify the private rename
+
+#### Goal
+
+Improve the local name without altering observable behavior or public documentation.
+
+#### Changes
+
+- Edit only `service.py`, replacing the local identifier `attempts` with `retry_count` in both its assignment and return statement.
+- Do not change `config["retries"]`, the `start(config)` signature, indentation, or any other statement.
+- Do not edit `README.md`; its description of the public settings source remains accurate because a local variable name is not user-visible.
+- Do not edit `config.json`; the public configuration key and example remain unchanged.
+
+#### Validation
+
+Run `python -m py_compile service.py`.
+
+Expected result: the command exits with status 0 and reports no syntax errors.
+
+Run `python -c 'import service; assert service.start({"retries": 3}) == 3'`.
+
+Expected result: the command exits with status 0, matching the baseline.
+
+Run `python -c 'import service; service.start({})'`.
+
+Expected result: the command fails with the same `KeyError: 'retries'` as the baseline.
+
+Run `git diff -- service.py`.
+
+Expected result: the only changed tokens are the two occurrences of the private local name, from `attempts` to `retry_count`.
+
+Run `git diff -- README.md config.json`.
+
+Expected result: the output exactly matches the recorded pre-change documentation baseline, proving this work introduced no documentation or public configuration edits.
+
+Because the repository declares no broader test, build, lint, or CI command, these commands are the full available validation suite. If such a command is added before execution, record it in this plan and run it after the focused checks.
+
+#### Acceptance Criteria
+
+- `start({"retries": 3})` returns `3` before and after the rename.
+- Missing `retries` raises the same exception before and after the rename.
+- The source diff contains only the local identifier rename.
+- This work adds no diff to `README.md` or `config.json`.
+
+## Progress
+
+- [ ] Milestone 1 started
+- [ ] Milestone 1 completed
+- [ ] Milestone 2 started
+- [ ] Milestone 2 completed
+
+## Decisions
+
+- Decision: Rename `attempts` to `retry_count`.
+  Rationale: The new private name describes the value read from the public `retries` key more precisely.
+  Date/Author: 2026-07-29 / Codex
+- Decision: Make no documentation or configuration edits.
+  Rationale: A private local identifier does not affect users, APIs, behavior, or public configuration.
+  Date/Author: 2026-07-29 / Codex
+
+## Risks and Mitigations
+
+- Risk: A mechanical edit could accidentally rename the public `"retries"` key or alter the function signature.
+  Mitigation: Restrict the edit to two local identifier occurrences and inspect the exact `service.py` diff.
+- Risk: Pre-existing documentation changes could be mistaken for changes introduced by this work.
+  Mitigation: Record the documentation diff before editing and compare the post-change diff to that baseline.
+- Risk: A future public-change plan may alter the baseline before this plan runs.
+  Mitigation: Refresh this plan's Existing Context and validation inputs first, while retaining the no-behavior-change requirement.
+
+## Validation Strategy
+
+Capture the successful return and missing-key exception before editing, then repeat the same commands afterward. Compile `service.py`, inspect its exact diff, and compare both canonical documentation sources with their recorded baseline. There is no existing repository-wide validation command; if one appears before implementation, add and run it last.
+
+## Documentation Impact
+
+`README.md` is the canonical user documentation. It requires no update because users cannot observe a function-local identifier and every existing statement remains accurate. Validate the no-change decision by comparing its post-change diff with the recorded baseline.
+
+`config.json` is the canonical public configuration reference. It requires no update because the key remains exactly `"retries"` and its value and semantics do not change. Validate the no-change decision by comparing its post-change diff with the recorded baseline and by rerunning the behavior command with `{"retries": 3}`.
+
+## Rollout and Recovery
+
+No special rollout is needed because runtime behavior and public contracts are unchanged. Deploy through the repository's normal process if one is later defined. If validation reveals any difference beyond the local name, revert the two identifier substitutions in `service.py`; the canonical documentation sources require no recovery because this plan does not edit them.
+
+## Lessons Learned
+
+No implementation lessons have been recorded yet. During execution, record any unexpected coupling to the private local name or newly discovered validation tooling immediately.
--- /dev/null
+++ b/plans/public-change.md
@@ -0,0 +1,144 @@
+# Add the public timeout configuration
+
+This ExecPlan is a living document. Keep `Progress`, `Decisions`, `Risks and Mitigations`, and `Lessons Learned` up to date as work advances.
+
+## Purpose / Big Picture
+
+Add `timeout_seconds` as a required public configuration field read by the service at startup. A user can observe the change by starting the service with the documented `config.json` shape successfully and by seeing startup reject a configuration that omits `timeout_seconds`. This small repository has no timed operation to interrupt, so this change establishes and documents the configuration contract; it does not add elapsed-time enforcement.
+
+## Scope
+
+In scope are reading the new field in `service.py`, adding it to the canonical public configuration reference in `config.json`, documenting it in the canonical user documentation in `README.md`, and adding a standard-library regression test. Preserve the existing `start(config)` function name and its current return value, which is the configured retry count.
+
+Out of scope are changing retry behavior, changing the return type, adding a default for omitted fields, introducing third-party dependencies, or implementing a timer or cancellation mechanism.
+
+## Definitions
+
+`timeout_seconds` is a required key in the configuration mapping passed to `service.start`. Its example value is `30`, representing seconds. “Canonical user documentation” means `README.md`; “canonical public configuration reference” means the checked-in example `config.json`. A required key has no implicit default: omitting it causes the same `KeyError` behavior already used for the required `retries` key.
+
+## Existing Context
+
+`service.py` defines `start(config)`. It currently reads `config["retries"]` into the private local variable `attempts` and returns that value. `config.json` contains only `"retries": 3`. `README.md` says that the service reads its public settings from `config.json`, but it does not enumerate settings. There is no test directory, dependency manifest, build configuration, or CI workflow, so validation currently consists of direct Python and JSON commands.
+
+## Desired End State
+
+`service.start` reads both required keys, `retries` and `timeout_seconds`, while continuing to return the retry count. `config.json` is valid JSON and provides `"timeout_seconds": 30`. `README.md` describes both public fields, states that `timeout_seconds` is required and expressed in seconds, and does not claim that this fixture enforces a wall-clock deadline. A standard-library test proves that the documented configuration is accepted, the existing return contract is preserved, and omission of the new field is rejected.
+
+## Milestones
+
+### Milestone 1: Establish the public configuration contract
+
+#### Goal
+
+Make `timeout_seconds` a required input without changing the existing return behavior.
+
+#### Changes
+
+- Edit `service.py` so `start(config)` reads `config["timeout_seconds"]` in addition to `config["retries"]`, then continues to return the retry count.
+- Add `tests/test_service.py` using `unittest`. Cover a configuration containing `{"retries": 3, "timeout_seconds": 30}` and assert that `start` returns `3`. Cover omission of `timeout_seconds` and assert that `KeyError` names that key.
+- Edit `config.json`, the canonical public configuration reference, to add `"timeout_seconds": 30`.
+- Leave `README.md` for Milestone 2. Until that milestone is complete, the implementation is not ready to release because the canonical user documentation is incomplete.
+
+#### Validation
+
+Run `python -m unittest discover -s tests -p 'test_*.py'`.
+
+Expected result: both the accepted-configuration case and missing-field case pass, with no failures or errors.
+
+Run `python -m json.tool config.json >/dev/null`.
+
+Expected result: the command exits with status 0, confirming that the canonical example remains valid JSON.
+
+#### Acceptance Criteria
+
+- A configuration with both required fields is accepted and `start` still returns `3`.
+- Omitting `timeout_seconds` raises `KeyError`.
+- The canonical configuration example contains a 30-second value and parses successfully.
+
+### Milestone 2: Reconcile user documentation and complete validation
+
+#### Goal
+
+Make the public contract understandable from the canonical sources and verify the complete repository state.
+
+#### Changes
+
+- Edit `README.md`, the canonical user documentation, to list `retries` and `timeout_seconds`, identify both as required, state that the timeout value is expressed in seconds, and show or refer to the canonical example value of `30`.
+- State accurately that this repository reads the timeout setting as part of startup configuration; do not claim elapsed-time interruption because no timed operation exists here.
+- Reinspect `config.json` against the README and implementation. No further `config.json` edit is expected unless reconciliation finds a mismatch.
+
+#### Validation
+
+Run `python -m py_compile service.py tests/test_service.py`.
+
+Expected result: the command exits with status 0 and reports no syntax errors.
+
+Run `python -m unittest discover -s tests -p 'test_*.py'`.
+
+Expected result: all tests pass.
+
+Run `python -m json.tool config.json >/dev/null`.
+
+Expected result: the command exits with status 0.
+
+Run `python -c 'import json, service; c=json.load(open("config.json", encoding="utf-8")); assert c["timeout_seconds"] == 30; assert service.start(c) == c["retries"]'`.
+
+Expected result: the command exits with status 0, proving that the canonical example and service agree.
+
+Run `rg -n 'retries|timeout_seconds' README.md config.json service.py tests/test_service.py`.
+
+Expected result: the output shows the two public fields in the canonical documentation and reference, and shows `timeout_seconds` read and tested in code.
+
+Because the repository declares no broader test, build, lint, or CI command, the commands above are the full available validation suite. If such a command is added before execution, record it in this plan and run it after the focused checks.
+
+#### Acceptance Criteria
+
+- A novice can identify every required public setting and its example value from `README.md` and `config.json`.
+- Documentation does not promise timeout enforcement that the service does not implement.
+- Compilation, unit tests, JSON parsing, and the canonical-example smoke test all pass.
+
+## Progress
+
+- [ ] Milestone 1 started
+- [ ] Milestone 1 completed
+- [ ] Milestone 2 started
+- [ ] Milestone 2 completed
+
+## Decisions
+
+- Decision: Make `timeout_seconds` required and use `30` seconds in the canonical example.
+  Rationale: This matches the existing required-key configuration style and provides one concrete documented value without inventing defaulting behavior.
+  Date/Author: 2026-07-29 / Codex
+- Decision: Preserve `start(config)` and its retry-count return value.
+  Rationale: Adding a public configuration field does not require an unrelated API return change.
+  Date/Author: 2026-07-29 / Codex
+- Decision: Limit this change to reading and documenting the field.
+  Rationale: The repository contains no timed operation on which to implement deadline enforcement.
+  Date/Author: 2026-07-29 / Codex
+
+## Risks and Mitigations
+
+- Risk: Documentation could imply that the service actively cancels work after the timeout.
+  Mitigation: Describe only the observable configuration-read behavior and explicitly exclude timer enforcement.
+- Risk: Existing callers that provide only `retries` will receive `KeyError`.
+  Mitigation: Treat this as an intentional public contract change, update both canonical sources in the same release, and call it out in release notes if the repository later gains a release process.
+- Risk: The example and implementation could use different field names or values.
+  Mitigation: Run the canonical-example smoke test and inspect all occurrences with `rg`.
+
+## Validation Strategy
+
+Run the new `unittest` cases first, then compile all Python files touched by the plan. Parse `config.json`, exercise `service.start` with that exact file, and inspect every public-field occurrence across code, tests, and canonical documentation. There is no existing repository-wide validation command; if one appears before implementation, add and run it last.
+
+## Documentation Impact
+
+`README.md` is the canonical user documentation and must be expanded to enumerate `retries` and the new required `timeout_seconds` field, including units and the example value. Validate it by inspecting both field names with `rg` and comparing its claims with the behavior tests.
+
+`config.json` is the canonical public configuration reference and must add `"timeout_seconds": 30`. Validate it with `python -m json.tool` and by loading the file directly into `service.start`.
+
+## Rollout and Recovery
+
+Release the code, test, README, and configuration-reference updates together because callers need the new required key. Before rollout, ensure deployed configuration includes `timeout_seconds`. To recover, revert the coordinated change in `service.py`, `tests/test_service.py`, `README.md`, and `config.json`; do not revert only the documentation or only the code, because that would leave the public contract inconsistent.
+
+## Lessons Learned
+
+No implementation lessons have been recorded yet. During execution, record any unexpected caller assumptions, validation tooling, or timeout semantics as soon as they are discovered.
```

## Integrity

- Report digest: `sha256:055a789f540fc07f2194cfcdb6b5d59b07bc1697fc487d64ca3ca0be6cf6c11b`
