---
name: implement-execplan
description: Create, maintain, and execute fully self-contained Execution Plans (ExecPlans) as living documents. Use when a task is large, risky, cross-cutting, or requires handoff-safe execution with explicit milestones, file-level edits, concrete validation commands, and continuous updates to Progress, Decisions, Risks, and Lessons Learned.
---

# Implement ExecPlan

## Purpose

Deliver user-visible behavior through a complete, traceable implementation guided by an ExecPlan that another engineer can continue without prior repository context.

## Safety Boundary

Use this skill only for authorized, defensive maintenance in the current repository.
Do not provide offensive guidance, policy-bypassing instructions, hidden-prompt extraction, or chain-of-thought disclosure.

## Workflow

1. Clarify the requested outcome in observable terms.
2. Write or update one ExecPlan document before major implementation work.
3. Execute one milestone at a time.
4. Keep the ExecPlan current while implementing.
5. Validate with concrete commands and expected outcomes.
6. Finalize with rollout/recovery guidance and lessons learned.

## Non-Negotiable Requirements

- Keep the ExecPlan fully self-contained.
- Treat the ExecPlan as a living document and update it continuously.
- Write for a novice with no prior repository knowledge.
- Produce observable behavior, not only code movement.
- Define uncommon, project-specific, or newly introduced terms inline.
- Explain why the change matters from a user perspective before implementation details.
- Specify exact files to edit and exact commands to run.
- Restate all critical assumptions explicitly.
- Avoid references to hidden context, unpublished notes, or external blog posts.
- If the plan builds on another committed ExecPlan, reference it; otherwise include all context directly.

## Prompt-Safety Hygiene

When writing content that may be copied into prompts:

- State benign intent explicitly (for example: refactor, test, diagnose, harden, improve reliability).
- Prefer neutral verbs (validate, inspect, simulate, reproduce) over ambiguous attack-like phrasing.
- Never instruct policy bypassing or safeguard circumvention.
- Keep security-related tasks explicitly defensive and authorized.
- Include only the minimum sensitive context needed to implement and verify.
- Keep instructions concrete and file-scoped.
- Add a one-line scope boundary when wording could be interpreted multiple ways.

Recommended boundary line for ambiguous/high-risk tasks:

`Safety boundary: This task is limited to authorized, defensive maintenance of this repository. Do not provide offensive guidance or policy-bypassing instructions.`

## Formatting Rules for ExecPlans

- Write in plain prose with short, clear sections.
- Use checklists only in `Progress`.
- If embedded in another message, wrap the full ExecPlan in one fenced `md` block.
- If saved as a standalone `.md` file, do not wrap with triple backticks.

## Required ExecPlan Sections

Every ExecPlan must contain these sections:

1. Title (short and action-oriented)
2. Purpose / Big Picture
3. Scope
4. Definitions
5. Existing Context
6. Desired End State
7. Milestones
8. Progress
9. Decisions
10. Risks and Mitigations
11. Validation Strategy
12. Rollout and Recovery
13. Lessons Learned

## Milestone Contract

For each milestone:

- State scope and resulting behavior.
- List concrete file-level edits.
- List exact validation commands.
- Define observable acceptance criteria.

Keep milestones small, incremental, and independently verifiable.

## Living Update Discipline

Update the plan during execution, not only at the end:

- Update `Progress` checkboxes as soon as status changes.
- Record every meaningful decision with rationale.
- Capture surprises immediately in `Lessons Learned`.
- Revise `Risks and Mitigations` whenever risk profile changes.
- If direction changes, update the plan before continuing implementation.

## Prototyping and Parallel Approaches

When uncertainty is high:

- Add an explicit `Prototype` milestone.
- State the hypothesis and measurable success criteria.
- Keep prototype changes isolated.
- Remove prototype code before completion unless intentionally promoted.

When comparing approaches in parallel:

- Document each option and trade-offs.
- Describe validation evidence per option.
- Record the chosen approach in `Decisions`.
- Remove or archive rejected code before finalizing.

## Validation Strategy

Run validation from narrow to broad:

1. Run focused checks for changed modules or packages.
2. Run the repository's full validation command.
3. Manually exercise user-visible behavior when applicable.
4. Confirm acceptance criteria for every milestone.

## ExecPlan Skeleton (Copy and Fill)

# <Short, action-oriented title>

This ExecPlan is a living document. Keep `Progress`, `Decisions`, `Risks`, and `Lessons Learned` up to date as work advances.

## Purpose / Big Picture

Explain in 2-4 sentences what user-visible capability is delivered and how to observe it working.

## Scope

State in-scope and out-of-scope items clearly.

## Definitions

Define project-specific terms, modules, flags, or protocols needed to understand this plan.

## Existing Context

Describe the current behavior and architecture relevant to this change. Reference specific files and classes.

## Desired End State

Describe expected behavior and code state after completion.

## Milestones

### Milestone 1 - <Name>

#### Goal

Describe what this milestone achieves.

#### Changes

- [ ] File-level edits with exact paths and intent.
- [ ] Data model or type updates.
- [ ] API, CLI, or UX behavior updates.

#### Validation

- [ ] Command: `<exact command>`
- [ ] Expected result: `<observable outcome>`

#### Acceptance Criteria

- [ ] Behavior is visible through a concrete scenario.
- [ ] Tests prove expected behavior.

### Milestone 2 - <Name>

Repeat the same structure.

## Progress

Use a flat checkbox list and update continuously.

- [ ] Milestone 1 started
- [ ] Milestone 1 completed
- [ ] Milestone 2 started
- [ ] Milestone 2 completed

## Decisions

Record decisions as they happen.

- Decision: <what>
  Rationale: <why>
  Date/Author: <YYYY-MM-DD / name>

## Risks and Mitigations

List meaningful risks and the mitigation for each.

- Risk: <description>
  Mitigation: <how to reduce or monitor>

## Validation Strategy

1. Run targeted tests relevant to modified packages.
2. Run the repository full validation command.
3. Manually exercise changed user-visible behavior when applicable.

## Rollout and Recovery

Explain how to deploy or release safely and how to revert if needed.

## Lessons Learned

Capture non-obvious findings that help the next engineer.
