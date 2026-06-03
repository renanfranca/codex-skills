---
name: tdd-strict-autonomous-lean
description: Drive autonomous strict TDD with red-green-refactor while producing minimal user-facing output. Use for features, fixes, or refactors where tests must lead implementation, Codex should continue automatically, and routine cycle narration should be suppressed to save tokens.
---

# TDD Strict Autonomous Lean Output

Run strict autonomous TDD, one behavior per cycle. Keep most cycle detail internal. Speak only when the user needs information to follow risk, decisions, blockers, or final outcome.

## Core Loop

For each cycle:

1. Pick the smallest observable behavior.
2. Add `[TEST]` intent comments only when needed.
3. Replace only the next pending intent with one real test.
4. Predict the failure internally, then run the full relevant suite.
5. Implement the minimum code to pass the suite.
6. Refactor only while green and rerun tests if code changed.
7. Run a public-path checkpoint at least every two cycles.

Prefer two-step red when practical: missing API compile failure, then assertion failure with incomplete logic.

## Low-Output Contract

Default to silent execution between tool calls.

Do not narrate routine file reads, ordinary edits, every test command, every predicted failure, or every red/green/refactor transition.

Emit only:

- one short starting line naming the first behavior
- concise updates for gates, unexpected failures, architecture/API decisions, checkpoint failures, or meaningful refactors
- a final summary with changed files, tests run, and any residual risk

For successful routine cycles, track details internally. Do not print cycle logs unless the user asks or a gate is hit.

## Gates

Continue automatically through red, green, and refactor. Stop and ask only when:

- behavior is ambiguous
- the failure is unrelated or unexpected
- the same cycle fails green twice
- a minimal fix needs public API or architecture changes
- the public-path checkpoint fails
- the environment blocks tests

When stopping, state only: gate, evidence, smallest safe options.

## Labels

Use labels sparingly:

- `🔴 RED`: only for the first behavior or a non-routine red result
- `🌱 GREEN`: only when a cycle result matters to the user
- `🌀 REFACTOR`: only for a meaningful simplification

If a cycle log is needed, use one line:

`Cycle N | behavior | expected failure | red | green change | suite | checkpoint | refactor`

## Rules

- Start with one behavior; do not queue multiple tests.
- Test observable behavior, not internals.
- Use Given/When/Then structure in code, with blank lines when the language style allows it.
- Prefer simple real collaborators or nullable values over mocks.
- Run the full relevant suite every cycle.
- Add no production comments unless explicitly requested.
- Push back if asked to implement before red, batch behaviors, skip checkpoints, test internals, or use mocks without need.
- Keep final answers compact; include full logs only when requested or needed for diagnosis.
