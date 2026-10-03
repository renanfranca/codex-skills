---
name: implement-approved-plan
description: Execute a user-approved repository plan in the invoking chat with its current model and effort, deterministic validation evidence, role-scoped leases, focal mutation testing, structural review, and pull-request/CI handoff. Separate persistent workers are an explicit option. Invoke only when the user explicitly names $implement-approved-plan; do not use to draft plans, merge pull requests, or clean unmerged work.
---

# Implement Approved Plan

Execute the approved plan without silently changing its scope or approval boundaries.

## Use the invoking chat by default

Before starting a new plan, inspect the target repository and approved plan for configured validation commands, CI checks, Sonar, mutation testing, and Habit hooks. Present the inventory with source, execution location, role owner and exclusions alongside the worker distribution. The existing initial confirmation covers both inventory and distribution. A configured local check that cannot run blocks startup; CI-only checks remain in the delivery workflow.

The default distribution is one worker `primary`, registered with the current chat's actual ID, model and effort, responsible for all seven roles. Recommend `gpt-6.1-sol`/`medium` without changing the invoking chat's settings or requiring that pair. Obtain the actual current identity/settings from session context or configured tools; never infer an ID or record recommended settings as actual settings. If they cannot be resolved, request the missing metadata. Continue in this chat: do not create another Coordinator or send messages to yourself. Optional Mutation Analyst and Habit Curator remain inactive unless their configured local checks are selected.

Offer separate specialist chats as an explicit alternative during the same initial confirmation. Accept grouping, splitting and model/effort choices through [references/workflow.md](references/workflow.md). Create chats only for a confirmed delegated distribution. Check exact pair availability and Full access before creating delegated workers; never substitute a pair. The current chat already demonstrates its own model/effort availability. Register each required worker once and preserve its identity across phases.

Coordinator alone assigns roles and operates ledger leases. Load the current role's instructions and applicable references at its phase, explicitly name the role, release the previous lease, then acquire the new role's lease even within `primary`. Compose `$tdd-behavior-autonomous-quiet` during implementation and `$refactor-design` during structural review; do not preload all role skills. A Validator lease never permits Committer actions. When Habit Curator shares Validator's worker, route every code correction to Implementer.

The chat conducts implementation, TDD, design review, interpretation, commits and delivery. Use `scripts/run_validation.py` for selected local validation commands and interpret its bounded evidence before recording gates through the existing ledger interfaces. Read [references/validation-runner.md](references/validation-runner.md) when configuring or invoking it. The deterministic executor does not alter the ledger or approve semantic criteria. Keep all existing checkpoints, initial/final validation, mutation classifications, structural review and delivery gates. Validation and review in the implementation context must be disclosed as sharing context and never called independent.

For resumes, retain recorded workers/chats, model/effort pairs and inventory for schemas v1–v6; reassess checks before the next validation gate. Do not change topology or settings or migrate an existing ledger to `primary`.

## Load the applicable procedures

- Read [references/workflow.md](references/workflow.md) before startup, worker creation, implementation, validation, mutation testing, or review.
- Read [references/ledger.md](references/ledger.md) before creating or changing workflow state.
- Read [references/github-delivery.md](references/github-delivery.md) before querying earlier pull requests, creating issues or pull requests, selecting labels, monitoring CI, or cleaning temporary files.

## Preserve authority boundaries

An approved plan authorizes its stated implementation and delivery operations, not merge, branch deletion, unrelated cleanup, label creation, amend, rebase, mutation-runner installation, commercial mutation integration, or changed-line mutation filtering. Keep corrective work as additional commits.

Pause for every human choice required by the plan. In particular, obtain the user's issue-reference and existing-label selections before creating a pull request when the plan calls for those choices.

Never create or modify Habit snooze state. A `snoozed` ledger result records a pre-existing state only after the user explicitly authorizes it. Schemas v3 through v6 do not require a Habit baseline commit.

Keep `.agent/tmp/<slug>.md`, `.agent/tmp/<slug>.workflow.json`, the worker configuration, validation inventory, collector configuration, and validation/mutation artifacts until a future invocation independently confirms the recorded pull request is `MERGED`. Never infer merge from a closed pull request, green CI, or local Git state.

For every new ledger, always pass an explicit confirmed worker configuration with `init --worker-plan`. New ledgers use schema v6 with immutable `worker_selection`, registered `workers`, declared base ref, immutable `base_sha`, and confirmed validation inventory. Existing v1–v5 ledgers retain their original `chats`, `model_selection` where applicable, defaults, interfaces, transitions, evidence, delivery and cleanup rules. Reading them never migrates or rewrites them.
