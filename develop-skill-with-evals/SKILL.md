---
name: develop-skill-with-evals
description: Create or improve Codex skills through impact-aware evaluation development with isolated fixtures, proportional RED and GREEN gates, deterministic checks, model session planning, stability evidence, and fresh-agent validation. Use when Codex is asked to build or change a skill, add skill evals, forward-test behavior, validate trigger selection, modify an evaluation runner or contract, or safely evolve this skill itself.
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
  --skill <candidate> --baseline <baseline> --impact <impact> [--case <id>]...
```

Planning is side effect free and uses no model. Inspect selected and regression cases, commands, executor and judge session counts, reasons, and warnings before executing.

## Apply proportional gates

For `static`, apply only the structural gates listed by the plan. Do not invent RED or run semantic cases incapable of observing the change.

For `deterministic`, add or change a deterministic case first. It must use direct mechanical checks, no executor, and no semantic judge. Demonstrate baseline failure, candidate success in three stable runs, and structural validity.

For `scoped`, add or change only the affected semantic cases first. Require baseline `FAIL`, three candidate `PASS` results with one stable normalized signature, and structural validity. Do not run unrelated suite cases.

For `cross-cutting`, apply the scoped gates to explicitly affected cases, then run every remaining suite case once as regression. Affected cases must not run again in the regression phase.

Use the integrated command:

```text
python3 develop-skill-with-evals/scripts/run_skill_evals.py validate-change \
  --skill <candidate> --baseline <baseline> --impact <impact> \
  [--case <id>]... [--approved-model-sessions <n>] --progress
```

The default approved limit is eight model sessions. An estimate above that limit stops with exit code 2 before artifacts or model calls. `--approved-model-sessions` is explicit approval for that count. Shell, sandbox, or command approval is not cost approval.

A model session is one executor or judge invocation. The count does not estimate tokens, duration, or financial cost.

## Treat every blocking result as evidence

`PASS` is the only promotable status. Stop on `FAIL`, `ERROR`, `INCONCLUSIVE`, `INVALID_RED`, or `UNSTABLE`. Diagnose and correct the cause, but never repeat an unchanged evaluation merely to obtain a favorable result. The three planned candidate executions are stability evidence, not automatic retries after failure.

Existing `run`, `verify-change`, and `stability` commands remain available for exploration and compatibility. Prefer `plan` plus `validate-change` for a change validation because they enforce selection and budget as one workflow.

The runner writes only JSON to standard output. Progress goes to standard error, is automatic for a TTY, can be forced with `--progress`, and can be suppressed with `--quiet`.

## Create a new skill

Use `skill-creator`'s `init_skill.py`. Freeze the untouched scaffold as baseline, add focused cases before behavior, and classify the initial implementation as `cross-cutting` unless its affected surface is already bounded. Require a valid RED, stable candidate GREEN, proportional regression, structural validation, matching metadata, and a fresh-agent forward test before promotion.

## Protect self evolution

When changing `develop-skill-with-evals`, keep canonical source untouched:

1. Preserve immutable baseline and isolated candidate copies.
2. Add the focused self evaluation before implementation.
3. Run development and validation with the candidate runner.
4. Forward-test with a fresh agent that receives only a realistic task and candidate path, never the expected answer or diagnosis.
5. Promote only the reviewed candidate patch after every required gate passes.

If fresh-agent validation is unavailable, report the missing gate and do not claim promotion readiness.

## Finish with structural validation

Run `skill-creator/scripts/quick_validate.py`, check `agents/openai.yaml` against this skill, validate changed JSON schemas, and inspect the diff for leaked fixtures, transcripts, generated responses, or artifacts. Keep failed artifacts under `/tmp`; remove successful workspaces. Version only cases, minimal fixtures, manifests, contracts, and deterministic runner tests.
