---
name: develop-skill-with-evals
description: Create or improve Codex skills through evaluation-driven development with isolated fixtures, a demonstrated baseline RED, candidate GREEN, stability repetitions, and full regression. Use when Codex is asked to build a new skill, change skill behavior, add skill evals, forward-test a skill, validate trigger selection, or safely evolve this skill itself. Use explicit `$develop-skill-with-evals` invocation as the reliable entry point; implicit activation is a convenience.
---

# Develop Skill with Evals

Develop skills through observable evaluation evidence, not instruction inspection alone.

## Load the foundation first

Before creating, editing, scaffolding, or evaluating a skill:

1. Announce that `skill-creator` is required.
2. Read its `SKILL.md` completely in the current turn.
3. Follow its creation, metadata, progressive-disclosure, validation, and forward-testing rules.

Do not proceed from memory or delegate reading these instructions.

## Resolve the writable source

Locate the canonical source of the target skill. Distinguish it from installed caches, plugin copies, generated bundles, and temporary candidates. Confirm authorization before writing outside the current workspace; use a temporary candidate when direct writes are not yet authorized.

Never commit, push, publish, or change a system skill unless the user explicitly authorizes that separate action.

## Prepare safe evaluations

Read [references/eval-contract.md](references/eval-contract.md) completely before creating or changing a case or invoking the runner. Validate reports against [references/eval-result.schema.json](references/eval-result.schema.json).

Reduce real examples to the smallest generic fixture that still reproduces the behavior. Remove credentials, private source, identifying data, and irrelevant project structure. Keep raw prompts and fixtures separate from expected contracts. Never put case directories, fixtures, or answer keys in normal skill references or mention them from the target `SKILL.md`.

Classify the requested change before editing:

- `behavioral`: changes when the skill triggers, what it decides, what actions it takes, or what outcome it produces;
- `non_behavioral`: corrects a typo, UI metadata, formatting, or organization without changing agent behavior.

When classification is uncertain, treat it as behavioral.

## Change behavior through RED and GREEN

For a behavioral change:

1. Add or change exactly the focused evaluation case first.
2. Freeze or resolve the baseline and run the new case against it.
3. Require an observable baseline failure. If it passes, report `INVALID_RED` and stop; strengthen or correct the case before implementation.
4. Edit the candidate skill with the smallest coherent change.
5. Run the focused case until it passes.
6. Run `verify-change` so baseline and candidate use the same resolved model and configuration.
7. Run `stability --runs 3` for every changed case. Treat divergent normalized verdicts as `UNSTABLE` and stop.
8. Run the entire candidate suite. Any `FAIL`, `ERROR`, `INCONCLUSIVE`, `INVALID_RED`, or `UNSTABLE` blocks promotion.

Use:

```text
python3 develop-skill-with-evals/scripts/run_skill_evals.py run --skill <path> --case <id> --source working-tree --progress
python3 develop-skill-with-evals/scripts/run_skill_evals.py verify-change --skill <path> --case <id> --baseline <path> --progress
python3 develop-skill-with-evals/scripts/run_skill_evals.py stability --skill <path> --case <id> --runs 3 --progress
python3 develop-skill-with-evals/scripts/run_skill_evals.py run --skill <path> --all --source working-tree --progress
```

Pass `--model` only when a specific model is required. The runner records the resolved selection and uses the same value for baseline and candidate within one comparison.

The runner writes only JSON to standard output. It reports progress to standard error automatically when that stream is a TTY. Pass `--progress` for monitored Codex CLI runs whose standard error is captured, or `--quiet` to suppress progress in a terminal. Progress never requests input or changes the autonomous workflow.

## Handle non-behavioral changes honestly

Do not invent RED evidence for a non-behavioral change. Apply the change, run `quick_validate.py`, inspect `agents/openai.yaml` against the current `SKILL.md`, and run the full regression suite. Reclassify and return to RED if any user-visible or agent-visible behavior changed.

## Create a new skill

For a new skill:

1. Use `skill-creator`'s `init_skill.py` and create only the scaffold plus required resource directories.
2. Freeze a temporary copy of that untouched scaffold as the baseline.
3. Add cases before replacing scaffold instructions.
4. Demonstrate RED against the scaffold.
5. Implement the candidate.
6. Require focused GREEN, `verify-change`, three stable repetitions, full regression, `quick_validate.py`, and matching `agents/openai.yaml` before promotion.

Do not manually recreate the official scaffold.

## Protect self-evolution

When changing `develop-skill-with-evals`, leave its canonical source untouched while working:

1. Copy the canonical skill to an isolated candidate and preserve a separate baseline.
2. Add the self-evaluation case to the candidate first.
3. Run all development and validation against the candidate.
4. Forward-test with fresh agents that receive only realistic task prompts and the candidate path, never the intended answer or diagnosis.
5. Apply the validated candidate to the canonical source only after the fresh evaluations pass.

If fresh-agent validation is unavailable, report the missing gate and do not claim promotion readiness.

## Finish with structural validation

Run `skill-creator/scripts/quick_validate.py` for every changed skill. Confirm that `agents/openai.yaml` has a concise display name, a 25–64 character short description, and a default prompt explicitly naming the skill. Inspect diffs for leaked fixtures, transcripts, generated responses, and artifacts.

Keep failed artifacts in `/tmp` for diagnosis. Remove successful workspaces. Version only cases, minimal fixtures, manifests, contracts, and deterministic runner tests.
