# Serialized specialist workflow

## Startup

1. Read the approved plan and repository instructions completely.
2. Read [github-delivery.md](github-delivery.md) and inspect prior ledgers before creating or reusing a branch. Clean only plans whose recorded pull requests GitHub confirms as `MERGED`.
3. Require a clean checkout apart from ignored `.agent/tmp` state. Do not stash, discard, or absorb unrelated changes.
4. Create or reuse the plan's clean feature branch from its declared base. Never delete a branch automatically.
5. Add `/.agent/tmp/` to `.git/info/exclude` if absent. Do not alter `.gitignore` for local workflow state.
6. Store the approved plan verbatim at `.agent/tmp/<slug>.md`, initialize `.agent/tmp/<slug>.workflow.json`, and use the ledger for every subsequent gate.
7. Create and register every specialist listed below. The ledger rejects the first `implementing` transition until all five IDs and their exact model/effort metadata are present.

## Exact specialist tasks

Resolve the saved project first. Create tasks in its existing checkout with the exact settings below; using the saved project directly is intentional because the ledger serializes one checkout.

Confirm Full access is active before creating any local task: `sandbox_mode = "danger-full-access"` and `approval_policy = "never"`. A prompt cannot grant permissions. If that exact profile is unavailable, stop before task creation and ask the user to enable it.

| Ledger role | Model | Effort | Task contract |
| --- | --- | --- | --- |
| `implementer` | `gpt-5.6-sol` | `xhigh` | Use `$tdd-behavior-autonomous-quiet`; implement only assigned behavior; do not commit. |
| `committer` | `gpt-5.6-terra` | `xhigh` | Use `$commit-the-changes`; inspect history and status; stage and commit only the assigned delta. |
| `validator` | `gpt-5.6-luna` | `xhigh` | Run the complete gate and supported Sonar analysis; do not edit source. |
| `habit-curator` | `gpt-5.6-luna` | `xhigh` | Run Habit quick checks, classify results, and report evidence. Never use `$refactor-design` or self-authorize work. Edit only deterministic, low-risk corrections explicitly assigned by the Coordinator with authorized files and expected evidence; never commit. |
| `structural-reviewer` | `gpt-5.6-sol` | `xhigh` | Use `$refactor-design` for an independent exhaustive review of changed contracts and adjacent responsibilities; do not commit. |

Create each task once per plan, register its returned task ID immediately, and reuse it with follow-up prompts. Create all five before implementation begins. If exact model/effort task creation is rejected or unavailable, stop without fallback or fabricated metadata.

Prompts must state the repository path, branch, plan path, current phase, authorized files, required skill, lease owner, expected evidence, and prohibition on commits when applicable. The Coordinator is the sole communication hub: it acquires the named lease before dispatch, receives the result, inspects the working tree, and releases the lease only after that task is idle. Specialists never dispatch or coordinate with one another.

## Main sequence

1. Transition to `implementing`. Give the Implementer one behavior-focused assignment. It runs RED/GREEN/refactor cycles, the full relevant suite every cycle, and a public-path checkpoint at least every two cycles. After the assigned behavior and focused tests are green, release its lease and transition to `implemented`.
2. Transition to `habit-checking`. Give the Habit Curator a quick check under its lease. Record one schema-v2 terminal result (`clean`, `ratcheted`, `snoozed`, or `not-applicable`) with the evidence required by [ledger.md](ledger.md). If the tool ran but no repository files were configured or scanned, record the separate non-terminal `no-configured-files` observation instead; it satisfies only this quick-check boundary.
3. The Habit Curator reports findings to the Coordinator and never self-authorizes corrections. The Coordinator may assign it only deterministic, low-risk corrections within the approved scope, naming the authorized files and expected evidence; all other findings return to the Coordinator for a scoped decision. Record the authorization/routing evidence in the corrective transition note. Any source correction returns through `implementing` and repeats the downstream sequence.
4. With acceptable current quick Habit evidence, transition to `checkpoint-committing`. Give the Committer the complete checkpoint delta, record an `implementation` or `correction` commit, release the lease, and transition to `initial-validating`.
5. Give the read-only Validator the repository's complete clean verification and normal Sonar analysis. Record `initial-verify` and `initial-sonar`. Both current attempts must be `passed`; route either failure to the Coordinator and repeat affected downstream gates after correction.
6. Transition to `structural-review`. The Structural Reviewer independently applies `$refactor-design` and may make only behavior-preserving refactors authorized by the plan and Coordinator. It does not commit.
7. Transition to `habit-rechecking` and rerun the Habit quick check on the reviewed tree. Record fresh terminal Habit evidence under the same four-state policy. A non-terminal quick observation cannot satisfy this final boundary. Route active, unscoped, or ambiguous results to the Coordinator.
8. If review or correction produced a delta, transition to `final-committing`; the Committer records a `correction`, `habit-refactor`, or `structural-refactor` commit before validation. If the checkout has no delta, transition directly to `final-validating`.
9. The Validator reruns clean verification and Sonar on the final commit. Record fresh `final-verify` and `final-sonar` attempts; both must be `passed` before `delivery-ready`.
10. Follow [github-delivery.md](github-delivery.md) for required human choices, the ready-for-review pull request, CI monitoring, and later cleanup.

Refactoring commits require a body that states the motivation, concrete risk removed, improvement, behavior preserved, and validation evidence, even if simpler commits in the repository normally omit bodies. This plan-specific requirement overrides the ordinary no-body preference.

## Habit v2 evidence

- `clean`: the raw finding count is zero.
- `ratcheted`: a previously user-authorized baseline is unchanged and the active finding count is zero.
- `snoozed`: the user explicitly authorized the already-existing snoozed state. Never create or modify snooze state as part of this workflow.
- `not-applicable`: the tool is genuinely unavailable and that observation is recorded.

There is no automatic freeze, prune step, or required baseline commit in schema v2.

### Non-terminal quick observation

`no-configured-files` means the Habit tool was available and executed, but repository configuration selected no files and the command scanned nothing. It is not a fifth Habit status, does not mean `clean`, and does not mean the tool is unavailable. The Coordinator records it separately under the `habit-checking` phase. It may unlock only `checkpoint-committing`; final Habit, `delivery-ready`, and pull-request recording still require one of the four terminal statuses above.

If a quick result was prematurely recorded as `not-applicable`, the Coordinator may use the ledger's auditable reclassification operation. That operation removes the inaccurate value from active `habit` evidence and embeds the original record in the new observation; it does not erase history.

## Failure routing

- Missing or incorrect observable behavior, including genuine coverage gaps: return to the same Implementer task and TDD path.
- Dead code, structural coupling, fragile state, or representation risk: return to the Structural Reviewer.
- Active Habit finding: return to the Coordinator for classification and an explicit assignment.
- Environment or tool failure: return to the Validator for diagnosis and evidence.

Do not add tests for internal topology to raise coverage. Route by evidence, create only additional commits, and repeat every affected downstream gate. Never amend or rebase corrective work.
