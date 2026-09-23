# Serialized specialist workflow

## Startup

1. Read the approved plan and target repository instructions completely. Before creating a Coordinator, branch, ledger, or specialist, inspect the repository's build/test scripts, manifests, analysis configuration, hooks, and CI workflows. Resolve which checks are explicitly required by the plan.
2. Build the validation inventory below. Check local command and service availability without installing tools or changing tracked files. Treat a configured check that cannot run in its intended environment as a startup blocker; show the failed prerequisite and command. CI-only checks require a configured CI workflow, not a local executable.
3. Show the inventory, exclusions, owners, and model defaults for all seven roles, marking optional specialists as inactive. Obtain the user's confirmation of checks and model overrides, including any desired model for a role activated later. If the user changes the inventory, resolve it before task creation. For a resumed schema-v5 ledger, use the recorded inventory and reassess before the next validation gate; older ledgers retain their original rules.
4. Read [github-delivery.md](github-delivery.md) and inspect prior ledgers before creating or reusing a branch. Clean only plans whose recorded pull requests GitHub confirms as `MERGED`.
5. Require a clean checkout apart from ignored `.agent/tmp` state. Do not stash, discard, or absorb unrelated changes. Create or reuse the plan's clean feature branch from its declared base; never delete a branch automatically.
6. Resolve the base once with `git rev-parse --verify '<base>^{commit}'`, retain the full 40-character SHA as `base_sha`, and do not refresh it if the base ref later moves.
7. Add `/.agent/tmp/` to `.git/info/exclude` if absent. Store the plan verbatim at `.agent/tmp/<slug>.md`, the confirmed inventory at `.agent/tmp/<slug>.validation.json`, and initialize the schema-v5 ledger. Do not alter `.gitignore` for local workflow state.
8. Create and register the four always active specialists. Create the Habit Curator and Mutation Analyst only when their local checks are selected. The ledger rejects `implementing` or `implemented` until every currently required task has its exact selected model/effort pair.

## Validation discovery and routing

Use repository configuration and the approved plan as sources of truth. Installed but unconfigured tools are not selected. Inspect relevant project scripts, build profiles/plugins, test and coverage configuration, Sonar settings, Habit hook configuration and scanned files, mutation runner configuration, and CI workflows. For each proposed check, show its source, exact local command or CI check, ability to run, and owner. Route tests, lint, coverage, static analysis, and local Sonar to the Validator; configured local mutation testing to the Mutation Analyst; configured local Habit hooks to the Habit Curator; and CI-only checks to the Coordinator. The Committer owns commit-message checks, and the Structural Reviewer owns code review rather than a project validation tool.

The inventory is a JSON object with a `checks` array. Every entry has string fields `id`, `kind` (`verify`, `sonar`, `mutation`, `habit`, or `ci`), `status` (`selected` or `skipped`), `execution` (`local`, `ci`, or `none`), `command`, `source`, `owner`, and `reason`. Use a unique `id` and a concrete configuration path or plan clause in `source`. Selected local checks require an executable `command` and empty `reason`; selected CI checks use `execution: ci`, may leave `command` empty, and have `owner: coordinator`. Skipped checks use `execution: none`, an empty command, and a concrete reason. Include exactly one Sonar, mutation, and Habit entry each, selected or skipped. Include one or more selected verification entries, or one skipped verification entry explaining why no automated local or CI verification applies. General CI checks may have `kind: ci`. This inventory is confirmed evidence, not a request to install or configure missing tools.

Reinspect the configuration before initial and final validation. If it changed, show the delta and obtain confirmation. Return through `implementing` with a Coordinator note, update the inventory under its lease, create any newly required specialist once, and repeat downstream gates. A check required by the approved plan cannot be silently removed. If a selected check becomes unavailable, block with diagnostic evidence; do not relabel it `not-applicable` or claim a pass. A selected check without applicable production changes may still record the existing `no-production-changes` mutation result. After a pull request, monitor every selected CI check by its inventory ID.

## Model selection and specialist tasks

