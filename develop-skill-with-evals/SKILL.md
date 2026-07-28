---
name: develop-skill-with-evals
description: Create or improve Codex skills through impact-aware evaluation development with isolated fixtures, diagnostic probes, proportional RED and GREEN gates, hidden mechanical oracles, durable execution evidence, session, token and duration telemetry, API price references, cumulative campaign budgets, stability evidence, model report comparison, and fresh-agent validation. Use when Codex is asked to build or change a skill, add skill evals, forward-test behavior, validate trigger selection, persist or compare evaluation reports, modify an evaluation runner or contract, or safely evolve this skill itself.
---

# Develop Skill with Evals

Develop skills through observable evidence while keeping evaluation cost proportional to the change.

## Load the foundation first

Before creating, editing, scaffolding, or evaluating a skill:

1. Announce that `skill-creator` is required.
2. Read its `SKILL.md` completely in the current turn.
3. Follow its creation, metadata, progressive disclosure, validation, and forward-testing rules.

Do not proceed from memory or delegate those instructions.

## Resolve the writable source

Locate the canonical source and distinguish it from installed caches, plugin copies, generated bundles, and temporary candidates. Confirm authorization before writing outside the workspace. Never commit, push, publish, or modify a system skill without explicit authorization.

## Prepare safe evaluations

Read [references/eval-contract.md](references/eval-contract.md) completely before changing a case or invoking the runner. Validate plans against [references/eval-plan.schema.json](references/eval-plan.schema.json) and reports against [references/eval-result.schema.json](references/eval-result.schema.json).

Reduce examples to minimal generic fixtures. Remove credentials, personal data, proprietary source, transcripts, and irrelevant structure. Keep raw prompts separate from hidden expected contracts. Never mention case fixtures or answer keys from the target skill instructions.

## Classify impact before choosing gates

Classify the proposed diff, not merely the user's label:

- `static`: documentation, comments, formatting, or display text that cannot affect selection or behavior;
- `deterministic`: runner, schema, serialization, exit code, artifact, or other behavior completely observable by code;
- `scoped`: agent behavior whose affected cases can be enumerated confidently;
- `cross-cutting`: triggering, safety, central workflow, shared references, or any change with uncertain reach.

Underestimating impact is a workflow error. Use `cross-cutting` whenever confidence in the boundary is insufficient.

Run `plan` before any model-backed evaluation:

```text
python3 develop-skill-with-evals/scripts/run_skill_evals.py plan \
  --skill <candidate> --baseline <baseline> --impact <impact> [--case <id>]... \
  --workflow promotion \
  --model <executor-model> --reasoning-effort <effort> \
  --judge-model <judge-model> --judge-reasoning-effort <effort>
```

Planning is side effect free and uses no model. Inspect selected and regression cases, commands, executor and judge session counts, runtime, case, source, runtime and evaluation fingerprints, campaign projection, execution blockers, reasons, and warnings before executing. Runtime declarations do not make model output deterministic; they make the intended execution auditable.

## Select runtime explicitly

Use zero real sessions for `static` and `deterministic` changes. For model backed evaluations in this repository, recommend `gpt-5.6-sol` with `medium` reasoning effort for both executor and judge. Declare the executor explicitly; a required judge may inherit that complete runtime or receive the same values through its own flags.

This recommendation is guidance, not a runner default. Always preserve a runtime explicitly chosen by the user. Do not retry an unchanged blocking evaluation; require diagnosis, a material change or new hypothesis, a new plan, and fresh cost approval.

## Apply proportional gates

For `static`, apply only the structural gates listed by the plan. Do not invent RED or run semantic cases incapable of observing the change.

For `deterministic`, add or change a deterministic case first. It must use direct mechanical checks, no executor, and no semantic judge. Demonstrate baseline failure, candidate success in three stable runs, and structural validity.

For `scoped`, add or change only the affected semantic cases first. Require baseline `FAIL`, three candidate `PASS` results with one stable normalized signature, and structural validity. Do not run unrelated suite cases.

For `cross-cutting`, apply the first candidate gate to explicitly affected cases, run every remaining suite case once as regression, then complete candidate repetitions two and three. Affected cases must not run again in the regression phase. Stop before repetitions two and three when an early regression fails.

Use the integrated command:

