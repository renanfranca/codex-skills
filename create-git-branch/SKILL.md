---
name: create-git-branch
description: Choose and create safe, meaningful Git branches for repository-changing work. Use whenever Codex is asked to create, name, rename, suggest, select, or prepare a branch, and before implementation starts from the repository's default branch. Do not use for read-only work that does not need a branch.
---

# Create Git Branch

Choose the branch name from the actual work context. A request to implement or change repository files authorizes creating a working branch from a clean default branch as normal setup; this skill does not authorize unrelated Git operations.

## Name the Branch

- Use concise English words, lowercase ASCII letters, digits, and hyphens only.
- Never use `/` anywhere in the name. In particular, never add `code/`, `codex/`, or another slash-separated prefix.
- When one primary issue is explicit or unambiguous, start with its number: `<issue-number>-<context>`.
- When no issue applies, use only `<context>`.
- Never add generic type prefixes such as `feat`, `fix`, `docs`, or `chore`.
- Prefer the smallest specific phrase that identifies the behavior or area. Omit vague words such as `change`, `update`, `task`, and `work`.
- Derive the context from the request, issue, specification, and established project terminology. If only an issue reference is available, inspect the issue when accessible before naming the branch.
- If several issues apply and no primary issue is clear, ask which number should lead the name.
- Validate the final name with `git check-ref-format --branch`.

For example, issue 160 about Java deep-nesting detection becomes `160-java-deep-nesting`. The same work without an issue becomes `java-deep-nesting`.

## Decide Whether to Create It

First inspect the current branch, the complete worktree state including untracked files, the repository's configured default branch, and matching local or remote branch names.

- If the user only asks for a name, return the name without changing Git state.
- Do not create a branch for planning, explanation, diagnosis, review, status, or other read-only work.
- On a clean default branch, create the validated, non-conflicting name with `git switch -c <name>` before the first repository-tracked edit.
- On a dirty default branch, do not create or switch branches. Show the relevant state and ask whether the existing changes belong to the new work.
- Away from the default branch, reuse the current branch only when it is clearly associated with the same issue or task. Otherwise stop before making changes and ask how to proceed.
- Treat detached HEAD, an ambiguous default branch, or any local or remote name collision as a reason to stop and ask. Never invent a numeric suffix, overwrite a ref, or reuse an existing branch silently.
- If an explicit user-provided name or a mandatory repository convention conflicts with these rules, explain the conflict and ask rather than silently normalizing or violating it.

After acting, state the selected name and whether the branch was created or reused.
