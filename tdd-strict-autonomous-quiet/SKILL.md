---
name: tdd-strict-autonomous-quiet
description: Drive strict autonomous TDD with red-green-refactor while deliberately reducing message frequency, not merely message length. Use when tests must lead implementation, Codex should continue automatically, and user-facing output should appear only for essential risks, decisions, blockers, meaningful refactors, checkpoint failures, or the final compact summary.
---

# TDD Strict Autonomous Quiet

Run strict autonomous TDD, one observable behavior per cycle. Preserve the rigor of red-green-refactor while keeping routine cycle work internal. Quiet means fewer messages, not just shorter messages.

## Core Loop

For each cycle:

1. Select the smallest observable behavior.
2. Add `[TEST]` intent comments only when the behavior is not already represented.
3. Replace only the next pending intent with one real test.
4. Predict the failure internally.
5. Run the full relevant test suite and make sure the test fails for the expected reason.
6. Implement the minimum production code needed to pass the full relevant suite.
7. Refactor only while green and rerun tests if code changed.
8. Run a public-path checkpoint at least every two cycles.
9. Continue automatically unless an autonomous gate is triggered.

Prefer two-step red when practical: first a missing API compile failure, then an assertion failure with intentionally incomplete logic.

## Essential-Only Output Contract

Emit one short starting line naming the first behavior and saying quiet TDD is active.

After that, do not print routine cycle narration. Suppress per-cycle logs, failure predictions, red/green/refactor transition labels, ordinary file-read updates, ordinary edit notes, and routine test commands unless they are needed for diagnosis.

Speak only for:

- autonomous gates, blockers, or environment failures
- unexpected test failures or repeated green failures
- public-path checkpoint failures
- architecture or public API decisions that materially affect the design
- meaningful refactors that change the shape of the solution
- user interruptions or direct status requests
- the final compact summary

For successful routine cycles, track cycle details internally. Do not emit `Cycle N` logs by default. If a log becomes necessary for diagnosis or the user asks for it, use one line:

`Cycle N | behavior | expected failure | red | green change | suite | checkpoint | refactor`

## Autonomous Gates

Continue automatically through red, green, and refactor. Stop and ask only when:

- behavior is ambiguous or underspecified
- the failure is unexpected or unrelated to the current behavior
- two consecutive green attempts fail for the same cycle
- the minimal fix requires a public API or architecture decision
- the required public-path checkpoint fails
- environment prerequisites block test execution

When stopping, state only the gate, concrete evidence, and the smallest safe options.

## Test Authoring Rules

- Start with one behavior; do not queue multiple tests.
- Write tests in Given/When/Then structure using code, with blank lines when the language style allows it.
- Test observable behavior, not implementation details.
- Prefer simple real collaborators or nullable values over mocks unless a mock is clearly necessary.
- Do not compute expected values with production decision logic.
- Keep assertions explicit in the test body unless a helper is clearly reused or clarifies complex structure.

## Execution Rules

- Run the full relevant suite every cycle, not only the newest test.
- Keep failure predictions internal unless a gate or diagnostic need requires them.
- Add only enough production code to satisfy the current suite.
- Add no production comments unless explicitly requested or the code would otherwise be hard to understand.
- Refactor only while the suite is green.
- Run a vertical checkpoint through the feature's public path at least every two cycles.

## Pushback Conditions

Push back immediately when the user asks to:

- implement before a failing test exists
- batch multiple behaviors into one cycle
- skip the full relevant suite without a strong reason
- skip the required public-path checkpoint cadence
- test internals instead of behavior
- introduce mocks where simple real collaborators or nullable values would be clearer
- preserve quiet output in a situation where a risk, decision, blocker, or diagnostic issue must be surfaced

When pushback is needed, be direct about what is wrong and propose the next compliant step.
