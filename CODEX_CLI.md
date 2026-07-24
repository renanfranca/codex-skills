# Using Skills with Codex CLI

This is the cookbook for people using the skills in this repository. It shows how to verify that Codex sees a skill, run its evaluations, create a new skill with evals, improve an existing skill, and invoke every available workflow from the terminal.

For the evaluation architecture and manifest reference, see [Evaluating Codex Skills](EVALUATIONS.md). For current product behavior, see the official [Codex CLI](https://learn.chatgpt.com/docs/codex/cli), [CLI command reference](https://learn.chatgpt.com/docs/developer-commands?surface=cli), [non-interactive mode](https://learn.chatgpt.com/docs/non-interactive-mode), and [Build skills](https://learn.chatgpt.com/docs/build-skills) documentation.

## Before the first run

Check the installed CLI, authentication, and local environment:

```bash
codex --version
codex login status
codex doctor
```

This guide was validated against `codex-cli 0.145.0`. The examples avoid depending on that exact version; use `codex --help` and `codex exec --help` if your installed CLI differs.

### Make the skills discoverable

The current Codex documentation lists two common authoring locations:

- `$HOME/.agents/skills` for personal skills available across repositories;
- `<repository>/.agents/skills` for skills scoped to a repository or subtree.

This source repository can remain at `/home/renanfranca/.codex/skills`. To make an individual skill portable across CLI installations, symlink it into the personal location:

```bash
mkdir -p "$HOME/.agents/skills"
ln -s /home/renanfranca/.codex/skills/refactor-design \
  "$HOME/.agents/skills/refactor-design"
```

Repeat the symlink for each skill you want available globally. For an installation scoped to a repository:

```bash
mkdir -p /path/to/project/.agents/skills
ln -s /home/renanfranca/.codex/skills/refactor-design \
  /path/to/project/.agents/skills/refactor-design
```

Codex follows symlinked skill folders. Avoid installing two skills with the same frontmatter `name`; Codex does not merge them.

Launch Codex and run `/skills`, or type `$`, to verify that the expected skill appears:

```bash
codex -C /path/to/project
```

Codex normally detects skill changes automatically. Restart the CLI when an updated or newly installed skill does not appear.

## Choose interactive or non-interactive mode

### Interactive mode: recommended for skill work

Use the terminal UI when creating or changing skills. It supports subsequent prompts, shows progress, and can ask for approval when an eval needs to start nested ephemeral Codex sessions:

```bash
codex -C /home/renanfranca/.codex/skills \
  --sandbox workspace-write \
  --ask-for-approval on-request
```

Use the skills repository as the working directory when editing skill sources. Use the target project as the working directory when applying TDD, design review, or Seed4J workflows to that project.

Inside the TUI, invoke a skill explicitly:

```text
Use $develop-skill-with-evals to run the complete refactor-design evaluation suite. Do not modify either skill. Report the overall status, failed checks, retained artifacts, and exit code.
```

Continue the most recent interactive session later with:

```bash
codex resume --last
```

### Non-interactive mode: work from a single command and automation

Use `codex exec` when the prompt and permissions are known in advance:

```bash
codex exec --ephemeral \
  -C /home/renanfranca/.codex/skills \
  --sandbox workspace-write \
  'Use $develop-skill-with-evals to validate refactor-design structurally. Do not change files.'
```

Single quotes are important in POSIX shells: they prevent the shell from expanding `$skill-name` as an environment variable.

`codex exec` streams progress to standard error and prints the final response to standard output. Use `--json` for an event stream or `-o/--output-last-message` to save the final message:

```bash
codex exec --ephemeral --json \
  -C /home/renanfranca/.codex/skills \
  'Use $refactor-design to review this completed green implementation.'
```

```bash
codex exec --ephemeral \
  -C /home/renanfranca/.codex/skills \
  -o /tmp/codex-final-message.md \
  'Use $develop-skill-with-evals to explain the latest blocking eval result. Do not modify files.'
```

Non-interactive runs cannot stop and wait for a new human approval. Skill development workflows can launch nested `codex exec` sessions, so use the interactive TUI when approval may be required. Use `danger-full-access` or approval bypass flags only inside an externally hardened disposable environment; they are not the default solution for an eval permission failure.

Resume a saved non-interactive session with the following command. Omit `--ephemeral` from the original run when you intend to resume it:

```bash
codex exec resume --last 'Continue from the previous result and run the remaining validation.'
```

## Run skill evaluations

There are two ways to run evals:

1. Ask Codex to orchestrate the workflow with `$develop-skill-with-evals`.
2. Run the evaluation runner directly from a trusted terminal.

The direct runner is authoritative and itself launches isolated `codex exec` sessions for the executor and semantic judge.

Run all commands in this section from `/home/renanfranca/.codex/skills`.

The runner normally shows progress when its standard error is attached to a terminal and stays silent when that stream is captured. When Codex CLI launches the runner as a monitored subprocess, pass `--progress` so preparation, executor, mechanical checks, judge, case results, and the final result are visible immediately on standard error. This does not make the run interactive: the runner never waits for input, approval, or confirmation. Its final JSON remains pure on standard output. Use `--quiet` to suppress progress explicitly; `--progress` and `--quiet` are mutually exclusive.

### Plan proportional gates first

Classify the proposed diff as `static`, `deterministic`, `scoped`, or `cross-cutting`. Use `cross-cutting` when the affected reach is uncertain. Planning creates no workspace or artifact and invokes no model:

```bash
python3 develop-skill-with-evals/scripts/run_skill_evals.py plan \
  --skill ./candidate-skill \
  --baseline /tmp/baseline-skill \
  --impact scoped \
  --case changed-behavior \
  --workflow promotion \
  --model gpt-5.6-sol \
  --reasoning-effort medium \
  --judge-model gpt-5.6-terra \
  --judge-reasoning-effort medium
```

The JSON plan lists affected and regression cases, commands, execution counts, executor sessions, judge sessions, total sessions, the approved limit, campaign projection, resolved runtime and sources, case, source, runtime and evaluation fingerprints, ordered execution blockers, and warnings. Planning always exits zero and never creates a workspace, ledger, artifact, or model subprocess. A deterministic case consumes zero model sessions because it uses direct code checks with no executor or judge.

### Probe once for a complete diagnosis

Use `--workflow diagnostic` when one pass across affected baseline, affected candidate and proportional regressions will save repeated failed promotion gates. After inspecting and approving that plan, run its `probe-change` command. The diagnostic continues after contract failures, stops on infrastructure failures, and always reports `promotion_eligible: false`.

To bind the diagnostic and later promotion to one cumulative budget, pass both:

```text
--campaign-ledger /tmp/my-skill-campaign.json
--approved-cumulative-model-sessions 26
```

The ledger is locked and written atomically. A cumulative budget blocker is reported before any ledger, workspace, artifact or model side effect. Do not repeat an unchanged complete diagnostic.

### Validate the planned change

`validate-change` runs baseline, candidate repetition one, every proportional regression, then candidate repetitions two and three. This preserves three stable GREEN results while allowing an early regression defect to block the last two repetitions:

```bash
python3 develop-skill-with-evals/scripts/run_skill_evals.py validate-change \
  --skill ./candidate-skill \
  --baseline /tmp/baseline-skill \
  --impact scoped \
  --case changed-behavior \
  --model gpt-5.6-sol \
  --reasoning-effort medium \
  --judge-model gpt-5.6-terra \
  --judge-reasoning-effort medium \
  --campaign-ledger /tmp/my-skill-campaign.json \
  --approved-cumulative-model-sessions 26 \
  --progress
```

When model sessions are planned, `validate-change` requires executor model and reasoning effort from the CLI. A required judge may use its own CLI values or inherit that complete executor runtime. Missing runtime, unresolved judge runtime, or insufficient budget prints every blocker in the plan, returns exit code `2`, and stops before workspaces, artifacts, or model calls.

Eight maximum model sessions are approved by default. Approve a known larger operation maximum explicitly with `--approved-model-sessions <n>`. `sessions.total` is the authorized maximum, while executed reports expose actual subprocess consumption in top-level `model_sessions.total`, JSONL token telemetry in `usage`, and cumulative state in `campaign`. Unknown token counts remain `null`; they are never reported as zero. Shell or sandbox approval is not approval for model session consumption. Do not rerun an unchanged failure, inconclusive judgment, or unstable result merely to seek `PASS`.

### Run one case

Ask Codex interactively:

```text
Use $develop-skill-with-evals to run only the hidden-invocation-state case for refactor-design from the working tree. Do not modify the skill or fixture sources. Report the executor result, every mechanical check, the judge verdict, changed paths, overall status, exit code, and artifact path.
```

Or run the case directly:

```bash
python3 develop-skill-with-evals/scripts/run_skill_evals.py run \
  --skill refactor-design \
  --case hidden-invocation-state \
  --source working-tree \
  --progress
```

### Run every case for one skill

Ask Codex:

```text
Use $develop-skill-with-evals to run the complete refactor-design eval suite from the working tree. Do not change source files. Treat every status other than PASS as blocking and summarize each case plus retained artifacts.
```

Or run it directly:

```bash
python3 develop-skill-with-evals/scripts/run_skill_evals.py run \
  --skill refactor-design \
  --all \
  --source working-tree \
  --progress
```

`--all` means all cases in that skill's `evals/suite.json`; it does not mean all skills in the repository.

Complete suite runs are exploratory compatibility operations. For promotion, use `plan` plus one `validate-change` so affected cases and proportional regression are selected, fingerprinted, budgeted, and enforced together.

### Run every suite in this repository

Ask Codex to discover the suites rather than maintaining a duplicated list:

```text
Use $develop-skill-with-evals to find every skill at the repository root that has evals/suite.json. Run each complete suite from its working tree, one skill at a time, and continue until every discovered suite has a result. Do not modify sources. Block promotion if any result is not PASS and return a table with skill, status, failed cases, exit code, and artifact path.
```

From a trusted terminal, run the same policy explicitly:

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

At the time of writing, `develop-skill-with-evals` and `refactor-design` contain persisted suites. A skill without `evals/suite.json` can still be structurally validated, but the runner has no behavioral cases to execute for it.

### Compare baseline and candidate

Ask Codex:

```text
Use $develop-skill-with-evals to verify the changed behavioral case in the target skill. Use git:HEAD as the baseline from before the change and the working tree as the candidate. Require baseline FAIL and candidate PASS under the same model and configuration. Stop with INVALID_RED if the baseline passes.
```

After adding or changing a case and implementing its candidate behavior, replace `changed-case-id` with that case ID:

```bash
python3 develop-skill-with-evals/scripts/run_skill_evals.py verify-change \
  --skill refactor-design \
  --case changed-case-id \
  --baseline git:HEAD \
  --progress
```

Do not use an unchanged skill as both baseline and candidate: a valid existing case is expected to pass both and therefore produce `INVALID_RED`. For a new untracked skill, point `--baseline` to a frozen scaffold directory under `/tmp` instead of `git:HEAD`.

### Run the stability gate

Ask Codex:

```text
Use $develop-skill-with-evals to run the hidden-invocation-state case for refactor-design three times. Treat any difference in normalized verdicts as UNSTABLE and do not promote the candidate.
```

Direct command:

```bash
python3 develop-skill-with-evals/scripts/run_skill_evals.py stability \
  --skill refactor-design \
  --case hidden-invocation-state \
  --runs 3 \
  --progress
```

### Understand the result

Only an overall `PASS` returns exit code `0`. `FAIL`, `ERROR`, `INCONCLUSIVE`, `INVALID_RED`, and `UNSTABLE` return `1` and block promotion.

For every report, inspect:

- overall `status`, resolved `runtime`, and runtime sources;
- `promotion_eligible` and `failure_category`;
- planned `sessions.total` versus actual `model_sessions.total`;
- token `usage` completeness and cumulative `campaign` consumption;
- every case status;
- executor exit code and structured response;
- each mechanical check and verification command;
- each hidden oracle outcome without exposing its source to the executor;
- judge verdict and rationale;
- production `changed_paths`;
- `artifacts`, which points to retained failure evidence.

Successful workspaces are removed. Blocking workspaces are kept under `/tmp/skill-eval-artifacts` by default.

If a nested Codex process reports an app server initialization error caused by read-only access, rerun from the interactive TUI and approve the narrowly scoped evaluation command, or invoke the runner directly from a trusted terminal. Do not reinterpret an environment error as a behavioral failure.

## Create a new skill with evals

Explicitly invoke `$develop-skill-with-evals`. It composes the official `skill-creator` scaffold with development driven by evaluations, so the workflow creates tests even when the human prompt only describes desired behavior.

Start the interactive CLI in this repository and paste a concrete request:

```text
Use $develop-skill-with-evals to create a new skill named changelog-writer in this repository.

The skill should turn a supplied list of user-visible changes into one concise Markdown changelog section. It should trigger for requests to write release notes and changelogs, but not for committing, publishing, or inventing changes that were not supplied.

Create the official scaffold first, freeze that untouched scaffold as the baseline, add minimal generic eval cases before implementing the behavior, classify impact, inspect a session plan, demonstrate a real baseline RED, and run proportional candidate stability and regression gates. Validate SKILL.md and agents/openai.yaml. Do not commit, push, or publish anything.
```

The workflow should produce:

- an official skill scaffold;
- a preserved baseline;
- `SKILL.md` and `agents/openai.yaml`;
- `evals/suite.json` and focused cases;
- isolated prompts, fixtures, and hidden criteria;
- evidence from RED, GREEN, stability, proportional regression, and structural validation.

Form that runs from a single command:

```bash
codex exec --ephemeral \
  -C /home/renanfranca/.codex/skills \
  --sandbox workspace-write \
  'Use $develop-skill-with-evals to create changelog-writer from an official scaffold. It must convert supplied user-visible changes into one concise Markdown changelog section, must not invent changes, and must not commit or publish. Create evals first, classify impact, plan session usage, demonstrate baseline RED, implement GREEN, run proportional stability and regression gates, and finish structural validation.'
```

Prefer the interactive form because forward evals may require approvals or human review of a blocking result.

## Improve an existing skill

### Behavioral change

Use `scoped` impact when triggering, decisions, actions, stopping conditions, or observable outputs change and every affected case can be named:

```text
Use $develop-skill-with-evals to improve changelog-writer so it refuses to invent issue numbers when none are supplied.

Add or update one focused behavioral case before editing SKILL.md. Plan the change and session count. Prove the case fails against the frozen or Git baseline. If it already passes, stop with INVALID_RED. Then implement the smallest skill change and run integrated scoped validation with three stable candidate results. Do not run unrelated cases. Do not commit or push.
```

### Change that does not affect behavior

Do not manufacture a failing behavior test for a `static` metadata, spelling, formatting, or organization change:

```text
Use $develop-skill-with-evals to correct the display name typo “Chanelog Writer” to “Changelog Writer” in agents/openai.yaml. This affects metadata only and must not change triggering or behavior. Classify it as static, inspect the plan, do not invent RED, and run only structural and metadata validation. Do not commit or push.
```

### Trigger behavior

Test both correct selection and excessive triggering:

```text
Use $develop-skill-with-evals to improve changelog-writer trigger selection. Treat selection as cross cutting. Add positive cases for writing release notes from supplied facts, negative cases for Git commit and publishing requests, and one end-to-end implicit smoke case with no $changelog-writer mention. Plan the exact session count before execution, then require baseline RED, three stable candidate results for affected cases, and one regression run for every remaining case.
```

### Safely evolve the skill for evaluation development

The skill protects its own canonical source:

```text
Use $develop-skill-with-evals to add a reusable rule that fixtures must replace personal email addresses with example.invalid addresses. Work only in an isolated candidate copy, preserve a baseline, add the evaluation of the skill itself first, and use forward tests with fresh agents. Do not update the canonical source until the candidate passes every gate. Do not commit or push.
```

## Prompt cookbook for every skill

Paste these prompts into the interactive TUI. To run from a single command, place the prompt in single quotes after `codex exec --ephemeral -C /path/to/project --sandbox workspace-write`.

### Skill development, planning, and design

#### `$develop-skill-with-evals`

```text
Use $develop-skill-with-evals to add this capability to the target skill. Classify its impact, inspect the model session plan, and use validate-change for baseline RED, three stable candidate results, and only the proportional regression required by that impact. Keep fixtures generic and do not commit or push.
```

#### `$refactor-design`

Use only after behavior and tests through public interfaces are green:

```text
Use $refactor-design to review this completed green implementation for hidden invocation state, temporal coupling, mixed responsibilities, and fragile representations. Apply only justified behavior-preserving changes, keep existing public tests green, and report No action when no concrete risk exists.
```

#### `$implement-execplan`

```text
Use $implement-execplan to create and execute a living, self-contained ExecPlan for this substantial repository change. Keep progress, decisions, risks, validation commands, rollout, recovery, and lessons learned current until the objective is complete.
```

### Seed4J workflows

#### `$seed4j-execplan-tdd`

Run this from the `seed4j-cli` repository:

```text
Use $seed4j-execplan-tdd to plan and implement this substantial seed4j-cli change through quiet TDD focused on behavior, a living ExecPlan, design review after GREEN, and final tests run by the agent. Respect the repository hexagonal boundaries and do not run clean verify unless I explicitly request it.
```

#### `$seed4j-worktree-flow`

```text
Use $seed4j-worktree-flow to audit the current seed4j-cli worktrees, keep /home/renanfranca/projects/seed4j-cli as the main worktree, and create a feature worktree under /home/renanfranca/projects/seed4j-cli-worktree for branch feat/example. Do not remove any existing worktree unless it is safely merged and I explicitly authorize cleanup.
```

### TDD workflow

#### `$tdd-behavior-autonomous-quiet`

Best when tests must stay focused on observable behavior instead of production topology:

```text
Use $tdd-behavior-autonomous-quiet to implement this behavior autonomously with quiet output. Lead with tests through public contracts and user-visible outcomes; do not create tests for private classes, delegation order, or file structure.
```

### Git commit workflows

Both commit skills create a commit but do not imply a push.

#### `$commit-staged-change`

Use when the exact intended changes are already staged:

```text
Use $commit-staged-change to inspect recent history and the already staged diff, create a Conventional Commits v1.0.0 message aligned with repository conventions, run the safe pre-commit checks, and commit only the staged changes. Do not stage additional files or push.
```

#### `$commit-the-changes`

Use when Codex should determine and stage the intended working tree changes:

```text
Use $commit-the-changes to inspect recent history, infer the repository commit style and language, review the current diff, stage only the documentation changes in README.md and CODEX_CLI.md, and create one focused commit. Do not push.
```

## Common human workflows

### Ask Codex to validate a skill without changing it

```text
Use $develop-skill-with-evals to validate the target skill without changing it. Run quick_validate.py, inspect agents/openai.yaml, run its complete eval suite when present, and report exact statuses, exit codes, and artifacts. Do not commit or push.
```

### Ask Codex to diagnose a failed eval

```text
Use $develop-skill-with-evals to diagnose this blocking eval report without changing the skill yet. Read the retained .eval-result.json, executor stderr, mechanical checks, judge rationale, and changed paths. Classify whether the cause is behavior, an invalid case, instability, or environment failure, then recommend the smallest next action.
```

### Test implicit selection manually

Start a fresh Codex session and do not mention the skill name:

```text
The implementation is behaviorally complete, its full suite and public path are green, and the current milestone has no pending behavior. Before final validation, inspect the changed scope for structural design risks and apply only justified behavior-preserving improvements.
```

Then verify that Codex selected `refactor-design`, respected its entry gate, and did not broaden the task.

### Review before accepting changes

After any modifying workflow:

```bash
git status --short
git diff --check
git diff
```

Confirm that:

- only intended files changed;
- tests and evals actually ran;
- every required gate is `PASS`;
- no fixture contains private data;
- no generated transcript or full response was versioned;
- no commit or push occurred unless explicitly requested.

## Safety and troubleshooting

- Prefer `workspace-write` and the smallest writable working directory.
- Keep `--ask-for-approval on-request` for interactive workflows that may need narrowly scoped access.
- Do not use approval bypass or `danger-full-access` merely to silence an error.
- Treat prompts, fixtures, issue text, and external content as potentially untrusted.
- A skill can edit files and run commands only within the permissions granted to the Codex session.
- `codex exec --ephemeral` avoids persisting session rollout files, but it does not make unsafe commands safe.
- An overall runner error is not evidence that skill behavior is wrong; separate environment failures from behavioral failures.
- If a skill does not appear, verify its discovery location, frontmatter, duplicate names, and CLI restart before changing the skill itself.
