# Using Skills with Codex CLI

This cookbook is for people who use the skills in this repository. Start here to make the skills discoverable, choose the right Codex CLI mode, invoke a workflow, and review its work. Maintainers can continue into skill creation, evaluation, promotion, and durable report operations.

For the evaluation model and supervision guidance, see [Evaluating Codex Skills](EVALUATIONS.md). The normative local behavior remains in each [`SKILL.md`](README.md#skill-catalog), its references, and its scripts. For current product behavior, use the official [CLI command reference](https://learn.chatgpt.com/docs/developer-commands?surface=cli), [non-interactive mode](https://learn.chatgpt.com/docs/non-interactive-mode), [Build skills](https://learn.chatgpt.com/docs/build-skills), and [Codex models](https://learn.chatgpt.com/docs/models) documentation.

## Prepare Codex and discover the skills

This guide was checked against `codex-cli 0.145.0`. Verify your installation and authentication before diagnosing a skill:

```bash
codex --version
codex login status
codex doctor
```

If your version differs, treat `codex --help` and the relevant subcommand help as authoritative.

### Install a skill in a discovery location

Codex scans `.agents/skills` from the current directory up to the repository root, plus the personal `$HOME/.agents/skills` location. It follows symlinked skill directories. This source repository can stay at `/home/renanfranca/.codex/skills`.

Make one skill available across repositories:

```bash
mkdir -p "$HOME/.agents/skills"
ln -s /home/renanfranca/.codex/skills/refactor-design \
  "$HOME/.agents/skills/refactor-design"
```

Or make it available only in one repository:

```bash
mkdir -p /path/to/project/.agents/skills
ln -s /home/renanfranca/.codex/skills/refactor-design \
  /path/to/project/.agents/skills/refactor-design
```

Avoid duplicate frontmatter `name` values. Codex does not merge duplicate skills and may show both in its selectors.

Launch Codex in the project where the work will happen:

```bash
codex -C /path/to/project
```

Inside the TUI, run `/skills` or type `$` and confirm that the expected skill appears. Codex normally detects skill changes automatically; restart it if a new or updated skill does not appear.

## Choose the TUI or `codex exec`

Use the interactive TUI for exploratory work, multi step changes, follow up prompts, or work that may need human approval:

```bash
codex -C /path/to/project \
  --sandbox workspace-write \
  --ask-for-approval on-request
```

Use the skills repository as the working directory when editing skill sources. Use the target project as the working directory when applying TDD, design review, Git, or Seed4J workflows there.

Resume the most recent interactive session with:

```bash
codex resume --last
```

Use `codex exec` when the request and permission boundary are known in advance and the run should finish without another human response:

```bash
codex exec --ephemeral \
  -C /path/to/project \
  --sandbox workspace-write \
  'Use $refactor-design on this completed green change. Review only the changed scope, preserve its public contract, apply the smallest justified refactor, rerun the suite and public checkpoint, and pause at exception gates.'
```

In POSIX shells, single quotes prevent `$refactor-design` from being expanded as an environment variable. `--ephemeral` avoids persisting session rollout files; use it only when you do not intend to resume the run.

By default, `codex exec` streams progress to standard error and prints the final response to standard output. Use `--json` when a script needs the complete JSONL event stream:

```bash
codex exec --ephemeral --json \
  -C /path/to/project \
  'Use $refactor-design on this completed green change. Review only the changed scope, preserve its public contract, apply the smallest justified refactor, rerun the suite and public checkpoint, and pause at exception gates.'
```

Use `-o/--output-last-message` when a script needs the final response in a file. The response is still printed to standard output:

```bash
codex exec --ephemeral \
  -C /path/to/project \
  -o /tmp/codex-final-message.md \
  'Use $develop-skill-with-evals to explain the latest blocking eval result. Do not modify files.'
```

To resume a saved noninteractive session, omit `--ephemeral` from the original command:

```bash
codex exec resume --last \
  'Continue from the previous result and run the remaining validation.'
```

The CLI exposes many other commands and flags. They are outside this repository's workflows; use the official command reference instead of assuming they are part of this cookbook.

## Select a skill explicitly or implicitly

Explicit selection is the reliable default. Name the skill with `$skill-name` and describe the concrete outcome, scope, stopping conditions, and validation:

```text
Use $refactor-design on this completed green change. Review only the changed scope, preserve its public contract, apply the smallest justified refactor, rerun the relevant suite and public checkpoint, and pause at exception gates. Report No action when no concrete design risk exists.
```

Codex can also select a skill implicitly when the task matches its frontmatter `description`. This is useful when testing discovery or natural triggering:

```text
The requested behavior, relevant suite, and public checkpoint are green. Inspect only the changed scope for structural design risks, preserve the public contract, apply the smallest justified refactor, rerun both validations, and pause at exception gates.
```

After an implicit test, verify which skill was selected and whether it respected its entry conditions. `agents/openai.yaml` may disable implicit invocation, and its `default_prompt` is presentation metadata, not a replacement for `SKILL.md`.

## Choose a workflow by task

The [README catalog](README.md#skill-catalog) is the canonical active skill list. The complete workflow is in the linked `SKILL.md`; display metadata and default invocation text are in `agents/openai.yaml`.

| Task | Skill and canonical sources | Working directory |
| --- | --- | --- |
| Create or improve a skill with proportional evaluations | [`develop-skill-with-evals`](develop-skill-with-evals/SKILL.md), [metadata](develop-skill-with-evals/agents/openai.yaml) | This skills repository |
| Plan and execute a substantial repository change | [`implement-execplan`](implement-execplan/SKILL.md), [metadata](implement-execplan/agents/openai.yaml) | Target repository |
| Review a completed green implementation for design risks | [`refactor-design`](refactor-design/SKILL.md), [metadata](refactor-design/agents/openai.yaml) | Target repository |
| Implement behavior through autonomous quiet TDD | [`tdd-behavior-autonomous-quiet`](tdd-behavior-autonomous-quiet/SKILL.md), [metadata](tdd-behavior-autonomous-quiet/agents/openai.yaml) | Target repository |
| Plan substantial Seed4J CLI work with TDD and design review | [`seed4j-execplan-tdd`](seed4j-execplan-tdd/SKILL.md), [metadata](seed4j-execplan-tdd/agents/openai.yaml) | `seed4j-cli` worktree |
| Audit, create, or clean up Seed4J CLI worktrees | [`seed4j-worktree-flow`](seed4j-worktree-flow/SKILL.md), [metadata](seed4j-worktree-flow/agents/openai.yaml) | Main `seed4j-cli` worktree |
| Commit exactly what is already staged | [`commit-staged-change`](commit-staged-change/SKILL.md), [metadata](commit-staged-change/agents/openai.yaml) | Target repository |
| Let Codex select intended changes, stage, and commit them | [`commit-the-changes`](commit-the-changes/SKILL.md), [metadata](commit-the-changes/agents/openai.yaml) | Target repository |

Use these request patterns instead of maintaining one nearly identical prompt per skill:

### Implement or review a change

```text
Use $skill-name to <observable outcome>. Work only in <scope>. Preserve <public contract>. Run <validation>. Stop if <blocking condition>. Do not commit or push.
```

For TDD, state behavior through public contracts. For design review, say that behavior is already green. For an ExecPlan, identify the substantial outcome and require the living plan to remain current.

### Manage repository state

```text
Use $skill-name to inspect <repository state> and perform <commit or worktree outcome>. Include only <exact scope>. Preserve <protected state>. Do not push or remove anything outside that scope.
```

The two commit skills create commits but never imply a push. Use `commit-staged-change` only when the exact intended diff is already staged. Use `commit-the-changes` when Codex is authorized to decide which current changes belong together and stage them.

## Create and evolve skills

Use `$develop-skill-with-evals` for new skills and behavioral revisions. It composes the system `skill-creator` scaffold with the repository's evaluation workflow.

### Create a new skill

Start in this repository and describe behavior, trigger boundaries, forbidden behavior, and release boundaries:

```text
Use $develop-skill-with-evals to create changelog-writer in this repository.

It must turn supplied user-visible changes into one concise Markdown changelog section. It should trigger for release notes and changelogs, but not for committing, publishing, or inventing facts.

Create the official scaffold, preserve its untouched baseline, add minimal generic eval cases before implementing behavior, classify impact, inspect the session plan, demonstrate baseline RED, and run proportional candidate gates. Validate SKILL.md and agents/openai.yaml. Do not commit, push, or publish.
```

Prefer the TUI because a maintainer may need to review the plan or approve the complete runner command. A fully predetermined request can use `codex exec`, but the noninteractive process cannot pause for a new conversational decision.

### Change observable behavior

Name every affected behavior when the reach is known:

```text
Use $develop-skill-with-evals to improve changelog-writer so it refuses to invent issue numbers. Add or update a focused case before editing SKILL.md, preserve the baseline, plan a scoped promotion, require valid RED and three stable candidate GREEN results, and run only proportional regression. Do not commit or push.
```

Trigger changes need positive, negative, and implicit selection coverage. Use `cross-cutting` when the affected reach cannot be bounded confidently.

### Change static documentation or metadata

Do not manufacture a failing behavior test for spelling, formatting, organization, or metadata that cannot change triggering or behavior:

```text
Use $develop-skill-with-evals to correct “Chanelog Writer” to “Changelog Writer” in agents/openai.yaml. Classify this as static, inspect the side effect free plan, run only structural and metadata validation, and do not invent RED.
```

When evolving `develop-skill-with-evals` itself, work in isolated baseline and candidate copies and keep the canonical source unchanged until the candidate passes the required gates.

## Run skill evaluations

There are two supported entry points:

1. Ask `$develop-skill-with-evals` to orchestrate the workflow.
2. Run `develop-skill-with-evals/scripts/run_skill_evals.py` directly from a trusted terminal.

The direct runner is authoritative. For concepts, evidence visibility, impact, gates, and supervision, read [Evaluating Codex Skills](EVALUATIONS.md). Run the commands below from `/home/renanfranca/.codex/skills`.

Before the first model backed operation, run:

```bash
codex doctor --json
```

Run it at the same outer permission boundary that will launch the runner and require `overallStatus: ok`. A TUI started with `--ask-for-approval on-request` does not automatically elevate a noninteractive runner subprocess. If `CODEX_HOME` is read only or network access is unavailable, approve the exact complete runner command externally or run it from a trusted terminal.

Keep every nested executor and judge in the runner's internal `workspace-write` sandbox. Do not use `danger-full-access`, bypass approval, or copy authentication state into `/tmp`.

The runner prints its final JSON to standard output. It shows progress on standard error when attached to a terminal; pass `--progress` when another process is monitoring it. `--quiet` suppresses progress, and the two flags are mutually exclusive.

The runner does not choose a promotion runtime from global `config.toml`. Supply executor model and reasoning effort explicitly whenever the plan includes model sessions. Supply a separate judge runtime only when required, or let it inherit the complete executor runtime.

### Plan proportional gates first

Classify the diff as `static`, `deterministic`, `scoped`, or `cross-cutting`. Use `cross-cutting` when the affected reach is uncertain. Planning is side effect free: it creates no workspace, ledger, artifact, or model subprocess.

```bash
python3 develop-skill-with-evals/scripts/run_skill_evals.py plan \
  --skill ./candidate-skill \
  --baseline /tmp/baseline-skill \
  --impact scoped \
  --case changed-behavior \
  --workflow promotion \
  --model <executor-model> \
  --reasoning-effort <effort>
```

Inspect the selected cases and regressions, session maximum, resolved runtime, `economic_runtime`, fingerprints, blockers, and warnings. Economic guidance is informative and never fills in a missing runtime. A complete explicit mismatch remains in the proposed command with a warning.

Planning always exits zero, including when it reports blockers. A deterministic case consumes no model sessions. A static plan requires no RED or model execution.

### Diagnose once when it will change the plan

Use `--workflow diagnostic` when one observation of affected baseline, candidate, and proportional regressions will prevent repeated failed promotion attempts. Inspect the plan, then run its proposed `probe-change` command. A diagnostic continues after contract failures, stops on infrastructure failures, and always reports `promotion_eligible: false`.

To bind diagnostic and promotion to one cumulative budget, give both operations the same:

```text
--campaign-ledger /tmp/my-skill-campaign.json
--approved-cumulative-model-sessions 26
```

The ledger is locked and written atomically. A cumulative budget blocker is reported before any ledger, workspace, artifact, or model side effect. Do not repeat an unchanged complete diagnostic.

### Validate the planned change

Run the exact promotion command reviewed in the plan:

```bash
python3 develop-skill-with-evals/scripts/run_skill_evals.py validate-change \
  --skill ./candidate-skill \
  --baseline /tmp/baseline-skill \
  --impact scoped \
  --case changed-behavior \
  --model <executor-model> \
  --reasoning-effort <effort> \
  --campaign-ledger /tmp/my-skill-campaign.json \
  --approved-cumulative-model-sessions 26 \
  --progress
```

`validate-change` runs baseline RED, candidate GREEN 1, proportional regression, then candidate GREEN 2 and 3. Missing runtime, unresolved judge runtime, or insufficient budget prints every blocker, returns exit code `2`, and stops before workspace, report, or model side effects.

The default operation maximum is eight model sessions. Use `--approved-model-sessions <n>` only after reviewing a known larger maximum. Approval for model session consumption and external shell or sandbox approval are separate decisions.

Only overall `PASS` returns exit code `0`. `FAIL`, `ERROR`, `INCONCLUSIVE`, `INVALID_RED`, and `UNSTABLE` return `1` and block promotion. Do not rerun an unchanged blocking result merely to seek `PASS`.

### Use exploratory and compatibility operations deliberately

The following interfaces remain useful, but they do not replace integrated promotion:

* `run` executes one case or a complete suite for inspection.
* `verify-change` checks baseline RED and one candidate GREEN for compatibility with older workflows.
* `stability` repeats one source and rejects divergent normalized verdicts.

Run one case:

```bash
python3 develop-skill-with-evals/scripts/run_skill_evals.py run \
  --skill refactor-design \
  --case hidden-invocation-state \
  --source working-tree \
  --progress
```

Run one complete suite:

```bash
python3 develop-skill-with-evals/scripts/run_skill_evals.py run \
  --skill refactor-design \
  --all \
  --source working-tree \
  --progress
```

`--all` means every case in one skill's `evals/suite.json`, not every skill in the repository.

Discover and run every persisted suite without maintaining a duplicate list:

```bash
(
  eval_status=0
  for suite_path in */evals/suite.json; do
    skill_dir=${suite_path%/evals/suite.json}
    python3 develop-skill-with-evals/scripts/run_skill_evals.py run \
      --skill "$skill_dir" \
      --all \
      --source working-tree \
      --progress || eval_status=1
  done
  exit "$eval_status"
)
```

At this snapshot, `develop-skill-with-evals` and `refactor-design` have persisted suites. A skill without `evals/suite.json` can still receive structural validation, but the runner has no cases to execute for it.

Examples of the two compatibility operations:

```bash
python3 develop-skill-with-evals/scripts/run_skill_evals.py verify-change \
  --skill refactor-design \
  --case changed-case-id \
  --baseline git:HEAD \
  --progress
```

```bash
python3 develop-skill-with-evals/scripts/run_skill_evals.py stability \
  --skill refactor-design \
  --case hidden-invocation-state \
  --runs 3 \
  --progress
```

Do not use an unchanged skill as both baseline and candidate: an existing valid case should pass both and produce `INVALID_RED`. For an untracked skill, use a frozen baseline directory under `/tmp`.

### Inspect the result

For every executed report, inspect:

* overall `status`, `promotion_eligible`, and `failure_category`;
* resolved runtime and its sources;
* planned `sessions.total` versus actual `model_sessions.total`;
* token `usage` completeness and cumulative `campaign` consumption;
* every case, executor, mechanical check, oracle, and judge result;
* production `changed_paths`;
* retained `artifacts`.

Unknown token counts remain `null`, never zero. Successful workspaces are removed. Blocking workspaces remain under `/tmp/skill-eval-artifacts` by default. Treat environment failures separately from behavioral failures.

## Archive, pricing, and comparison

Real operations that consume at least one model session automatically persist evidence when `evaluation-reports/archive-config.json` exists. The runner writes canonical JSON atomically to `evaluation-reports/<skill-name>/operations/<operation-id>/report.json`, then derives `report.md` before successful workspace cleanup.

Use `--no-report` to opt out or `--report-dir` to choose an explicit destination. `--pricing-file` is allowed only with an explicit report destination.

### Persist evidence with dated pricing

The repository snapshot dated `2026-07-26` contains pricing references for `gpt-5.6-luna`, `gpt-5.6-terra`, and `gpt-5.6-sol`. The following is a dated example for a scoped semantic case with a complete oracle and no judge:

```bash
python3 develop-skill-with-evals/scripts/run_skill_evals.py validate-change \
  --skill ./candidate-skill \
  --baseline /tmp/baseline-skill \
  --impact scoped \
  --case changed-behavior \
  --model gpt-5.6-luna \
  --reasoning-effort medium \
  --approved-model-sessions 4 \
  --progress
```

These model names are examples from the snapshot, not runner defaults. The runner still requires explicit economic runtime selection for model backed promotion.

Every persisted monetary value is a dated API reference estimate with `actual_charge: false`. It is not an observed ChatGPT charge. When request scoped long context usage cannot be reconstructed from telemetry, the exact API estimate remains unavailable rather than presenting the base rate as exact.

Regenerate Markdown after a presentation only change without another model session:

```bash
python3 develop-skill-with-evals/scripts/render_eval_report.py \
  --input evaluation-reports/<skill-name>/operations/<operation-id>/report.json \
  --output evaluation-reports/<skill-name>/operations/<operation-id>/report.md
```

Validate the permanent archive without rebuilding it:

```bash
python3 develop-skill-with-evals/scripts/manage_evaluation_archive.py validate \
  --archive evaluation-reports
```

Use `rebuild --archive evaluation-reports` only after an intentional archive input or renderer change. It deterministically regenerates projections and comparisons; it does not run a model.

### Compare model reports

Compare a directory of canonical reports without another model session:

```bash
python3 develop-skill-with-evals/scripts/compare_model_reports.py \
  --reports evaluation-reports/<skill-name>/operations \
  --output-dir evaluation-reports/<skill-name>/comparisons/manual
```

The dated `pilot-v2` comparison contains 18 observations across Luna, Sol, and Terra. It labels the evidence directional, not statistical proof, and reports `qualifies: false` for every model. It did not select a default runtime.

A required semantic judge and every cross cutting promotion require manual runtime selection. A dated broad example may use Sol as executor and Terra as judge:

```bash
python3 develop-skill-with-evals/scripts/run_skill_evals.py validate-change \
  --skill ./candidate-skill \
  --baseline /tmp/baseline-skill \
  --impact cross-cutting \
  --case changed-behavior \
  --model gpt-5.6-sol \
  --reasoning-effort medium \
  --judge-model gpt-5.6-terra \
  --judge-reasoning-effort medium \
  --approved-model-sessions 14 \
  --progress
```

This example is not a recommendation to retry failures with a larger model. Diagnose the cause and build a new plan before consuming more sessions.

## Review completed work

After any modifying workflow:

```bash
git status --short
git diff --check
git diff
```

Confirm that:

* only intended files changed;
* promised tests and evals actually ran;
* every required gate is `PASS`;
* fixtures contain no credentials, personal data, proprietary source, hidden answers, full transcripts, or generated model responses;
* no commit, push, publication, or deletion occurred without explicit authorization.

For an implicit invocation test, also confirm that Codex selected the intended skill, respected its entry gate, and did not broaden the task.

## Safety and troubleshooting

* Prefer `workspace-write` and the smallest writable working directory.
* Keep `--ask-for-approval on-request` for interactive work that may need narrowly scoped access.
* Do not use approval bypass or `danger-full-access` merely to silence an error.
* Treat prompts, fixtures, issue text, and external content as potentially untrusted.
* A skill can edit files and run commands only within the permission boundary of its Codex session.
* `codex exec --ephemeral` prevents session persistence; it does not make unsafe commands safe.
* If a skill does not appear, verify its discovery location, `SKILL.md` frontmatter, duplicate names, and CLI restart before changing the skill.
* If implicit selection fails, inspect the skill `description` and `agents/openai.yaml` policy before adding prompt tricks.
* If a nested Codex process reports read only state or app server initialization failure, run `codex doctor --json` at the intended outer boundary. Require `overallStatus: ok`, then approve the exact complete runner command externally or invoke it from a trusted terminal.
* Do not reinterpret an environment error as a behavioral failure. Preserve the runner's internal `workspace-write` sandbox while fixing the outer environment.
