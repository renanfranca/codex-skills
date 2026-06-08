---
name: seed4j-execplan-tdd
description: Use for seed4j-cli requests that need an ExecPlan, a plan saved in the shared seed4j-cli AI context directory, or implementation through quiet autonomous TDD. Triggers when the user asks to plan, implement, execute, or continue substantial seed4j-cli work with ExecPlan discipline and tdd-strict-autonomous-quiet.
---

# Seed4J ExecPlan TDD

Use this skill only for work in `/home/renanfranca/projects/seed4j-cli`.

## Workflow

1. Load and follow the `implement-execplan` skill before creating or updating any plan.
2. Save every ExecPlan under `/home/renanfranca/projects/seed4j-cli/_temporary/ai_agent/seed4j-cli-ai-context/shared`.
3. Name new plans as `<YYYY-MM-DD>_<TYPE>_<short-kebab-title>-exec-plan.md`, where `TYPE` is a concise uppercase change category such as `FEATURE`, `FIX`, `REFACTOR`, `DOCS`, or `TEST`.
4. Before implementing from an ExecPlan, load and follow the `tdd-behavior-autonomous-quiet` skill.
5. Keep the ExecPlan living during execution: update Progress, Decisions, Risks, Lessons Learned, validation results, and any scope changes as work proceeds.

## Seed4J Constraints

Respect the repository `AGENTS.md` instructions, especially:

- preserve hexagonal architecture boundaries;
- use Types Driven Development for business concepts;
- validate incrementally with focused tests or checks;
- do not run `./mvnw clean verify` automatically unless the user explicitly asks.

If a requested change conflicts with those constraints, flag it before implementation.
