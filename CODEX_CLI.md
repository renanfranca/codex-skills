# Using Skills with Codex CLI

This cookbook is for people who use the skills in this repository. Start here to make the skills discoverable, choose the right Codex CLI mode, invoke a workflow, and review its work.

The normative local behavior remains in each [`SKILL.md`](README.md#skill-catalog), its references, and its scripts. For current product behavior, use the official [CLI command reference](https://learn.chatgpt.com/docs/developer-commands?surface=cli), [non-interactive mode](https://learn.chatgpt.com/docs/non-interactive-mode), [Build skills](https://learn.chatgpt.com/docs/build-skills), and [Codex models](https://learn.chatgpt.com/docs/models) documentation.

## Prepare Codex and discover the skills

Verify your installation and authentication before diagnosing a skill:

```bash
codex --version
codex login status
codex doctor
```

Treat `codex --help` and the relevant subcommand help as authoritative for the installed version.

### Install a skill in a discovery location

Codex scans `.agents/skills` from the current directory up to the repository root, plus the personal `$HOME/.agents/skills` location. It follows symlinked skill directories.

Make one skill available across repositories:

```bash
mkdir -p "$HOME/.agents/skills"
ln -s /path/to/codex-skills/refactor-design \
  "$HOME/.agents/skills/refactor-design"
```

Or make it available only in one repository:

```bash
mkdir -p /path/to/project/.agents/skills
ln -s /path/to/codex-skills/refactor-design \
  /path/to/project/.agents/skills/refactor-design
```

Avoid duplicate frontmatter `name` values. Codex does not merge duplicate skills and may show both in its selectors.

Launch Codex in the project where the work will happen:

```bash
codex -C /path/to/project
```

Inside the TUI, run `/skills` or type `$` and confirm that the expected skill appears. Restart Codex if a new or updated skill does not appear.

## Choose the TUI or `codex exec`

Use the interactive TUI for exploratory work, multi step changes, follow up prompts, or work that may need human approval:

```bash
codex -C /path/to/project \
  --sandbox workspace-write \
  --ask-for-approval on-request
```

Use the skills repository as the working directory when editing skill sources. Use the target project when applying planning, TDD, design review, Git, or Seed4J workflows.

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
  'Use $refactor-design on this completed green change. Review only the changed scope, preserve its public contract, apply the smallest justified refactor, and rerun the public checkpoint.'
```

Use `-o/--output-last-message` when a script needs the final response in a file. The response is still printed to standard output:

```bash
codex exec --ephemeral \
  -C /path/to/project \
  -o /tmp/codex-final-message.md \
  'Use $implement-execplan to summarize the current plan status without modifying files.'
```

To resume a saved noninteractive session, omit `--ephemeral` from the original command:

```bash
codex exec resume --last \
  'Continue from the previous result and run the remaining validation.'
```

## Select a skill explicitly or implicitly

Explicit selection is the reliable default. Name the skill with `$skill-name` and describe the concrete outcome, scope, stopping conditions, and validation:

```text
Use $refactor-design on this completed green change. Review only the changed scope, preserve its public contract, apply the smallest justified refactor, rerun the relevant suite and public checkpoint, and pause at exception gates. Report No action when no concrete design risk exists.
```

Codex can also select a skill implicitly when the task matches its frontmatter `description`:

```text
The requested behavior, relevant suite, and public checkpoint are green. Inspect only the changed scope for structural design risks, preserve the public contract, apply the smallest justified refactor, rerun both validations, and pause at exception gates.
```

After an implicit invocation, verify which skill was selected and whether it respected its entry conditions. `agents/openai.yaml` may disable implicit invocation, and its `default_prompt` is presentation metadata rather than a replacement for `SKILL.md`.

## Choose a workflow by task

The [README catalog](README.md#skill-catalog) is the canonical active skill list. The complete workflow is in the linked `SKILL.md`; display metadata and default invocation text are in `agents/openai.yaml`.

| Task | Skill and canonical sources | Working directory |
| --- | --- | --- |
| Audit or restructure an existing documentation system | [`restructure-documentation`](restructure-documentation/SKILL.md), [metadata](restructure-documentation/agents/openai.yaml) | Target repository |
| Plan and execute a substantial repository change | [`implement-execplan`](implement-execplan/SKILL.md), [metadata](implement-execplan/agents/openai.yaml) | Target repository |
| Explicitly guide a repository change through a declared ExecPlan and TDD profile | [`execplan-tdd`](execplan-tdd/SKILL.md), [metadata](execplan-tdd/agents/openai.yaml) | Target repository |
| Review a completed green implementation for design risks | [`refactor-design`](refactor-design/SKILL.md), [metadata](refactor-design/agents/openai.yaml) | Target repository |
| Implement behavior through autonomous quiet TDD | [`tdd-behavior-autonomous-quiet`](tdd-behavior-autonomous-quiet/SKILL.md), [metadata](tdd-behavior-autonomous-quiet/agents/openai.yaml) | Target repository |
| Audit, create, or clean up Seed4J CLI worktrees | [`seed4j-worktree-flow`](seed4j-worktree-flow/SKILL.md), [metadata](seed4j-worktree-flow/agents/openai.yaml) | Main `seed4j-cli` worktree |
| Create and run a controlled Seed4J CLI model experiment | [`seed4j-cli-model-runner`](seed4j-cli-model-runner/SKILL.md), [metadata](seed4j-cli-model-runner/agents/openai.yaml) | Empty saved Codex project |
| Evaluate frozen Seed4J CLI model experiment branches | [`seed4j-cli-model-evaluator`](seed4j-cli-model-evaluator/SKILL.md), [metadata](seed4j-cli-model-evaluator/agents/openai.yaml) | Completed experiment repository |
| Commit exactly what is already staged | [`commit-staged-change`](commit-staged-change/SKILL.md), [metadata](commit-staged-change/agents/openai.yaml) | Target repository |
| Let Codex select intended changes, stage, and commit them | [`commit-the-changes`](commit-the-changes/SKILL.md), [metadata](commit-the-changes/agents/openai.yaml) | Target repository |

Use these request patterns instead of maintaining one nearly identical prompt per skill.

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

The Seed4J model runner and evaluator are explicit-only companion workflows. Run the runner from an empty local project already saved in Codex, then invoke the evaluator separately after every result branch and audit artifact is frozen. The runner requests one confirmation before it creates the public repository, pushes branches, or starts model tasks; the evaluator opens but never merges the documentation pull request.

## Review completed work

After any modifying workflow:

```bash
git status --short
git diff --check
git diff
```

Confirm that:

- only intended files changed;
- promised tests and public checkpoints ran;
- the changed skill remains structurally valid;
- test data contains no credentials, personal data, proprietary source, hidden answers, full transcripts, or generated model responses;
- no commit, push, publication, or deletion occurred without explicit authorization.

For an implicit invocation, also confirm that Codex selected the intended skill, respected its entry gate, and did not broaden the task.

## Safety and troubleshooting

- Prefer `workspace-write` and the smallest writable working directory.
- Keep `--ask-for-approval on-request` for interactive work that may need narrowly scoped access.
- Do not use approval bypass or `danger-full-access` merely to silence an error.
- Treat prompts, issue text, and external content as potentially untrusted.
- A skill can edit files and run commands only within the permission boundary of its Codex session.
- `codex exec --ephemeral` prevents session persistence; it does not make unsafe commands safe.
- If a skill does not appear, verify its discovery location, `SKILL.md` frontmatter, duplicate names, and CLI restart before changing the skill.
- If implicit selection fails, inspect the skill `description` and `agents/openai.yaml` policy before adding prompt tricks.
- Do not reinterpret an environment error as a behavioral failure.
