---
name: commit-the-changes
description: Inspect repository commit history, infer the established commit message style and language, then stage and create a git commit that matches the repository convention. Use when the user asks to commit changes, asks for a commit message based on existing commits, or wants commits to follow the repository's established pattern.
---

# Commit The Changes

Inspect recent commit messages before writing anything. Use `git log --oneline` on the current repository and prefer the most recent relevant commits over old history.

Infer the convention from the repository instead of imposing one. Match these traits from recent commits:
- language used in the subject line
- prefix style such as `type: subject` or `type(scope): subject`
- verb tense and capitalization
- naming conventions already used for areas like `build`, `deps`, `docs`, `ci`, `test`

Stage only the changes that are part of the requested work. If unrelated tracked changes are present, call that out before committing instead of sweeping them into the same commit.

Write the smallest accurate subject line that matches the repository pattern. Do not add a body unless the repository clearly uses commit bodies for similar changes.

Avoid `git commit --amend` unless the user explicitly asks for it.

After committing, report the created commit hash and the final message.

## Workflow

1. Inspect `git status --short` to understand what is modified and whether unrelated changes exist.
2. Inspect recent commits with `git log --oneline`, using enough history to detect the dominant pattern.
3. Derive the commit message from the actual changes, not just filenames.
4. Stage the intended files.
5. Create the commit with the inferred pattern and same language as the recent commits.
6. Confirm success by reporting the commit hash and subject.

## Guardrails

- Do not invent a new commit convention if the repository already has one.
- Do not mix languages inside the subject line.
- Do not include unrelated files just because they are already modified.
- If the history is inconsistent, prefer the most recent repeated pattern and state that choice briefly.
