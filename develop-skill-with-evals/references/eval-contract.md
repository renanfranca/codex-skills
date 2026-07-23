# Evaluation contract

Use this reference when adding cases or interpreting runner results. Do not load files under `evals/` into the executor prompt except the selected case's raw `prompt.md` and fixture tree.

## Suite layout

Store a suite at `<skill>/evals/suite.json`:

```json
{
  "version": 1,
  "cases": ["case-id"]
}
```

Store every case at `<skill>/evals/cases/<case-id>/` with:

- `case.json`: runner configuration and hidden expected contract;
- `prompt.md`: raw user request sent to the executor;
- `fixture/`: optional isolated starting workspace.

The case manifest supports:

```json
{
  "id": "case-id",
  "kind": "behavioral",
  "prompt_file": "prompt.md",
  "implicit_skill": false,
  "mechanical": {
    "expected_exit_code": 0,
    "required_paths": ["src/result.txt"],
    "forbidden_changed_paths": [".agents/skills/**"],
    "commands": [{"argv": ["python3", "-m", "unittest"], "exit_code": 0}]
  },
  "judge": {
    "enabled": true,
    "criteria": ["The response identifies the demonstrated design risk."],
    "no_action_acceptable": false
  }
}
```

`kind` is `behavioral`, `non_behavioral`, or `trigger`. Behavioral changes require a real baseline failure. `implicit_skill` omits the explicit `$skill-name` instruction while still installing a repository-scoped copy for trigger smoke tests.

Paths are relative to the disposable workspace. Glob patterns use Python `fnmatch` semantics. Commands run without a shell after the executor returns. Never put credentials, proprietary source, full transcripts, or an answer key in fixtures.

## Execution isolation

For each run, the runner creates a fresh directory under `/tmp`, copies the fixture, initializes a Git repository for change detection, and installs the evaluated skill under `.agents/skills/<name>`. It invokes `codex exec` with `--ephemeral`, `--sandbox workspace-write`, a structured output schema, and the selected model. The executor receives only the raw prompt plus the explicit skill instruction when `implicit_skill` is false.

The runner snapshots files before and after execution, verifies commands and paths, and separately asks a judge to evaluate the case criteria when enabled. The judge receives the expected criteria, executor response, mechanical evidence, and diff summary; the executor never receives the criteria.

## Progress output

The runner reserves standard output for the JSON report. Progress goes only to standard error and is flushed immediately without colors, spinners, timestamps, or captured subprocess output.

Without an explicit option, progress is enabled when standard error is a TTY and disabled otherwise. `--progress` forces it for monitored runs with captured standard error; `--quiet` suppresses it in a terminal. The options are mutually exclusive. TTY detection controls output only: every operation remains autonomous and never requests input or confirmation.

Progress covers operation and case preparation, executor invocation, mechanical checks, semantic judgment, each case result, and the final result. `verify-change` labels baseline and candidate phases, while `stability` labels the current repetition and total.

## Status policy

- `PASS`: all mechanical checks and the semantic judge pass.
- `FAIL`: an observable contract check fails.
- `ERROR`: the runner, manifest, or process cannot execute reliably.
- `INCONCLUSIVE`: the judge cannot establish the contract.
- `INVALID_RED`: a behavioral case passes on the baseline.
- `UNSTABLE`: repeated verdict signatures disagree.

All statuses except `PASS` block promotion. Keep detailed artifacts for blocking results and remove successful workspaces. Reports conform to `eval-result.schema.json`.

## Change verification

`verify-change` evaluates the same case against baseline and candidate with the same resolved model and runner configuration. A valid behavioral change requires baseline `FAIL` and candidate `PASS`. A passing baseline yields `INVALID_RED`. For non-behavioral cases, skip the artificial RED and require structural validation plus the full candidate regression.

`stability --runs 3` compares normalized verdict signatures: overall status, mechanical check outcomes, judge verdict, and outcome-relevant changed-path set. Harness files named `.eval-*` and generated Python `__pycache__`/`.pyc` files are excluded; production-path differences remain significant. Any other difference yields `UNSTABLE`.