Resolve the saved project first. Before creating the Coordinator, show this table for all seven roles with active/inactive status and ask the user to accept all defaults or specify overrides by role, model, and effort. Display the effective selection before task creation. For a resumed plan with an existing ledger, use its recorded selection without asking again. Create tasks in the saved project's existing checkout; the ledger serializes one checkout.

Confirm Full access before creating any local task: `sandbox_mode = "danger-full-access"` and `approval_policy = "never"`. A prompt cannot grant permissions. If that exact profile is unavailable, stop before task creation and ask the user to enable it.

| Role | Default model | Default effort | Task contract |
| --- | --- | --- | --- |
| `coordinator` | `gpt-6-sol` | `medium` | Own assignments, ledger leases, gates, and delivery; do not create another Coordinator. |
| `implementer` | `gpt-6-sol` | `medium` | Use `$tdd-behavior-autonomous-quiet`; implement only assigned behavior; do not commit. |
| `committer` | `gpt-6-luna` | `xhigh` | Use `$commit-the-changes`; inspect history and status; stage and commit only the assigned delta. |
| `validator` | `gpt-6-luna` | `xhigh` | Run selected local verification and Sonar checks; record the absence of local checks when applicable; do not edit source. |
| `habit-curator` | `gpt-6-luna` | `xhigh` | When local Habit hooks are selected, run quick checks, classify results, and report evidence. Never use `$refactor-design` or self-authorize work. Edit only deterministic, low-risk corrections explicitly assigned by the Coordinator with authorized files and expected evidence; never commit. |
| `mutation-analyst` | `gpt-6-luna` | `xhigh` | When local mutation testing is selected, run at most one configured runner per attempt, classify results, and persist complete output under `.agent/tmp`; never edit code, install tools, or commit. |
| `structural-reviewer` | `gpt-6-sol` | `medium` | Use `$refactor-design` for an independent exhaustive review of changed contracts and adjacent responsibilities; do not commit. |

At startup, verify that the selected model/effort pair is callable for all seven roles, including inactive roles that may become active later. Do not silently substitute another pair. Initialize a schema-v5 ledger with `init --validation-plan .agent/tmp/<slug>.validation.json` and any `--model role=model:effort` overrides. Its `model_selection` retains all seven selections so a later specialist can be created without changing its model. Pass both selections from the bootstrap task to the Coordinator. Registered task identities never change during a run.

Create each required task once per plan, register its returned task ID immediately, and reuse it with follow-up prompts. Optional specialists may be created later only when a confirmed inventory revision activates their local check. If exact model/effort task creation is rejected or unavailable, stop without fallback or fabricated metadata.

Prompts must state the repository path, branch, plan path, `base_sha`, current phase, authorized files, required skill, lease owner, expected evidence, and prohibition on commits when applicable. The Coordinator is the sole communication hub: it acquires the named lease before dispatch, receives the result, inspects the working tree, and releases the lease only after that task is idle. Specialists never dispatch or coordinate with one another.

## Commit message contract

Before dispatching the Committer, inspect the repository instructions, recent relevant commit history, and available commit-message lint configuration. Preserve the observed type and scope convention, language, capitalization, tense, and naming. Resolve the effective maximum line length separately for the header, body, and footer; use 100 characters for any part without a repository-defined limit. Reflow prose at word boundaries without truncating, omitting, or replacing its content.

Every commit created by this workflow requires a body with these three semantic fields. Translate both the labels and their content into the repository's observed commit language; the English labels below are the canonical example:

```text
type(scope): summary in the repository's observed style

- Motivation: Explain why the change is needed.
- Avoided: Name the concrete risk or undesirable outcome avoided.
- Improvement: State what becomes better after the change.
```

Keep these bullets and their wrapped continuation lines in the body. Start the footer after a blank line and reserve it for actual trailers. For refactoring commits, append two more body fields:

```text
- Behavior preserved: Identify the public behavior that remains unchanged.
- Validation: Name the evidence that verifies the preserved behavior.
```

