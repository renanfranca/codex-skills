---
name: seed4j-execplan-tdd
description: Use for substantial seed4j-cli work requiring a living ExecPlan, behavior-focused quiet TDD, and a post-green design review before final validation. Triggers when the user asks to plan, implement, execute, or continue substantial seed4j-cli changes with ExecPlan discipline.
---

# Seed4J ExecPlan TDD

Use this skill only for work in `/home/renanfranca/projects/seed4j-cli`.

## Workflow

1. Load and follow the `implement-execplan` skill before creating or updating any plan.
2. Save every ExecPlan under `/home/renanfranca/projects/seed4j-cli/_temporary/ai_agent/seed4j-cli-ai-context/shared`.
3. Name new plans as `<YYYY-MM-DD>_<TYPE>_<short-kebab-title>-exec-plan.md`, where `TYPE` is a concise uppercase change category such as `FEATURE`, `FIX`, `REFACTOR`, `DOCS`, or `TEST`.
4. Before implementing from an ExecPlan, load and follow the `tdd-behavior-autonomous-quiet` skill.
5. Keep the ExecPlan living during execution: update Progress, Decisions, Risks, Lessons Learned, validation results, and any scope changes as work proceeds.
6. Confirm that all milestone behavior is complete and that the relevant suite and public-path checkpoint are green.
7. Load and follow `refactor-design` before final repository validation. Keep the ExecPlan living during the review and record meaningful refactors, decisions, risks, validation results, and reusable learning candidates.
8. If the review discovers missing or incorrect behavior, return to `tdd-behavior-autonomous-quiet` and restore a green behavior checkpoint before resuming the design review.
9. Run final repository validation only after post-green design consolidation is green.

## Seed4J Constraints

Respect the repository `AGENTS.md` instructions, especially:

- preserve hexagonal architecture boundaries;
- use Types Driven Development for business concepts;
- validate incrementally with focused tests or checks;
- do not run `./mvnw clean verify` automatically unless the user explicitly asks.

If a requested change conflicts with those constraints, flag it before implementation.
