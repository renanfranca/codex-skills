# Codex Skills

Reusable [Codex](https://openai.com/codex/) workflows for skill development, execution planning, behavior focused TDD, design review, Git commits, and Seed4J CLI maintenance.

This repository keeps each workflow self contained, inspectable, and ready to install where Codex can discover it.

Browse the skills and their archived evaluation evidence at [renanfranca.github.io/codex-skills](https://renanfranca.github.io/codex-skills/).

## What is a Codex skill?

A Codex skill is a reusable workflow stored in a directory with a required `SKILL.md`. That file defines the skill's name, when Codex should use it, and the instructions to follow. A skill may also include references, scripts, templates, and optional `agents/openai.yaml` interface metadata.

Codex first sees each skill's name and description, then loads its full instructions and relevant resources when needed. You can invoke a skill explicitly with `$skill-name`, or Codex can select it when your request matches its description. See the official [Build skills documentation](https://learn.chatgpt.com/docs/build-skills) for the complete model.

## Quick start

Clone the repository and copy one skill into the user discovery location:

```bash
git clone https://github.com/renanfranca/codex-skills.git /path/to/codex-skills
mkdir -p "$HOME/.agents/skills"
cp -R /path/to/codex-skills/refactor-design "$HOME/.agents/skills/"
```

For a skill shared by one project, copy it to `<repository>/.agents/skills` instead. Then invoke the installed skill directly:

```text
Use $refactor-design to review this completed green change. Limit work to the changed scope, preserve its public contract, apply only the smallest justified refactor, rerun the relevant suite and public checkpoint, and pause at any exception gate.
```

## Skill catalog

### Skill development and design

- [`develop-skill-with-evals`](develop-skill-with-evals/SKILL.md) — Create or improve Codex skills with impact aware evaluation gates, durable evidence, stability checks, and cumulative cost controls.
- [`restructure-documentation`](restructure-documentation/SKILL.md) — Audit and reorganize existing documentation around clear audiences, canonical sources, ordered concepts, and validated navigation.
- [`refactor-design`](refactor-design/SKILL.md) — Review completed green implementations for structural risks and apply behavior preserving refactors.
- [`implement-execplan`](implement-execplan/SKILL.md) — Create, maintain, and execute self contained living plans for substantial or handoff sensitive work.

### Seed4J workflows

- [`seed4j-execplan-tdd`](seed4j-execplan-tdd/SKILL.md) — Combine a living ExecPlan, behavior focused TDD, and post GREEN design review for substantial `seed4j-cli` changes.
- [`seed4j-worktree-flow`](seed4j-worktree-flow/SKILL.md) — Audit, create, and clean up Seed4J CLI feature worktrees while keeping the main worktree stable.

### Test driven development

- [`tdd-behavior-autonomous-quiet`](tdd-behavior-autonomous-quiet/SKILL.md) — Run strict autonomous TDD quietly, with tests centered on observable behavior and stable public contracts.

### Git commits

- [`commit-staged-change`](commit-staged-change/SKILL.md) — Inspect and commit already staged changes safely with a Conventional Commits message aligned to repository conventions.
- [`commit-the-changes`](commit-the-changes/SKILL.md) — Infer the repository's commit style, stage the intended changes, and create a matching commit.

## Where to go next

- [Using Skills with Codex CLI](CODEX_CLI.md) covers discovery checks, TUI and `codex exec` workflows, task selection, sandbox behavior, resuming work, and troubleshooting.
- [Evaluating Codex Skills](EVALUATIONS.md) explains evaluation concepts, evidence, supervision, and promotion.
- [Repository Guidelines](AGENTS.md) defines contribution conventions, validation expectations, and repository safety.

<details>
<summary>Disabled skills retained for historical compatibility</summary>

These source directories preserve references and links from earlier material. They are disabled in the local Codex configuration and are not part of the active skill catalog:

- [`tdd`](tdd/SKILL.md)
- [`tdd-strict-cycle-confirmation`](tdd-strict-cycle-confirmation/SKILL.md)
- [`tdd-strict-autonomous`](tdd-strict-autonomous/SKILL.md)
- [`tdd-strict-autonomous-quiet`](tdd-strict-autonomous-quiet/SKILL.md)

</details>

## License

Licensed under the [Apache License 2.0](LICENSE).
