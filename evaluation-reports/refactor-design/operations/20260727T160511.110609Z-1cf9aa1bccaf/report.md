# Evaluation evidence: 20260727T160511.110609Z-1cf9aa1bccaf

- Operation: `probe-change`
- Status: `ERROR`
- Provenance: `executed`
- Started: `2026-07-27T16:05:11.110609Z`
- Finished: `2026-07-27T16:05:11.342435Z`
- Duration: `325 ms`
- Executor model: `gpt-5.6-sol`
- Executor effort: `medium`
- Codex CLI: `codex-cli 0.145.0`
- Authentication: `unknown`
- Runner SHA-256: `30f579584ba4eb2c9d21a68786aaae41f336a012c01cad35f4079e72a1e640e5`

## Consumption

- Tokens: input `unknown`, cached input `unknown`, output `unknown`, reasoning output `unknown`
- Normalized usage events: `0`, complete `false`, scopes `none`
- Sessions: planned `32`, executed `1`

## API reference estimate

- Reference amount: unavailable
- This is not an actual charge.
- Estimate status: `unavailable`
- Limitation: This is an API reference estimate, not an observed charge.
- Limitation: This dated table is an API reference and is not an observed ChatGPT charge.
- Limitation: Prompts above 272,000 input tokens use the documented higher rates; an exact estimate is unavailable when normalized telemetry does not expose request scoped input.
- Limitation: Cache write charges are not estimated because Codex JSONL usage does not identify cache writes.
- Limitation: Reasoning output tokens are reported separately but are already included in output tokens.
- Limitation: Observed token usage is incomplete.

## Observation 1: hidden-invocation-state

- Status: `ERROR`
- Role: `baseline`
- Repetition: `1`
- Duration: `181 ms`
- Workspace retention: `retained`
- Tokens: input `unknown`, cached input `unknown`, output `unknown`, reasoning output `unknown`
- Normalized usage events: `0`, complete `false`, scopes `none`

### Executor account

Executor did not provide a structured response.

### Mechanical facts

- Mechanical result: `FAIL`
- Oracle result: `PASS`
- Judge verdict: `SKIPPED`
- `executor exit code`: `FAIL`
- `executor response schema`: `FAIL`
- `required path: report_builder.py`: `PASS`
- `required path: test_report_builder.py`: `PASS`
- `forbidden changed path: release_notes.md`: `PASS`
- `forbidden changed path: test_report_builder.py`: `PASS`
- `forbidden changed path: .agents/skills/**`: `PASS`
- `evaluated skill remained unchanged`: `PASS`
- `command: python3 -m unittest -q`: `PASS`

### Changed files

- None.

### Sanitized diff

```diff

```

## Integrity

- Report digest: `sha256:91df6fdba4518e996ab34bcd300761ea4a1f08a430c886d117a59be4de0506ea`