This workflow-specific body requirement overrides `$commit-the-changes`' ordinary preference to omit bodies when similar repository commits do not use them.

Classify every proposed commit as breaking or non-breaking. Use breaking markers only for a real incompatible behavior that requires consumers to migrate. When the repository uses Conventional Commits, a breaking commit requires both the `!` marker and the `BREAKING CHANGE:` trailer, even though the specification permits either marker independently:

```text
feat(scope)!: imperative summary

- Motivation: Explain why the incompatible change is needed.
- Avoided: Name the concrete risk or undesirable outcome avoided.
- Improvement: State what becomes better after the change.

BREAKING CHANGE: Explain the incompatible behavior and required migration.
Continue the explanation on wrapped lines when necessary.
```

Treat `feat(scope)` as illustrative: use the type, optional scope, and subject style supported by the repository. Keep the `BREAKING CHANGE:` token in English so parsers recognize it, but write its explanation in the observed language. Non-breaking commits must contain neither `!` nor `BREAKING CHANGE:`. In repositories that do not use Conventional Commits, preserve their observed breaking-change convention instead of introducing these markers.

Each Committer prompt must state the observed convention and language, the effective header/body/footer limits, that the body is required, the breaking classification, and the exact command available to validate the complete candidate message. If the repository provides commitlint, validate the complete message before committing and commit that same validated content. This pre-validation supplements normal Git hooks; never use `--no-verify`, `HUSKY=0`, or an equivalent bypass. If no candidate-message validation command is available, state that explicitly in the prompt instead of fabricating one.

## Focal mutation scope

For every executed mutation attempt, compare `base_sha` with the commit being analyzed using rename detection. Select production files whose destination path is added, modified, or renamed. Exclude deleted paths, tests, fixtures, generated documentation, prose documentation, and anything outside the repository's production source roots. On a final rerun, recompute the complete target set from `base_sha`; do not mutate only the delta since the initial attempt and do not filter by changed lines.

