---
name: implement-approved-plan-deepseek
description: Execute an explicitly approved repository plan entirely inside DSH through an existing Coordinator session, six persistent top-level specialist sessions, serialized leases, behavioral TDD, independent validation, mutation testing, structural review, and GitHub delivery. Invoke as /implement-approved-plan-deepseek; never use to draft plans or merge pull requests.
disable-model-invocation: true
user-invocable: true
---

# Implement Approved Plan with DeepSeek

The current top-level DSH session becomes Coordinator. Do not create another
Coordinator. Use the native `workflow_*` tools supplied by the persistent Host
plugin; do not represent specialists with subagents or external agent processes.

DSH owns the connection, credentials, default model and per-role reasoning
configuration. Use the actual selections registered by the Host; do not
override them through prompts. All sessions require native
`danger-full-access` / approval `never`. Confirm actual permission state;
prompts cannot grant permissions.

Read [workflow](references/workflow.md), [ledger](references/ledger.md) and
[orchestration](references/orchestration.md) before startup. Read
[GitHub delivery](references/github-delivery.md) before external delivery.

## Start and execute

Use the latest plan approved through this session's native `/plan` review, or
provide an approved-plan file to `workflow_start`. The Host verifies approval.
Choose a slug, feature branch and declared base from the approved plan. Store
the approved Markdown verbatim. Capture the immutable base SHA once.

`workflow_start` reserves, creates and registers Implementer, Committer,
Validator, Habit Curator, Mutation Analyst and Structural Reviewer exactly once.
They share this workspace and checkout. Use `workflow_dispatch` for assignments,
`workflow_collect` for evidence, and `workflow_control` for every ledger action.
The Coordinator alone grants leases, routes corrections and changes phases.

Continue automatically through all authorized gates. Dispatch only one checkout
assignment at a time. End the Coordinator turn with `workflow_wait` while a
specialist runs; the Host queues a completion notification into this same
Coordinator session. Collect the result, inspect scope and checkout, record
evidence under the specialist lease, and only then release it.

Preserve the exact serialized procedure: behavior TDD, Habit, checkpoint commit,
clean verification and Sonar, focal mutation, independent structural review,
fresh Habit, additional commit when needed, final verification and Sonar,
mutation recheck, PR, and CI. All corrections return through implementation and
repeat downstream gates. Do not fabricate evidence or turn missing tools into
successful runs. Follow the commit body contract and breaking-change rules in
the workflow reference.

## Authority and recovery

Specialists return evidence to the Coordinator. They never contact each other,
alter the ledger, acquire leases, or dispatch work. Human conversations with them
are informational until a Coordinator assignment authorizes checkout actions.

Approval authorizes the stated implementation and delivery, not merge, branch
deletion, unrelated cleanup, new labels, amend, rebase, automatic mutation-runner
installation, or Habit snooze changes. Preserve artifacts until GitHub confirms
the recorded PR was merged. Ask only for choices required by the approved plan
or an actual exception gate, using DSH's native user-question interface.

After interruption call `workflow_resume` in the original Coordinator session.
Reuse all registered IDs and reconcile pending assignments, branch, HEAD,
working tree and processes before releasing a lease or repeating side effects.
See [recovery](references/recovery.md). Do not return automatically to Plan Mode.

Installation and Android commands: [environment guide](references/environment.md).
