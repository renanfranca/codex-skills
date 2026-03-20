---
name: commit-staged-change
description: Create Conventional Commits v1.0.0 messages and execute safe commits for already staged changes. Use when Codex should inspect history and staged diffs, align with repository conventions when they are already conventional, and run git commit safely.
---

# Commit Staged Change

## Objective

Draft and execute a safe `git commit` for currently staged files using the Conventional Commits v1.0.0 format, while aligning with repository history when the repository already follows Conventional Commits.

## Conventional Commits Rules

- Subject format: `<type>[optional scope][!]: <description>`.
- Allowed `type` values: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`.
- Use imperative mood and keep the subject concise (preferably up to 72 chars).
- Use `!` when the change introduces a breaking change.
- Add footer `BREAKING CHANGE: <details>` when breaking behavior needs explicit migration context.
- Add body/footer only when useful for rationale, context, references, or migration notes.

Reference: https://www.conventionalcommits.org/en/v1.0.0/

## History-Aware Convention Strategy

- Inspect recent commit subjects with `git log --pretty=format:%s -n 100`.
- Detect whether the repository already uses Conventional Commits consistently.
- If yes, prefer the repository's local conventions while remaining valid Conventional Commits v1.0.0:
  - common `type` usage and naming choices
  - scope presence and scope naming style
  - subject language and wording style
  - common footer/reference patterns
- If not, still produce a valid Conventional Commit using neutral defaults from this skill.

## Workflow

1. Inspect repository state.
- Run `git rev-parse --show-toplevel` and `git status --short --branch`.
- Stop and ask for staging if no files are staged.
- Stop and resolve conflicts first when merge/rebase/cherry-pick state is active.

2. Analyze commit history.
- Run `git log --pretty=format:%s -n 100`.
- Identify whether Conventional Commits are dominant.
- Extract repository-specific conventions when dominant.

3. Understand staged changes.
- Inspect staged files with `git diff --cached --name-status`.
- Inspect staged patch with `git diff --cached`.
- Summarize intent before drafting the message.
- Warn when staged changes appear unrelated; suggest splitting commits.

4. Draft the commit message in Conventional Commits format.
- Pick the best `type` from the staged intent.
- Add scope when it increases clarity and follows repository style.
- Write a compliant subject line.
- Add body/footer only when needed.
- If the user asks for draft-only, stop before execution.

5. Perform safety checks.
- Verify author configuration with `git config user.name` and `git config user.email`.
- Recheck staging with `git status --short` before commit.
- Show final message and staged file summary before executing.

6. Execute the commit.
- Run `git commit -m "<subject>"`.
- Add additional `-m` flags for body/footer paragraphs when needed.
- Return resulting hash and summary from `git log -1 --oneline`.

## Guardrails

- Avoid non-Conventional-Commits subjects unless explicitly requested.
- Avoid `git commit --amend` unless explicitly requested.
- Avoid signing, pushing, rebasing, or force operations unless explicitly requested.
- Avoid `--allow-empty` unless explicitly requested.
- Avoid modifying staging (`git add`, `git restore --staged`, `git reset`) unless explicitly requested.
- Commit only staged content.

## Example Triggers

- `Create a conventional commit from staged changes and commit it.`
- `Use Conventional Commits v1.0.0 and draft only.`
- `Follow repository conventions if they already use conventional commits.`
