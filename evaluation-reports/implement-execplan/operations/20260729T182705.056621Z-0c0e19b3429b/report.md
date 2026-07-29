# Evaluation evidence: 20260729T182705.056621Z-0c0e19b3429b

- Operation: `validate-change`
- Status: `FAIL`
- Provenance: `executed`
- Started: `2026-07-29T18:27:05.056621Z`
- Finished: `2026-07-29T18:34:00.907836Z`
- Duration: `416184 ms`
- Executor model: `gpt-5.6-sol`
- Executor effort: `medium`
- Codex CLI: `codex-cli 0.146.0`
- Authentication: `chatgpt`
- Runner SHA-256: `64808412e5d77fbb0bac91a724053821acfe2fd4b38d05c2c92c657ec5065cd2`

## Consumption

- Tokens: input `588562`, cached input `513024`, output `16404`, reasoning output `3016`
- Normalized usage events: `2`, complete `true`, scopes `turn`
- Sessions: planned `4`, executed `2`

## API reference estimate

- Reference amount: unavailable
- This is not an actual charge.
- Base-rate amount: `1.126322000000 USD`
- Estimate status: `indeterminate-long-context`
- Limitation: This is an API reference estimate, not an observed charge.
- Limitation: This dated table is an API reference and is not an observed ChatGPT charge.
- Limitation: Prompts above 272,000 input tokens use the documented higher rates; an exact estimate is unavailable when normalized telemetry does not expose request scoped input.
- Limitation: Cache write charges are not estimated because Codex JSONL usage does not identify cache writes.
- Limitation: Reasoning output tokens are reported separately but are already included in output tokens.
- Limitation: A reported usage event exceeded a request-scoped threshold, but the event is not request scoped; the exact multiplier cannot be audited.

## Observation 1: documentation-impact-contract

- Status: `FAIL`
- Role: `baseline`
- Repetition: `1`
- Duration: `170737 ms`
- Workspace retention: `retained`
- Tokens: input `176564`, cached input `142848`, output `7093`, reasoning output `1033`
- Normalized usage events: `1`, complete `true`, scopes `turn`

### Executor account

Diagnosis: The repository has no test harness and provides `python3` without a `python` alias.

Approach:
- Inspected the service and canonical documentation.
- Created self contained milestones with exact edits, commands, and acceptance criteria.
- Validated required sections, checklist placement, executable naming, and whitespace.

Decisions:
- Treat `timeout_seconds` as required, matching the existing configuration access pattern.
- Preserve `start(config)` return behavior and exclude timeout enforcement.
- Use `retry_count` as the renamed private local.
- Keep `README.md` and `config.json` unchanged for the internal refactor.
- Use `python3` for validation commands.

Rejected Alternatives:
- None recorded.

Key Changes:
- The public plan explicitly reconciles both canonical documentation sources.
- The internal plan verifies documentation nonimpact using hashes and scoped diff inspection.

