# Evaluating Codex Skills

Skill evaluations test what a fresh Codex agent does and what deterministic code can prove. Structural validation shows that a skill is well formed. Evaluation gates show that a change has the intended behavior, preserves relevant contracts, and stops safely.

The runner lives at [`develop-skill-with-evals/scripts/run_skill_evals.py`](develop-skill-with-evals/scripts/run_skill_evals.py). Its detailed contract is [`eval-contract.md`](develop-skill-with-evals/references/eval-contract.md). Plans follow [`eval-plan.schema.json`](develop-skill-with-evals/references/eval-plan.schema.json), and executed reports follow [`eval-result.schema.json`](develop-skill-with-evals/references/eval-result.schema.json).

## Choose gates by impact

Classify the proposed diff before running an evaluation:

| Impact | Use when | Gates |
| --- | --- | --- |
| `static` | Documentation, comments, formatting, or display text cannot affect behavior. | Structural validation only. |
| `deterministic` | Code can observe the complete runner, schema, serialization, exit code, or artifact contract. | Baseline once and candidate three times using deterministic cases. |
| `scoped` | Affected semantic cases can be enumerated confidently. | RED once and candidate GREEN three times for those cases only. |
| `cross-cutting` | Selection, safety, central workflow, shared references, or reach is uncertain. | Scoped gates for affected cases, then every remaining case once. |

Underclassification is a workflow error. Use `cross-cutting` when the affected boundary is uncertain. Do not run unrelated semantic cases merely because they exist, and do not label semantic behavior deterministic merely to reduce cost.

## Plan before spending model sessions

Run:

```bash
python3 develop-skill-with-evals/scripts/run_skill_evals.py plan \
  --skill ./candidate-skill \
  --baseline /tmp/baseline-skill \
  --impact scoped \
  --case changed-behavior
```

`--case` is repeatable. Scoped and cross cutting plans require at least one affected case. Deterministic planning selects all deterministic suite cases when none are supplied; explicit selections must all be deterministic. Static planning accepts no cases.

`plan` reads and validates manifests but creates no workspace or artifact and invokes no model. Its JSON reports:

- selected affected cases and remaining regression cases;
- ordered steps and proposed commands;
- baseline and candidate execution counts;
- executor, judge, and total model sessions;
- the approved limit and whether approval is required;
- classification reasons, warnings, and a normalized manifest fingerprint.

A model session is one executor or judge invocation. A semantic case with an enabled judge costs two sessions per execution. A deterministic case costs zero. Session count does not estimate tokens, duration, or financial cost.

## Validate a change as one operation

Run:

```bash
python3 develop-skill-with-evals/scripts/run_skill_evals.py validate-change \
  --skill ./candidate-skill \
  --baseline /tmp/baseline-skill \
  --impact scoped \
  --case changed-behavior \
  --progress
```

The default approved limit is eight model sessions. An estimate of eight runs. An estimate of nine stops before artifacts or model calls, prints the plan as JSON, and returns exit code 2. To approve a known larger count:

```bash
python3 develop-skill-with-evals/scripts/run_skill_evals.py validate-change \
  --skill ./candidate-skill \
  --baseline /tmp/baseline-skill \
  --impact cross-cutting \
  --case changed-behavior \
  --approved-model-sessions 14 \
  --progress
```

This option is explicit approval for up to that estimated count. Permission to run a shell command or leave a sandbox is not model cost approval.

When the budget permits execution, the runner snapshots the sources and verifies that the candidate manifests still match the approved fingerprint and counts. It then:

1. snapshots baseline and candidate;
2. runs every affected case once on baseline and requires `FAIL`;
3. runs each affected case three times on candidate and requires `PASS`;
4. compares normalized candidate signatures and returns `UNSTABLE` on divergence;
5. for cross cutting changes, runs each remaining suite case once without repeating affected cases;
6. deletes successful workspaces or retains blocking artifacts.

It stops on the first non `PASS` candidate or regression result. It never retries a failure, inconclusive judgment, or unstable result. Do not rerun an unchanged evaluation merely to seek PASS.

## Semantic case contract

A semantic case uses an executor and optionally a judge:

```json
{
  "id": "changed-behavior",
  "kind": "behavioral",
  "prompt_file": "prompt.md",
  "mechanical": {
    "expected_exit_code": 0,
    "required_paths": ["result.txt"],
    "forbidden_changed_paths": [".agents/skills/**"],
    "commands": [
      {"argv": ["python3", "-m", "unittest", "-q"], "exit_code": 0}
    ]
  },
  "judge": {
    "enabled": true,
    "criteria": ["The result satisfies the expected behavior."],
    "no_action_acceptable": false
  }
}
```

The runner copies the minimal fixture to a disposable workspace, installs the evaluated skill under `.agents/skills/<name>` without its `evals/`, and invokes an ephemeral Codex executor. Mechanical commands use direct argument arrays without a shell. An enabled judge receives hidden criteria, executor evidence, mechanical outcomes, and a diff summary. The executor never receives the criteria or other answer keys.

