# Serialized specialist workflow

## Startup

1. Read the approved plan and repository instructions completely.
2. Read [github-delivery.md](github-delivery.md) and inspect prior ledgers before creating or reusing a branch. Clean only plans whose recorded pull requests GitHub confirms as `MERGED`.
3. Require a clean checkout apart from ignored `.agent/tmp` state. Do not stash, discard, or absorb unrelated changes.
4. Create or reuse the plan's clean feature branch from its declared base. Never delete a branch automatically.
5. Resolve the base once with `git rev-parse --verify '<base>^{commit}'`, retain the full 40-character SHA as `base_sha`, and do not refresh it if the base ref later moves.
6. Add `/.agent/tmp/` to `.git/info/exclude` if absent. Do not alter `.gitignore` for local workflow state.
7. Store the approved plan verbatim at `.agent/tmp/<slug>.md`, initialize `.agent/tmp/<slug>.workflow.json`, and use the ledger for every subsequent gate.
8. Create and register every specialist below. The ledger rejects the first `implementing` transition until all six IDs and exact model/effort values are present.

## Exact specialist tasks

Resolve the saved project first. Create tasks in its existing checkout with the exact settings below; using the saved project directly is intentional because the ledger serializes one checkout.

Confirm Full access before creating any local task: `sandbox_mode = "danger-full-access"` and `approval_policy = "never"`. A prompt cannot grant permissions. If that exact profile is unavailable, stop before task creation and ask the user to enable it.

| Ledger role | Model | Effort | Task contract |
| --- | --- | --- | --- |
| `implementer` | `gpt-5.6-sol` | `xhigh` | Use `$tdd-behavior-autonomous-quiet`; implement only assigned behavior; do not commit. |
| `committer` | `gpt-5.6-terra` | `xhigh` | Use `$commit-the-changes`; inspect history and status; stage and commit only the assigned delta. |
| `validator` | `gpt-5.6-luna` | `xhigh` | Run the complete clean gate and supported Sonar analysis; do not edit source. |
| `habit-curator` | `gpt-5.6-luna` | `xhigh` | Run Habit quick checks, classify results, and report evidence. Never use `$refactor-design` or self-authorize work. Edit only deterministic, low-risk corrections explicitly assigned by the Coordinator with authorized files and expected evidence; never commit. |
| `mutation-analyst` | `gpt-5.6-luna` | `xhigh` | Select the focal scope, run at most one configured mutation runner per attempt, classify results, and persist complete output under `.agent/tmp`; never edit code, install tools, or commit. |
| `structural-reviewer` | `gpt-5.6-sol` | `xhigh` | Use `$refactor-design` for an independent exhaustive review of changed contracts and adjacent responsibilities; do not commit. |

