---
name: plan-behavioral-acceptance
description: Deepen behavioral acceptance criteria during Codex planning or ExecPlan preparation, grounding expectations in repository sources and mapping them to planned verification and evidence. Complement implement-execplan for acceptance quality; do not use to implement changes or report execution as complete.
---

# Plan Behavioral Acceptance

Deliver a plan with verifiable behavioral expectations and the evidence an
executor must obtain. Work in the existing planning document; reuse repository
documents, tests, and records. When working with an ExecPlan,
[implement-execplan](../implement-execplan/SKILL.md) owns its structure and
maintenance. Enrich its milestones and validation without imposing another
template or creating a separate acceptance tracker.

## Ground the expectations

Inspect the relevant requirements, code, tests, and documentation before
formulating criteria. Identify the public or stable observation point and cite
the source that establishes each expected result. Current implementation and
passing tests are evidence to inspect, not sufficient authority for the intended
behavior.

Write concrete examples with context, action, and observable result, including
exact values, errors, or side effects when they determine acceptance. For
example: with one item remaining, reserving it succeeds and makes availability
zero; another reservation is rejected and availability remains zero. Examine
transitions, boundaries, repeated actions, and simultaneous events only when
they affect the requested behavior. For simultaneous events, specify allowed
outcomes and invariants without inventing an ordering guarantee.

When behavior depends on state or time, specify how it starts, persists, and
ends. Include the first observable step after the real triggering event and
the event immediately after a relevant boundary when either can change the
result. Preparing an intermediate state alone may miss creation or transition
errors.

For historical preservation or compatibility, verify the expectation against
the original source at the relevant revision, not merely the current code or
test. Record its location/revision and any approved exception with the source
of approval. Resolve conflicting sources and ambiguities that change the
expected result through documented decisions or focused user clarification
before finishing the plan. If unresolved, keep planning incomplete and state
the missing decision; do not silently choose an expectation.

## Check expectation and proof separately

For each criterion, answer two questions:

1. **Is the expectation correct?** Check the requested behavior and applicable
   source contract, including historical guarantees and approved exceptions.
2. **Would the verification demonstrate it?** Inspect the scenario, observation
   point, and assertions. Confirm they distinguish the expected result from a
   plausible incorrect result, including relevant transitions. A green test
   with the wrong expected value or insufficient assertions proves neither.

Check that the scenario's initial conditions make a plausible incorrect
behavior observable. Another condition must not prevent the consequence and
make the assertion pass regardless of the behavior under test. For example,
to demonstrate that interception prevents damage, use a target that could
otherwise take damage.

Reuse a test or record that already demonstrates the criterion; do not add a
duplicate. If coverage is insufficient, describe the missing behavioral check
through a public or stable path for the executor to add. Avoid checks tied to
internal topology or expected values derived from production decision logic.

## Prepare the execution handoff

Associate every criterion with its source, context/action/result example,
planned verification (existing test or record, exact command or manual
procedure), expected evidence, and any coverage gap. Keep these associations
in the plan's existing acceptance and validation content.

Write explicit obligations into the plan for the executor, before delivery:

- Recheck expectation correctness against the cited sources and approved
  exceptions, separately from checking whether the tests demonstrate it.
- Perform the planned verification and record evidence obtained for each
  criterion: command/procedure, observed result, and relevant assertion or
  artifact location. A suite's success alone does not establish every criterion.
- Record missing coverage, failed checks, and unverified criteria before
  delivery; do not present a criterion with an unresolved gap as satisfied.

Label planned checks and expected evidence separately from observed results.
Read-only checks performed during planning may be recorded as observations
with their command and result, but do not establish future implementation
success. This skill prepares acceptance; it does not execute the implementation.

## Optional benefit assessment

Only when requested, use existing plan or review records over two or three
planning/delivery cycles to record findings before and after delivery, their
classification (incorrect expectation, verification gap, missing behavioral
case, or another supported category), and additional effort. Identify estimates
as estimates. Do not attribute savings to the skill without sufficient
comparison of comparable work. Report recurring difficulties supported by
subsequent use as candidates for later skill changes, keeping additions
proportional to observed benefit.
