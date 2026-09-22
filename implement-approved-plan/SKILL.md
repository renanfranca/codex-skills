---
name: implement-approved-plan
description: Execute a user-approved repository plan through serialized specialist Codex tasks, a guarded local ledger, independent validation, focal mutation testing, structural review, and pull-request/CI handoff. Invoke only when the user explicitly names $implement-approved-plan; do not use to draft plans, merge pull requests, or clean unmerged work.
---

# Implement Approved Plan

Execute the approved plan without silently changing its scope or approval boundaries.

## Enforce the coordinator contract

Before starting a new plan, show the seven-role model and effort table in [references/workflow.md](references/workflow.md). Ask the user to accept all defaults or name only the roles to change, and resolve every requested model/effort pair. Do this even if the initial request specifies overrides. For a resumed plan, reuse its recorded selection without asking again. Once selected, use one dedicated Coordinator with that exact pair. If this is a bootstrap task, create the Coordinator in the saved project with the local checkout, pass the complete selection to it, and tell it not to create another Coordinator. If this task is already that dedicated Coordinator, continue here.

Before changing files, confirm that every required model/effort combination is callable. Never substitute a model or effort. Stop and ask the user if any exact combination is unavailable.

Before creating the Coordinator or any local specialist task, confirm that the active permissions profile is Full access (`sandbox_mode = "danger-full-access"` with `approval_policy = "never"`). Permissions are environment state, not a prompt instruction. If the exact profile is unavailable, stop and ask the user instead of creating a task that will require interactive command approvals.

Create and register all six specialist tasks exactly once before the first `implementing` transition, using the selected combinations recorded in the new ledger. Only the Coordinator communicates with specialists, grants assignments, and operates ledger leases. Reuse the registered tasks for the entire plan; never ask specialists to coordinate with each other or change a registered task's model mid-run.

## Load the applicable procedures

- Read [references/workflow.md](references/workflow.md) before startup, specialist creation, implementation, validation, mutation testing, or review.
- Read [references/ledger.md](references/ledger.md) before creating or changing workflow state.
- Read [references/github-delivery.md](references/github-delivery.md) before querying earlier pull requests, creating issues or pull requests, selecting labels, monitoring CI, or cleaning temporary files.

## Preserve authority boundaries

An approved plan authorizes its stated implementation and delivery operations, not merge, branch deletion, unrelated cleanup, label creation, amend, rebase, mutation-runner installation, commercial mutation integration, or changed-line mutation filtering. Keep corrective work as additional commits.

Pause for every human choice required by the plan. In particular, obtain the user's issue-reference and existing-label selections before creating a pull request when the plan calls for those choices.

Never create or modify Habit snooze state. A `snoozed` ledger result records a pre-existing state only after the user explicitly authorizes it. Schema v3 does not require a Habit baseline commit.

Keep `.agent/tmp/<slug>.md`, `.agent/tmp/<slug>.workflow.json`, and mutation logs/reports until a future invocation independently confirms the recorded pull request is `MERGED`. Never infer merge from a closed pull request, green CI, or local Git state.

New ledgers use schema v4 and capture both the declared base ref and its immutable `base_sha` plus the resolved seven-role model selection. Existing schema-v1, schema-v2, and schema-v3 ledgers remain readable and retain their original model, transition, evidence, pull-request, and cleanup rules; reading them never migrates or rewrites them.
