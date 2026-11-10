---
name: plan-handoff
description: Plan a repository change as an ExecPlan with implement-execplan and plan-behavioral-acceptance, stop for user approval, then print a short handoff that another Claude Code session executes through branch creation, implementation, lc, and lp. Manual Claude Code workflow; use only when the user invokes /plan-handoff.
disable-model-invocation: true
---

# Plan Handoff

Plan the requested work in this session and hand execution to a new session that the user opens. This session only plans: it never creates branches, implements, commits, or pushes.

## Check the starting state

Before planning, inspect the repository:

- Confirm the working directory is inside a Git repository and record its root.
- Record the current branch and run `git status --porcelain --untracked-files=all`.
- If the worktree already has changes, warn the user: the executor accepts only the ExecPlan as a pending change and will stop otherwise. Ask whether to continue.
- If `.agent/execplans/` is ignored by Git (`git check-ignore`), warn the user that the plan would not be committed, and ask how to proceed.

## Plan

1. Load and follow `implement-execplan` and `plan-behavioral-acceptance`.
2. Research the repository as those skills require. Do not edit anything other than the plan file.
3. Write the ExecPlan to `.agent/execplans/<context>.md`, where `<context>` is a short lowercase English name for the work.
4. Make sure the plan states the final validation commands, because the executor commits only after they pass.

## Stop for approval

Summarize the plan in a few lines with its path, then stop and ask the user to approve it. Apply requested changes to the plan file and ask again. Do not print the handoff before explicit approval.

## Print the handoff

After approval, print the handoff below in one code block, with the placeholders filled. Do not copy plan content into it; the ExecPlan is the single source of truth. Then end the turn.

```
Execute the ExecPlan at `<plan path>` in the repository `<repository root>`.

This message is my explicit request, in this session, to create a branch, commit with `lc`, and push with `lp`.

1. Run `git status --porcelain --untracked-files=all`. The only expected pending change is `<plan path>`, and it belongs to this work. If anything else appears, stop and ask me. Otherwise, use the create-git-branch skill to create the branch for this work; the plan file moves with it.
2. Implement the whole plan with the implement-execplan and tdd-behavior-autonomous-quiet skills, keeping the ExecPlan progress current.
3. Run the final validation listed in the ExecPlan. If it fails, stop and report.
4. Using the Bash tool, run `lc`, then `lp`. Do not use `lp -f` or `lp -m`, and never commit or push with git directly. If either command fails, stop and report.
5. Report the branch name, the commits created, and the push result.
```
