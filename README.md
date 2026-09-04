# Codex Skills

Reusable [Codex](https://openai.com/codex/) workflows for execution planning, documentation restructuring, behavior focused TDD, design review, Git commits, and Seed4J CLI maintenance and evaluation.

This repository keeps each workflow self contained, inspectable, and ready to install where Codex can discover it.

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

Repository contributors also need the separate project memory clone for ExecPlans, decisions, and lessons:

```bash
git clone https://github.com/renanfranca/codex-skills-ai-context.git _temporary/codex-skills-ai-context
```

The root `AGENTS.md` defines the required remote check and safety boundary.

## Skill catalog

### Planning and design

- [`restructure-documentation`](restructure-documentation/SKILL.md) — Audit and reorganize existing documentation around clear audiences, canonical sources, ordered concepts, and validated navigation.
- [`refactor-design`](refactor-design/SKILL.md) — Review completed green implementations for structural risks and apply behavior preserving refactors.
- [`implement-execplan`](implement-execplan/SKILL.md) — Create, maintain, and execute self contained living plans for substantial or handoff sensitive work.
- [`execplan-tdd`](execplan-tdd/SKILL.md) — Explicitly invoke the complete living ExecPlan, behavior TDD, public checkpoint, design review, documentation reconciliation, and final validation workflow.

### Seed4J workflows

- [`seed4j-worktree-flow`](seed4j-worktree-flow/SKILL.md) — Audit, create, and clean up Seed4J CLI feature worktrees while keeping the main worktree stable.
- [`seed4j-cli-model-runner`](seed4j-cli-model-runner/SKILL.md) — Create a specification-only public experiment and preserve sequential, configurable Codex model runs with deterministic audit evidence.
- [`seed4j-cli-model-evaluator`](seed4j-cli-model-evaluator/SKILL.md) — Score frozen Seed4J CLI experiment branches against one evidence-linked rubric and open a documentation-only evaluation PR.

### Test driven development

- [`tdd-behavior-autonomous-quiet`](tdd-behavior-autonomous-quiet/SKILL.md) — Run strict autonomous TDD quietly, with tests centered on observable behavior and stable public contracts.

### Git commits

- [`commit-staged-change`](commit-staged-change/SKILL.md) — Inspect and commit already staged changes safely with a Conventional Commits message aligned to repository conventions.
- [`commit-the-changes`](commit-the-changes/SKILL.md) — Infer the repository's commit style, stage the intended changes, and create a matching commit.

## Where to go next

- [Using Skills with Codex CLI](CODEX_CLI.md) covers discovery checks, TUI and `codex exec` workflows, task selection, sandbox behavior, resuming work, and troubleshooting.
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
