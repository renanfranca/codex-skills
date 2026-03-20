---
name: commit-staged-change
description: Build commit messages from repository history and execute git commits. Use when Codex must infer commit conventions (format, scope, tone, and language), draft a message aligned with existing commits, and commit staged changes safely.
---

# Commit Staged Change

## Objective

Infer the repository's commit conventions, draft a compliant message for staged changes, and execute a safe `git commit`.

## Workflow

1. Inspect repository state.
- Run `git rev-parse --show-toplevel` and `git status --short --branch`.
- Stop and ask for staging if no files are staged.
- Stop and resolve conflicts first when merge/rebase/cherry-pick state is active.

2. Infer the commit convention from recent history.
- Read recent subjects with `git log --pretty=format:%s -n 50`.
- Detect dominant patterns: prefix style, scope usage, tense, language, and ticket IDs.
- Follow the dominant recent pattern on the current branch when multiple styles exist.

3. Understand staged changes.
- Inspect staged files with `git diff --cached --name-status`.
- Inspect staged patch with `git diff --cached`.
- Summarize intent before drafting the message.
- Warn when staged changes appear unrelated; suggest splitting commits.

4. Draft the commit message.
- Write a subject that matches inferred style.
- Keep the subject concise (usually up to 72 characters unless repository history shows otherwise).
- Add a body only when needed for rationale, context, or migration notes.
- Keep message language aligned with recent repository commits.

5. Perform safety checks.
- Verify author configuration with `git config user.name` and `git config user.email`.
- Recheck staging with `git status --short` before commit.
- Show final message and staged file summary before executing.
- Stop before execution when user requests a dry run.

6. Execute the commit.
- Run `git commit -m "<subject>"`.
- Add additional `-m` flags for multi-paragraph body text when needed.
- Return resulting hash and summary from `git log -1 --oneline`.

## Guardrails

- Avoid `git commit --amend` unless explicitly requested.
- Avoid signing, pushing, rebasing, or force operations unless explicitly requested.
- Avoid `--allow-empty` unless explicitly requested.
- Avoid modifying staging (`git add`, `git restore --staged`, `git reset`) unless explicitly requested.
- Commit only staged content.

## Example Triggers

- `Create a commit message from history and commit staged changes.`
- `Infer our commit format and prepare the best commit message.`
- `Write the message in the same language used by recent commits.`
- `Draft only; do not run git commit.`
