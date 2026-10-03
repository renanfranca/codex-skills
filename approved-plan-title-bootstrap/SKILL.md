---
name: approved-plan-title-bootstrap
description: $implement-approved-plan bootstrap that names the invoking chat primary by default or gives explicitly delegated workers exact shared-prefix titles and hands off. Apply only when a message explicitly invokes $implement-approved-plan from its bootstrap task; do not use for an existing Coordinator or unrelated title changes.
---

# Bootstrap Approved-Plan Titles

Add this title contract, then follow `$implement-approved-plan` without changing its model/effort choices, roles, gates, authorization boundaries or Git behavior.

## Resolve the prefix

Before initializing a new workflow, inspect the current task title. If it matches exactly `^[a-z]+-[a-z]+-(boot|primary)$`, reuse the two-term prefix unchanged. Otherwise derive exactly two unambiguous lowercase ASCII terms from the approved specification: `<area-or-language>-<capability>`, such as `java-nesting`. Retain only ASCII letters in each term. If no clear prefix follows from the specification, ask for the exact prefix and wait.

Start the base skill's inventory and worker selection. Its existing initial confirmation fixes the distribution. Resolve titles from that selection; do not force a separate Coordinator or change the invoking chat's actual model/effort.

## Name the single current chat

For the default new schema-v6 distribution, rename the invoking task to exactly `<prefix>-primary` with the title tool. Verify success and report that exact title before initializing/registering `primary` with this same chat's ID. Continue implementation and all subsequent roles here. Do not create a bootstrap replacement, create another Coordinator or message this chat.

A custom confirmed single current-chat worker uses `<prefix>-<worker-id>`. Every role transition preserves the title, chat identity and recorded model/effort.

## Name explicitly delegated workers and hand off

Only when the user confirms a delegated distribution, name the bootstrap `<prefix>-boot` and verify success before creating workflow chats. Every new v6 worker gets exactly `<prefix>-<worker-id>`, including the one containing Coordinator. For example, `implementation`, `quality` and `structural-review` get those suffixes. Seven separate workers get seven worker titles; do not add titles per role or a separate `-coordinator` when its role is grouped elsewhere.

Pass the prefix, schema version, confirmed worker selection and complete title contract in the Coordinator worker's initial context. Do not derive the prefix again or send the contract only in a follow-up. The Coordinator verifies its own title and each created worker title before assignments, reuses them across phases, and gives later activated optional workers the same contract.

After successful handoff to the Coordinator worker, end bootstrap work. The bootstrap does not continue implementing, issuing leases or coordinating alongside that worker. If the invoking chat is already the confirmed Coordinator worker, execute locally and do not hand off to itself.

If any required exact rename fails or cannot be verified, stop before initializing or dispatching workflow work.

## Resume recorded executions

When already inside the recorded Coordinator worker, do not repeat bootstrap or rename it to `-boot`. Use the supplied prefix and verify its recorded v6 `<prefix>-<worker-id>` title. Existing v6 distributions keep registered identities and titles; do not collapse them to `primary`.

For resumed v1–v5 ledgers, preserve recorded Coordinator/per-role chats and their existing titles, including legacy `<prefix>-coordinator`, `<prefix>-implementer`, `<prefix>-committer`, `<prefix>-validator`, `<prefix>-habit-curator`, `<prefix>-mutation-analyst` and `<prefix>-structural-reviewer` when present. Apply the legacy per-role contract only when an absent optional chat must be created under its schema's rules. Never migrate their topology or title contract to v6.

Branch creation, Git actions, ledger and delivery remain governed by the base skill and approved plan.
