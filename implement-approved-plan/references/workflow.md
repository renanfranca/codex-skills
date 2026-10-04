# Serialized role and worker workflow

## Startup

1. Read the approved plan and target repository instructions completely. Before creating a worker, branch, or ledger, inspect the repository's build/test scripts, manifests, analysis configuration, hooks, and CI workflows. Resolve which checks are explicitly required by the plan.
2. Build the validation inventory below. Check local command and service availability without installing tools or changing tracked files. Treat a configured check that cannot run in its intended environment as a startup blocker; show the failed prerequisite and command. CI-only checks require a configured CI workflow, not a local executable.
3. Show the inventory, exclusions, role owners and resulting worker distribution, marking every optional role active or inactive. Use one initial confirmation for checks, the default current-chat primary or explicit delegation, grouping and model/effort pairs, including inactive workers. Resolve requested changes before ledger initialization or delegated task creation. For a resumed schema-v5/v6 ledger, use the recorded inventory and reassess before the next validation gate; older ledgers retain their original rules.
4. Apply [approved-plan-title-bootstrap](../../approved-plan-title-bootstrap/SKILL.md) after distribution confirmation. In a new single-chat run, set and verify `<prefix>-primary` (or the confirmed custom worker ID) before initializing the ledger or registering the current chat. For delegation, verify `<prefix>-boot` before creating chats, pass the complete title contract in Coordinator's initial context, and verify `<prefix>-<worker-id>` before that worker's registration; Coordinator verifies its own title before ledger initialization. Do not continue after an unverified rename. Resumes verify existing titles and keep recorded identities/topology; never restart bootstrap or derive a new prefix.
5. Read [github-delivery.md](github-delivery.md) and inspect prior ledgers before creating or reusing a branch. Clean only plans whose recorded pull requests GitHub confirms as `MERGED`.
6. Require a clean checkout apart from ignored `.agent/tmp` state. Do not stash, discard, or absorb unrelated changes. Create or reuse the plan's clean feature branch from its declared base; never delete a branch automatically.
7. Resolve the base once with `git rev-parse --verify '<base>^{commit}'`, retain the full 40-character SHA as `base_sha`, and do not refresh it if the base ref later moves.
8. Add `/.agent/tmp/` to `.git/info/exclude` if absent. Store the plan verbatim at `.agent/tmp/<slug>.md`, the confirmed inventory at `.agent/tmp/<slug>.validation.json`, and the internally generated confirmed worker JSON at `.agent/tmp/<slug>.workers.json`. Store complementary collectors at `.agent/tmp/<slug>.collectors.json` without changing the inventory schema. Always initialize the schema-v6 ledger with the explicit confirmed `--worker-plan` after title verification. Do not alter `.gitignore` for local workflow state.
9. In the default path, register `primary` with the invoking chat ID and its actual current model/effort; continue here without creating chats or self-messaging. For explicit delegation, register the worker containing Coordinator and create/register each worker containing an always active role (Implementer, Committer, Validator or Structural Reviewer). Create workers containing only Habit Curator and/or Mutation Analyst when their local checks are selected. Reuse any worker already registered for another role. Verify each title before registration, including optional workers activated later. The ledger rejects `implementing` or `implemented` until every currently required worker has its exact pair.

## Validation discovery and routing

Use repository configuration and the approved plan as sources of truth. Installed but unconfigured tools are not selected. Inspect relevant project scripts, build profiles/plugins, test and coverage configuration, Sonar settings, Habit hook configuration and scanned files, mutation runner configuration, and CI workflows. For each proposed check, show its source, exact local command or CI check, ability to run, and owner. Route tests, lint, coverage, static analysis, and local Sonar to the Validator; configured local mutation testing to the Mutation Analyst; configured local Habit hooks to the Habit Curator; and CI-only checks to the Coordinator. The Committer owns commit-message checks, and the Structural Reviewer owns code review rather than a project validation tool.

