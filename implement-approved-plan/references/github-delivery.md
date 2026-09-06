# GitHub delivery and recovery

## Reconcile earlier plans

At every invocation, inspect each `.agent/tmp/*.workflow.json`. For a ledger with a recorded pull request, query that exact repository and number using GitHub's authoritative pull-request fields. Call protected ledger cleanup only when GitHub reports `MERGED` and an unambiguous merge timestamp.

Preserve both files when the pull request is open, closed without merge, absent, inaccessible, the query fails, or the response is ambiguous. Do not delete a local or remote branch during reconciliation.

## Prepare human choices

When the approved plan requires linking a public issue and selecting labels:

1. Create the issue described by the plan.
2. Query the repository's existing labels without creating or editing any.
3. Pause and ask the user to choose exactly one issue reference, `See #N` or `Closes #N`, and zero or more labels from the returned existing set.
4. Do not create the pull request until the user answers. Use the selected reference verbatim in its body and apply only selected existing labels.

This is a human gate. Never infer whether the pull request should close the issue.

## Create the pull request

Before creation, confirm the ledger is `delivery-ready`, current `final-verify` and `final-sonar` attempts are green, final Habit evidence is acceptable, the branch is pushed, and the checkout has no uncommitted delivery delta. Acceptable schema-v2 Habit evidence is `clean`, `ratcheted`, explicitly user-authorized `snoozed`, or genuinely unavailable `not-applicable`. Do not create or modify snooze state. A schema-v2 pull request does not require a baseline commit.

Create a pull request ready for review, never a draft, against the base named by the plan.

The body must explain intent and observable behavior, list validation commands and observed results, state coverage/Sonar/Habit evidence, disclose known risks, and include the selected issue reference. Record repository, number, URL, status, reference kind, and labels in the ledger, then transition to `pr-open` and `ci-monitoring`.

Do not merge the pull request and do not delete either branch.

## Monitor CI

Follow every required check to a terminal result. Record run identifiers, URLs, and diagnostic evidence.

- Route a code failure back to the responsible specialist, produce additional commits, push, and repeat affected gates.
- Route an environment failure to the Validator.
- Re-run a failure only when evidence shows it is transient. Permit one transient retry for the entire recorded CI flow; the ledger rejects another.

When all required checks are green, record current `passed` CI evidence, transition to `ready-for-merge`, and pause for the user to merge. Keep the plan, ledger, and branches intact. A future explicit invocation performs GitHub confirmation and protected cleanup of only the plan/ledger pair. Cleanup never deletes a branch.
