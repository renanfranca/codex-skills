The small runner in `target-skill/scripts/target-runner.py` currently writes its JSON status to standard error. I intend to move that JSON to standard output while preserving the exit code and keeping standard error empty.

Before editing anything, choose the appropriate impact and use the public planning operation from the repository-scoped `develop-skill-with-evals` runner. Evaluate `target-skill` against `target-baseline`; let the runner select the applicable suite cases.

Run the planning operation exactly once. Save its standard output as `evaluation-plan.json`, its standard error as `plan-stderr.log`, and its decimal exit code as `plan-exit-code.txt`. This is planning only: do not modify either skill and do not run an evaluation.