The inventory is a JSON object with a `checks` array. Every entry has string fields `id`, `kind` (`verify`, `sonar`, `mutation`, `habit`, or `ci`), `status` (`selected` or `skipped`), `execution` (`local`, `ci`, or `none`), `command`, `source`, `owner`, and `reason`. Use a unique `id` and a concrete configuration path or plan clause in `source`. Selected local checks require an executable `command` and empty `reason`; selected CI checks use `execution: ci`, may leave `command` empty, and have `owner: coordinator`. Skipped checks use `execution: none`, an empty command, and a concrete reason. Include exactly one Sonar, mutation, and Habit entry each, selected or skipped. Include one or more selected verification entries, or one skipped verification entry explaining why no automated local or CI verification applies. General CI checks may have `kind: ci`. This inventory is confirmed evidence, not a request to install or configure missing tools.

Reinspect the configuration before initial and final validation. If it changed, show the delta and obtain confirmation. Return through `implementing` with a Coordinator note, update the inventory under its lease, reuse its registered worker or create/register a newly required optional worker once, and repeat downstream gates. A check required by the approved plan cannot be silently removed. If a selected check becomes unavailable, block with diagnostic evidence; do not relabel it `not-applicable` or claim a pass. A selected check without applicable production changes may still record the existing `no-production-changes` mutation result. After a pull request, monitor every selected CI check by its inventory ID.

## Conversational worker selection

For every new plan, propose `primary` with all seven role IDs and the invoking chat's actual model/effort. `gpt-6.1-sol`/`medium` is a recommendation only. The user does not need to switch models or supply JSON. Resolve the actual current chat ID/settings through session metadata or configured tools; request missing metadata if unavailable, never fabricate it. Register this same chat and continue its work locally.

Offer delegated specialists as an explicit alternative, for example `implementation` (Coordinator + Implementer), `quality` (Committer + Validator + Mutation Analyst + Habit Curator), and `structural-review` (Structural Reviewer). No delegated partition or pair is mandatory. Resolve the saved project only when creating delegated workers. Accept conversational grouping, splitting or pair choices before the existing initial confirmation; splits inherit the source pair, and merging different pairs requires resolving the pair. Each of the seven roles belongs to exactly one nonempty worker with a unique kebab-case ID and one model/effort pair.

Present optional roles as active/inactive based on discovery even when grouped in `primary`. Explain that default validation and review share implementation context. Separate contexts can be chosen when independent review matters; never describe same-context review as independent. This disclosure needs no separate confirmation.

For delegated workers, verify exact pair availability, including wholly inactive workers, and Full access (`sandbox_mode = "danger-full-access"`, `approval_policy = "never"`) before creating local chats. Do not substitute settings. The invoking chat's own active pair needs no new callability probe or worker creation. Generate `.agent/tmp/<slug>.workers.json` internally and always pass `init --worker-plan`, including for `primary`. The offline script's old no-flag default remains compatible for other callers; the skill never uses it for a new run.

Resume v6 using immutable `worker_selection` and registered `workers`. Resume v1–v5 with recorded `chats`, defaults and `model_selection` where applicable. Never migrate a resumed run, select settings again, or collapse existing workers to `primary`.

## Role contracts and persistent workers

| Active role | Contract |
| --- | --- |
| `coordinator` | Own assignments, ledger leases, gates and delivery; do not create another worker containing Coordinator. |
| `implementer` | Use `$tdd-behavior-autonomous-quiet`; implement only assigned behavior; do not commit. |
| `committer` | Use `$commit-the-changes` for history, convention, language, message and staging of the assigned delta; new v6 runs execute and record through `commit-staged`. |
| `validator` | Use the deterministic executor for selected local verification and Sonar checks, then interpret evidence; record absence of local checks when applicable; do not edit source. |
| `habit-curator` | Use the deterministic executor for selected local Habit hooks, classify findings and report evidence. Never use `$refactor-design`, self-authorize work or commit. If sharing a worker with Validator, route every code correction to Implementer. Otherwise edit only deterministic, low-risk corrections explicitly assigned by Coordinator, with authorized files and expected evidence. |
| `mutation-analyst` | Use the deterministic executor for at most one configured runner per attempt, classify every survivor and no-coverage case and persist complete output under `.agent/tmp`; never edit code, install tools or commit. |
| `structural-reviewer` | Use `$refactor-design` for exhaustive review of changed contracts and adjacent responsibilities; do not commit. Claim independence only when its worker differs from Implementer's. |