Validation:
- Structural validation passed for all required ExecPlan sections.
- Checklists appear only in `Progress`.
- `git diff --check` passed.
- No implementation was performed.

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
@@ -0,0 +1,207 @@
+# Rename the private retry local
+
+This ExecPlan is a living document. Keep `Progress`, `Decisions`, `Risks`, and `Lessons Learned` up to date as work advances.
+
+## Purpose / Big Picture
+
+Rename one private local variable in `service.py` to make its meaning clearer while preserving all observable behavior. Users and callers should see no difference: the function signature, return value, accepted configuration, exceptions, and canonical documentation remain unchanged.
+
+## Scope
+
+In scope is only the local variable `attempts` inside `service.start` in `service.py`. Rename it to `retry_count` and update its local reference.
+
+Out of scope are public API changes, configuration changes, behavior changes, documentation edits, formatting unrelated code, and introducing a test framework. `README.md` and `config.json` are canonical public sources, but this private rename does not alter their contract, so they must remain byte-for-byte unchanged.
+
+## Definitions
+
+A private local variable exists only while a function runs and is not part of the function's callable interface. Here, `attempts` is a private local holding the value read from the public `retries` configuration key.
+
+Observable behavior includes the `start(config)` signature, its returned value, which configuration keys it reads, and exceptions raised for invalid input.
+
+## Existing Context
+
+`service.py` defines:
+
+    def start(config):
+      attempts = config["retries"]
+      return attempts
+
+`README.md` states that the service reads public settings from `config.json`. `config.json` contains the public `retries` example. There are no tests, dependency files, build scripts, or committed repository history.
+
+The critical assumption is that `retry_count` is the intended replacement name. The rename must not change `config["retries"]`, function indentation, evaluation order, return behavior, or any public file.
+
+## Desired End State
+
+Within `service.start`, the value of `config["retries"]` is assigned to `retry_count` and returned through that new name. The identifier `attempts` no longer appears in `service.py`.
+
+For representative inputs, results and exceptions are identical to the current implementation. `README.md` and `config.json` have no changes because the public documentation and configuration contract are unaffected.
+
+## Milestones
+
+### Milestone 1: Capture the unchanged public files and baseline behavior
+
+#### Goal
+
+Establish reproducible evidence for the behavior and canonical public files that the rename must preserve.
+
+#### Changes
+
+Do not edit any file. Record hashes of `README.md` and `config.json`, then exercise the current `service.start` behavior with representative values and a missing required key.
+
+#### Validation
+
+Run:
+
+    sha256sum README.md config.json
+
+Save the two hashes in the implementation session notes or in the `Lessons Learned` section before editing.
+
+Then run:
+
+    python3 - <<'PY'
+    import service
+
+    assert service.start({"retries": 0}) == 0
+    assert service.start({"retries": 3}) == 3
+    marker = object()
+    assert service.start({"retries": marker}) is marker
+    try:
+        service.start({})
+    except KeyError as error:
+        assert error.args == ("retries",)
+    else:
+        raise AssertionError("missing retries must raise KeyError")
+    PY
+
+Expected result: both commands exit with status 0, two hashes are captured, configured values are returned unchanged, and a missing `retries` key raises `KeyError`.
+
+#### Acceptance Criteria
+
+The baseline behavior passes and the exact pre-change hashes of both canonical public files are available for comparison after the rename.
+
+### Milestone 2: Rename only the private local
+
+#### Goal
+
+Improve the local name without altering behavior or public contracts.
+
+#### Changes
+
+Edit only `service.py`. Replace the local declaration `attempts = config["retries"]` with `retry_count = config["retries"]`, and return `retry_count`. Make no other textual or structural edit.
+
+#### Validation
+
+Run:
+
+    python3 - <<'PY'
+    import service
+
+    assert service.start({"retries": 0}) == 0
+    assert service.start({"retries": 3}) == 3
+    marker = object()
+    assert service.start({"retries": marker}) is marker
+    try:
+        service.start({})
+    except KeyError as error:
+        assert error.args == ("retries",)
+    else:
+        raise AssertionError("missing retries must raise KeyError")
+    PY
+
+Then run:
+
+    python3 - <<'PY'
+    from pathlib import Path
+
+    source = Path("service.py").read_text()
+    assert "attempts" not in source
+    assert 'retry_count = config["retries"]' in source
+    assert "return retry_count" in source
+    PY
+
+Expected result: both commands exit with status 0. Behavior matches the baseline and the source contains only the intended new local name.
+
+#### Acceptance Criteria
+
+Only the two local identifier occurrences change, representative return values retain identity and equality, and the missing-key exception remains `KeyError("retries")`.
+
+### Milestone 3: Prove no documentation or configuration impact
+
+#### Goal
+
+Confirm the private refactor did not change either canonical public source or any public interface.
+
+#### Changes
+
+Do not edit `README.md` or `config.json`. Compare their current hashes with the values captured in Milestone 1, inspect the final diff, and update this plan's living sections.
+
+#### Validation
+
+Run:
+
+    sha256sum README.md config.json
+
+Expected result: both hashes exactly match the Milestone 1 values.
+
+Then run:
+
+    git diff -- service.py README.md config.json
+
+Expected result: the diff shows only `attempts` changing to `retry_count` in `service.py`, with no output for `README.md` or `config.json`.
+
+Then run:
+
+    python3 -m py_compile service.py
+    git diff --check
+
+Expected result: both commands exit with status 0.
+
+#### Acceptance Criteria
+
+The final diff contains exactly the private rename in `service.py`; canonical documentation and configuration hashes are unchanged; syntax, baseline behavior, and whitespace checks pass.
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
+  Rationale: The new name directly identifies the value read from the `retries` configuration key.
+  Date/Author: 2026-07-29 / Codex
+- Decision: Leave `README.md` and `config.json` unchanged and verify that with hashes and diff inspection.
+  Rationale: A private local rename does not change behavior, APIs, or the public configuration contract.
+  Date/Author: 2026-07-29 / Codex
+- Decision: Use focused behavior assertions instead of adding tests.
+  Rationale: The repository has no test harness, and adding one would exceed a two-occurrence private rename.
+  Date/Author: 2026-07-29 / Codex
+
+## Risks and Mitigations
+
+- Risk: A mechanical rename could miss the return reference and cause a `NameError`.
+  Mitigation: Assert representative calls and inspect the source for both intended `retry_count` occurrences.
+- Risk: An editor could introduce unrelated formatting or canonical documentation changes.
+  Mitigation: Restrict edits to `service.py`, compare documentation hashes, and require a two-line identifier-only diff.
+- Risk: A supposedly internal refactor could alter missing-key behavior.
+  Mitigation: Verify that an empty configuration still raises `KeyError` for `retries`.
+
+## Validation Strategy
+
+Run the same focused behavior assertions before and after the edit. Confirm the old identifier is absent and the new declaration and return are present. Compare pre-change and post-change hashes for `README.md` and `config.json`, compile `service.py`, inspect the scoped diff, and run `git diff --check`.
+
+There is no repository test harness or full validation command. If one is added before implementation, run it after the focused checks and record its command and result in this plan.
+
+## Rollout and Recovery
+
+This is an internal, behavior-preserving source change and needs no configuration migration or coordinated documentation release. Ship through the repository's normal review process after the validations pass.
+
+To recover, rename `retry_count` back to `attempts` in its declaration and return statement. Do not touch `README.md` or `config.json`.
+
+## Lessons Learned
+
+The repository's entire current behavior is small enough to cover with direct assertions. Hashing the two canonical public files makes the intended lack of documentation impact explicit and independently verifiable.
--- /dev/null
+++ b/plans/public-change.md
@@ -0,0 +1,185 @@
+# Add the public timeout configuration
+
+This ExecPlan is a living document. Keep `Progress`, `Decisions`, `Risks`, and `Lessons Learned` up to date as work advances.
+
+## Purpose / Big Picture
+
+Add `timeout_seconds` to the service's public configuration so operators can provide an explicit timeout value alongside `retries`. A user can observe the completed change by seeing the field documented in `README.md`, represented in the canonical `config.json`, and required when `service.start` reads configuration.
+
+## Scope
+
+In scope are `service.py`, the canonical user documentation in `README.md`, and the canonical public configuration reference in `config.json`. The change adds one required configuration key while preserving the existing `start(config)` function signature and its current return value.
+
+Out of scope are timeout enforcement, retries behavior changes, configuration file loading, a new configuration framework, and unrelated refactoring. The repository has no test suite, so this plan uses focused Python assertions rather than introducing a test framework.
+
+## Definitions
+
+`timeout_seconds` is a public configuration key whose value expresses a timeout duration in seconds. In this change it is required and read by `service.start`; actual timeout enforcement is outside scope.
+
+The canonical user documentation is `README.md`, the file users read to learn how to configure the service. The canonical public configuration reference is `config.json`, the repository's authoritative example of supported configuration keys.
+
+## Existing Context
+
+`service.py` defines `start(config)`. It currently reads the required `retries` key with `config["retries"]`, stores the value in the local variable `attempts`, and returns that value.
+
+`README.md` currently says only that the service reads public settings from `config.json`. `config.json` currently contains `{"retries": 3}`. There are no tests, dependency files, build scripts, or committed repository history.
+
+Critical assumptions are that `timeout_seconds` follows the same required-key convention as `retries`, that no default is introduced, and that this narrowly scoped change does not define validation constraints or runtime timeout enforcement. The example value in `config.json` is illustrative, not a default.
+
+## Desired End State
+
+`service.start` reads both `retries` and `timeout_seconds` from its input mapping, still returns the configured retry count, and raises `KeyError` when either required key is absent. `config.json` contains a valid example `timeout_seconds` value. `README.md` names both public keys, explains that `timeout_seconds` is required and measured in seconds, and clarifies that the reference value is an example.
+
+The three public contract surfaces agree on the exact spelling `timeout_seconds`. No timeout enforcement or unrelated API change is present.
+
+## Milestones
+
+### Milestone 1: Read the new public field
+
+#### Goal
+
+Make `service.start` consume the new required field without changing its signature or existing return behavior.
+
+#### Changes
+
+Edit `service.py` so `start(config)` reads `config["timeout_seconds"]` next to the existing `retries` lookup. Keep returning the retry value. Do not add a default, validation rules, timeout enforcement, or unrelated refactoring.
+
+#### Validation
+
+Run:
+
+    python3 - <<'PY'
+    import service
+
+    assert service.start({"retries": 3, "timeout_seconds": 30}) == 3
+    try:
+        service.start({"retries": 3})
+    except KeyError as error:
+        assert error.args == ("timeout_seconds",)
+    else:
+        raise AssertionError("timeout_seconds must be required")
+    PY
+
+Expected result: the command exits with status 0. A complete configuration preserves the existing result, while omitting `timeout_seconds` raises `KeyError`.
+
+#### Acceptance Criteria
+
+`service.start` reads the exact public key `timeout_seconds`, accepts a configuration containing both required keys, and preserves the return value for the existing `retries` setting.
+
+### Milestone 2: Reconcile canonical public documentation
+
+#### Goal
+
+Make both canonical documentation sources accurately describe the public contract introduced in Milestone 1.
+
+#### Changes
+
+Edit `config.json` to add an illustrative numeric `timeout_seconds` value while retaining `retries`. Edit `README.md` to list `retries` and `timeout_seconds`, state that both are required, define `timeout_seconds` as seconds, and identify values in `config.json` as examples rather than defaults.
+
+#### Validation
+
+Run:
+
+    python3 - <<'PY'
+    import json
+    from pathlib import Path
+
+    config = json.loads(Path("config.json").read_text())
+    readme = Path("README.md").read_text()
+    assert set(config) == {"retries", "timeout_seconds"}
+    assert isinstance(config["timeout_seconds"], (int, float))
+    assert "timeout_seconds" in readme
+    assert "required" in readme.lower()
+    assert "seconds" in readme.lower()
+    PY
+
+Expected result: the command exits with status 0, proving the reference JSON is valid and both the key and its required seconds-based meaning appear in the canonical user documentation.
+
+#### Acceptance Criteria
+
+`README.md`, `config.json`, and `service.py` use the exact same key spelling and agree that the field is required. The example configuration can be passed to `service.start` without an exception.
+
+### Milestone 3: Validate the complete public contract
+
+#### Goal
+
+Confirm the code and both canonical documentation sources remain synchronized.
+
+#### Changes
+
+Inspect the final diff for `service.py`, `README.md`, and `config.json`. Remove any unrelated edits and update this plan's living sections with implementation progress, decisions, risks, and lessons.
+
+#### Validation
+
+Run:
+
+    python3 -m json.tool config.json
+
+Then run:
+
+    python3 - <<'PY'
+    import json
+    from pathlib import Path
+    import service
+
+    config = json.loads(Path("config.json").read_text())
+    assert service.start(config) == config["retries"]
+    assert "timeout_seconds" in config
+    assert "timeout_seconds" in Path("README.md").read_text()
+    PY
+
+Then run:
+
+    git diff --check
+
+Expected result: all commands exit with status 0; the reference configuration parses, works with `service.start`, and is described by `README.md`; Git reports no whitespace errors.
+
+#### Acceptance Criteria
+
+Every milestone's acceptance criteria are satisfied, only the three scoped implementation and documentation files plus this living plan changed, and the final diff contains no timeout enforcement or unrelated refactoring.
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
+- Decision: Make `timeout_seconds` a required key with no default, matching the existing `config["retries"]` access pattern.
+  Rationale: This extends the repository's current configuration convention without introducing an unrequested defaulting mechanism.
+  Date/Author: 2026-07-29 / Codex
+- Decision: Preserve the current return value and exclude timeout enforcement.
+  Rationale: The requested change adds a public configuration field, while runtime timeout semantics and API changes were not specified.
+  Date/Author: 2026-07-29 / Codex
+- Decision: Update both `README.md` and `config.json`.
+  Rationale: They are the stated canonical user documentation and public configuration reference, so a public field would be incomplete if either remained stale.
+  Date/Author: 2026-07-29 / Codex
+
+## Risks and Mitigations
+
+- Risk: Users may mistake the example timeout for a default.
+  Mitigation: State in `README.md` that the field is required and the reference value is illustrative.
+- Risk: Reading the field without enforcing a timeout may imply behavior beyond this scope.
+  Mitigation: Document that this change only adds configuration consumption and leave enforcement to a separately specified change.
+- Risk: Code and canonical documentation may use different spellings or requirements.
+  Mitigation: Use the exact name `timeout_seconds` everywhere and run the cross-file assertions in Milestones 2 and 3.
+
+## Validation Strategy
+
+Validate from narrow to broad. First exercise `service.start` with present and missing `timeout_seconds` values. Next parse `config.json` and assert that `README.md` states the field's required seconds-based meaning. Finally pass the canonical example into `service.start`, run `python -m json.tool config.json`, and run `git diff --check`.
+
+There is no repository test harness or full validation command. If one is added before implementation, run it after the listed checks and record its command and result in this plan.
+
+## Rollout and Recovery
+
+Release the code and both canonical documentation updates together because configurations without `timeout_seconds` will begin raising `KeyError`. Before rollout, operators must add the required field to deployed configurations.
+
+To recover, revert the coordinated edits to `service.py`, `README.md`, and `config.json` together. Reverting only the code or only the documentation would leave the public contract inconsistent. No data migration is required.
+
+## Lessons Learned
+
+The current repository exposes its configuration contract through three small files and has no automated test suite. Direct Python assertions provide reproducible validation without expanding this change into test infrastructure work.
```

## Observation 2: documentation-impact-contract

- Status: `FAIL`
- Role: `candidate`
- Repetition: `1`
- Duration: `245331 ms`
- Workspace retention: `retained`
- Tokens: input `411998`, cached input `370176`, output `9311`, reasoning output `1983`
- Normalized usage events: `1`, complete `true`, scopes `turn`

### Executor account

Diagnosis: The public change requires documentation reconciliation; the private rename does not affect canonical documentation.

Approach:
- Inspected the repository source, canonical documentation, and available validation tooling.
- Created self contained plans with exact file edits, commands, acceptance criteria, rollout, and recovery guidance.
- Validated plan structure and confirmed implementation files were untouched.

Decisions:
- Define `timeout_seconds` as a required positive integer in seconds, with `30` as the canonical example.
- Preserve the existing `start(config)` signature and return value.
- Keep `README.md` and `config.json` unchanged for the private variable rename.

Rejected Alternatives:
- None recorded.

Key Changes:
- Added `plans/public-change.md`, requiring updates to `service.py`, `README.md`, and `config.json`.
- Added `plans/internal-change.md`, limiting implementation to renaming `attempts` to `retry_count` in `service.py`.

Validation:
- Confirmed every required ExecPlan section exists in order.
- Confirmed planned commands use the available `python3` interpreter.
- Confirmed source and canonical documentation content remained unchanged.

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
@@ -0,0 +1,116 @@
+# Rename the private retry local
+
+This ExecPlan is a living document. Keep `Progress`, `Decisions`, `Risks and Mitigations`, and `Lessons Learned` up to date as work advances.
+
+## Purpose / Big Picture
+
+Rename a private local variable in `service.py` to make its meaning clearer without changing any observable behavior. Callers continue to pass the same configuration and receive the same retry count, and neither public configuration nor user documentation changes.
+
+## Scope
+
+In scope is renaming the function local `attempts` to `retry_count` inside `start(config)` and verifying behavioral equivalence. Changes to function names, parameters, return values, configuration keys, configuration values, validation rules, `README.md`, or `config.json` are out of scope.
+
+## Definitions
+
+A private local variable exists only within a function and is not part of the callable API. `start(config)` is the public function defined in `service.py`. A canonical source is an authoritative repository document: `README.md` is the canonical user documentation, and `config.json` is the canonical public configuration reference.
+
+## Existing Context
+
+`service.py` defines `start(config)`. It assigns `config["retries"]` to the local name `attempts` and returns that value. `README.md` says the service reads public settings from `config.json`. `config.json` contains the public setting `"retries": 3`. The repository has no test framework or build configuration.
+
+## Desired End State
+
+Within `start(config)`, the result of `config["retries"]` is stored in `retry_count` and returned through that new local name. For the same inputs, the function produces the same return values and exceptions as before. The public key remains `retries`. `README.md` and `config.json` are byte for byte unchanged because neither private implementation names nor public behavior appear in them.
+
+## Milestones
+
+### Milestone 1: Apply the behavior preserving rename
+
+#### Goal
+
+Improve the internal name without changing the function's inputs, configuration access, output, or error behavior.
+
+#### Changes
+
+Before editing, run `cp service.py /tmp/internal-change-service.before` and `sha256sum README.md config.json > /tmp/internal-change-docs.sha256` from the repository root. These snapshots provide comparison evidence even when the files are not tracked by Git.
+
+Edit only `service.py`. Rename the local variable `attempts` to `retry_count` at both its assignment and return sites. Do not alter `start`, `config`, the string key `"retries"`, or the control flow. Do not edit `README.md` or `config.json`.
+
+No canonical documentation changes are required: both files describe public configuration and do not expose the private local name.
+
+#### Validation
+
+Run:
+
+    python3 - <<'PY'
+    from service import start
+    assert start({"retries": 3}) == 3
+    assert start({"retries": 0}) == 0
+    marker = object()
+    assert start({"retries": marker}) is marker
+    try:
+        start({})
+    except KeyError as error:
+        assert error.args == ("retries",)
+    else:
+        raise AssertionError("missing retries must still raise KeyError")
+    PY
+
+Expected result: the command exits with status 0 and prints no output, demonstrating unchanged pass through and missing key behavior.
+
+Run:
+
+    sha256sum -c /tmp/internal-change-docs.sha256
+
+Expected result: the command reports `README.md: OK` and `config.json: OK`, confirming that both canonical documentation sources remain unchanged.
+
+Run:
+
+    diff -u /tmp/internal-change-service.before service.py
+
+Expected result: the diff contains exactly two substitutions from `attempts` to `retry_count`, at the assignment and return sites, and no other change. The command returns status 1 because differences were intentionally found; inspect the output instead of treating that status as a validation failure.
+
+#### Acceptance Criteria
+
+`service.py` uses `retry_count` and no longer uses the local name `attempts`. The public function signature, `"retries"` key access, return values, object identity, and missing key exception are unchanged. The service snapshot shows only the two intended identifier substitutions, and both canonical documentation checksums are unchanged.
+
+## Progress
+
+- [ ] Milestone 1 started
+- [ ] Milestone 1 completed
+
+## Decisions
+
+- Decision: Rename `attempts` to `retry_count`.
+  Rationale: The new local name matches the meaning of the existing `retries` configuration value without changing the public key.
+  Date/Author: 2026-07-29 / Codex
+- Decision: Leave both canonical documentation files unchanged.
+  Rationale: A function local is private implementation detail, and the rename changes no behavior, API, or configuration fact documented by either source.
+  Date/Author: 2026-07-29 / Codex
+
+## Risks and Mitigations
+
+- Risk: An accidental edit could rename the public `"retries"` key or change the returned value.
+  Mitigation: Limit the patch to the two local identifier occurrences and run assertions for values, identity, and the missing key exception.
+- Risk: Unnecessary documentation edits could imply a public contract change.
+  Mitigation: Capture both files' checksums before implementation and require both checksum validations to pass afterward.
+
+## Validation Strategy
+
+Before editing, capture the service snapshot and documentation checksums using the commands in Milestone 1. Run the focused Python assertions from the repository root. Since there is no broader test suite, these assertions are also the full available behavioral validation. Compare `service.py` with its snapshot and verify exactly two local identifier substitutions, then validate the `README.md` and `config.json` checksums. Finally run `python3 -m py_compile service.py` and require exit status 0.
+
+## Documentation Impact
+
+`README.md` remains accurate without edits because it documents only that public settings come from `config.json`; the private local variable is not mentioned and service behavior is unchanged.
+
+`config.json` remains accurate without edits because the public key is still `"retries"` with the same example value. The rename changes only the in-function name used after that key is read.
+
+Validation requires matching pre-change checksums for both canonical sources, plus comparison with the pre-change `service.py` snapshot to confirm that no public string or signature changed.
+
+## Rollout and Recovery
+
+This is an internal, behavior preserving source change and needs no configuration migration or staged rollout. Deploy it through the normal repository process after validation. If an unexpected regression appears, revert only the two identifier substitutions in `service.py`; no documentation or configuration recovery is needed.
+
+## Lessons Learned
+
+The repository has no automated test harness, so a small executable assertion set and a constrained diff provide the available evidence of behavioral equivalence. The canonical documentation describes public contracts only and intentionally excludes private local names.
--- /dev/null
+++ b/plans/public-change.md
@@ -0,0 +1,137 @@
+# Add the public timeout configuration
+
+This ExecPlan is a living document. Keep `Progress`, `Decisions`, `Risks and Mitigations`, and `Lessons Learned` up to date as work advances.
+
+## Purpose / Big Picture
+
+Add `timeout_seconds` to the service's public configuration so callers can supply a timeout duration in seconds. A caller can observe that `start(config)` recognizes the new required setting while its existing return value, the configured retry count, remains unchanged.
+
+## Scope
+
+In scope are loading the new field in `service.py`, adding it to the canonical public configuration example in `config.json`, documenting it in the canonical user guide `README.md`, and validating the public contract. The field is a required positive integer expressed in seconds; the example value is `30`. Implementing elapsed time handling, changing retry behavior, or changing the return value of `start(config)` is out of scope.
+
+## Definitions
+
+`timeout_seconds` is the maximum duration configured for service work, represented as a positive whole number of seconds. A canonical source is the repository file that is authoritative for a particular kind of information: `README.md` is authoritative user documentation, and `config.json` is the authoritative public configuration reference and example. `start(config)` is the public function in `service.py` that reads configuration.
+
+## Existing Context
+
+The repository has three relevant files and no test framework or build configuration. `service.py` defines `start(config)`, reads the required `retries` key into the local variable `attempts`, and returns that retry count. `config.json` contains only `"retries": 3`. `README.md` says that public settings come from `config.json`, but it does not list or explain individual settings.
+
+Because no timeout driven operation exists in this repository, this change introduces and loads the configuration contract without pretending to enforce elapsed time. Any later implementation that consumes the timeout operationally must receive a separate behavioral plan.
+
+## Desired End State
+
+`service.py` reads both required public keys, `retries` and `timeout_seconds`, from the supplied configuration. A complete configuration containing `{"retries": 3, "timeout_seconds": 30}` makes `start(config)` return `3`, preserving the existing return contract. Omitting `timeout_seconds` raises `KeyError`, consistently with the existing required `retries` lookup. `README.md` explains the field, its unit, its positive integer constraint, and its required status. `config.json` contains the canonical example value.
+
+## Milestones
+
+### Milestone 1: Define and load the public field
+
+#### Goal
+
+Establish the required `timeout_seconds` configuration contract in code while preserving the observable retry result from `start(config)`.
+
+#### Changes
+
+Edit `service.py` so `start(config)` reads `config["timeout_seconds"]` into a clearly named local value alongside `config["retries"]`. Do not change the function signature or the returned retry count. Keep the edit limited to configuration loading because the repository contains no operation to which a runtime timeout can honestly be applied.
+
+This milestone also edits the canonical sources `README.md` and `config.json`, as detailed in Milestone 2, before the change is considered complete.
+
+#### Validation
+
+Run:
+
+    python3 - <<'PY'
+    from service import start
+    assert start({"retries": 3, "timeout_seconds": 30}) == 3
+    try:
+        start({"retries": 3})
+    except KeyError as error:
+        assert error.args == ("timeout_seconds",)
+    else:
+        raise AssertionError("timeout_seconds must be required")
+    PY
+
+Expected result: the command exits with status 0 and prints no output.
+
+#### Acceptance Criteria
+
+With both public settings present, `start(config)` still returns the retry count. With `timeout_seconds` absent, it fails on that required key. No elapsed time behavior, public function signature, or return contract changes.
+
+### Milestone 2: Reconcile canonical public documentation
+
+#### Goal
+
+Make both canonical documentation sources describe the same new public contract as the code.
+
+#### Changes
+
+Edit `config.json` to add `"timeout_seconds": 30` while retaining `"retries": 3` and valid JSON syntax. Edit `README.md` to list `timeout_seconds`, say that it is required, define seconds as the unit, state that the value is a positive integer, and point readers to the example in `config.json`.
+
+#### Validation
+
+Run:
+
+    python3 - <<'PY'
+    import json
+    from pathlib import Path
+    config = json.loads(Path("config.json").read_text())
+    readme = Path("README.md").read_text()
+    assert config == {"retries": 3, "timeout_seconds": 30}
+    for text in ("timeout_seconds", "required", "positive integer", "seconds"):
+        assert text in readme
+    PY
+
+Expected result: the command exits with status 0 and prints no output.
+
+Then run the Milestone 1 command again as the repository's full available behavioral validation.
+
+#### Acceptance Criteria
+
+`config.json` parses and contains both public settings. `README.md` gives enough information to configure `timeout_seconds` without consulting implementation code. The documented required status, type, unit, and example agree with `service.py` and `config.json`.
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
+- Decision: Define `timeout_seconds` as a required positive integer in seconds, using `30` in the canonical example.
+  Rationale: The name supplies the unit, and an explicit required contract matches the direct key access already used by `service.py`.
+  Date/Author: 2026-07-29 / Codex
+- Decision: Preserve the signature and retry count return value of `start(config)`.
+  Rationale: The request adds a configuration field but does not authorize an unrelated API return change.
+  Date/Author: 2026-07-29 / Codex
+
+## Risks and Mitigations
+
+- Risk: Loading the field could be mistaken for enforcing an operational timeout.
+  Mitigation: State the boundary in code adjacent documentation and in `README.md`; schedule actual timeout enforcement separately when a timeout capable operation exists.
+- Risk: Code and the two canonical sources could disagree about whether the field is required or what unit it uses.
+  Mitigation: Validate the missing key behavior, the JSON example, and the required type and unit wording together.
+- Risk: Existing callers that supply only `retries` will receive `KeyError`.
+  Mitigation: Treat this as an intentional public configuration migration, document the required field, and ensure deployment configuration is updated before releasing the code.
+
+## Validation Strategy
+
+First run the focused `start(config)` assertions from Milestone 1. Next parse and inspect both canonical documents with the Milestone 2 command. Then rerun both commands from the repository root as the full available validation because this repository has no broader test suite. Finally inspect `service.py`, `README.md`, and `config.json` directly and confirm that every changed public fact is represented consistently in all three files; do not rely on `git diff`, because this fixture's files are not tracked.
+
+## Documentation Impact
+
+`README.md` must change because adding a public field changes what users must supply. It must define `timeout_seconds` as required, positive, integer valued, and measured in seconds.
+
+`config.json` must change because it is the canonical public configuration reference. It must retain `retries` and add `"timeout_seconds": 30` as the valid example.
+
+Both sources are validated in Milestone 2 and reconciled against the direct required lookup in `service.py`.
+
+## Rollout and Recovery
+
+Before release, add `timeout_seconds` to every deployed configuration using an approved positive integer value. Release the configuration update together with, or immediately before, the code change so existing deployments do not fail on the new required key. To recover, revert the `service.py`, `README.md`, and `config.json` edits together; do not leave the canonical sources describing a field the code no longer loads. Extra `timeout_seconds` keys in already updated external configurations can remain temporarily because the reverted function ignores unknown keys.
+
+## Lessons Learned
+
+The repository currently has no timeout capable operation and no automated test harness. This plan therefore separates introducing the public configuration contract from future operational timeout enforcement and provides standalone Python assertions for validation.
```

## Integrity

- Report digest: `sha256:012a8493e86f468c1eb1956306e1a071a6850883170a989576848e0ed43766cd`
