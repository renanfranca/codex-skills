---
name: seed4j-worktree-flow
description: Manage the local seed4j-cli Git worktree workflow safely. Use when Codex is asked to audit seed4j-cli worktrees, create a feature worktree, clean up a completed worktree, decide which branches are already merged into main, or keep /home/renanfranca/projects/seed4j-cli as the main worktree while feature work happens under /home/renanfranca/projects/seed4j-cli-worktree.
---

# Seed4J Worktree Flow

Use this skill only for `/home/renanfranca/projects/seed4j-cli`.

## Defaults

- Treat `/home/renanfranca/projects/seed4j-cli` as the permanent `main` worktree.
- Treat `/home/renanfranca/projects/seed4j-cli-worktree/<branch>` as the location for feature worktrees.
- Use `main` as the base branch for new feature worktrees.
- Never delete remote branches automatically.
- Never remove a dirty worktree.
- Ask before running destructive cleanup when the user has not explicitly requested it.

## Script

Prefer `scripts/seed4j_worktree_flow.sh` instead of hand-writing Git worktree command sequences.

Run it from the skill directory:

```bash
scripts/seed4j_worktree_flow.sh status
scripts/seed4j_worktree_flow.sh start <branch>
scripts/seed4j_worktree_flow.sh finish <branch>
```

## Workflow

1. Start with `status` to inspect the current worktree layout, dirty states, and branch relationship to `main`.
2. For a new task, use `start <branch>`.
   - If the branch exists locally, the script creates a worktree for it.
   - If the branch does not exist locally, the script creates it from `main`.
3. For completed work, use `finish <branch>` only after the branch is merged into `main`.
4. If `finish` fails, report the exact guardrail that blocked cleanup and do not bypass it with `--force`.

## Guardrails

- Keep the main repository on `main` whenever possible.
- If a branch is already checked out in another worktree, do not create a second checkout for it.
- If a target directory already exists, inspect it before taking action.
- If `main` is stale and the task depends on remote state, fetch or pull only when the user asks or when the task explicitly requires current remote information.
- If validation is requested before merge, prefer focused checks first, then ask the user to run `./mvnw clean verify` unless they explicitly ask Codex to run it.