For a confirmed delegated distribution, create one chat per required worker in the saved project's existing checkout and register its returned thread ID immediately with `register-worker`. The worker containing Coordinator conducts the workflow and executes any of its other roles locally, without messages to itself. Register Coordinator's worker and all mandatory workers before `implementing`. Create a wholly optional worker only when its local check is selected. On later activation, reuse an existing worker that already contains the role or register its configured worker before leaving `implementing`. Reuse each chat across phases; never create extra chats per role, change a registered identity, model or effort, or let workers coordinate with one another.

Coordinator is the sole communication hub and lease operator. In `primary`, assignments are local role transitions; do not message this chat or create another Coordinator. Before each assignment, load that role's required skill and the references relevant to the current phase; state the active role, repository path, branch, plan path, `base_sha`, phase, authorized files, lease owner and expected evidence. A worker's earlier instructions remain in history: distinguish role-local restrictions from workflow-wide prohibitions explicitly. For example, Validator's “do not edit source” applies while acting as Validator; switching to Committer requires a released Validator lease and an explicit Committer assignment. Switching roles never relaxes human authorization or scope boundaries.

Acquire `--owner <role>` before checkout work, dispatch only that role, wait until it is idle, inspect its result and working tree, and release before the next role. For local roles, apply the same contract and lease sequence without dispatch. Leases remain exclusive even for two roles in the same worker; a Validator lease cannot record Committer, Habit or mutation evidence. Keep every gate and artifact attributed to its logical role regardless of grouping.

## Commit message contract

Before dispatching the Committer, inspect the repository instructions, recent relevant commit history, and available commit-message lint configuration. Preserve the observed type and scope convention, language, capitalization, tense, and naming. Resolve the effective maximum line length separately for the header, body, and footer; use 100 characters for any part without a repository-defined limit. Reflow prose at word boundaries without truncating, omitting, or replacing its content.

Every commit created by this workflow requires a body with these three semantic fields. Translate both the labels and their content into the repository's observed commit language; the English labels below are the canonical example:

```text
type(scope): summary in the repository's observed style

- Motivation: Explain why the change is needed.
- Avoided: Name the concrete risk or undesirable outcome avoided.
- Improvement: State what becomes better after the change.
```

Keep these bullets and their wrapped continuation lines in the body. Start the footer after a blank line and reserve it for actual trailers. For refactoring commits, append two more body fields:

```text
- Behavior preserved: Identify the public behavior that remains unchanged.
- Validation: Name the evidence that verifies the preserved behavior.
```

This workflow-specific body requirement overrides `$commit-the-changes`' ordinary preference to omit bodies when similar repository commits do not use them.

Classify every proposed commit as breaking or non-breaking. Use breaking markers only for a real incompatible behavior that requires consumers to migrate. When the repository uses Conventional Commits, a breaking commit requires both the `!` marker and the `BREAKING CHANGE:` trailer, even though the specification permits either marker independently:

```text
feat(scope)!: imperative summary

- Motivation: Explain why the incompatible change is needed.
- Avoided: Name the concrete risk or undesirable outcome avoided.
- Improvement: State what becomes better after the change.

BREAKING CHANGE: Explain the incompatible behavior and required migration.
Continue the explanation on wrapped lines when necessary.
```

Treat `feat(scope)` as illustrative: use the type, optional scope, and subject style supported by the repository. Keep the `BREAKING CHANGE:` token in English so parsers recognize it, but write its explanation in the observed language. Non-breaking commits must contain neither `!` nor `BREAKING CHANGE:`. In repositories that do not use Conventional Commits, preserve their observed breaking-change convention instead of introducing these markers.

Each Committer prompt must state the observed convention and language, the effective header/body/footer limits, that the body is required, the breaking classification, and the exact command available to validate the complete candidate message. If no candidate-message validation command is available, state that explicitly instead of fabricating one. Native pre-validation supplements normal Git hooks; never use `--no-verify`, `HUSKY=0`, or an equivalent bypass.

