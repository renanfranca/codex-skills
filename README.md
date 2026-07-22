# Codex Skills

Personal [Codex](https://openai.com/codex/) skills for test-driven development, design review, execution planning, Git workflows, and Seed4J CLI maintenance.

Each top-level skill directory is self-contained. Install the skills you need under `$CODEX_HOME/skills` (or `~/.codex/skills` when `CODEX_HOME` is unset), then invoke one explicitly with `$skill-name`. Skills may also support implicit activation, but explicit invocation is the most reliable entry point.

## Skill catalog

### Skill development and design

- [`develop-skill-with-evals`](develop-skill-with-evals/SKILL.md) — Create or improve skills through isolated RED, GREEN, stability, and regression evaluations.
- [`refactor-design`](refactor-design/SKILL.md) — Review completed green implementations for structural risks and apply behavior-preserving refactors.
- [`implement-execplan`](implement-execplan/SKILL.md) — Create and execute self-contained, handoff-safe implementation plans for substantial work.

### Seed4J workflows

- [`seed4j-execplan-tdd`](seed4j-execplan-tdd/SKILL.md) — Combine an ExecPlan, behavior-focused TDD, and post-green design review for substantial `seed4j-cli` changes.
- [`seed4j-worktree-flow`](seed4j-worktree-flow/SKILL.md) — Create, audit, and clean up Seed4J CLI Git worktrees safely.

### Test-driven development

- [`tdd`](tdd/SKILL.md) — Run strict RED–GREEN–REFACTOR cycles with confirmation at each checkpoint.
- [`tdd-strict-cycle-confirmation`](tdd-strict-cycle-confirmation/SKILL.md) — Pause for explicit approval after every completed TDD cycle.
- [`tdd-strict-autonomous`](tdd-strict-autonomous/SKILL.md) — Preserve strict TDD while continuing automatically between exception gates.
- [`tdd-strict-autonomous-quiet`](tdd-strict-autonomous-quiet/SKILL.md) — Run autonomous TDD with deliberately sparse progress output.
- [`tdd-behavior-autonomous-quiet`](tdd-behavior-autonomous-quiet/SKILL.md) — Drive quiet autonomous TDD through observable behavior and stable public contracts.

### Git commits

- [`commit-staged-change`](commit-staged-change/SKILL.md) — Inspect and commit changes that are already staged using Conventional Commits.
- [`commit-the-changes`](commit-the-changes/SKILL.md) — Infer the repository’s commit convention, stage the intended changes, and create the commit.

## Installation and usage

Copy or symlink an individual skill directory into your Codex skills directory. Avoid replacing `.system`, which is managed by Codex.

Invoke a skill by name in your request:

```text
Use $develop-skill-with-evals to add a behavioral evaluation to my skill.
Use $refactor-design to review this completed green implementation.
Use $seed4j-worktree-flow to create a feature worktree.
```

Codex loads the selected `SKILL.md` and follows its progressive-disclosure links only when they are relevant to the task.

## Repository conventions

A skill always contains `SKILL.md` and may include:

- `agents/openai.yaml` for display metadata and the default invocation prompt;
- `references/` for detailed guidance loaded on demand;
- `scripts/` for deterministic automation;
- `evals/` for isolated cases, fixtures, and expected contracts used during skill development.

Evaluation fixtures and oracles belong under `evals/`, not in normal skill references. The local `.system` and `_temporary` directories are not part of the public skill catalog.

## Developing a skill

Use `$develop-skill-with-evals` for new skills and behavioral revisions. It composes the system `skill-creator` workflow with baseline RED, candidate GREEN, three-run stability, and full regression gates.

Typical validation commands include:

```bash
python3 -m unittest discover -s develop-skill-with-evals/scripts/tests -v
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" ./skill-name
python3 develop-skill-with-evals/scripts/run_skill_evals.py run --skill ./skill-name --all --source working-tree
git diff --check
```

Do not commit, push, or publish skill changes unless that action is explicitly requested.

## License

Licensed under the [Apache License 2.0](LICENSE).
