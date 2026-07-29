---
name: execplan-tdd
description: Guide repository code changes through a self contained living ExecPlan, behavior focused quiet TDD, a green public checkpoint, post GREEN design review, documentation reconciliation, and final validation. Use when Codex is asked to plan, implement, execute, or continue a software code change and the repository instructions declare a complete workflow profile. Do not use for skill development, documentation only changes, or repositories without the required profile.
---

# ExecPlan TDD

Deliver authorized code behavior through the repository's declared workflow. Keep output quiet according to the loaded TDD and design review skills, while keeping the ExecPlan current.

## Enforce the scope and profile gate

Before creating a plan or editing any file:

1. Read every applicable repository instruction file, including nested instructions for the changed scope.
2. Confirm that the request changes software code. For a documentation only task, do not use this workflow; follow the repository's documentation guidance instead.
3. Extract all required profile fields:
   - exact ExecPlan destination and naming convention;
   - relevant test suite for each TDD cycle;
   - checkpoint through a public or consumer facing path;
   - complete final validation commands;
   - canonical documentation sources for the changed scope.
4. Confirm that each field is explicit, locally applicable, and executable in the current environment.

If any field is missing, ambiguous, contradictory, or unavailable, stop without creating or updating an ExecPlan and without editing tests, code, configuration, generated output, or documentation. Report the exact missing profile fields and request repository level clarification. Never invent commands, sources, destinations, or fallback locations.

## Create or resume the living plan

Load and follow `implement-execplan` before creating or updating the plan.

- Use exactly the destination and naming convention from the repository profile.
- Keep the plan self contained even when the repository also provides historical memory.
- Record the relevant suite, public checkpoint, final validation, and canonical documentation sources.
- Keep `Progress`, `Decisions`, `Risks and Mitigations`, `Documentation Impact`, validation evidence, scope changes, and `Lessons Learned` current throughout the work.
- Start or resume the smallest milestone that can deliver observable behavior. A small change may use one milestone.

Do not treat plan creation as authorization to commit, push, publish, deploy, clone repositories, or use an undeclared location.

## Implement through behavior TDD

Load and follow `tdd-behavior-autonomous-quiet` before implementation.

For each observable behavior:

1. Add one behavior focused test through the highest useful stable observation point.
2. Run the profile's full relevant suite and confirm the expected RED.
3. Implement only enough code for GREEN.
4. Rerun the full relevant suite.
5. Run the declared public checkpoint at the cadence required by the TDD skill and at milestone completion.
6. Update the ExecPlan with concrete progress, decisions, risks, and validation evidence.

Do not edit disposable generated projections. Change their canonical source and regenerate only through repository commands when the profile requires it.

## Enforce the post GREEN design gate

Before design review, confirm:

- every behavior in the current milestone is complete;
- the relevant suite is green;
- the declared public checkpoint is green;
- no milestone behavior remains pending.

Load and follow `refactor-design` only after all four conditions hold. Keep the ExecPlan current during the review.

If design review discovers missing or incorrect observable behavior, stop that review and return to `tdd-behavior-autonomous-quiet`. Restore the relevant suite and public checkpoint to GREEN before restarting the design gate. Apply behavior preserving refactors only within the authorized scope and rerun both gates after material changes.

## Reconcile documentation

After code and design are green, inspect every canonical documentation source named by the repository profile.

- Update sources whose public behavior, configuration, examples, operations, or contributor guidance changed.
- For each source left unchanged, record a concrete justification in `Documentation Impact`.
- Confirm that generated documentation remains a projection of canonical sources and was not edited directly.

Documentation reconciliation is incomplete when a canonical source is silently ignored.

## Run final validation

Run every final validation command declared by the repository, in its required order, only after TDD, the public checkpoint, design review, and documentation reconciliation are complete.

Record exact commands and outcomes in the ExecPlan. On failure, return to the applicable gate, keep the plan current, and rerun the complete final validation after the correction. Finish only when every milestone acceptance criterion and final command is green.
