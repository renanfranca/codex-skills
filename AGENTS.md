# Repository Guidelines

## Project Structure & Module Organization

This repository contains self contained Codex skills. Each top level skill directory requires a `SKILL.md` and may include:

- `agents/openai.yaml` for display metadata and invocation defaults
- `references/` for guidance loaded only when needed
- `scripts/` for deterministic automation

Repository guides live in `README.md` and `CODEX_CLI.md`. Treat `.system/` as Codex managed and `_temporary/` as local scratch space; neither belongs in normal contributions.

## Auditable Project Memory

Use `_temporary/codex-skills-ai-context` as the required local clone for ExecPlans and durable project memory. Before creating an ExecPlan:

1. Confirm that `_temporary/codex-skills-ai-context` is an existing Git worktree.
2. Confirm that its `origin` is exactly `https://github.com/renanfranca/codex-skills-ai-context.git`.
3. Stop before creating the plan if either check fails.

Never use another location as a fallback. Do not clone the memory repository automatically, and do not commit or push either repository unless the user explicitly requests it.

Name new plans `<YYYY-MM-DD>_<TYPE>_<short-kebab-title>-exec-plan.md`, where `TYPE` is a concise uppercase category such as `FEATURE`, `FIX`, `REFACTOR`, `DOCS`, or `TEST`.

Every ExecPlan must remain fully self contained. Historical files in the memory repository provide complementary context only and do not promise a complete project history.

## Build, Test, and Development Commands

There is no compilation or packaging step. Run commands from the repository root:

```bash
python3 -m unittest discover -s restructure-documentation/scripts/tests -v
python3 .system/skill-creator/scripts/quick_validate.py ./skill-name
python3 restructure-documentation/scripts/check_markdown_links.py README.md CODEX_CLI.md AGENTS.md
git diff --check
```

The first command runs the repository's deterministic script tests. `quick_validate.py` checks skill structure and frontmatter. The link checker validates local Markdown targets and fragments without accessing external URLs.

## Coding Style & Naming Conventions

Use kebab-case for skill directories, such as `refactor-design` and `restructure-documentation`. Keep skill frontmatter names aligned with directory names. Python uses two space indentation, `snake_case` functions and variables, `PascalCase` test classes, and `test_` method names. Preserve existing two space YAML and JSON indentation. Write concise Markdown with descriptive headings and executable examples.

## Testing Guidelines

Use Python `unittest` for deterministic script behavior and place tests in `scripts/tests/`. Run the focused suite for every changed script, validate each changed skill with `quick_validate.py`, and check affected Markdown links. Keep fixtures minimal and free of credentials, personal data, proprietary source, full transcripts, or generated model responses.

## Commit & Pull Request Guidelines

Follow Conventional Commits used in history: `feat(skill-name): add ...`, `chore(skill-name): update ...`, or `docs: clarify ...`. Keep subjects imperative and scoped when one skill is affected. Pull requests should explain intent and behavior, link relevant issues, list validation commands and results, and disclose known risks.

## Security & Agent Guidance

Do not add credentials, personal data, proprietary source, full transcripts, or generated model responses to tests or documentation. Do not commit, push, publish, or modify managed system skills unless explicitly requested.

Run GitHub CLI commands outside the filesystem sandbox. The sandbox may not inherit the host's GitHub CLI authentication and can incorrectly report that its credentials have expired.
