# Repository Guidelines

## Project Structure & Module Organization

This repository contains self contained Codex skills. Each top level skill directory requires a `SKILL.md` and may include:

- `agents/openai.yaml` for display metadata and invocation defaults
- `references/` for guidance loaded only when needed
- `scripts/` for deterministic automation
- `evals/` for suites, cases, prompts, and isolated fixtures

Repository guides live in `README.md`, `CODEX_CLI.md`, and `EVALUATIONS.md`. Treat `.system/` as Codex managed and `_temporary/` as local scratch space; neither belongs in normal contributions.

## Build, Test, and Development Commands

There is no compilation or packaging step. Run commands from the repository root:

```bash
python3 -m unittest discover -s develop-skill-with-evals/scripts/tests -v
python3 .system/skill-creator/scripts/quick_validate.py ./skill-name
python3 develop-skill-with-evals/scripts/run_skill_evals.py plan --skill ./candidate-skill --baseline /tmp/baseline-skill --impact scoped --case changed-case --model <executor-model> --reasoning-effort <effort> --judge-model <judge-model> --judge-reasoning-effort <effort>
git diff --check
```

The first command runs deterministic runner tests. `quick_validate.py` checks skill structure and frontmatter. Planning is side effect free and reports runtime blockers plus the maximum model sessions before execution.

## Coding Style & Naming Conventions

Use kebab-case for skill directories and eval case IDs, such as `refactor-design` and `hidden-invocation-state`. Keep skill frontmatter names aligned with directory names. Python uses two space indentation, `snake_case` functions and variables, `PascalCase` test classes, and `test_` method names. Preserve existing two space YAML and JSON indentation. Write concise Markdown with descriptive headings and executable examples.

## Testing Guidelines

Use Python `unittest` for runner behavior. Place tests in `scripts/tests/`. Eval cases belong under `<skill>/evals/cases/<case-id>/` with `case.json`, `prompt.md`, and only the minimal fixture needed. Behavioral skill changes require baseline RED and three stable candidate GREEN results for affected cases. Scoped changes stop there; cross cutting changes add every remaining suite case once as proportional regression. Model-backed promotion requires an explicit executor model and reasoning effort, with any required judge runtime declared separately or inherited. Never expose judge criteria in prompts or fixtures.

## Commit & Pull Request Guidelines

Follow Conventional Commits used in history: `feat(skill-name): add ...`, `chore(skill-name): update ...`, or `docs: clarify ...`. Keep subjects imperative and scoped when one skill is affected. Pull requests should explain intent and behavior, link relevant issues, list validation commands and results, and disclose retained eval artifacts or known risks.

## Security & Agent Guidance

Do not add credentials, personal data, proprietary source, full transcripts, or generated model responses to fixtures. Do not commit, push, publish, or modify managed system skills unless explicitly requested.