```text
python3 develop-skill-with-evals/scripts/run_skill_evals.py validate-change \
  --skill <candidate> --baseline <baseline> --impact <impact> \
  [--case <id>]... \
  --model <executor-model> --reasoning-effort <effort> \
  --judge-model <judge-model> --judge-reasoning-effort <effort> \
  [--approved-model-sessions <n>] \
  [--campaign-ledger <path> --approved-cumulative-model-sessions <n>] \
  --progress
```

When the plan includes model sessions, `validate-change` requires the executor model and reasoning effort explicitly from CLI. A required judge may declare its own CLI values or inherit the complete executor runtime. The runner never reads `config.toml`. `CODEX_MODEL` remains compatible with exploratory commands but is not sufficient for promotion.

The default approved limit is eight model sessions. Missing promotion runtime, unresolved required judge runtime, an estimate above the operation limit, or a campaign projection above cumulative approval returns the complete plan with exit code 2 before workspaces, artifacts, ledger creation, or model calls. `--approved-model-sessions` approves one operation. The paired campaign options bind diagnostic and promotion consumption to one locked, atomically written ledger under an explicit cumulative maximum. Shell, sandbox, or command approval is not cost approval.

Before the first nested model backed operation, run `codex doctor --json` at the same permission boundary that will launch the runner and require `overallStatus: ok`. Starting the interactive TUI with `--ask-for-approval on-request` does not automatically elevate its noninteractive subprocesses. If the preflight reports that `CODEX_HOME` is read only or that network access is unavailable, request external approval for the complete runner command. Keep every nested executor and judge in the runner's internal `workspace-write` sandbox. Do not use `danger-full-access`, bypass approval, or copy authentication state into `/tmp`.

Obtain model session cost authorization separately from shell approval. Cost authorization limits executor and judge consumption; external approval permits the exact runner process to access its normal Codex state and network. Neither authorization implies the other.

A model session is one executor or judge invocation. `sessions.total` is the planned maximum; top-level `model_sessions.total` is actual consumption. A judge skipped after mechanical or oracle failure consumes no session and reports `executed: false` with `verdict: SKIPPED`. `usage` aggregates JSONL token events from `codex exec --json` and preserves ordered normalized event counts, source types, scopes, and token fields without retaining raw JSONL. Missing token fields remain `null` with `complete: false`.

## Persist execution evidence

Keep the repository's `evaluation-reports/archive-config.json` when real Codex executions should be archived automatically. An executed operation that consumes at least one session with a command named `codex` writes to `evaluation-reports/<skill-name>/operations/<operation-id>/`. The archive's dated pricing file is applied automatically.

Use `--report-dir <directory>` for an explicit destination or `--no-report` to disable persistence. Explicit destinations take precedence over the archive. `--pricing-file <json>` is optional, requires `--report-dir`, and overrides archive pricing. `--no-report` is incompatible with both options. Fakes, deterministic operations, and operations that consume no sessions require an explicit destination.

The runner writes `<report-dir>/<operation-id>/report.json` atomically before removing a successful workspace, then renders `report.md` only from that JSON. A persistence failure after session consumption blocks the operation and retains diagnostic artifacts. The runner never stages, commits, or publishes reports.

Use an explicit dated pricing file with this shape:

```json
{
  "version": 1,
  "effective_date": "2026-07-26",
  "source": "https://example.test/pricing",
  "currency": "USD",
  "unit": "per_million_tokens",
  "models": {
    "model-id": {
      "input": 1.0,
      "cached_input": 0.5,
      "output": 2.0,
      "long_context": {
        "input_token_threshold": 272000,
        "input_multiplier": 2.0,
        "output_multiplier": 1.5,
        "applies_per": "request"
      }
    }
  },
  "limitations": ["Reference pricing is not an observed charge."]
}
```

Treat every calculated amount as an API reference estimate. ChatGPT authentication does not expose a per execution monetary charge, so the report records `actual_charge: false`, billing mode, pricing date, source, and limitations. A `turn.completed` usage event is turn scoped, not proof of an individual request size. When a turn aggregate exceeds a request scoped long context threshold, report the exact amount as unavailable and retain only a labeled base rate reference.

Reports persist concise executor declarations, mechanical facts, oracle and judge outcomes, runtime and source fingerprints, usage, reasoning output token availability, durations, and bounded file evidence. They never persist raw JSONL, full transcripts, private reasoning, installed skill contents, hidden oracle contents, `.eval-*`, Python caches, or `.git`.

