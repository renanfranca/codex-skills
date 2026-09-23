---
name: implement-approved-plan
description: Execute a user-approved repository plan through serialized specialist Codex tasks, a guarded local ledger, independent validation, focal mutation testing, structural review, and pull-request/CI handoff. Invoke only when the user explicitly names $implement-approved-plan; do not use to draft plans, merge pull requests, or clean unmerged work.
---

# Implement Approved Plan

Execute the approved plan without silently changing its scope or approval boundaries.

## Enforce the coordinator contract

Before starting a new plan, inspect the target repository and approved plan for configured validation commands, CI checks, Sonar, mutation testing, and Habit hooks. Show the proposed validation inventory with source, execution location, specialist owner, and exclusions; obtain the user's confirmation before creating the Coordinator or ledger. A configured local check that cannot run blocks startup with a concrete diagnosis. A CI-only check is monitored after the pull request. Do not select a tool merely because it is installed. Follow [references/workflow.md](references/workflow.md) for discovery and later reassessment.

Show the model and effort defaults for all seven roles, marking optional specialists as inactive when their checks are excluded, and ask the user to accept them or name only the roles to change. This also fixes the model if an optional role becomes active later. Do this even if the initial request specifies overrides. For a resumed plan, reuse its recorded validation and model selections, then reassess checks before the next validation gate. Once selected, use one dedicated Coordinator with that exact pair. If this is a bootstrap task, create the Coordinator in the saved project with the local checkout, pass both selections to it, and tell it not to create another Coordinator. If this task is already that dedicated Coordinator, continue here.

Before changing files, confirm that all seven selected model/effort combinations are callable, including the inactive specialists that may be activated later. Never substitute a model or effort. Stop and ask the user if any exact combination is unavailable.

Before creating the Coordinator or any local specialist task, confirm that the active permissions profile is Full access (`sandbox_mode = "danger-full-access"` with `approval_policy = "never"`). Permissions are environment state, not a prompt instruction. If the exact profile is unavailable, stop and ask the user instead of creating a task that will require interactive command approvals.

Create and register the Implementer, Committer, Validator, and Structural Reviewer before the first `implementing` transition. Create the Habit Curator and Mutation Analyst only when selected local checks require them; if a later confirmed reassessment adds one, create and register it before leaving `implementing`. Only the Coordinator communicates with specialists, grants assignments, and operates ledger leases. Reuse registered tasks; never ask specialists to coordinate with each other or change a registered task's model mid-run.

## Load the applicable procedures

- Read [references/workflow.md](references/workflow.md) before startup, specialist creation, implementation, validation, mutation testing, or review.
- Read [references/ledger.md](references/ledger.md) before creating or changing workflow state.
- Read [references/github-delivery.md](references/github-delivery.md) before querying earlier pull requests, creating issues or pull requests, selecting labels, monitoring CI, or cleaning temporary files.

## Preserve authority boundaries

An approved plan authorizes its stated implementation and delivery operations, not merge, branch deletion, unrelated cleanup, label creation, amend, rebase, mutation-runner installation, commercial mutation integration, or changed-line mutation filtering. Keep corrective work as additional commits.

Pause for every human choice required by the plan. In particular, obtain the user's issue-reference and existing-label selections before creating a pull request when the plan calls for those choices.

Never create or modify Habit snooze state. A `snoozed` ledger result records a pre-existing state only after the user explicitly authorizes it. Schemas v3 through v5 do not require a Habit baseline commit.

Keep `.agent/tmp/<slug>.md`, `.agent/tmp/<slug>.workflow.json`, the validation inventory, and mutation logs/reports until a future invocation independently confirms the recorded pull request is `MERGED`. Never infer merge from a closed pull request, green CI, or local Git state.

New ledgers use schema v5 and capture the declared base ref, immutable `base_sha`, resolved model selection, and confirmed validation inventory. Existing schema-v1 through schema-v4 ledgers remain readable and retain their original model, transition, evidence, pull-request, and cleanup rules; reading them never migrates or rewrites them.
