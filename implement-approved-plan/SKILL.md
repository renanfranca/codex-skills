---
name: implement-approved-plan
description: Execute a user-approved repository plan through serialized specialist Codex tasks, a guarded local ledger, independent validation and design review, and pull-request/CI handoff. Invoke only when the user explicitly names $implement-approved-plan; do not use to draft plans, merge pull requests, or clean unmerged work.
---

# Implement Approved Plan

Execute the approved plan without silently changing its scope or approval boundaries.

## Enforce the coordinator contract

Use a dedicated `gpt-5.6-sol` Coordinator at `xhigh`. If this is a bootstrap task, create that Coordinator in the saved project with the local checkout and tell it not to create another Coordinator. If this task is already that dedicated Coordinator, continue here.

Before changing files, confirm that every required model/effort combination is callable. Never substitute a model or effort. Stop and ask the user if any exact combination is unavailable.

Before creating the Coordinator or any local specialist task, confirm that the active permissions profile is Full access (`sandbox_mode = "danger-full-access"` with `approval_policy = "never"`). Permissions are environment state, not a prompt instruction. If the exact profile is unavailable, stop and ask the user instead of creating a task that will require interactive command approvals.

Only the Coordinator communicates with specialists. Reuse one new task per role for the entire plan, and serialize all checkout activity with the ledger lease. Never ask specialists to coordinate with each other.

## Load the applicable procedures

- Read [references/workflow.md](references/workflow.md) before startup, specialist creation, implementation, validation, or review.
- Read [references/ledger.md](references/ledger.md) before creating or changing workflow state.
- Read [references/github-delivery.md](references/github-delivery.md) before querying earlier pull requests, creating issues or pull requests, selecting labels, monitoring CI, or cleaning temporary files.

## Preserve authority boundaries

An approved plan authorizes its stated implementation and delivery operations, not merge, branch deletion, unrelated cleanup, label creation, amend, or rebase. Keep corrective work as additional commits.

Pause for every human choice required by the plan. In particular, obtain the user's issue-reference and existing-label selections before creating a pull request when the plan calls for those choices.

Keep `.agent/tmp/<slug>.md` and `.agent/tmp/<slug>.workflow.json` until a future invocation independently confirms the recorded pull request is `MERGED`. Never infer merge from a closed pull request, green CI, or local Git state.
