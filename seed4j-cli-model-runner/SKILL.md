---
name: seed4j-cli-model-runner
description: Run a controlled, auditable comparison of Codex models implementing one SPEC.md with Seed4J CLI. Use only when the user explicitly wants to create a public experiment repository, choose a model/reasoning-effort matrix, execute one new Codex task per result branch sequentially, and preserve each implementation and transcript for later evaluation.
---

# Seed4J CLI Model Runner

Create the experiment and preserve its raw results. Do not score implementations, write the evaluation report, merge branches, or repair a model's outcome. Use `$seed4j-cli-model-evaluator` later for evaluation.

Before execution, read [Audit and artifact contract](references/audit-contract.md). Resolve the directory containing this `SKILL.md`; use its transcript exporter rather than reconstructing a conversation manually.

## Required input

Collect one specification and an ordered run matrix:

```yaml
spec: <pasted text, local file, raw text URL, or GitHub blob URL>
prompt: <optional shared prompt>
runs:
  - model: gpt-5.6-sol
    effort: low
  - model: gpt-5.6-terra
    effort: xhigh
    alias: terra-xhigh
```

`model` and `effort` are required. `alias` is optional. Derive it by removing a leading `gpt-<version>-` when a family remains, then append the effort; otherwise slug the complete model and effort. For example, `gpt-5.6-sol` plus `low` becomes `sol-low`. Require lowercase kebab-case and reject duplicate aliases or resulting branches. An explicit alias replaces the derived value.

Default the shared prompt to this exact text:

```text
Implement the specification in SPEC.md using the already-installed Seed4J CLI tool as support.
```

Allow one replacement before the first task. After confirmation, preserve the prompt byte-for-byte for every run.

## Preconditions

- Start in an empty local directory already saved as a Codex project. Accept either no Git repository or an unborn, clean repository with no remote. Do not erase or adopt existing content.
- Require `git`, an authenticated `gh`, and `seed4j`. Discover the installed CLI/runtime with `seed4j --version`; never install, update, or switch versions implicitly.
- Accept URLs only when they are raw text/Markdown or GitHub blob URLs that can be converted to raw content. Show extracted content and ask before transforming generic HTML.
- Confirm every requested model/effort pair is advertised by the current task-creation tool before creating the repository or any branch. Reject the complete matrix atomically when any pair is unsupported.
- Treat the repository as public. Derive `<spec-slug>` from the first Markdown H1, then the source filename, then a concise content slug. Derive the repository as `seed4j-cli-<spec-slug>` and stop on a local or GitHub collision; never append a silent numeric suffix.

Show one preflight summary containing the GitHub owner, public repository name, specification source/hash, exact prompt/hash, observed Seed4J versions, base branch, ordered runs, task titles, and result branches. Obtain one explicit confirmation. After it, continue without routine pauses; stop only for unsafe residue, missing authority, unsupported state, or unavailable infrastructure.

## Bootstrap the experiment

1. Initialize `main` when needed and materialize the specification as root `SPEC.md` without adding provenance or generated metadata to it.
2. Commit as `docs: add specification`. Assert that `git ls-files` returns exactly `SPEC.md` before creating the public GitHub repository and pushing `main`.
3. Create `<spec-slug>-seed4j-base` directly from `main`.
4. Run `seed4j skill install`. Accept only `.agents/skills/seed4j-cli/**` as the resulting tracked change; stop on any other path.
5. Commit as `docs: add Seed4J CLI skill`, push the base branch, and record its full commit plus a SHA-256 over the sorted `git ls-tree -r` output for the installed skill.
6. Freeze the prompt, matrix, common base, `SPEC.md` hash, CLI/runtime output, and skill hash. Do not update them after the first task starts.

The base branch contains the `main` specification plus the installed repository-local skill and nothing else.

## Run the matrix sequentially

For each run, in declared order:

1. Require a clean worktree. Create `<spec-slug>-<alias>` from the exact frozen base and check it out in the saved project directory.
2. Create one Codex task in that project with local execution, the requested model and reasoning effort, title exactly equal to the branch, and the frozen prompt as its first message. Never use a worktree task.
3. Wait for that task alone to finish. Do not change branches, files, or Git state while it runs. Do not mention previous outcomes or answer implementation clarifications; a clarification request makes the run `blocked` and is preserved as such.
4. Inspect the resulting tree without fixing it. Run the repository-native validation command when it can be identified unambiguously. Record the exact command, exit code, and concise result; absence of a runnable validator is a recorded failure, not permission to invent one.
5. Send this same delivery follow-up to the task, substituting only the commit subject:

```text
Preserve the experimental implementation exactly as it is. Do not change production code or tests. Remove only regenerable build output if present, commit any remaining implementation files using `<commit-subject>`, and push the current branch with upstream. If validation failed or there is nothing to commit, report that fact without repairing the result.
```

Use `feat: implement <spec-title>` as `<commit-subject>`. Wait for completion. If delivery alone fails, the coordinator may commit and push the unchanged outcome and must record `coordinator` as the delivery actor.
6. Capture the final implementation commit before adding audit files. Locate the task rollout by its task ID under `$CODEX_HOME/sessions` and run:

```bash
python3 <runner-skill-dir>/scripts/export_codex_transcript.py \
  --thread-id <task-id> \
  --model <model> \
  --effort <effort> \
  --branch <branch> \
  --output CONVERSATION_TRANSCRIPT.md
```

7. Create `.seed4j-evaluation/run.json` according to the audit contract. Validate JSON syntax, prompt/spec hashes, branch/commit identities, task metadata, status, and transcript cutoff.
8. Commit only the transcript and manifest as `docs: add <alias> run audit`, then push.
9. Remove only known regenerable untracked roots such as `target/`, `build/`, `dist/`, `coverage/`, `.gradle/`, and `node_modules/` after verifying each is inside the repository and untracked or ignored. Stop on any other residue before the next checkout.

Do not fetch, enumerate, inspect, or summarize previous result branches while a later task is running. A shared remote can still be deliberately queried; record that discoverability as an evaluation limitation.

## Failure policy and completion

Preserve failed, blocked, partial, or test-red outcomes without human correction and continue after safe cleanup. A result branch may contain only the frozen base plus its audit commit when the task produced no implementation.

At completion, report the repository URL, frozen base, each branch/task/status/pinned result, validation outcomes, and prompt hash. Stop there. Do not invoke the evaluator automatically; its separate invocation is the experiment's review boundary.