Regenerate presentation without rerunning a model:

```text
python3 develop-skill-with-evals/scripts/render_eval_report.py \
  --input <report.json> --output <report.md>
```

Compare a directory of reports deterministically:

```text
python3 develop-skill-with-evals/scripts/compare_model_reports.py \
  --reports <directory> --output-dir <directory>
```

The renderer and comparator require canonical schema version 1 and a valid report digest. Compare only reports from one skill. Rebuild or validate a permanent archive without a model:

```text
python3 develop-skill-with-evals/scripts/manage_evaluation_archive.py rebuild \
  --archive evaluation-reports
python3 develop-skill-with-evals/scripts/manage_evaluation_archive.py validate \
  --archive evaluation-reports
```

Inspect qualification, per case stability, token totals and medians, cache ratio, output and reasoning output, duration, API reference cost, effective cost per stable gate, and explanation completeness. Treat small matrices as directional pilots, never statistical proof or authority to change runtime defaults automatically.

## Diagnose before promotion when useful

Plan with `--workflow diagnostic`, then run the proposed `probe-change` command once. It observes affected baseline, affected candidate and every proportional regression one time, continues after contract failures, and stops immediately on infrastructure, authentication, quota or subprocess failure. Its report always has `promotion_eligible: false`.

Use the diagnostic to collect problems, not as promotion evidence. After fixing mechanically reproducible defects, plan `--workflow promotion` and run one `validate-change`. Do not repeat an unchanged full diagnostic.

Keep mechanical expected contracts under each case's `oracle/` directory when code can cover the complete semantic criterion. Declare them through `oracle.commands`; the runner fingerprints them and executes them outside the executor workspace. Never copy or expose the oracle directory to the executor. Keep a judge only when interpretation remains genuinely semantic.

Require literal text in a hidden oracle only when the public prompt requires that same literal text. When wording may vary but the required concepts are mechanically bounded, use controlled lexical equivalence while keeping structural checks exact; do not accept free paraphrases.

## Treat every blocking result as evidence

`PASS` is the only promotable status. Stop on `FAIL`, `ERROR`, `INCONCLUSIVE`, `INVALID_RED`, or `UNSTABLE`. Diagnose and correct the cause, but never repeat an unchanged evaluation merely to obtain a favorable result. The three planned candidate executions are stability evidence, not automatic retries after failure.

Existing `run`, `verify-change`, and `stability` commands remain available for exploration and compatibility. They accept the same four runtime selection options and propagate every known value. Executed commands also accept evidence report controls. Without repository archive configuration, omitting them preserves the existing stdout and cleanup behavior. Prefer diagnostic `plan` plus `probe-change` for one pass investigation and promotion `plan` plus `validate-change` for promotion because these workflows integrate selection, complete runtime, full fingerprints, blockers and budget.

The runner writes only JSON to standard output. Progress goes to standard error, is automatic for a TTY, can be forced with `--progress`, and can be suppressed with `--quiet`.

## Create a new skill

Use `skill-creator`'s `init_skill.py`. Freeze the untouched scaffold as baseline, add focused cases before behavior, and classify the initial implementation as `cross-cutting` unless its affected surface is already bounded. Require a valid RED, stable candidate GREEN, proportional regression, structural validation, matching metadata, and a fresh-agent forward test before promotion.

## Protect self evolution

When changing `develop-skill-with-evals`, keep canonical source untouched:

1. Preserve immutable baseline and isolated candidate copies.
2. Add the focused self evaluation before implementation.
3. Run development and validation with the candidate runner.
4. Run an approved diagnostic at most once when it adds evidence.
5. Run one approved promotion gate.
6. Forward-test with a fresh agent that receives only a realistic task and candidate path, never the expected answer or diagnosis.
7. Promote only the reviewed candidate patch after every required gate passes.

If fresh-agent validation is unavailable, report the missing gate and do not claim promotion readiness.

## Finish with structural validation

Run `skill-creator/scripts/quick_validate.py`, check `agents/openai.yaml` against this skill, validate changed JSON schemas, and inspect the diff for leaked fixtures, transcripts, generated responses, or artifacts. Keep failed artifacts under `/tmp`; remove successful workspaces. Version only cases, minimal fixtures, manifests, contracts, and deterministic runner tests.
