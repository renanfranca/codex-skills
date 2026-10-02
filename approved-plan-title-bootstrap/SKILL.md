---
name: approved-plan-title-bootstrap
description: $implement-approved-plan bootstrap that gives the bootstrap chat and configurable worker chats exact shared-prefix titles. Apply only when a message explicitly invokes $implement-approved-plan from its bootstrap task; do not use for an existing Coordinator or for unrelated title changes.
---

# Bootstrap Approved-Plan Titles

Add only the title bootstrap described here, then follow `$implement-approved-plan` without changing its models, efforts, sequence, responsibilities, authorization boundaries, or Git behavior.

## Resolve and apply the prefix first

Complete this section before starting the base workflow or creating its Coordinator worker.

1. Inspect the current root task title. If it matches exactly `^[a-z]+-[a-z]+-boot$`, remove the `-boot` suffix and reuse the remaining two-term prefix unchanged.
2. Otherwise, derive exactly two unambiguous lowercase ASCII terms from the approved specification: `<area-or-language>-<capability>`, such as `java-nesting`. Prefer the specification's own terminology and retain only ASCII letters in each term.
3. If the specification does not yield one clear two-term prefix, ask the user for the exact prefix and wait. Never invent an ambiguous label or silently choose among plausible alternatives.
4. Rename the current task to exactly `<prefix>-boot` with the task-title tool. Verify the successful result and tell the user the exact resulting title.

If renaming fails or the exact result cannot be confirmed, stop before starting `$implement-approved-plan` or creating any workflow task.

## Carry the prefix into the workflow

After the verified root rename, start `$implement-approved-plan`. Resolve and confirm the worker distribution through the base workflow, then pass the prefix, schema version, confirmed worker selection and complete title contract in the initial context of the worker containing Coordinator. Do not derive the prefix again or send the title contract only in a follow-up.

For a new schema-v6 execution, every worker chat has the exact title `<prefix>-<worker-id>`, including the worker containing Coordinator. With the suggested distribution, the titles are:

- `<prefix>-implementation`
- `<prefix>-quality`
- `<prefix>-structural-review`

Use the confirmed kebab-case worker IDs for custom distributions: seven separate workers produce seven chats; all roles in `all-roles` produce one `<prefix>-all-roles` chat. Keep `<prefix>-boot` for the bootstrap. Do not create additional chats or titles per role, and do not create a separate `-coordinator` chat when Coordinator belongs to another worker.

The Coordinator role must verify every created worker title before dispatching work. If an exact title cannot be applied or verified, stop. Reuse each registered worker and title across phases; an optional worker created after reassessment gets the same `<prefix>-<worker-id>` contract.

When this skill is discovered inside the worker already containing Coordinator, do not repeat the root bootstrap or rename it to `-boot`. Use the supplied prefix, verify its own `<prefix>-<worker-id>` title against `worker_selection`, and continue the base workflow.

For resumed v1–v5 executions, preserve the recorded Coordinator and per-role chats and their existing titles, including legacy `<prefix>-coordinator`, `<prefix>-implementer`, `<prefix>-committer`, `<prefix>-validator`, `<prefix>-habit-curator`, `<prefix>-mutation-analyst`, and `<prefix>-structural-reviewer` when present. Do not rename them to v6 worker titles or create a new topology. Apply the legacy per-role contract only when a previously absent optional chat must be created under its schema's rules.

Do not create or rename branches, perform Git operations, or modify `$implement-approved-plan` on behalf of this bootstrap; those concerns remain governed by the base workflow and approved plan.