Compose [commit-the-changes](../../commit-the-changes/SKILL.md) for preparation. Only within this workflow, replace its commit execution and success-reporting steps with [commit-staged](ledger.md#execute-and-record-staged-commits). The standalone skill is unchanged. For every new v6 run, save the complete candidate under `.agent/tmp`, pass its discovered line limits and native validation command to the executor, and use a unique attempt ID. The executor never stages files; it validates the snapshot, runs native validation when configured, then invokes `git commit` once with normal hooks and verifies exit code, new SHA, parent, prepared tree, effective message and resulting checkout before recording.

Only a zero exit with `status: recorded` authorizes Committer's completion, lease release and phase advancement. A failure preserves the current phase and artifacts; do not follow it with `record-commit` or another manual commit. If Git committed but ledger persistence failed, repeat the same attempt ID with identical inputs to verify the existing commit and finish only its registration. Divergent inputs, HEAD, branch or checkout block recovery. An already invoked failed/uncertain attempt never retries Git; investigate its journal/log before an explicitly new attempt. No amend or rebase. Existing v1–v5 executions retain their `record-commit` procedure and must still confirm Git success before recording or advancing.

## Focal mutation scope

For every executed mutation attempt, compare `base_sha` with the commit being analyzed using rename detection. Select production files whose destination path is added, modified, or renamed. Exclude deleted paths, tests, fixtures, generated documentation, prose documentation, and anything outside the repository's production source roots. On a final rerun, recompute the complete target set from `base_sha`; do not mutate only the delta since the initial attempt and do not filter by changed lines.

For PIT, map each selected Java source to its package-qualified top-level class and append `*`, for example `com.example.OrderService*`. Pass those globs through `targetClasses`; do not narrow `targetTests`, so every eligible test can kill the selected mutants. The [PIT Maven quickstart](https://pitest.org/quickstart/maven/) documents `targetClasses` globs and explains that the final `*` includes inner classes.

Before running, write a canonical, deterministically ordered input manifest to the attempt log. Hash it with SHA-256. The manifest includes:

- each selected production path and its blob SHA at `analyzed_sha`;
- every test eligible to exercise the targets in their affected modules, with path and blob SHA;
- mutation-runner configuration, plugin/version inputs, profiles, and the exact normalized runner command.

This digest is the attempt `fingerprint`. For PIT, all tests eligible in the affected Maven modules belong in the manifest because only `targetClasses` is narrowed. If repository-specific configuration makes a smaller test set genuinely eligible, record that rule and evidence in the log.

The Mutation Analyst invokes the deterministic executor once per attempt with the configured mutation command. Store the canonical input manifest, complete logs, XML and HTML reports under `.agent/tmp`; for PIT request XML alongside HTML through the confirmed execution configuration when necessary. Do not narrow `targetTests`, use changed-line filtering, or repeat commands automatically. The executor returns individual mutants and metrics; the chat must classify every survivor and no-coverage case before recording evidence. Its execution fingerprint does not replace the focal mutation manifest or ledger reuse comparisons. Its response to the Coordinator contains only analyzed SHA and scope, fingerprint, metrics, classifications, result, and artifact paths; it does not paste raw runner output into chat.

For a new schema-v6 run, exclude mutation testing during discovery when no configured runner exists; the inventory records the reason and both mutation phases are skipped. If a selected runner has no changed production class, record `not-applicable` with `no-production-changes`. A selected runner that becomes unavailable blocks the gate. Never install a runner automatically, describe absence as `passed`, or create a synthetic green report. Schemas v3/v4 keep their original `runner-unavailable` evidence rule; v5 already uses inventory exclusions.

## Main sequence

1. Transition to `implementing`. Give the Implementer one behavior-focused assignment. It runs RED/GREEN/refactor cycles, the full relevant suite every cycle, and a public-path checkpoint at least every two cycles. After the assigned behavior and focused tests are green, release its lease and transition to `implemented`.
2. If local Habit hooks were selected, transition to `habit-checking`, give the Habit Curator a quick check under its lease, and record terminal evidence. If no files are configured, reassess the inventory and route back through `implementing`. Otherwise go directly to `checkpoint-committing`.
3. Route Habit findings through the Coordinator. When Habit Curator shares a worker with Validator, assign every code correction to Implementer. When their workers differ, only deterministic, low-risk, explicitly scoped corrections may return to Habit Curator. Any source correction returns through `implementing` and repeats every downstream gate.
4. Transition to `checkpoint-committing`. Under the commit message contract, the Committer prepares the complete checkpoint as `implementation` or `correction` with `$commit-the-changes` and executes `commit-staged` in new v6 runs. Only after proven, recorded success release the lease and transition to `initial-validating`.
5. Reassess the inventory. The Validator uses [validation-runner.md](validation-runner.md) to execute every selected local verification and local Sonar check in sequence, then analyzes counts, states, metrics, diagnostics and conclusion excerpts against the required criteria before recording gates. Additional reads must answer a specific failure, question or omission. Preserve command breadth: `./mvnw clean verify` stays the complete check. Missing, invalid, stale required reports or cancellation block a pass. Sonar follows its discovered local/CI location; never run a CI-only check locally. Record `initial-verify` as `passed` only if all selected local verification commands pass, otherwise record a documented `not-applicable` when there are none. Record `initial-sonar` only when local Sonar is selected. CI-only checks wait for CI.
6. If local mutation testing was selected, transition to `mutation-testing`. The Mutation Analyst selects every production class changed from `base_sha`, computes the fingerprint, and records exactly one attempt. `structural-review` requires a current accepted `passed` or `not-applicable` result. If mutation was excluded, transition directly to `structural-review`. A failed, incomplete, or actionable selected attempt blocks progress.
7. Transition to `structural-review`. The Structural Reviewer applies `$refactor-design` and may make only behavior-preserving refactors authorized by the plan and Coordinator. It does not commit.
8. Consolidate the repository's acceptance documentation, implementation outcomes and available evidence before the last commit and final gates. Include any documentation delta when deciding whether a final commit is needed. If local Habit hooks were selected, transition to `habit-rechecking` and record fresh terminal evidence; otherwise skip that phase. For a reviewed/documentation delta, use `final-committing`, prepare a `correction`, `habit-refactor`, or `structural-refactor` commit under the message contract, and execute `commit-staged` in new v6 runs. Release and advance only after proven, recorded success. Without a delta, transition directly to `final-validating`.
9. Reassess the inventory. The Validator reruns all selected local verification and Sonar checks on the final commit and records current `final-verify` plus `final-sonar` when selected.
10. If local mutation testing was selected, transition to `mutation-rechecking`. Recompute the focal target set and fingerprint against the same `base_sha`. Reuse accepted initial evidence only when all inputs match; otherwise run the configured runner once against all selected production targets. If mutation was excluded, transition directly to `delivery-ready` after final validation.
11. Transition to `delivery-ready` only with current evidence for every selected local gate. Follow [github-delivery.md](github-delivery.md) for human choices, pull request, CI, and cleanup.

## Mutation classifications and routing

Every `survived` or `no-coverage` mutant in a completed run must have one unique ID, one classification, and a concrete justification. The mutation gate is accepted only when the runner has no execution error, killed/surviving/uncovered metrics account for every generated mutant, every survivor or uncovered mutant is classified exactly once, and actionable findings equal zero. An interrupted environmental failure may preserve partial metrics without pretending its unfinished mutants were classified.

- `behavior-gap`: actionable; return to the Implementer through the behavior-focused TDD path.
- `dead-code` or `redundant-code`: actionable; the Coordinator assigns the correction to the registered Structural Reviewer while the ledger returns through `implementing`. The formal `structural-review` phase remains blocked until a repeated mutation attempt is accepted.
- `equivalent`: non-actionable only with a concrete explanation of why no observable test can distinguish it.
- Environmental runner failure: record `failed` with diagnostic evidence and no code change; return diagnosis to the Coordinator. A selected runner cannot be relabeled unavailable to bypass the gate.

Every correction uses a non-empty Coordinator routing note, returns to `implementing`, creates only additional commits, and repeats the applicable selected gates from the checkpoint onward. Never amend or rebase corrective work.

## Habit evidence

- `clean`: raw finding count is zero.
- `ratcheted`: a previously user-authorized baseline is unchanged and active finding count is zero.
- `snoozed`: the user explicitly authorized the already-existing snoozed state. Never create or modify snooze state in this workflow.
- `not-applicable`: retained for older ledgers when the Habit tool is genuinely unavailable. Schemas v5/v6 exclude unconfigured Habit hooks during discovery and blocks a selected hook that becomes unavailable.

`no-configured-files` means Habit ran but scanned nothing. For schemas v5/v6, reassess the inventory and return through `implementing`; do not record a synthetic clean result. Older ledgers retain their original observation and gate rules.