The deliberate Luna choice is supported by the [official OpenAI model page](https://developers.openai.com/api/docs/models/gpt-5.6-luna), which lists `xhigh` and positions the model for cost-sensitive, high-volume workloads.

Create each task once per plan, register its returned task ID immediately, and reuse it with follow-up prompts. Create all six before implementation begins. If exact model/effort task creation is rejected or unavailable, stop without fallback or fabricated metadata.

Prompts must state the repository path, branch, plan path, `base_sha`, current phase, authorized files, required skill, lease owner, expected evidence, and prohibition on commits when applicable. The Coordinator is the sole communication hub: it acquires the named lease before dispatch, receives the result, inspects the working tree, and releases the lease only after that task is idle. Specialists never dispatch or coordinate with one another.

## Focal mutation scope

For every executed mutation attempt, compare `base_sha` with the commit being analyzed using rename detection. Select production files whose destination path is added, modified, or renamed. Exclude deleted paths, tests, fixtures, generated documentation, prose documentation, and anything outside the repository's production source roots. On a final rerun, recompute the complete target set from `base_sha`; do not mutate only the delta since the initial attempt and do not filter by changed lines.

For PIT, map each selected Java source to its package-qualified top-level class and append `*`, for example `com.example.OrderService*`. Pass those globs through `targetClasses`; do not narrow `targetTests`, so every eligible test can kill the selected mutants. The [PIT Maven quickstart](https://pitest.org/quickstart/maven/) documents `targetClasses` globs and explains that the final `*` includes inner classes.

Before running, write a canonical, deterministically ordered input manifest to the attempt log. Hash it with SHA-256. The manifest includes:

- each selected production path and its blob SHA at `analyzed_sha`;
- every test eligible to exercise the targets in their affected modules, with path and blob SHA;
- mutation-runner configuration, plugin/version inputs, profiles, and the exact normalized runner command.

This digest is the attempt `fingerprint`. For PIT, all tests eligible in the affected Maven modules belong in the manifest because only `targetClasses` is narrowed. If repository-specific configuration makes a smaller test set genuinely eligible, record that rule and evidence in the log.

The Mutation Analyst performs one runner invocation per attempt and redirects complete stdout/stderr plus the manifest to `.agent/tmp`. Copy every generated report there before recording evidence. Its response to the Coordinator contains only analyzed SHA and scope, fingerprint, metrics, classifications, result, and artifact paths; it does not paste raw runner output into chat.

If no configured mutation runner exists, record `not-applicable` with `runner-unavailable`. If no changed production class exists, record `not-applicable` with `no-production-changes`. Never install a runner automatically, describe absence as `passed`, or create a synthetic green report.

## Main sequence

1. Transition to `implementing`. Give the Implementer one behavior-focused assignment. It runs RED/GREEN/refactor cycles, the full relevant suite every cycle, and a public-path checkpoint at least every two cycles. After the assigned behavior and focused tests are green, release its lease and transition to `implemented`.
2. Transition to `habit-checking`. Give the Habit Curator a quick check under its lease. Record one terminal result (`clean`, `ratcheted`, `snoozed`, or `not-applicable`). A `no-configured-files` observation unlocks only the initial checkpoint.
3. Route Habit findings through the Coordinator. Only deterministic, low-risk, explicitly scoped corrections may return to the Habit Curator. Any source correction returns through `implementing` and repeats every downstream gate.
4. Transition to `checkpoint-committing`. The Committer records the complete checkpoint as `implementation` or `correction`; then transition to `initial-validating`.
5. The Validator runs the repository's complete clean verification and normal Sonar analysis. Record current passed `initial-verify` and `initial-sonar` evidence.
6. Transition to `mutation-testing`. The Mutation Analyst selects every production class changed from `base_sha`, computes the fingerprint, and records exactly one attempt. `structural-review` requires a current accepted `passed` or `not-applicable` result. A `failed`, incomplete, or actionable attempt blocks progress.
7. Transition to `structural-review`. The Structural Reviewer independently applies `$refactor-design` and may make only behavior-preserving refactors authorized by the plan and Coordinator. It does not commit.
8. Transition to `habit-rechecking` and record fresh terminal Habit evidence. If review produced a delta, use `final-committing` and record a `correction`, `habit-refactor`, or `structural-refactor` commit. Otherwise transition directly to `final-validating`.
9. The Validator reruns clean verification and Sonar on the final commit. Record current passed `final-verify` and `final-sonar`, then always transition to `mutation-rechecking`.
10. Recompute the focal target set and fingerprint against the same `base_sha`. If production targets, eligible tests, and runner configuration are identical to the latest accepted initial attempt, record `reused` with both analyzed SHAs and the shared fingerprint. If any input differs, execute the runner once against all production targets changed from `base_sha` and record a fresh `passed`, `failed`, or `not-applicable` attempt.
11. Transition to `delivery-ready` only with current final `passed`, `reused`, or `not-applicable` mutation evidence. Follow [github-delivery.md](github-delivery.md) for human choices, pull request, CI, and cleanup.

Refactoring commits require a body that states motivation, concrete risk removed, improvement, behavior preserved, and validation evidence, even if repository history normally prefers no body.

## Mutation classifications and routing

Every `survived` or `no-coverage` mutant in a completed run must have one unique ID, one classification, and a concrete justification. The mutation gate is accepted only when the runner has no execution error, killed/surviving/uncovered metrics account for every generated mutant, every survivor or uncovered mutant is classified exactly once, and actionable findings equal zero. An interrupted environmental failure may preserve partial metrics without pretending its unfinished mutants were classified.

- `behavior-gap`: actionable; return to the Implementer through the behavior-focused TDD path.
- `dead-code` or `redundant-code`: actionable; the Coordinator assigns the correction to the registered Structural Reviewer while the ledger returns through `implementing`. The formal `structural-review` phase remains blocked until a repeated mutation attempt is accepted.
- `equivalent`: non-actionable only with a concrete explanation of why no observable test can distinguish it.
- Environmental runner failure: record `failed` with diagnostic evidence and no code change; return diagnosis to the Coordinator.

Every correction uses a non-empty Coordinator routing note, returns to `implementing`, creates only additional commits, and repeats Habit, checkpoint commit, clean validation, mutation testing, structural review, final Habit, final commit when needed, final validation, and mutation recheck. Never amend or rebase corrective work.

## Habit evidence

- `clean`: raw finding count is zero.
- `ratcheted`: a previously user-authorized baseline is unchanged and active finding count is zero.
- `snoozed`: the user explicitly authorized the already-existing snoozed state. Never create or modify snooze state in this workflow.
- `not-applicable`: the Habit tool is genuinely unavailable and that observation is recorded.

`no-configured-files` means Habit ran but scanned nothing. It is not a terminal status, does not mean `clean`, and does not mean the tool is unavailable. It may unlock only `checkpoint-committing`; final Habit, delivery, and pull request still require a terminal Habit result.
