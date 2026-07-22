---
name: refactor-design
description: Review completed green implementations for structural design risks and apply behavior-preserving refactors with quiet output. Use after behavior-focused TDD or when a feature is functionally complete and Codex should inspect temporal coupling, hidden mutable state, mixed responsibilities, fragile representations, or architecture leakage before final validation. Do not use to discover new behavior or change public contracts.
---

# Refactor Design

Consolidate the design that emerged from a completed implementation without changing observable behavior.

## Enforce the entry gate

Before reviewing design, confirm all of the following:

- the requested behavior is complete;
- the relevant test suite is green;
- a checkpoint through the public path is green;
- the current milestone has no pending behavior.

Return to the applicable behavior-focused TDD workflow if any condition fails. Do not use this skill to discover or implement missing behavior.

## Set the review scope

Inspect the changed files, the contracts crossed by the change, and only adjacent code that received new responsibility. Do not review the repository indiscriminately or broaden the task to unrelated cleanup.

## Load the review references

Always read `references/design-review-rubric.md` completely before classifying findings.

Also read `references/java-spring-hexagonal.md` completely when the reviewed scope uses Java, Spring, or hexagonal architecture. Do not load that reference for unrelated technology stacks.

## Classify findings before changing code

Classify each candidate as one of:

- **Defect:** the design can already produce incorrect observable behavior.
- **Design risk:** behavior is correct today but depends on a fragile structural condition.
- **Maintainability opportunity:** the improvement is useful but not necessary for the current task.
- **No action:** evidence, benefit, scope, or confidence does not justify a change.

For every actionable finding, identify the inadequate dependency, state, responsibility, or representation; explain the concrete risk; consider false positives and cost; and show why the proposed refactor removes that risk. Do not introduce patterns, abstractions, value objects, or extracted classes merely because a checklist suggests them.

## Refactor while preserving behavior

Handle one coherent finding at a time:

1. State the structural risk and the behavior that must remain unchanged.
2. Reuse the existing behavior tests and public-path checkpoint as protection.
3. Apply the smallest coherent structural change that removes the demonstrated risk.
4. Run the relevant suite after each significant change.
5. Repeat the public-path checkpoint.
6. Continue automatically while the behavior stays green and the change remains in scope.

Do not add tests for extracted classes, collaborator order, framework wiring, or internal topology. Add or change a behavior test only through the TDD workflow when a missing or incorrect observable behavior is discovered.

## Stop at exception gates

Pause the review and report the gate when any of these occurs:

- behavior is missing or incorrect;
- the refactor requires a public API or contract change;
- a material, unplanned architecture decision is required;
- existing tests cannot protect the behavior being refactored;
- the work would materially expand the authorized scope;
- the same refactoring attempt fails twice consecutively.

Return to behavior-focused TDD for missing behavior. Ask for direction when new authority or a material public or architectural decision is required.

## Keep output quiet

Emit one short opening line. Suppress routine narration. Communicate only exception gates, concrete risks needing user judgment, meaningful structural changes, validation failures, and the final compact summary.

## Consolidate learning without self-modification

After validation, classify newly observed heuristics as contextual, repository-specific, or generally reusable.

- Do not record contextual findings.
- Report repository-specific findings for possible project documentation or executable enforcement.
- Report generally reusable findings as candidates for a separate, explicit skill-evolution task.
- Never modify this `SKILL.md`, its description, or files under `references/` as a side effect of an ordinary design review.

Evolve the skill only in an explicitly authorized task against its writable source repository, with a visible diff, validation, and a fresh forward test.
