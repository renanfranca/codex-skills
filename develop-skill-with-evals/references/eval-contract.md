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
  "oracle": {
    "commands": [
      {"argv": ["python3", "{oracle_dir}/check_contract.py"], "exit_code": 0}
    ]
  },
  "judge": {
    "enabled": true,
    "criteria": ["The response satisfies the expected semantic outcome."],
    "no_action_acceptable": false
  }
}
```

The runner creates a disposable workspace, installs the evaluated skill under `.agents/skills/<name>` without `evals/`, invokes an ephemeral Codex executor, runs public mechanical checks and hidden oracle commands as direct argument arrays without a shell, and invokes the judge when enabled. The executor receives only the raw prompt, public fixture and explicit skill instruction unless `implicit_skill` is true. It never receives judge criteria, answer keys or the case's `oracle/` directory.

Place a checker under `<case>/oracle/` only when it covers the complete expected contract. Use `{oracle_dir}` in `oracle.commands` argv or read `SKILL_EVAL_ORACLE_DIR`. The runner fingerprints oracle modes and bytes, resolves the placeholder to an absolute runner controlled path and never copies that directory into the executor workspace. A manifest without `oracle` remains valid.

A hidden oracle may require literal text only when the public prompt requires that same literal text. If wording may vary and code can completely bound the required concepts, use controlled lexical equivalence and retain exact structural checks. Do not accept unrestricted paraphrases.

One executor invocation is one model session. An enabled judge adds one planned session, but is skipped without consumption when mechanical or oracle checks fail. The executor response includes the compatibility fields `summary`, `classification`, `evidence`, and `files_changed` plus `diagnosis`, `approach`, `decisions`, `rejected_alternatives`, `key_changes`, and `validation`. The added arrays may be empty. Record concise decisions actually made; never request private reasoning or reconstructed chain of thought.

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

`plan` loads and validates all manifests, selects gates, resolves the declared runtime, and calculates sessions without creating workspaces, ledger files or artifacts. It always exits zero, including when `execution_blockers` is nonempty. `--workflow` accepts `diagnostic` or `promotion` and defaults to `promotion`. With deterministic impact and no `--case`, it selects every deterministic suite case. Explicit deterministic selections must be deterministic. Scoped and cross cutting plans require at least one affected case. Cross cutting plans assign every remaining suite case to one regression execution.

The plan conforms to `eval-plan.schema.json`. `manifest_fingerprint` preserves the normalized manifest hash. `case_fingerprints` cover each case's manifest, prompt, fixture and oracle with file modes. `source_fingerprints` cover baseline and candidate inputs. `evaluation_fingerprint` binds those values to selection, workflow and runtime. Every fingerprint is recomputed from materialized snapshots before the first model.

Promotion reports one baseline and three candidate executions for each affected case. It orders affected baseline, affected candidate repetition one, remaining cross cutting regressions, then affected repetitions two and three. Diagnostic reports one affected baseline, one affected candidate and one execution of every regression. Session totals derive from case kind and judge configuration, so deterministic cases add zero, semantic cases add one executor session, and enabled judges add one maximum judge session per execution.

Planning counts sessions, not tokens, elapsed time, or money. Treat uncertain reach as cross cutting; reducing the declared impact merely to avoid cost is invalid workflow.

## Auditable runtime

All six commands accept `--model`, `--reasoning-effort`, `--judge-model`, and `--judge-reasoning-effort`. Executor model precedence is CLI, `CODEX_MODEL`, then an unknown configured default. Executor reasoning effort comes from CLI or remains an unknown configured default. Judge fields use their CLI values or inherit the executor.

The runner does not read `config.toml`. Unknown defaults are `null` in the runtime object and `configured-default` in the compatibility top-level `model` field. Every known model is passed as `--model <value>`. Every known effort is passed as the direct argument pair `-c`, `model_reasoning_effort="<value>"`.

A promotion runtime is complete when every model-backed plan has executor model and effort from CLI and every required judge field is either supplied by judge CLI options or inherited from that complete executor. `CODEX_MODEL` is propagated for compatibility but produces exploratory, not promotion, audit quality.

`runtime_fingerprint` hashes canonical JSON containing the manifest fingerprint, role requirements, resolved values, and sources. It excludes paths, budget, and derived fields. `evaluation_fingerprint` adds case and source inputs plus workflow and selection. These values record intended execution without claiming deterministic model output.

## Economic runtime guidance

Every plan contains an informative `economic_runtime` object with policy version 1. It never changes explicit runtime values, planned commands, blockers, CLI defaults or session approval.

`zero-session` applies to static and deterministic plans and recommends neither role. `scoped-complete-oracle` applies only when every selected scoped case is semantic, declares at least one `oracle.commands` entry and disables the judge; it recommends `gpt-5.6-luna` with `medium` for the executor. Every other model backed plan uses `manual-selection` for the executor. A required judge independently recommends `gpt-5.6-terra` with `medium`.

`matches_explicit_runtime` is `null` when no recommendation exists or the corresponding role lacks a complete CLI declaration. A complete declaration that differs from the recommendation sets it to `false` and adds a warning without adding a blocker. The runtime supplied by the user remains in the planned command.

Bind the complete `economic_runtime` object into `evaluation_fingerprint`, but not `runtime_fingerprint`. Recompute and compare it with the original plan after materializing baseline and candidate snapshots.

## Diagnostic workflow

`probe-change` uses the diagnostic plan and is never promotion eligible. It observes each planned execution once and continues after `contract` failures so one paid pass can report multiple defects. It stops immediately when `failure_category` is `infrastructure`, including authentication, quota, process launch and unavailable subprocess failures.

A valid affected baseline `FAIL` is expected RED and does not make the diagnostic fail. An affected baseline `PASS` produces `INVALID_RED`. Candidate or regression contract failures produce a blocking diagnostic result. Do not rerun a complete unchanged diagnostic to seek a better outcome.

## Integrated change validation

`validate-change` builds the same promotion plan before allocating an operation directory. It aggregates missing explicit executor runtime, unresolved required judge runtime, insufficient operation budget and insufficient cumulative campaign budget as ordered blockers. Any blocker prints the plan, creates no workspace, artifact or ledger, invokes no model, and returns exit code 2. The default approved limit is eight maximum model sessions.

`--campaign-ledger` and `--approved-cumulative-model-sessions` must be supplied together. The ledger uses an exclusive file lock, atomic replacement and a conservative maximum reservation. Budget checks include consumed sessions and every active reservation. Actual consumption is recorded after every executor or judge result, including failures; unused reservation is released when the operation finishes. A corrupt or inconsistent ledger blocks execution.

After approval, the runner snapshots both sources and verifies that the candidate manifest fingerprint, runtime fingerprint, selection, and counts still match the approved plan. Validation then:

1. snapshots baseline and candidate;
2. runs every affected case once on baseline;
3. returns `INVALID_RED` if a baseline passes and blocks on any baseline status other than `FAIL`;
4. runs each affected case once on candidate and stops at the first non `PASS`;
5. for cross cutting impact, runs each remaining case once and stops at the first non `PASS`;
6. runs affected candidate repetitions two and three;
7. returns `UNSTABLE` when three passing normalized signatures diverge.

There are no automatic retries after failures, inconclusive judgments, or instability. Repeating an unchanged evaluation to seek PASS is prohibited.

## Progress and compatibility

Standard output contains only the JSON plan or result. Progress goes only to standard error and flushes immediately without colors, spinners, timestamps, or captured subprocess output.

Without an option, progress follows `stderr.isatty()`. `--progress` forces it and `--quiet` suppresses it; they are mutually exclusive. Existing `run`, `verify-change`, and `stability` behavior remains compatible. Deterministic cases omit executor and judge progress phases because neither runs.

Executed stdout results include the resolved runtime, top-level actual `model_sessions`, `promotion_eligible`, `failure_category`, `usage` and `campaign`. Every executor and judge invocation uses `codex exec --json`. Token aggregation preserves missing values as `null`; `usage.complete` retains compatibility for input, cached input, and output while `reasoning_output_tokens_complete` states whether reasoning output was exposed. Preserve each sanitized usage object's sequence, source event type, scope, token counts, and completeness under `usage.events`; never persist the raw JSONL event. Treat `turn.completed` as turn scoped and every unrecognized event as unknown scope. It never substitutes zero for unknown usage. Per-result session fields remain compatible. A disabled judge has `enabled: false`, `executed: false`, and `PASS`. An executed judge has both flags true. A judge skipped after mechanical or oracle failure has `enabled: true`, `executed: false`, `SKIPPED`, and zero actual sessions.

## Durable evidence reports

Executed commands accept `--report-dir` and `--no-report`. An explicit report directory persists canonical evidence at `<report-dir>/<operation-id>/report.json` before successful workspace cleanup, then renders `report.md` deterministically from the JSON. `--pricing-file` requires `--report-dir`. `--no-report` is incompatible with either option.

When neither option is present, locate `evaluation-reports/archive-config.json` relative to the repository containing the runner. Automatically archive only operations that consumed at least one session and used a Codex command whose basename is `codex`. Write under `evaluation-reports/<skill-name>/operations/<operation-id>/` and apply the pricing snapshot named by the config. Fakes, deterministic operations, and zero session operations do not archive implicitly. Without the config, preserve compatibility. Report persistence does not change the stdout result contract.

Treat a persistence failure after session consumption as blocking infrastructure failure and retain diagnostic artifacts. Never stage, commit, push, or publish from the runner.

Canonical evidence records operation, workflow, role, repetition, provenance `executed`, fingerprints, Codex CLI version when available, sanitized authentication mode, runner digest, runtime by role, planned and executed sessions, timestamps, durations, usage completeness, case prompt, structured executor response, mechanical facts, oracle and judge results, changed files, bounded diff, bounded fragments, truncations, and a SHA-256 report digest.

Query failures for CLI version or authentication metadata do not block evaluation. Never persist raw metadata output. Normalize authentication only to `chatgpt`, `api-key`, or `unknown`.

An explicit pricing snapshot uses version 1, an effective date, source, currency, `per_million_tokens`, model rates for `input`, `cached_input`, and `output`, and limitations. It may add a `long_context` object containing `input_token_threshold`, `input_multiplier`, `output_multiplier`, and `applies_per: request`. Calculate uncached input as input minus cached input. Do not add reasoning output tokens a second time because they are part of output tokens. When a non request scoped event exceeds a request scoped threshold, set the exact estimate to unavailable and preserve only `base_rate_amount` with status `indeterminate-long-context`. Every amount is an API reference estimate with `actual_charge: false`; this is especially important for ChatGPT authentication.

Evidence excludes any path under `.git`, `.agents/skills`, `.eval-*`, or `__pycache__`, plus `*.pyc`. Enforce deterministic per file and per report limits and declare every truncation. Do not persist raw JSONL, complete transcripts, private reasoning, hidden oracle contents, credentials, or generated model responses beyond the bounded structured executor contract.

Canonical reports conform to [eval-report.schema.json](eval-report.schema.json). Renderers and comparisons reject incompatible schemas and invalid digests. Use `render_eval_report.py` to replay Markdown without a model. Use `compare_model_reports.py` only on one skill at a time to group reports by executor model and case, reject duplicate operation IDs, require at least three stable PASS observations in every represented case for qualification, and compare tokens, cache ratio, duration, complete API reference cost, base rate reference, effective cost per stable gate, and explanation completeness and coherence. Never sum a partial set of exact estimates. A small comparison remains directional evidence.

Use `manage_evaluation_archive.py rebuild --archive evaluation-reports` to regenerate every report Markdown file, manifest, and configured comparison from canonical JSON. Use `validate` to verify schema versions, digests, unique IDs, byte identical projections, pricing semantics, manifest consistency, forbidden artifact classes, and credential patterns without invoking a model.

## Status and artifacts

- `PASS`: every required gate passed.
- `FAIL`: an observable contract check failed.
- `ERROR`: a runner, manifest, or process could not execute reliably.
- `INCONCLUSIVE`: a judge could not establish the contract.
- `INVALID_RED`: an affected case passed on baseline.
- `UNSTABLE`: candidate normalized signatures diverged.

Only `PASS` permits promotion. Blocking operations retain artifacts; successful workspaces are removed. Plans conform to `eval-plan.schema.json`, and executed reports conform to `eval-result.schema.json`.

Normalized stability signatures contain overall status, mechanical check outcomes, judge verdict, and outcome relevant changed paths. Harness files named `.eval-*` and generated `__pycache__` or `.pyc` files are excluded; production paths remain significant.
