# Workflow ledger

Use `scripts/workflow_state.py` with Python's standard library. Keep the plan, ledger, and mutation artifacts under the repository's ignored `.agent/tmp` directory.

```text
python3 <skill>/scripts/workflow_state.py --state .agent/tmp/<slug>.workflow.json <command> ...
```

New ledgers use schema v3. Existing schema-v1 and schema-v2 ledgers remain readable and retain their original validation, transitions, evidence, pull-request, and cleanup rules. Reading an old ledger does not migrate, normalize, or rewrite it. The script uses atomic replacement and rejects corrupt state, conflicting identities, invalid transitions, conflicting leases, specialist fallback, incomplete mutation classifications, unjustified reuse, premature pull requests, repeated transient CI retries, and cleanup without a matching GitHub `MERGED` confirmation.

## Initialize and inspect

Resolve the declared base ref once and pass its full commit SHA:

```text
base_sha=$(git rev-parse --verify '<base>^{commit}')
python3 <skill>/scripts/workflow_state.py \
  --state .agent/tmp/<slug>.workflow.json \
  init --slug <slug> --plan .agent/tmp/<slug>.md \
  --repo <absolute-repo> --branch <branch> --base <base> --base-sha "$base_sha"
python3 <skill>/scripts/workflow_state.py \
  --state .agent/tmp/<slug>.workflow.json show
```

`base` preserves the plan's branch/ref name; `base_sha` is a 40-character immutable comparison point and is part of the ledger identity. `init` is idempotent only for the same slug, paths, repository, branch, base, and `base_sha`.

## Register and serialize specialists

```text
register-chat --role <role> --thread-id <id> --model <exact-model> --effort xhigh
acquire --owner <coordinator-or-role>
release --owner <same-owner>
```

Acquire before dispatching any task that reads or mutates the checkout. A second owner is rejected. CI and GitHub status queries do not need the checkout lease; source-changing corrections do.

Schema v3 requires these exact registrations before the first `implementing` transition:

| Role | Model | Effort |
| --- | --- | --- |
| `implementer` | `gpt-5.6-sol` | `xhigh` |
| `committer` | `gpt-5.6-terra` | `xhigh` |
| `validator` | `gpt-5.6-luna` | `xhigh` |
| `habit-curator` | `gpt-5.6-luna` | `xhigh` |
| `mutation-analyst` | `gpt-5.6-luna` | `xhigh` |
| `structural-reviewer` | `gpt-5.6-sol` | `xhigh` |

Every task ID must be non-empty. Register each role once and reuse it. Roles and leases introduced by v3 are rejected by v1/v2 ledgers.

## Phases and ordinary evidence

```text
transition --to <phase> [--note <Coordinator-routing-evidence>]
record-commit --sha <sha> --kind <kind> --subject <subject>
record-gate --name <initial-verify|initial-sonar|final-verify|final-sonar> --status <passed|failed|not-applicable> --details <observed-result> [--url <url>]
record-habit --status clean --details <evidence> --finding-count 0
record-habit --status ratcheted --details <evidence> --finding-count N --active-finding-count 0 --baseline-authorized --baseline-unchanged
record-habit --status snoozed --details <evidence> --finding-count N --user-authorized-snooze
record-habit --status not-applicable --details <evidence> --tool-unavailable
record-habit-observation --kind no-configured-files --details <evidence> [--reclassify-current]
```

Commit recording requires the `committer` lease; clean-verification and Sonar gate recording require `validator`; terminal Habit recording requires `habit-curator`; Habit observation and pull-request recording require `coordinator`. Terminal Habit stage is inferred from `habit-checking` or `habit-rechecking`. Legacy freeze controls remain rejected for schema v3.

The schema-v3 forward phases are:

```text
initialized -> implementing -> implemented -> habit-checking
-> checkpoint-committing -> initial-validating -> mutation-testing
-> structural-review -> habit-rechecking
-> [final-committing ->] final-validating -> mutation-rechecking
-> delivery-ready -> pr-open -> ci-monitoring -> ready-for-merge -> merged
```

Use `final-committing` only when post-review work changed the checkout; the direct `habit-rechecking -> final-validating` path means no delivery delta. Any correction returns to `implementing` with a non-empty Coordinator note and repeats all downstream gates. Schema v3 intentionally has no corrective shortcut from final validation to Habit or structural review.

Current quick Habit evidence is required before the checkpoint, a current checkpoint commit before initial validation, current passed clean/Sonar gates before each mutation phase, fresh terminal Habit evidence after review, and a current final commit when the reviewed tree has a delta. Earlier attempts cannot satisfy a repeated phase.

## Record mutation attempts

`record-mutation` is schema-v3-only and requires the `mutation-analyst` lease during `mutation-testing` or `mutation-rechecking`. The phase infers `stage` as `initial` or `final`.

An executed attempt records one runner invocation:

