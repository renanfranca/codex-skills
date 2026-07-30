# Repository Guidelines

## Project Structure & Module Organization

This repository contains self contained Codex skills. Each top level skill directory requires a `SKILL.md` and may include:

- `agents/openai.yaml` for display metadata and invocation defaults
- `references/` for guidance loaded only when needed
- `scripts/` for deterministic automation
- `evals/` for suites, cases, prompts, and isolated fixtures

Repository guides live in `README.md`, `CODEX_CLI.md`, and `EVALUATIONS.md`. Treat `.system/` as Codex managed and `_temporary/` as local scratch space; neither belongs in normal contributions.

## Auditable Project Memory

Use `_temporary/codex-skills-ai-context` as the required local clone for ExecPlans and durable project memory. Before creating an ExecPlan:

1. Confirm that `_temporary/codex-skills-ai-context` is an existing Git worktree.
2. Confirm that its `origin` is exactly `https://github.com/renanfranca/codex-skills-ai-context.git`.
3. Stop before creating the plan if either check fails.

Never use another location as a fallback. Do not clone the memory repository automatically, and do not commit or push either repository unless the user explicitly requests it.

Name new plans `<YYYY-MM-DD>_<TYPE>_<short-kebab-title>-exec-plan.md`, where `TYPE` is a concise uppercase category such as `FEATURE`, `FIX`, `REFACTOR`, `DOCS`, or `TEST`.

Every ExecPlan must remain fully self contained. Historical files in the memory repository provide complementary context only and do not promise a complete project history.

When the changed scope includes `website/`, read and follow `website/AGENTS.md` in addition to this file.

## Build, Test, and Development Commands

There is no compilation or packaging step. Run commands from the repository root:

```bash
python3 -m unittest discover -s develop-skill-with-evals/scripts/tests -v
python3 .system/skill-creator/scripts/quick_validate.py ./skill-name
python3 develop-skill-with-evals/scripts/run_skill_evals.py plan --skill ./candidate-skill --baseline /tmp/baseline-skill --impact scoped --case changed-case --model <executor-model> --reasoning-effort <effort> --judge-model <judge-model> --judge-reasoning-effort <effort>
git diff --check
```

The first command runs deterministic runner tests. `quick_validate.py` checks skill structure and frontmatter. Planning is side effect free and reports full evaluation fingerprints, runtime blockers, campaign projection, and maximum model sessions before execution.

## Coding Style & Naming Conventions

Use kebab-case for skill directories and eval case IDs, such as `refactor-design` and `hidden-invocation-state`. Keep skill frontmatter names aligned with directory names. Python uses two space indentation, `snake_case` functions and variables, `PascalCase` test classes, and `test_` method names. Preserve existing two space YAML and JSON indentation. Write concise Markdown with descriptive headings and executable examples.

## Testing Guidelines

Use Python `unittest` for runner behavior. Place tests in `scripts/tests/`. Eval cases belong under `<skill>/evals/cases/<case-id>/` with `case.json`, `prompt.md`, and only the minimal fixture needed. Put complete code observable contracts under `oracle/`, never in the public fixture. Behavioral skill changes require baseline RED and three stable candidate GREEN results for affected cases. Scoped changes stop there; cross cutting changes run every remaining suite case after GREEN 1 and before GREEN 2 and 3. Model-backed promotion requires an explicit executor model and reasoning effort, with any required judge runtime declared separately or inherited. Diagnostic and promotion operations may share a locked cumulative campaign ledger. Never expose judge criteria or hidden oracles in prompts or fixtures.

## Model Runtime Recommendation

Use zero model sessions for static and deterministic work. For model-backed evaluations and fresh-agent validation, recommend `gpt-5.6-sol` with `medium` reasoning effort for both executor and judge. This is repository guidance, not a runner default: pass the model and effort explicitly for promotion and obtain separate authorization for model session cost. Preserve any runtime explicitly chosen by the user.

## Commit & Pull Request Guidelines

Follow Conventional Commits used in history: `feat(skill-name): add ...`, `chore(skill-name): update ...`, or `docs: clarify ...`. Keep subjects imperative and scoped when one skill is affected. Pull requests should explain intent and behavior, link relevant issues, list validation commands and results, and disclose retained eval artifacts or known risks.

## Security & Agent Guidance

Do not add credentials, personal data, proprietary source, full transcripts, or generated model responses to fixtures. Do not commit, push, publish, or modify managed system skills unless explicitly requested.

Run GitHub CLI commands outside the filesystem sandbox. The sandbox may not inherit the host's GitHub CLI authentication and can incorrectly report that its credentials have expired.