For PIT, map each selected Java source to its package-qualified top-level class and append `*`, for example `com.example.OrderService*`. Pass those globs through `targetClasses`; do not narrow `targetTests`, so every eligible test can kill the selected mutants. The [PIT Maven quickstart](https://pitest.org/quickstart/maven/) documents `targetClasses` globs and explains that the final `*` includes inner classes.

Before running, write a canonical, deterministically ordered input manifest to the attempt log. Hash it with SHA-256. The manifest includes:

- each selected production path and its blob SHA at `analyzed_sha`;
- every test eligible to exercise the targets in their affected modules, with path and blob SHA;
- mutation-runner configuration, plugin/version inputs, profiles, and the exact normalized runner command.

This digest is the attempt `fingerprint`. For PIT, all tests eligible in the affected Maven modules belong in the manifest because only `targetClasses` is narrowed. If repository-specific configuration makes a smaller test set genuinely eligible, record that rule and evidence in the log.

The Mutation Analyst performs one runner invocation per attempt and redirects complete stdout/stderr plus the manifest to `.agent/tmp`. Copy every generated report there before recording evidence. Its response to the Coordinator contains only analyzed SHA and scope, fingerprint, metrics, classifications, result, and artifact paths; it does not paste raw runner output into chat.

For a new schema-v5 run, exclude mutation testing during discovery when no configured runner exists; the inventory records the reason and both mutation phases are skipped. If a selected runner has no changed production class, record `not-applicable` with `no-production-changes`. A selected runner that becomes unavailable blocks the gate. Never install a runner automatically, describe absence as `passed`, or create a synthetic green report. Older ledgers keep their original `runner-unavailable` evidence rule.

## Main sequence

1. Transition to `implementing`. Give the Implementer one behavior-focused assignment. It runs RED/GREEN/refactor cycles, the full relevant suite every cycle, and a public-path checkpoint at least every two cycles. After the assigned behavior and focused tests are green, release its lease and transition to `implemented`.
2. If local Habit hooks were selected, transition to `habit-checking`, give the Habit Curator a quick check under its lease, and record terminal evidence. If no files are configured, reassess the inventory and route back through `implementing`. Otherwise go directly to `checkpoint-committing`.
3. Route Habit findings through the Coordinator. Only deterministic, low-risk, explicitly scoped corrections may return to the Habit Curator. Any source correction returns through `implementing` and repeats every downstream gate.
4. Transition to `checkpoint-committing`. Under the commit message contract, the Committer records the complete checkpoint as `implementation` or `correction`; then transition to `initial-validating`.
5. Reassess the inventory. The Validator runs every selected local verification and local Sonar check. Record `initial-verify` as `passed` only if all selected local verification commands pass, otherwise record a documented `not-applicable` when there are none. Record `initial-sonar` only when local Sonar is selected. CI-only checks wait for CI.
6. If local mutation testing was selected, transition to `mutation-testing`. The Mutation Analyst selects every production class changed from `base_sha`, computes the fingerprint, and records exactly one attempt. `structural-review` requires a current accepted `passed` or `not-applicable` result. If mutation was excluded, transition directly to `structural-review`. A failed, incomplete, or actionable selected attempt blocks progress.
7. Transition to `structural-review`. The Structural Reviewer independently applies `$refactor-design` and may make only behavior-preserving refactors authorized by the plan and Coordinator. It does not commit.
8. If local Habit hooks were selected, transition to `habit-rechecking` and record fresh terminal evidence; otherwise skip that phase. If review produced a delta, use `final-committing` and record a `correction`, `habit-refactor`, or `structural-refactor` commit under the commit message contract. Otherwise transition directly to `final-validating`.
9. Reassess the inventory. The Validator reruns all selected local verification and Sonar checks on the final commit and records current `final-verify` plus `final-sonar` when selected.
10. If local mutation testing was selected, transition to `mutation-rechecking`. Recompute the focal target set and fingerprint against the same `base_sha`. Reuse accepted initial evidence only when all inputs match; otherwise run the configured runner once against all selected production targets. If mutation was excluded, transition directly to `delivery-ready` after final validation.
11. Transition to `delivery-ready` only with current evidence for every selected local gate. Follow [github-delivery.md](github-delivery.md) for human choices, pull request, CI, and cleanup.

## Mutation classifications and routing

Every `survived` or `no-coverage` mutant in a completed run must have one unique ID, one classification, and a concrete justification. The mutation gate is accepted only when the runner has no execution error, killed/surviving/uncovered metrics account for every generated mutant, every survivor or uncovered mutant is classified exactly once, and actionable findings equal zero. An interrupted environmental failure may preserve partial metrics without pretending its unfinished mutants were classified.

- `behavior-gap`: actionable; return to the Implementer through the behavior-focused TDD path.
- `dead-code` or `redundant-code`: actionable; the Coordinator assigns the correction to the registered Structural Reviewer while the ledger returns through `implementing`. The formal `structural-review` phase remains blocked until a repeated mutation attempt is accepted.
- `equivalent`: non-actionable only with a concrete explanation of why no observable test can distinguish it.
- Environmental runner failure: record `failed` with diagnostic evidence and no code change; return diagnosis to the Coordinator. A selected runner cannot be relabeled unavailable to bypass the gate.

Every correction uses a non-empty Coordinator routing note, returns to `implementing`, creates only additional commits, and repeats the applicable selected gates from the checkpoint onward. Never amend or rebase corrective work.

## Habit evidence

- `clean`: raw finding count is zero.
- `ratcheted`: a previously user-authorized baseline is unchanged and active finding count is zero.
- `snoozed`: the user explicitly authorized the already-existing snoozed state. Never create or modify snooze state in this workflow.
- `not-applicable`: retained for older ledgers when the Habit tool is genuinely unavailable. Schema v5 excludes unconfigured Habit hooks during discovery and blocks a selected hook that becomes unavailable.

`no-configured-files` means Habit ran but scanned nothing. For schema v5, reassess the inventory and return through `implementing`; do not record a synthetic clean result. Older ledgers retain their original observation and gate rules.
