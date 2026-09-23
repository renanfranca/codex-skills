# GitHub delivery and recovery

## Reconcile earlier plans

At every invocation, inspect each `.agent/tmp/*.workflow.json`. For a ledger with a recorded pull request, query that exact repository and number using GitHub's authoritative pull-request fields. Call protected ledger cleanup only when GitHub reports `MERGED` and an unambiguous merge timestamp.

Preserve plan, ledger, mutation artifacts, and branches when the pull request is open, closed without merge, absent, inaccessible, or ambiguous, or when the query fails. Do not delete a local or remote branch during reconciliation.

## Prepare human choices

When the approved plan requires linking a public issue and selecting labels:

1. Create the issue described by the plan.
2. Query the repository's existing labels without creating or editing any.
3. Pause and ask the user to choose exactly one issue reference, `See #N` or `Closes #N`, and zero or more labels from the returned existing set.
4. Do not create the pull request until the user answers. Use the selected reference verbatim in its body and apply only selected existing labels.

This is a human gate. Never infer whether the pull request should close the issue.

## Create the pull request

Before creation, confirm the ledger is `delivery-ready`, the branch is pushed, and the checkout has no uncommitted delivery delta. For schema v5, require current evidence for every selected local validation. Older ledgers retain their original requirements. In particular:

- current passed `final-verify` for selected local checks, or documented `not-applicable` when no local verification applies; `final-sonar` only when local Sonar was selected;
- final Habit evidence of `clean`, `ratcheted`, or explicitly user-authorized `snoozed` only when local Habit was selected;
- current final mutation evidence of `passed`, `reused`, or `no-production-changes` `not-applicable` only when local mutation was selected.

Mutation `failed`, actionable findings, incomplete classifications, missing evidence, or stale evidence block pull-request creation. Older ledgers retain `runner-unavailable` evidence when applicable; schema v5 blocks a selected runner that becomes unavailable. Never describe absence as a green mutation run. A schema-v3/v4/v5 pull request does not require a Habit baseline commit.

Create a pull request ready for review, never a draft, against the base named by the plan. The body must explain intent and observable behavior; list the confirmed validation inventory, selected commands and observed results; identify excluded and CI-only checks; and summarize mutation scope and evidence when mutation was selected. For `reused`, include initial and final analyzed SHAs and the shared fingerprint. For `not-applicable`, include the explicit reason. Disclose known risks and include the selected issue reference.

Apply only the selected existing labels. Record repository, number, URL, status, reference kind, and labels in the ledger, then transition to `pr-open` and `ci-monitoring`.

Do not merge the pull request and do not delete either branch.

## Monitor CI

Follow every required check to a terminal result. For schema v5, record each selected CI-only inventory check with `record-ci --check-id`, including its run identifier, URL, and diagnostic evidence. The ledger requires a current pass for every such check before `ready-for-merge`.

- Route a code failure back through `implementing`, produce an additional commit, push, and repeat Habit, clean validation, mutation testing, structural review, final Habit, final validation, and mutation recheck as applicable.
- Route an environment failure to the Validator; mutation-runner environment failures remain diagnostic work for the Mutation Analyst and Coordinator and do not authorize code changes.
- Re-run a CI failure only when evidence shows it is transient. Permit one transient retry for the entire recorded CI flow; the ledger rejects another.

When all required checks are green, record current `passed` CI evidence, transition to `ready-for-merge`, and pause for the user to merge. Keep plan, ledger, mutation artifacts, and branches intact. A future explicit invocation performs GitHub confirmation and protected cleanup of only the plan/ledger pair. Cleanup never deletes a branch.
