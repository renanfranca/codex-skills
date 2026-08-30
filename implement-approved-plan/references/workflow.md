# Serialized specialist workflow

## Startup

1. Read the approved plan and repository instructions completely.
2. Read [github-delivery.md](github-delivery.md) and inspect prior ledgers before creating or reusing a branch. Clean only plans whose recorded pull requests GitHub confirms as `MERGED`.
3. Require a clean checkout apart from ignored `.agent/tmp` state. Do not stash, discard, or absorb unrelated changes.
4. Create or reuse the plan's clean feature branch from its declared base. Never delete a branch automatically.
5. Add `/.agent/tmp/` to `.git/info/exclude` if absent. Do not alter `.gitignore` for local workflow state.
6. Store the approved plan verbatim at `.agent/tmp/<slug>.md`, initialize `.agent/tmp/<slug>.workflow.json`, and use the ledger for every subsequent gate.

## Exact specialist tasks

Resolve the saved project first. Create tasks in its existing checkout with the exact settings below; using the saved project directly is intentional because the ledger serializes one checkout.

| Ledger role | Model | Effort | Task contract |
| --- | --- | --- | --- |
| `implementer` | `gpt-5.6-sol` | `xhigh` | Use `$tdd-behavior-autonomous-quiet`; implement only assigned behavior; do not commit. |
| `committer` | `gpt-5.6-terra` | `xhigh` | Use `$commit-the-changes`; inspect history and status; stage and commit only the assigned delta. |
| `validator` | `gpt-5.6-luna` | `xhigh` | Run the complete gate and supported Sonar analysis; do not edit source. |
| `habit-curator` | `gpt-5.6-sol` | `xhigh` | Use `$refactor-design`; address only classified Habit findings, one coherent improvement at a time; do not commit. |
| `structural-reviewer` | `gpt-5.6-sol` | `xhigh` | Use `$refactor-design` for an independent exhaustive review of changed contracts and adjacent responsibilities; do not commit. |

Create each task once per plan, register its returned task ID immediately, and reuse it with follow-up prompts. If exact model/effort task creation is rejected or unavailable, stop without fallback.

Prompts must state the repository path, branch, plan path, current phase, authorized files, required skill, lease owner, expected evidence, and prohibition on commits when applicable. The Coordinator acquires the named lease before dispatch and releases it after the task is idle and its output and working tree have been inspected.

## Main sequence

1. Transition to `implementing`. Give the Implementer one behavior-focused assignment. It runs RED/GREEN/refactor cycles and public-path checkpoints at least every two cycles.
2. After requested behavior is complete and green, transition to `implemented`. Give the Committer only that delta. Record the resulting hash as `implementation` or `correction`, release the lease, and transition through `committed` to `initial-validating`.
3. Give the Validator the repository's complete gate: focused tests, full suite/build, coverage, static checks, and Sonar when supported. Record each observed result and a green `public-checkpoint` before design review.
4. The Coordinator independently checks behavior, coverage quality, and Sonar evidence, then transitions to `coordinator-review` and `habit-curation`.
5. If Habit is unavailable, record `not-applicable` with evidence. If available, run an unsnoozed full analysis, classify every finding, and let the Habit Curator handle one coherent improvement per cycle. After each green improvement, release the curator lease, give only that delta to the Committer, create an additional `habit-refactor` commit, then resume the same curator task.
6. Transition to `structural-review` only after the ledger accepts the green public checkpoint. The Structural Reviewer performs an independent exhaustive `$refactor-design` pass. Commit each coherent improvement separately as `structural-refactor`, with no amend or rebase.
7. Transition to `final-validating`. The Validator repeats the complete gate and supported Sonar analysis. Record the final gate only from observed results.
8. Freeze Habit only after every current finding is classified. Use full-analysis results, `habit-snooze --snooze --until-changed`, and `habit-snooze --prune`; record counts and both actions. If Habit is unavailable, preserve the earlier not-applicable evidence.
9. Transition to `habit-frozen`. Give the Committer the baseline-only delta and record an additional `baseline` commit. Transition to `baseline-committed`.
10. Follow [github-delivery.md](github-delivery.md) for the human choice, ready-for-review pull request, CI, and later cleanup.

Refactoring commits require a body that states the motivation, concrete risk removed, improvement, behavior preserved, and validation evidence, even if simpler commits in the repository normally omit bodies. This plan-specific requirement overrides the ordinary no-body preference.

## Failure routing

- Missing or incorrect observable behavior, including genuine coverage gaps: return to the same Implementer task and TDD path.
- Dead code, structural coupling, fragile state, or representation risk: return to the Structural Reviewer.
- Active Habit finding: return to the Habit Curator.
- Environment or tool failure: return to the Validator for diagnosis and evidence.

Do not add tests for internal topology to raise coverage. Route by evidence, create only additional commits, and repeat every affected downstream gate.