`kind` may be `behavioral`, `non_behavioral`, or `trigger`. `implicit_skill: true` omits the explicit `$skill-name` prefix for trigger smoke tests.

## Deterministic case contract

Use a deterministic case only when code completely observes the behavior:

```json
{
  "id": "runner-json-output",
  "kind": "deterministic",
  "mechanical": {
    "commands": [
      {"argv": ["python3", "check_runner.py"], "exit_code": 0}
    ]
  },
  "judge": {
    "enabled": false,
    "criteria": []
  }
}
```

Deterministic cases do not require `prompt.md`, create no executor response, record executor and judge as disabled, and consume zero model sessions. They must define at least one required path, forbidden changed path, or command. They cannot define executor settings, `implicit_skill`, `prompt_file`, `mechanical.expected_exit_code`, or an enabled judge.

Every command receives `SKILL_EVAL_SKILL_DIR`, which points to the absolute immutable snapshot under evaluation. Commands execute as direct argv in a fresh fixture workspace. The runner verifies that the skill snapshot remains unchanged.

## Suite layout and fixture safety

```text
example-skill/
├── SKILL.md
├── agents/
│   └── openai.yaml
└── evals/
    ├── suite.json
    └── cases/
        └── example-case/
            ├── case.json
            ├── prompt.md
            └── fixture/
```

`suite.json` has version 1 and a unique ordered array of case IDs. Keep fixtures minimal and generic. Never include credentials, personal information, proprietary source, customer data, full transcripts, generated model responses, or hidden answers in prompts.

## Existing commands remain available

Run one case:

```bash
python3 develop-skill-with-evals/scripts/run_skill_evals.py run \
  --skill refactor-design \
  --case hidden-invocation-state \
  --source working-tree
```

Run a complete suite:

```bash
python3 develop-skill-with-evals/scripts/run_skill_evals.py run \
  --skill refactor-design \
  --all \
  --source working-tree
```

Compare one baseline and candidate execution:

```bash
python3 develop-skill-with-evals/scripts/run_skill_evals.py verify-change \
  --skill refactor-design \
  --case hidden-invocation-state \
  --baseline git:HEAD
```

Repeat one candidate case:

```bash
python3 develop-skill-with-evals/scripts/run_skill_evals.py stability \
  --skill refactor-design \
  --case hidden-invocation-state \
  --runs 3
```

These operations retain their schemas, codes, artifacts, and progress behavior. Prefer `plan` plus `validate-change` when validating a change because they enforce proportional selection and budget before execution.

## Progress and results

Standard output is always JSON. Progress uses standard error and flushes immediately. It is automatic when standard error is a TTY, silent for a pipe, forced by `--progress`, and suppressed by `--quiet`. Progress options are mutually exclusive and never make the workflow interactive.

| Status | Meaning |
| --- | --- |
| `PASS` | Every required check and judgment passed. |
| `FAIL` | An observable contract failed. |
| `ERROR` | The runner, manifest, source, or process failed unreliably. |
| `INCONCLUSIVE` | The judge could not establish the contract. |
| `INVALID_RED` | An affected case passed on baseline. |
| `UNSTABLE` | Three passing candidate signatures diverged. |

Only `PASS` returns exit code 0 for executed evaluations. Blocking executed operations return 1 and retain artifacts. Budget refusal returns 2 with the plan and creates no artifacts.

Normalized signatures compare status, mechanical outcomes, judge verdict, and outcome relevant changed paths. They ignore runner `.eval-*` files and generated Python caches, but preserve production paths.

## Development workflow

1. Load `skill-creator` and the evaluation contract.
2. Preserve a baseline and isolated candidate.
3. Add the smallest case that can observe the change.
4. Run `plan` and inspect classification, selected cases, counts, and warnings.
5. Obtain explicit cost approval when the estimate exceeds eight sessions.
6. Run `validate-change` without opportunistic retries.
7. Diagnose every blocking result before changing or repeating a gate.
8. Run structural validation, validate schemas, inspect metadata, and check the diff.
9. Forward-test significant skill changes with a fresh agent before promotion.

For self evolution, never edit canonical source until the isolated candidate passes its required gates. A fresh agent receives only a realistic task and candidate path, not the intended answer or prior diagnosis.

## Structural validation

```bash
python3 -m unittest discover \
  -s develop-skill-with-evals/scripts/tests \
  -v

python3 .system/skill-creator/scripts/quick_validate.py \
  ./skill-name

python3 -m json.tool develop-skill-with-evals/references/eval-plan.schema.json
python3 -m json.tool develop-skill-with-evals/references/eval-result.schema.json
git diff --check
```

Do not commit, push, publish, or promote unless that separate action is authorized.
