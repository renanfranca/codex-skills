---
name: tdd-strict-autonomous
description: Drive strict test-driven development in autonomous mode using red-green-refactor without per-cycle user confirmations. Use when Codex should preserve TDD rigor for new features, bug fixes, refactors, or collaborative sessions while continuing automatically and pausing only on explicit exception gates.
---

# TDD Strict Autonomous

Guide the session as an autonomous TDD coach. Keep one behavior per cycle, force design to emerge from tests, and continue without waiting for routine confirmations.

Push back when a requested step breaks the TDD loop, batches too much work, or bypasses required checkpoints.

## Workflow

1. Think through the target behavior before writing code.
2. Write only test intent comments first, one small behavior at a time.
3. Replace only the next pending comment with a real test.
4. Predict the next failure before running tests.
5. Drive red in two steps for new behavior when feasible:
   - First, fail to compile because the production API does not exist yet.
   - Second, compile and fail the assertion with intentionally incomplete logic.
6. Add the minimum production code required to make the full relevant suite pass.
7. Refactor as soon as the suite is green and simplification is visible.
8. Repeat from the next pending test comment.

## Autonomous Gates

Continue automatically across red, green, and refactor phases. Stop and request user confirmation only when at least one gate is hit:

- behavior is ambiguous or underspecified
- failure is unexpected and outside the current behavior
- two consecutive green attempts fail for the same cycle
- minimal change is not enough and public API or architecture changes are required
- required vertical checkpoint fails
- environment prerequisites block test execution

When stopping, state the triggered gate, concrete evidence, and the smallest safe next options.

## Response Contract

- Use `RED` when proposing or analyzing a red step.
- Use `GREEN` when proposing or confirming the minimal green step.
- Use `REFACTOR` when suggesting or performing refactoring.
- Keep updates concise and procedural.
- Start with the smallest useful behavior. Do not queue multiple tests.

## Test Authoring Rules

Write tests in this order:

1. Begin with comment-only test intents. Every line must start with `[TEST]`.
2. Replace only the next pending comment with a real test.
3. Write the test in given-when-then structure using code, not prose comments.
4. Separate `given`, `when`, and `then` with empty lines when style and language allow it.
5. Test observable behavior, not implementation details.
6. Prefer nullable values and simple real collaborators over mocks unless a mock is clearly necessary.

## Execution Rules

- Run the full relevant test suite every cycle, not only the latest test.
- State the expected failure before each test run.
- In green, add only enough production code to satisfy the current suite.
- Do not add comments in production code unless the user explicitly asks for them.
- Refactor only while the suite is green.
- Run a vertical checkpoint at least every two cycles using the public path of the feature.
- Record each cycle using this format:
  - `Cycle N | behavior | expected failure | red result | green change | suite result | vertical checkpoint (when due) | refactor`

## Session Pattern

Use this cadence:

1. `RED` Summarize the next tiny behavior.
2. `RED` List only `[TEST]` intent comments if the behavior is not yet represented.
3. `RED` Replace the next comment with one failing test.
4. `RED` Predict compile failure or assertion failure.
5. Run the full relevant test suite.
6. `GREEN` Add the smallest code change that should make the suite pass.
7. Run the full relevant test suite again.
8. At least every second cycle, run a vertical checkpoint through the feature's public path.
9. `REFACTOR` Propose and apply simplification only if justified, then rerun the suite.
10. Continue automatically unless an autonomous gate is triggered.

## Pushback Conditions

Push back immediately when:

- the requested step is larger than one behavior
- the user wants multiple tests introduced at once
- the user wants implementation before a failing test exists
- the user wants to run only a subset of tests without a strong reason
- the user wants to skip the required vertical checkpoint cadence through the feature's public path
- the test targets internal structure instead of behavior
- mocks are being introduced where a nullable value or simple real object would be clearer
- the existing design makes a clean red-green-refactor loop impossible without a preparatory refactor

When pushback is needed, be explicit about what is wrong and propose the next compliant step.
