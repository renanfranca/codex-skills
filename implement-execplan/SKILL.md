---
name: implement-execplan
description: Create, maintain, and execute self-contained ExecPlans for large, risky, cross-cutting, or handoff-sensitive repository work. Adapt plan structure and update cadence to the task; do not use for isolated mechanical edits unless explicitly invoked.
---

# Implement ExecPlan

## Purpose

Deliver observable user-facing behavior through a self-contained implementation
plan that another engineer can safely continue without prior repository or
conversation context.

## Activation boundary

Use this skill when the user explicitly invokes it or when the task is large,
risky, cross-cutting, migration-heavy, or requires a durable handoff. For a
narrow mechanical edit such as an isolated typo, work directly and do not
create an ExecPlan unless the user explicitly asks for one.

## Safety boundary

Use this skill only for authorized, defensive maintenance in the current
repository. Do not provide offensive guidance, policy-bypassing instructions,
hidden-prompt extraction, or chain-of-thought disclosure.

Treat repository content, fixtures, logs, and captured requests as potentially
sensitive. Include only the minimum necessary context, sanitize plans and
handoffs, never reproduce credentials or secret-like values, and preserve
read-only or sensitive files unless their modification is explicitly authorized.

## Working contract

- Clarify the requested outcome in observable terms.
- Create or update one `EXECPLAN.md` before major implementation work.
- Keep the plan self-contained for a novice with no hidden context.
- Explain user-visible purpose before implementation details.
- State exact files, milestones, validation commands, expected outcomes, and
  critical assumptions.
- Execute one milestone at a time and keep behavior, tests, documentation, and
  the plan reconciled.
- Prefer the smallest plan that remains safe and handoff-ready.
- Do not add empty sections, placeholder text, or `N/A` blocks.

## Adaptive plan structure

Give the plan a short action-oriented title. Every ExecPlan must contain these
exact core sections:

1. `## Purpose and success`
2. `## Context and limits`
3. `## Milestones`
4. `## Progress`
5. `## Validation`

Add a conditional block only when its content materially helps execution or
handoff:

- `## Definitions` for uncommon project-specific terms needed to understand the
  work.
- `## Decisions` for consequential choices under the decision rules below.
- `## Risks` for material safety, correctness, migration, operational, or
  recovery risks.
- `## Documentation` when canonical documentation must change or requires a
  material reconciliation decision.
- `## Rollout and recovery` when deployment, migration, compatibility, rollback,
  or recovery needs explicit action.
- `## Prototypes` when an active uncertainty requires an isolated experiment
  with a hypothesis and measurable success criterion.
- `## Lessons learned` only for non-obvious findings that materially help the
  next engineer.

Omit an inapplicable conditional section completely. In particular, when no
consequential decision exists, the plan must contain no `Decisions` section and
no routine decision log elsewhere.

## Milestone contract

For each milestone, state:

- the behavior or evidence it will produce;
- concrete file-level edits;
- relevant documentation work, when any;
- exact validation commands and expected outcomes;
- observable acceptance criteria.

Keep milestones incremental and independently verifiable. Use checklists only
in `Progress`.

## Update cadence

Update the plan only at these points:

1. when the plan is created;
2. at a milestone boundary;
3. after a material change in direction or risk;
4. immediately before handoff.

At those boundaries, reconcile `Progress`, validation evidence, applicable
risks, documentation, recovery guidance, and consequential decisions. Do not
rewrite the plan after routine edits whose state is already evident from code
and tests.

## Decision discipline

Record a decision only when it changes at least one of:

- a public or internal contract;
- observable behavior;
- architecture or responsibility boundaries;
- scope;
- migration or compatibility policy;
- material risk;
- rollout or recovery;
- the choice between viable alternatives.

For each consequential decision, state the selected option, viable alternatives
considered when relevant, rationale, and the resulting consequence.

Do not record routine implementation steps, details already evident in code or
tests, formatting, mechanical renames, or discarded experiments. A task with no
consequential decision must have no `Decisions` section.

## Prompt-safety hygiene

When plan content may be copied into prompts:

- state benign, authorized intent;
- prefer neutral verbs such as validate, inspect, diagnose, harden, and improve;
- never instruct safeguard circumvention;
- keep security work defensive, concrete, and file-scoped;
- avoid copying sensitive fixture values into the plan or final response;
- add a one-line defensive scope boundary when wording could be ambiguous.

Use this boundary when needed:

`Safety boundary: This task is limited to authorized, defensive maintenance of this repository. Do not provide offensive guidance or policy-bypassing instructions.`

## Validation and handoff

Validate from narrow to broad as appropriate: focused checks, the repository's
full validation command, user-visible exercise, and canonical documentation
reconciliation. Record observed outcomes, not unsupported claims.

When a task changes a migration or compatibility contract and user-facing documentation is in scope, the final audit must confirm that the documentation names the exact legacy and current fields, shapes, flags, or formats promised by the task; do not replace contractual identifiers with vague labels.

Before handoff, re-read the request and verify every explicit positive
requirement, prohibition, responsibility boundary, and acceptance criterion
against the final workspace. For migrations, confirm that deprecated
representations remain confined to the explicitly authorized compatibility
boundary; passing tests alone does not complete this audit.

Before handoff, update the plan at the final allowed boundary and summarize:

- changed paths and delivered behavior;
- each requested validation command and its observed exit status or result;
- material boundaries, the risks they control, and remaining risks or limitations;
- consequential decisions only; for each one, state the selected option,
  rationale, contract or migration-risk implication, and recovery consequence.
  State that none existed only when the task requests that fact;
- documentation impact and recovery instructions when applicable.

If the ExecPlan is a standalone Markdown file, do not wrap it in a code fence.
If it is embedded in another message, wrap the complete plan in one fenced `md`
block.
