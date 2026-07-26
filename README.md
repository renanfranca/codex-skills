# Codex Skills

Personal [Codex](https://openai.com/codex/) skills for test-driven development, design review, execution planning, Git workflows, and Seed4J CLI maintenance.

Each skill directory at the repository root is self-contained. For portable Codex CLI discovery, copy or symlink the skills you need into `$HOME/.agents/skills` for personal use or `<repository>/.agents/skills` for use within a repository. Then invoke one explicitly with `$skill-name`. Skills may also support implicit activation, but explicit invocation is the most reliable entry point.

## Skill catalog

### Skill development and design

- [`develop-skill-with-evals`](develop-skill-with-evals/SKILL.md) — Create or improve skills through auditable runtime declarations and proportional RED, GREEN, stability, and regression gates.
- [`refactor-design`](refactor-design/SKILL.md) — Review completed green implementations for structural risks and apply behavior-preserving refactors.
- [`implement-execplan`](implement-execplan/SKILL.md) — Create and execute self-contained implementation plans that are safe for handoff during substantial work.

### Seed4J workflows

- [`seed4j-execplan-tdd`](seed4j-execplan-tdd/SKILL.md) — Combine an ExecPlan, TDD focused on behavior, and design review after GREEN for substantial `seed4j-cli` changes.
- [`seed4j-worktree-flow`](seed4j-worktree-flow/SKILL.md) — Create, audit, and clean up Seed4J CLI Git worktrees safely.

### Test-driven development

- [`tdd-behavior-autonomous-quiet`](tdd-behavior-autonomous-quiet/SKILL.md) — Drive quiet autonomous TDD through observable behavior and stable public contracts.

### Git commits

- [`commit-staged-change`](commit-staged-change/SKILL.md) — Inspect and commit changes that are already staged using Conventional Commits.
- [`commit-the-changes`](commit-the-changes/SKILL.md) — Infer the repository’s commit convention, stage the intended changes, and create the commit.

### Disabled skills

These source directories remain available to preserve historical references and links from published articles, but the skills are disabled in the local Codex configuration and are unavailable for explicit or implicit invocation:

- [`tdd`](tdd/SKILL.md)
- [`tdd-strict-cycle-confirmation`](tdd-strict-cycle-confirmation/SKILL.md)
- [`tdd-strict-autonomous`](tdd-strict-autonomous/SKILL.md)
- [`tdd-strict-autonomous-quiet`](tdd-strict-autonomous-quiet/SKILL.md)

## Installation and usage

Copy or symlink an individual skill directory into a documented Codex skill discovery location. This source repository can remain at `/home/renanfranca/.codex/skills`; it does not need to be moved. Avoid replacing `.system`, which is managed by Codex, and avoid installing duplicate skills with the same `name`.

Invoke a skill by name in your request:

```text
Use $develop-skill-with-evals to add a behavioral evaluation to my skill.
Use $refactor-design to review this completed green implementation.
Use $seed4j-worktree-flow to create a feature worktree.
```

Codex loads the selected `SKILL.md` and follows its links for progressive disclosure only when they are relevant to the task.

## Using Codex CLI

See [Using Skills with Codex CLI](CODEX_CLI.md) for the practical cookbook: verify installation, run one or every eval suite, create and improve skills through prompts, automate safe runs from a single command, and invoke every skill in this repository.

## Repository conventions

A skill always contains `SKILL.md` and may include:

- `agents/openai.yaml` for display metadata and the default invocation prompt;
- `references/` for detailed guidance loaded on demand;
- `scripts/` for deterministic automation;
- `evals/` for isolated cases, fixtures, and expected contracts used during skill development.

Evaluation fixtures and oracles belong under `evals/`, not in normal skill references. The local `.system` and `_temporary` directories are not part of the public skill catalog.

## Skill evaluations

See [Evaluating Codex Skills](EVALUATIONS.md) for the complete guide to suites, isolated fixtures, hidden mechanical oracles, diagnostic probes, cumulative campaign budgets, promotion gates, and the real `refactor-design` examples. Executed evaluations can now persist canonical JSON plus deterministic Markdown, retain normalized usage telemetry, apply an optional dated API pricing reference, regenerate presentation, and compare model reports without another model session; see [Durable evidence and pricing](EVALUATIONS.md#durable-evidence-and-pricing), [Economic runtime policy](EVALUATIONS.md#economic-runtime-policy), and the [copyable CLI recipes](CODEX_CLI.md#persist-evidence-with-dated-pricing).

## Developing a skill

Use `$develop-skill-with-evals` for new skills and behavioral revisions. It composes the system `skill-creator` workflow with an optional one pass diagnostic, baseline RED, three stable candidate GREEN results, and regression proportional to the classified impact. Cross cutting promotion runs regressions after GREEN 1 so a defect blocks before GREEN 2 and 3. Model-backed workflows declare executor and judge runtimes explicitly, report structured token usage, and enforce both operation and cumulative campaign session limits.

Follow the [evaluation guide](EVALUATIONS.md) when adding a suite to another skill or interpreting runner reports and blocking statuses.

Typical validation commands include:

```bash
python3 -m unittest discover -s develop-skill-with-evals/scripts/tests -v
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" ./skill-name
python3 develop-skill-with-evals/scripts/run_skill_evals.py plan --skill ./candidate-skill --baseline /tmp/baseline-skill --impact scoped --case changed-case --model <executor-model> --reasoning-effort <effort> --judge-model <judge-model> --judge-reasoning-effort <effort>
git diff --check
```

Do not commit, push, or publish skill changes unless that action is explicitly requested.

## License

Licensed under the [Apache License 2.0](LICENSE).
