# Website Workflow

Apply these instructions to all work under `website/`, together with the repository root `AGENTS.md`.

## Code Changes

Use `$execplan-tdd` for every website code change, including small fixes. A small change may use one milestone.

- ExecPlan destination: `_temporary/codex-skills-ai-context`
- ExecPlan naming: `<YYYY-MM-DD>_<TYPE>_<short-kebab-title>-exec-plan.md`
- Relevant suite for every TDD cycle: `npm test`
- Public checkpoint: `npm run test:e2e`
- Final validation, in order: `npm test`, `npm run prettier:check`, `npm run build`, `npm run test:e2e`
- Canonical documentation sources: `website/README.md`, the applicable public configuration, and root repository documentation

Run website commands from `website/`. Keep each ExecPlan self contained and update its `Documentation Impact` section with changes to each applicable canonical source or a concrete justification for leaving it unchanged.

Treat `website/.generated/` as a disposable projection. Never edit it directly; update canonical sources and use repository commands to regenerate it.

## Documentation Only Changes

Do not use `execplan-tdd` for a documentation only change. Use `implement-execplan` only when the documentation work is substantial, risky, or needs handoff safe execution.
