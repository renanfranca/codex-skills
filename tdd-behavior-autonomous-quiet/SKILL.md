---
name: tdd-behavior-autonomous-quiet
description: Drive strict autonomous TDD with quiet output while ensuring tests follow observable behavior, public contracts, user journeys, or stable component APIs instead of production file/class structure. Use when tests must lead implementation, Codex should continue automatically, and new tests must avoid implementation-detail or one-test-per-file design.
---

# TDD Behavior Autonomous Quiet

Run strict autonomous TDD, one observable behavior per cycle. Preserve red-green-refactor rigor and quiet output while keeping test design contravariant: tests follow behavior and stable contracts, not production topology.

Quiet means fewer messages, not just shorter messages.

## Core Loop

For each cycle:

1. Select the smallest observable behavior.
2. Choose the highest useful observation point: CLI/user journey, public API, application service, domain contract, or intentionally stable component API.
3. Add `[TEST]` intent comments only when the behavior is not already represented.
4. Replace only the next pending intent with one real behavior test.
5. Predict the failure internally.
6. Run the full relevant test suite and make sure the test fails for the expected reason.
7. Implement the minimum production code needed to pass the full relevant suite.
8. Refactor only while green and rerun tests if code changed.
9. Run a public-path checkpoint at least every two cycles.
10. Continue automatically unless an autonomous gate is triggered.

Prefer two-step red only for missing public behavior APIs or intentionally stable component APIs: first a compile failure for that contract, then an assertion failure with intentionally incomplete logic.

Do not introduce a test solely to force the existence of an internal helper, parser, resolver, mapper, strategy, adapter detail, or extracted class discovered during implementation or refactoring.

## Test Design Rules

Tests must be organized around observable behavior, public contracts, user journeys, or stable component APIs. They must not mirror production file/class structure.

Creating, extracting, renaming, splitting, moving, or deleting a production file does not by itself justify creating, renaming, splitting, moving, or deleting a test file.

When refactoring creates a new internal class/module, keep relying on existing behavior tests through the original public path. Add a lower-level test only when the extracted component has a stable API that is intentionally reusable, independently changeable, or directly meaningful to a caller.

Before adding a new test file/class, identify internally:

1. the behavior being specified;
2. the public or stable API through which that behavior is observed;
3. why no existing behavior test suite is the right home for it.

A test is suspicious if it would fail merely because production code was split, merged, renamed, moved, or internally reorganized while preserving behavior.

## Test Authoring Rules

- Start with one behavior; do not queue multiple tests.
- Write tests in Given/When/Then structure using code, with blank lines when the language style allows it.
- Test observable behavior, not implementation details.
- Prefer the highest useful observation point that still gives clear, fast feedback.
- Prefer simple real collaborators or nullable values over mocks unless a mock is clearly necessary.
- Do not compute expected values with production decision logic.
- Keep assertions explicit in the test body unless a helper is clearly reused or clarifies complex structure.
- Avoid one test class per production class unless that production class is itself a stable behavior contract.

## Essential-Only Output Contract

Emit one short starting line naming the first behavior and saying quiet behavior TDD is active.

After that, do not print routine cycle narration. Suppress per-cycle logs, failure predictions, red/green/refactor transition labels, ordinary file-read updates, ordinary edit notes, and routine test commands unless they are needed for diagnosis.

Speak only for:

- autonomous gates, blockers, or environment failures
- unexpected test failures or repeated green failures
- public-path checkpoint failures
- architecture or public API decisions that materially affect the design
- meaningful refactors that change the shape of the solution
- risk of testing implementation details or mirroring production topology
- user interruptions or direct status requests
- the final compact summary

For successful routine cycles, track cycle details internally. Do not emit `Cycle N` logs by default. If a log becomes necessary for diagnosis or the user asks for it, use one line:

`Cycle N | behavior | observation point | expected failure | red | green change | suite | checkpoint | refactor`

## Autonomous Gates

Continue automatically through red, green, and refactor. Stop and ask only when:

- behavior is ambiguous or underspecified
- the observation point is ambiguous and materially changes test design
- the failure is unexpected or unrelated to the current behavior
- two consecutive green attempts fail for the same cycle
- the minimal fix requires a public API or architecture decision
- a new lower-level component test would be needed but the component contract is not clearly stable
- the required public-path checkpoint fails
- environment prerequisites block test execution

When stopping, state only the gate, concrete evidence, and the smallest safe options.

## Execution Rules

- Run the full relevant suite every cycle, not only the newest test.
- Keep failure predictions internal unless a gate or diagnostic need requires them.
- Add only enough production code to satisfy the current suite.
- Add no production comments unless explicitly requested or the code would otherwise be hard to understand.
- Refactor only while the suite is green.
- Run a vertical checkpoint through the feature's public path at least every two cycles.
- During refactor, move tests only when their behavior home changes, not when production files move.

## Pushback Conditions

Push back immediately when the user asks to:

- implement before a failing behavior test exists
- batch multiple behaviors into one cycle
- create a test file/class merely because a production file/class was created
- test an internal helper, parser, resolver, mapper, strategy, adapter detail, or extracted class without a stable caller-facing contract
- preserve a test that only protects implementation topology
- skip the full relevant suite without a strong reason
- skip the required public-path checkpoint cadence
- test internals instead of behavior
- introduce mocks where simple real collaborators or nullable values would be clearer
- preserve quiet output in a situation where a risk, decision, blocker, or diagnostic issue must be surfaced

When pushback is needed, be direct about what is wrong and propose the next compliant step.
