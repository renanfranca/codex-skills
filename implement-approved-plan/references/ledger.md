# Workflow ledger

Use `scripts/workflow_state.py` with Python's standard library. Keep the plan and ledger together under the repository's ignored `.agent/tmp` directory.

```text
python3 <skill>/scripts/workflow_state.py --state .agent/tmp/<slug>.workflow.json <command> ...
```

New ledgers use schema v2. Existing schema-v1 ledgers remain readable and retain their original validation and cleanup rules; reading them does not migrate or rewrite them. The script uses atomic replacement and rejects corrupt state, conflicting plan identities, invalid transitions, conflicting leases, specialist model fallback, duplicate conflicting records, incomplete evidence, premature pull requests, repeated transient CI retries, and cleanup without a matching GitHub `MERGED` confirmation.

## Initialize and inspect

```text
init --slug <slug> --plan .agent/tmp/<slug>.md --repo <absolute-repo> --branch <branch> --base <base>
show
```

`init` is idempotent only for the same slug, paths, repository, branch, and base.

## Register and serialize specialists

```text
register-chat --role <role> --thread-id <id> --model <exact-model> --effort xhigh
acquire --owner <coordinator-or-role>
release --owner <same-owner>
```

Acquire before dispatching any task that can read and mutate the checkout. A second owner is rejected. CI observation and GitHub status queries do not need the checkout lease; source-changing corrections do.

Schema v2 requires these exact registrations before the first `implementing` transition:

| Role | Model | Effort |
| --- | --- | --- |
| `implementer` | `gpt-5.6-sol` | `xhigh` |
| `committer` | `gpt-5.6-terra` | `xhigh` |
| `validator` | `gpt-5.6-luna` | `xhigh` |
| `habit-curator` | `gpt-5.6-luna` | `xhigh` |
| `structural-reviewer` | `gpt-5.6-sol` | `xhigh` |

Every task ID must be non-empty. Register each role once and reuse it.

## Advance and record evidence

```text
transition --to <phase> [--note <evidence>]
record-commit --sha <sha> --kind <kind> --subject <subject>
record-gate --name <initial-verify|initial-sonar|final-verify|final-sonar> --status <passed|failed|not-applicable> --details <observed-result> [--url <url>]
record-habit --status clean --details <evidence> --finding-count 0
record-habit --status ratcheted --details <evidence> --finding-count N --active-finding-count 0 --baseline-authorized --baseline-unchanged
record-habit --status snoozed --details <evidence> --finding-count N --user-authorized-snooze
record-habit --status not-applicable --details <evidence> --tool-unavailable
record-habit-observation --kind no-configured-files --details <evidence> [--reclassify-current]
record-pr --repo <owner/name> --number N --url <url> --status OPEN [--issue-reference <see|closes>] [--label <existing-label>]...
record-ci --status <queued|running|passed|code-failed|environment-failed|transient-failed|retrying> --run-id <id> --url <url> --details <evidence>
```

Commit recording requires the `committer` lease; gate recording requires the `validator` lease; terminal Habit recording requires the `habit-curator` lease; Habit observation and pull-request recording require the `coordinator` lease. Record evidence promptly and release leases even when a specialist reports a failure. In schema v2, terminal Habit stage is inferred from `habit-checking` or `habit-rechecking`; legacy freeze controls are rejected.

`record-habit-observation` is schema-v2-only and valid only during `habit-checking`. `no-configured-files` records that the tool ran but repository configuration selected and scanned no files. It is stored in `habit_observations`, not in the active terminal `habit` field. With `--reclassify-current`, the command atomically replaces a premature quick `not-applicable` classification with this observation and preserves the complete former Habit record inside `reclassified_habit`. Repeating the same operation is idempotent. Existing v2 ledgers without `habit_observations` remain readable; the field is created when the observation is first recorded.

The schema-v2 forward phases are:

```text
initialized -> implementing -> implemented -> habit-checking
-> checkpoint-committing -> initial-validating -> structural-review
-> habit-rechecking -> [final-committing ->] final-validating
-> delivery-ready -> pr-open -> ci-monitoring -> ready-for-merge -> merged
```

Use `final-committing` only when post-review work changed the checkout; that path requires a current commit. The direct `habit-rechecking -> final-validating` path represents no delivery delta.

The state machine permits documented corrective returns to the responsible earlier phase. Every schema-v2 corrective transition requires a non-empty Coordinator authorization/routing note. It also requires current quick Habit evidence before the checkpoint: either a terminal quick status or the non-terminal `no-configured-files` observation. A current checkpoint commit is required before initial validation, current passed clean-verification and Sonar gates are required before each forward validation boundary, fresh terminal Habit evidence is required after structural review, and current passed CI is required before `ready-for-merge`. Earlier attempts cannot satisfy a later repeated validation phase.

Schema-v2 pull-request recording requires `delivery-ready`, final `clean`, `ratcheted`, explicitly authorized `snoozed`, or genuinely unavailable `not-applicable` Habit evidence, plus current passed `final-verify` and `final-sonar`. It does not require a baseline commit. Schema-v1 ledgers keep their original phase, Habit, gate, and baseline rules.

## Protected cleanup

Only after querying the exact recorded pull request on GitHub and observing `state=MERGED` with an unambiguous merge timestamp, run:

```text
cleanup --github-status MERGED --repo <recorded-owner/name> --number <recorded-number>
```

This removes only `.agent/tmp/<slug>.md` and its matching ledger for either supported schema. Any other status or mismatched identity preserves both. The command never deletes branches.
