# Evaluation contract

Use this reference when adding cases, planning gates, or interpreting results. Do not load files under `evals/` into an executor prompt except the selected semantic case's raw prompt and fixture.

## Suite layout

Store a suite at `<skill>/evals/suite.json`:

```json
{
  "version": 1,
  "cases": ["case-id"]
}
```

Each ID is unique and maps to `<skill>/evals/cases/<case-id>/case.json`. Semantic cases also have `prompt.md`; every case may have a minimal `fixture/`.

## Semantic cases

`behavioral`, `non_behavioral`, and `trigger` cases keep the existing executor contract:

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
    "criteria": ["The response satisfies the expected semantic outcome."],
    "no_action_acceptable": false
  }
}
```

The runner creates a disposable workspace, installs the evaluated skill under `.agents/skills/<name>` without `evals/`, invokes an ephemeral Codex executor, runs mechanical checks as direct argument arrays without a shell, and invokes the judge when enabled. The executor receives only the raw prompt plus the explicit skill instruction unless `implicit_skill` is true. It never receives judge criteria or answer keys.

One executor invocation is one model session. An enabled judge adds one planned session, but is skipped without consumption when mechanical checks fail.

## Deterministic cases

Use `kind: "deterministic"` only when code can observe the complete contract:

```json
{
  "id": "runner-output",
  "kind": "deterministic",
  "mechanical": {
    "commands": [
      {"argv": ["python3", "check_output.py"], "exit_code": 0}
    ]
  },
  "judge": {
    "enabled": false,
    "criteria": []
  }
}
```

A deterministic case:

- requires at least one required path, forbidden changed path, or command;
- forbids `prompt_file`, `implicit_skill`, `executor`, `mechanical.expected_exit_code`, and an enabled judge;
- does not require `prompt.md`;
- does not create an executor response;
- records executor and judge as disabled;
- consumes zero model sessions;
- runs commands as direct argv without a shell;
- sets `SKILL_EVAL_SKILL_DIR` to the absolute, immutable snapshot being evaluated.

Commands run inside a fresh fixture workspace. The runner hashes the evaluated snapshot before and after every case and blocks any mutation.

## Impact planning

Classify each proposed change:

- `static`: text or formatting unable to affect behavior;
- `deterministic`: behavior completely observable by code;
- `scoped`: semantic behavior limited to enumerated cases;
- `cross-cutting`: central or shared behavior, safety, selection, or uncertain reach.

`plan` loads and validates all manifests, selects gates, resolves the declared runtime, and calculates sessions without creating workspaces or artifacts. It always exits zero, including when `execution_blockers` is nonempty. With deterministic impact and no `--case`, it selects every deterministic suite case. Explicit deterministic selections must be deterministic. Scoped and cross cutting plans require at least one affected case. Cross cutting plans assign every remaining suite case to one regression execution.

The plan conforms to `eval-plan.schema.json` and includes a normalized manifest fingerprint, runtime fingerprint, runtime object, and ordered blockers. It reports one baseline and three candidate executions for each affected case. Remaining cross cutting regression cases run once on the candidate. Session totals derive from case kind and judge configuration, so deterministic cases add zero, semantic cases add one executor session, and enabled judges add one maximum judge session per execution.

Planning counts sessions, not tokens, elapsed time, or money. Treat uncertain reach as cross cutting; reducing the declared impact merely to avoid cost is invalid workflow.

## Auditable runtime

All five commands accept `--model`, `--reasoning-effort`, `--judge-model`, and `--judge-reasoning-effort`. Executor model precedence is CLI, `CODEX_MODEL`, then an unknown configured default. Executor reasoning effort comes from CLI or remains an unknown configured default. Judge fields use their CLI values or inherit the executor.

The runner does not read `config.toml`. Unknown defaults are `null` in the runtime object and `configured-default` in the compatibility top-level `model` field. Every known model is passed as `--model <value>`. Every known effort is passed as the direct argument pair `-c`, `model_reasoning_effort="<value>"`.

A promotion runtime is complete when every model-backed plan has executor model and effort from CLI and every required judge field is either supplied by judge CLI options or inherited from that complete executor. `CODEX_MODEL` is propagated for compatibility but produces exploratory, not promotion, audit quality.

`runtime_fingerprint` hashes canonical JSON containing the manifest fingerprint, role requirements, resolved values, and sources. It excludes paths, budget, and derived fields. This records the intended runtime without claiming deterministic model output.

## Integrated change validation

`validate-change` builds the same plan before allocating an operation directory. It aggregates missing explicit executor runtime, unresolved required judge runtime, and insufficient budget as ordered blockers. Any blocker prints the plan, creates no workspace or artifact, invokes no model, and returns exit code 2. The default approved limit is eight maximum model sessions.

After approval, the runner snapshots both sources and verifies that the candidate manifest fingerprint, runtime fingerprint, selection, and counts still match the approved plan. Validation then:

1. snapshots baseline and candidate;
2. runs every affected case once on baseline;
3. returns `INVALID_RED` if a baseline passes and blocks on any baseline status other than `FAIL`;
4. runs each affected case up to three times on candidate, stopping at the first non `PASS`;
5. returns `UNSTABLE` when three passing normalized signatures diverge;
6. for cross cutting impact, runs each remaining case once and stops at the first non `PASS`.

There are no automatic retries after failures, inconclusive judgments, or instability. Repeating an unchanged evaluation to seek PASS is prohibited.

## Progress and compatibility

Standard output contains only the JSON plan or result. Progress goes only to standard error and flushes immediately without colors, spinners, timestamps, or captured subprocess output.

Without an option, progress follows `stderr.isatty()`. `--progress` forces it and `--quiet` suppresses it; they are mutually exclusive. Existing `run`, `verify-change`, and `stability` behavior remains compatible. Deterministic cases omit executor and judge progress phases because neither runs.

Executed reports include the resolved runtime and top-level actual `model_sessions`. Per-result session fields remain compatible. A disabled judge has `enabled: false`, `executed: false`, and `PASS`. An executed judge has both flags true. A judge skipped after mechanical failure has `enabled: true`, `executed: false`, `SKIPPED`, and zero actual sessions.

## Status and artifacts

- `PASS`: every required gate passed.
- `FAIL`: an observable contract check failed.
- `ERROR`: a runner, manifest, or process could not execute reliably.
- `INCONCLUSIVE`: a judge could not establish the contract.
- `INVALID_RED`: an affected case passed on baseline.
- `UNSTABLE`: candidate normalized signatures diverged.

Only `PASS` permits promotion. Blocking operations retain artifacts; successful workspaces are removed. Plans conform to `eval-plan.schema.json`, and executed reports conform to `eval-result.schema.json`.

Normalized stability signatures contain overall status, mechanical check outcomes, judge verdict, and outcome relevant changed paths. Harness files named `.eval-*` and generated `__pycache__` or `.pyc` files are excluded; production paths remain significant.