```text
record-mutation \
  --runner pit --result passed \
  --analyzed-sha <40-character-commit-sha> \
  --fingerprint <64-character-sha256> \
  --target-class 'com.example.OrderService*' \
  --generated N --killed N --survived N --no-coverage N \
  --execution-errors 0 \
  --classification-file .agent/tmp/<attempt>-classifications.json \
  --log .agent/tmp/<attempt>.log \
  --report .agent/tmp/<attempt>-report \
  --details <concise-result>
```

Repeat `--target-class` and `--report` when needed. `runner=pit` rejects a target without the final `*`, preserving inner-class coverage. Log, classification file, and reports must already exist under `<repository>/.agent/tmp`; external paths and missing artifacts are rejected. `passed` requires at least one production target and report.

The classification file is a JSON list. Each surviving or uncovered mutant appears exactly once:

```json
[
  {
    "mutant_id": "OrderService.java:42:NEGATE_CONDITIONALS",
    "outcome": "survived",
    "classification": "equivalent",
    "justification": "The constructor normalizes both branches before observation."
  }
]
```

`outcome` is `survived` or `no-coverage`. `classification` is `behavior-gap`, `dead-code`, `redundant-code`, or `equivalent`. IDs must be non-empty and unique; every justification must be non-empty and concrete. Counts by outcome must equal `survived` and `no_coverage`. `behavior-gap`, `dead-code`, and `redundant-code` contribute to `actionable_findings`; `passed` requires zero actionable findings, `execution_errors=0`, and `generated = killed + survived + no_coverage`.

Record absence without claiming a green execution:

```text
record-mutation \
  --runner pit --result not-applicable \
  --analyzed-sha <sha> --fingerprint <fingerprint> \
  --not-applicable-reason <runner-unavailable|no-production-changes> \
  --log .agent/tmp/<attempt>.log --details <explicit-reason>
```

`runner-unavailable` may retain the selected targets to show what could not run. `no-production-changes` requires an empty target list. Both require zero metrics, no classifications, and no runner reports. The workflow never installs a missing tool.

Record an environmental execution failure without editing code:

```text
record-mutation \
  --runner pit --result failed --failure-kind environmental \
  --analyzed-sha <sha> --fingerprint <fingerprint> \
  --target-class 'com.example.OrderService*' \
  --execution-errors N --log .agent/tmp/<attempt>.log \
  --details <diagnosis>
```

`failed` requires a positive execution-error count and never unlocks a mutation gate. It may retain partial metrics and classifications produced before an environmental interruption; completeness is enforced only for a finished, accepted run.

During `mutation-rechecking`, reuse only the latest accepted initial attempt when the recomputed fingerprint and complete target set are identical:

```text
record-mutation \
  --runner pit --result reused \
  --analyzed-sha <final-sha> --fingerprint <unchanged-fingerprint> \
  --target-class 'com.example.OrderService*' \
  --reused-from-sha <initial-analyzed-sha> \
  --reused-from-fingerprint <unchanged-fingerprint> \
  --log .agent/tmp/<recheck>.log --details <input-comparison>
```

The ledger compares runner, fingerprint, target set, source SHA, and source fingerprint. A valid `reused` record copies initial metrics, classifications, classification path, report paths, and applicability reason into the final attempt while retaining the final `analyzed_sha` and recheck log. Any mismatch is rejected and requires a fresh runner attempt against all targets selected from `base_sha`.

Every item in append-only `mutation_attempts` records `stage`, `result`, `runner`, `analyzed_sha`, `fingerprint`, `target_classes`, metrics (`generated`, `killed`, `survived`, `no_coverage`, `execution_errors`), classifications, `actionable_findings`, classification/log/report paths, details, applicability or failure metadata, reuse provenance, and `recorded_at`.

The initial gate accepts only current `passed` or `not-applicable` evidence. The final gate accepts current `passed`, `reused`, or `not-applicable` evidence. `delivery-ready` and pull-request recording both require the final gate; actionable, incomplete, or failed attempts block delivery.

## Pull request, CI, and cleanup commands

```text
record-pr --repo <owner/name> --number N --url <url> --status OPEN [--issue-reference <see|closes>] [--label <existing-label>]...
record-ci --status <queued|running|passed|code-failed|environment-failed|transient-failed|retrying> --run-id <id> --url <url> --details <evidence>
cleanup --github-status MERGED --repo <recorded-owner/name> --number <recorded-number>
```

Pull-request recording requires `delivery-ready`, current passed `final-verify` and `final-sonar`, fresh terminal Habit evidence, and current accepted final mutation evidence. Current passed CI is required before `ready-for-merge`. One transient retry is allowed for the recorded CI flow.

Protected cleanup runs only after the exact recorded pull request is authoritatively observed as `MERGED` with an unambiguous merge timestamp. It removes only `.agent/tmp/<slug>.md` and its matching ledger for schemas v1, v2, or v3. Mutation artifacts remain available for repository-specific cleanup policy; the command never deletes branches or unrelated files.
