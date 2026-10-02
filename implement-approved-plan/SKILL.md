---
name: implement-approved-plan
description: Execute a user-approved repository plan through configurable persistent Codex workers, role-scoped leases, a guarded local ledger, validation, focal mutation testing, structural review, and pull-request/CI handoff. Invoke only when the user explicitly names $implement-approved-plan; do not use to draft plans, merge pull requests, or clean unmerged work.
---

# Implement Approved Plan

Execute the approved plan without silently changing its scope or approval boundaries.

## Enforce the coordinator contract

Before starting a new plan, inspect the target repository and approved plan for configured validation commands, CI checks, Sonar, mutation testing, and Habit hooks. Show the proposed validation inventory with source, execution location, role owner, and exclusions; obtain the user's confirmation before creating the Coordinator worker or ledger. A configured local check that cannot run blocks startup with a concrete diagnosis. A CI-only check is monitored after the pull request. Do not select a tool merely because it is installed. Follow [references/workflow.md](references/workflow.md) for discovery and later reassessment.

Present the resulting worker distribution alongside the inventory, marking optional roles active or inactive, and use the existing initial confirmation to fix both selections. A role is a responsibility; a worker is one persistent chat with a single model/effort pair and one or more roles. Suggest `implementation` (Coordinator + Implementer, `gpt-6-sol`/`medium`), `quality` (Committer + Validator + Mutation Analyst + Habit Curator, `gpt-6-luna`/`high`), and `structural-review` (Structural Reviewer, `gpt-6-sol`/`medium`). Accept natural-language requests to group or split roles and change a worker's pair; generate the confirmed JSON internally. Every role belongs to exactly one worker. Splits inherit the original pair unless specified; merging different pairs requires resolving the pair before initial confirmation.

Separate contexts are recommended for independent validation and review. Explain any loss of independence in the initial presentation; all groupings remain allowed without an additional confirmation. Never claim independence for validation or review sharing the implementation context. For resumes, reuse recorded workers, pairs and inventory, then reassess checks before the next validation gate. Do not change topology or pairs during a run.

Before changing files or creating workers, verify every selected model/effort pair is callable, including workers containing only inactive optional roles. Never substitute a pair. Stop and ask the user if an exact pair is unavailable. Before creating any local worker, confirm Full access (`sandbox_mode = "danger-full-access"`, `approval_policy = "never"`). Permissions are environment state; if unavailable, stop and ask the user.

The worker containing Coordinator conducts the workflow. If this is the bootstrap chat, create that worker in the saved project's local checkout, pass the confirmed selections, and prohibit creating another Coordinator worker. If this chat is already that worker, continue here. Create and register it plus every worker containing Implementer, Committer, Validator or Structural Reviewer before `implementing`. Create workers containing only optional roles when their local checks become selected; reuse an existing worker containing the newly activated role. Do not create extra chats per role.

Coordinator alone assigns roles and operates ledger leases. For a role in its own worker, execute locally without self-messaging. Load the active role's instructions and applicable references at each phase, name that role explicitly, and retain awareness of restrictions already present in history. Release the previous lease before switching roles, even within one chat. A Validator lease never permits Committer actions. If Habit Curator shares a worker with Validator, send all code corrections to Implementer; a separate Habit worker retains only the explicitly assigned limited correction contract in [references/workflow.md](references/workflow.md).

## Load the applicable procedures

- Read [references/workflow.md](references/workflow.md) before startup, worker creation, implementation, validation, mutation testing, or review.
- Read [references/ledger.md](references/ledger.md) before creating or changing workflow state.
- Read [references/github-delivery.md](references/github-delivery.md) before querying earlier pull requests, creating issues or pull requests, selecting labels, monitoring CI, or cleaning temporary files.

## Preserve authority boundaries

An approved plan authorizes its stated implementation and delivery operations, not merge, branch deletion, unrelated cleanup, label creation, amend, rebase, mutation-runner installation, commercial mutation integration, or changed-line mutation filtering. Keep corrective work as additional commits.

Pause for every human choice required by the plan. In particular, obtain the user's issue-reference and existing-label selections before creating a pull request when the plan calls for those choices.

Never create or modify Habit snooze state. A `snoozed` ledger result records a pre-existing state only after the user explicitly authorizes it. Schemas v3 through v6 do not require a Habit baseline commit.

Keep `.agent/tmp/<slug>.md`, `.agent/tmp/<slug>.workflow.json`, the worker configuration, validation inventory, and mutation logs/reports until a future invocation independently confirms the recorded pull request is `MERGED`. Never infer merge from a closed pull request, green CI, or local Git state.

New ledgers use schema v6 with immutable `worker_selection`, registered `workers`, declared base ref, immutable `base_sha`, and confirmed validation inventory. Existing v1–v5 ledgers retain their original `chats`, `model_selection` where applicable, defaults, interfaces, transitions, evidence, delivery and cleanup rules. Reading them never migrates or rewrites them.
