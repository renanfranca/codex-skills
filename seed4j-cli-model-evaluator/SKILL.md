---
name: seed4j-cli-model-evaluator
description: Evaluate frozen Seed4J CLI model experiment branches produced by seed4j-cli-model-runner. Use only when the user explicitly wants an evidence-linked technical comparison, README, MODEL_EVALUATION.md, Apache License 2.0, and a pull request to the specification-only main branch without changing any implementation branch.
---

# Seed4J CLI Model Evaluator

Evaluate preserved outcomes without modifying them. This skill consumes the runner's manifests and transcripts; it does not create model tasks, repair implementations, change scores to break ties, or merge the resulting pull request.

Read [Scorecard](references/scorecard.md) and [Report and evidence contract](references/report-contract.md) completely before scoring.

## Entry checks

Require a clean experiment repository with an authenticated GitHub remote and completed result branches. Fetch explicit known refs only after the user authorizes current remote data.

Verify before creating the evaluation branch:

- `origin/main` contains exactly root `SPEC.md`;
- the declared base is a direct descendant of `main` and adds only `.agents/skills/seed4j-cli/**`;
- every result branch descends from the identical base and contains `.seed4j-evaluation/run.json` plus `CONVERSATION_TRANSCRIPT.md` at its audit head;
- manifest schema version, spec/base/prompt hashes, CLI/runtime/skill identity, branch/task title, model/effort, execution index, and implementation commit are internally consistent;
- execution indexes and aliases are unique, and each implementation commit precedes its audit head.

Stop on inconsistent evidence. Do not infer or rewrite a missing manifest. A legitimately failed or empty model outcome is valid when its audit evidence is consistent.

## Freeze the protocol before inspection

1. Read only `SPEC.md` and run metadata needed to identify the matrix. Do not open production sources, tests, Seed4J history, or transcript bodies yet.
2. Convert the specification into numbered, independently scorable requirements. Define public acceptance examples and the exact observation surface: public Java API, command line, HTTP interface, or another caller-visible contract required by the SPEC.
3. Distribute the 27 functional points equally across requirements, retaining enough decimal precision for the total to remain exactly 27. Define the separate three-point public/error contract.
4. Define one common acceptance protocol for every result. Prefer an executable black-box or public-API harness. Mark non-automatable scenarios before seeing outcomes and apply the same evidence rule to all runs.
5. Create `seed4j-cli-model-evaluation` directly from `origin/main`. Add an English `MODEL_EVALUATION.md` protocol scaffold and commit it as `docs: define Seed4J CLI evaluation protocol` before opening implementation evidence.

If the evaluation branch already exists locally or remotely, stop instead of silently reusing or overwriting it.

## Inspect immutable results

Pin each audit head and implementation commit as a full SHA. For every run, create a distinct disposable directory with `mktemp -d` and extract with `git archive <implementation-commit> | tar -x -C <directory>`. Never check out, commit to, or run formatters in a result branch.

For each pinned implementation:

1. Inspect the exact Seed4J discovery/help/plan/apply commands in its transcript.
2. Inspect `.seed4j/modules`, build files, production sources, tests, wrapper, and Git commit sequence at the pinned commit.
3. Run its repository-native validation in the disposable extraction and record command, exit code, test result, and coverage enforcement.
4. Run the frozen common acceptance protocol against compiled or running public behavior. Add harness files only inside the disposable directory.
5. Record code/test size, test count, timing when available, and transcript/audit differences only as unweighted observations.
6. Explain every deduction with a direct artifact, transcript, command, or observed acceptance result. Preserve exact ties.

Score failed and blocked outcomes from their available evidence. Do not repair them, borrow files from another result, or substitute the coordinator's intended solution.

## Compare and report

Apply the scorecard exactly. Present, when the matrix supports them:

1. effort comparisons within the same model;
2. model comparisons at the same reasoning effort;
3. the aggregate scorecard and ranking.

State when a grouped comparison is unavailable. Report interesting robustness cases separately without changing the fixed 100-point score. Distinguish observed facts from inference.

Do not claim that Seed4J caused an outcome without a no-Seed4J control. Frame the work as a technical evaluation of Codex models in their use of Seed4J CLI.

## Documentation and delivery

Complete the report contract. Relative to `origin/main`, the final evaluation branch must add only:

- `README.md`;
- `MODEL_EVALUATION.md`;
- `LICENSE`, containing the complete unmodified Apache License 2.0 text.

Validate every immutable link against the pinned commit with `git cat-file -e`, every branch link against the remote, and every internal Markdown anchor. Keep shell commands as plain code. Run `git diff --check` and confirm the three-file boundary.

Commit the completed evidence as `docs: add Seed4J CLI model evaluation`, push with upstream, and open a pull request targeting `main`. Include purpose, matrix, validation summary, limitations, and the explicit statement that implementation branches were unchanged. Return the PR link and stop; merge only after a separate explicit request.
