---
name: approved-plan-title-bootstrap
description: $implement-approved-plan bootstrap that gives the root task, Coordinator, and specialist tasks exact shared-prefix titles. Apply only when a message explicitly invokes $implement-approved-plan from its bootstrap task; do not use for an existing Coordinator or for unrelated title changes.
---

# Bootstrap Approved-Plan Titles

Add only the title bootstrap described here, then follow `$implement-approved-plan` without changing its models, efforts, sequence, responsibilities, authorization boundaries, or Git behavior.

## Resolve and apply the prefix first

Complete this section before starting the base workflow or creating its Coordinator.

1. Inspect the current root task title. If it matches exactly `^[a-z]+-[a-z]+-boot$`, remove the `-boot` suffix and reuse the remaining two-term prefix unchanged.
2. Otherwise, derive exactly two unambiguous lowercase ASCII terms from the approved specification: `<area-or-language>-<capability>`, such as `java-nesting`. Prefer the specification's own terminology and retain only ASCII letters in each term.
3. If the specification does not yield one clear two-term prefix, ask the user for the exact prefix and wait. Never invent an ambiguous label or silently choose among plausible alternatives.
4. Rename the current task to exactly `<prefix>-boot` with the task-title tool. Verify the successful result and tell the user the exact resulting title.

If renaming fails or the exact result cannot be confirmed, stop before starting `$implement-approved-plan` or creating any workflow task.

## Carry the prefix into the workflow

After the verified root rename, start `$implement-approved-plan`. Pass the resolved prefix and the complete title contract in the Coordinator's initial creation context, not in a later follow-up and not by asking the Coordinator to derive it again. Create the Coordinator with the exact title `<prefix>-coordinator` and require it to create or reuse its specialists with these exact titles:

- `<prefix>-implementer`
- `<prefix>-committer`
- `<prefix>-validator`
- `<prefix>-habit-curator`
- `<prefix>-structural-reviewer`

The Coordinator must verify each created task's title and stop before dispatching work if any exact title cannot be applied. Reuse the same titled task for each role as required by the base workflow.

If this skill is also discovered inside the already-created dedicated Coordinator, do not repeat the root bootstrap or rename it to `-boot`. Use the verified prefix supplied in its initial context, confirm that its own title is exactly `<prefix>-coordinator`, enforce the specialist title contract above, and continue with `$implement-approved-plan`.

Do not create extra roles or tasks. Do not create or rename branches, perform Git operations, or modify `$implement-approved-plan` on behalf of this bootstrap; those concerns remain exclusively governed by the base workflow and the user's approved plan.
