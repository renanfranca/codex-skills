# Workflow ledger

Use `scripts/workflow_state.py` with Python's standard library. Keep the plan and ledger together under the repository's ignored `.agent/tmp` directory.

```text
python3 <skill>/scripts/workflow_state.py --state .agent/tmp/<slug>.workflow.json <command> ...
```

The script uses atomic replacement and rejects corrupt state, conflicting plan identities, invalid transitions, conflicting leases, specialist model fallback, duplicate conflicting records, premature pull requests, repeated transient CI retries, incomplete Habit freezes, and cleanup without a matching GitHub `MERGED` confirmation.

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

## Advance and record evidence

```text
transition --to <phase> [--note <evidence>]
record-commit --sha <sha> --kind <kind> --subject <subject>
record-gate --name <initial|public-checkpoint|sonar|final> --status <passed|failed|not-applicable> --details <observed-result> [--url <url>]
record-habit --status <active|curated|frozen|not-applicable> --details <evidence> [--finding-count N --classified-count N --snoozed-until-changed --pruned]
record-pr --repo <owner/name> --number N --url <url> --status OPEN [--issue-reference <see|closes>] [--label <existing-label>]...
record-ci --status <queued|running|passed|code-failed|environment-failed|transient-failed|retrying> --run-id <id> --url <url> --details <evidence>
```

Commit recording requires the `committer` lease; gate recording requires the `validator` lease; Habit recording requires the `habit-curator` lease; pull-request recording requires the `coordinator` lease. Record observations promptly and release leases even when a specialist reports a failure.

The normal forward phases are:

```text
initialized -> implementing -> implemented -> committed -> initial-validating
-> coordinator-review -> habit-curation -> structural-review -> final-validating
-> habit-frozen -> baseline-committed -> pr-open -> ci-monitoring
-> ready-for-merge -> merged
```

The state machine permits documented corrective returns to the responsible earlier phase. It does not permit structural review before a passed `public-checkpoint` or pull-request recording before a passed final gate and `baseline-committed` phase.

## Protected cleanup

Only after querying the exact recorded pull request on GitHub and observing `state=MERGED` with an unambiguous merge timestamp, run:

```text
cleanup --github-status MERGED --repo <recorded-owner/name> --number <recorded-number>
```

This removes only `.agent/tmp/<slug>.md` and its matching ledger. Any other status or mismatched identity preserves both. The command never deletes branches.
