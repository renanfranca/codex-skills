# Deterministic local validation evidence

Read this reference when preparing collectors or executing selected checks. The active chat retains its role, lease, interpretation and ledger responsibilities. The executor runs commands and collects artifacts; it never records gates or calls model, worker or GitHub tools.

## Configure without changing the inventory

Keep the confirmed inventory's existing `checks` shape and fields from [workflow.md](workflow.md). Put a complementary JSON mapping by check ID at `.agent/tmp/<slug>.collectors.json`. Every selected local check for the requested role needs an explicit `collector`: `generic`, `maven`, `kof`, `pit` or `habit`. Discovery determines the collector and actual report locations; IDs need not match tool names. Unknown commands use `generic`, with unavailable metrics represented by `null`.

Optional `reports` entries contain a repository-relative `glob`, `format` (`junit`, `jacoco`, `kof`, `pit`, `artifact`), and boolean `required` (default true). A Kof report also needs `target`. Use `artifact` for HTML, stylesheets and other opaque artifacts. `inputs` optionally lists additional repository-relative file globs, including ignored runtime/configuration inputs that affect the check. Missing configured inputs block execution. Do not add collector fields to the inventory or consumer manifests.

Before any selected command runs, the executor validates every selected collector/report pair:

| Collector | Accepted declared formats |
| --- | --- |
| `maven` | `junit`, `jacoco`, `artifact` |
| `kof` | `kof`, `artifact` |
| `pit` | `pit`, `artifact` |
| `generic`, `habit` | `artifact` only, for additional opaque artifacts |

An incompatible pair returns invalid-configuration exit two, identifying the check, collector, format and glob, before executing even an earlier valid check. Never relabel a structured report as `artifact` to avoid its collector's parsing or required-report gate.

Example configuration; replace IDs, globs and requiredness with repository discovery:

```json
{
  "maven-verify": {
    "collector": "maven",
    "reports": [
      {"glob": "target/surefire-reports/TEST-*.xml", "format": "junit", "required": true},
      {"glob": "target/failsafe-reports/*.xml", "format": "junit", "required": true},
      {"glob": "target/jacoco/jacoco.xml", "format": "jacoco", "required": false}
    ]
  },
  "model-jvm": {"collector": "kof", "target": "jvm"},
  "pit": {
    "collector": "pit",
    "reports": [
      {"glob": "target/pit-reports/mutations.xml", "format": "pit", "required": true},
      {"glob": "target/pit-reports/index.html", "format": "artifact", "required": true},
      {"glob": "target/pit-reports/**/*.css", "format": "artifact", "required": false}
    ]
  },
  "habit": {"collector": "habit", "inputs": [".habit-hooks/config.toml"]},
  "lint": {"collector": "generic"}
}
```

Maven module paths and JaCoCo layouts vary. Require Failsafe or coverage reports only when the selected command/configuration produces them. For PIT, preserve HTML and request XML through its execution configuration, for example the confirmed command's `-DoutputFormats=HTML,XML` when supported by that runner ([PIT output formats](https://pitest.org/quickstart/maven/#outputformats)). Preserve existing formats, profiles and focal `targetClasses`; never narrow `targetTests`. The executor does not append flags or replace commands. For timestamped PIT directories, configure the actual report location so old attempts do not match required report globs.

## Execute once in the active phase

Acquire the logical role's lease, then invoke:

```text
python3 <skill>/scripts/run_validation.py \
  --repo <absolute-repository> \
  --inventory .agent/tmp/<slug>.validation.json \
  --config .agent/tmp/<slug>.collectors.json \
  --phase initial-validating --role validator
```

Allowed phase/role pairs:

| Phases | Role | Selected local checks |
| --- | --- | --- |
| `initial-validating`, `final-validating` | `validator` | Verification and local Sonar |
| `habit-checking`, `habit-rechecking` | `habit-curator` | Habit |
| `mutation-testing`, `mutation-rechecking` | `mutation-analyst` | Mutation |

By default all selected local checks for that role run in inventory order, sequentially. Repeated `--check-id <id>` selects an explicit subset for targeted diagnosis; it does not authorize a gate until every selected check has current evidence. Skipped entries, CI checks and other roles never run. Sonar follows the discovered repository location; CI-only Sonar stays in [github-delivery.md](github-delivery.md).

The inventory command runs unchanged under Bash with `pipefail` and inherited `ERR` observation. This records unhandled earlier failures even if a later statement succeeds, without using `errexit` to omit later suites. Explicitly handled shell conditions retain their native semantics; the collectors also preserve reported test failures. A command such as `./mvnw clean verify` continues to execute the full build, tests, integration tests, coverage and analysis configured by the repository. The executor does not reduce it to `test` or selected tests and never retries commands automatically.

SIGINT/SIGTERM cancellation terminates the active process group, preserves evidence, blocks evaluation and stops remaining checks. An explicit new invocation is a new attempt, never a hidden retry.

## Read execution, collection and evaluation separately

Each run gets a unique directory under `.agent/tmp/validation/`, with numbered check attempts. An attempt contains `command.log`, `inputs.json`, `evidence.json`, copied reports with their relative directory structure, and shell exit observations when applicable. Habit adds `sensors.json`, `guides.log` and both stages' stderr logs. Full output is written to files, never streamed into the chat. `summary.json` preserves the full run evidence.

The JSON returned on stdout is at most 16 KiB, including its newline and UTF-8 bytes. Each check identifies its ID, effective command, collector, analyzed Git revision, input fingerprint, command duration, exit code(s), execution status, collection state/issues, available metrics, findings/diagnostics and artifact paths. Generic checks also return `conclusion`: the last nonempty log lines, limited to four lines and 512 UTF-8 bytes; this is an output excerpt, not an executor judgment. Custom Habit commands using generic execution receive the same excerpt. Large findings/report lists and strings are abbreviated with `summary_truncated`; omitted checks are counted by `checks_omitted`. Full logs, reports and evidence remain available.

Read counts, execution/collection/evaluation states, metrics, diagnostics and conclusion excerpts first. Open `evidence`, `artifacts.evidence` or a specific log/report only to answer a concrete failure, question, omission or classification; do not routinely load complete logs into chat. Account for every omitted check/finding before recording its gate. This reading order preserves the chat's analysis of every surviving/uncovered mutant and Habit finding, including native Habit output needed to establish whether files were scanned. A compact excerpt never replaces required semantic review or full artifacts.

`inputs.json` records the exact command, collector configuration and SHA-256 hashes of tracked/unignored working inputs plus configured `inputs`, excluding workflow scratch unless explicitly listed in `inputs`, and excluding configured report outputs. Include the focal mutation manifest in `inputs` for traceability. The fingerprint uses canonical sorted JSON; it describes the inputs before execution, including dirty file content. It is execution evidence, not automatic approval or mutation reuse authorization. The chat must still create the focal mutation manifest and perform the ledger's existing comparisons from [workflow.md](workflow.md) and [ledger.md](ledger.md).

Execution `completed` means the process ended successfully and no unhandled shell failures were observed. Collection `complete` means the declared required reports exist, are fresh and parse successfully. Required missing, invalid or stale reports block evaluation. Freshness requires a post-start modification timestamp and a changed pre-run signature; optional old artifacts are retained with `fresh: false` and excluded from metrics. Reports are copied before parsing so malformed evidence remains inspectable.

Evaluation is either `blocked` or `needs-analysis`; it is never automatically `passed`. CLI exit zero means evidence is available for chat analysis. Exit one means at least one attempted check is blocked; exit two reports invalid configuration/preflight. Check `selected_count`, `executed_count`, `blocked_count` and any omissions before concluding that the phase completed. Collection errors, cancelled/failed commands or tool errors cannot support a green gate. A chat evaluates all required criteria and uses existing `record-gate`, `record-habit` and `record-mutation` interfaces under the correct lease.

## Collector semantics

- **Maven:** Parse leaf Surefire/Failsafe JUnit suites, avoiding nested aggregate totals, overlapping report globs and duplicate Failsafe summary totals. Preserve any failure in testcase or summary evidence. Collect JaCoCo root counters separately per report, without adding overlapping package/module coverage. Build failures remain in execution codes and compact log diagnostics; zero tests or skipped tests still need interpretation.
- **Kof:** Collect every structured `N failed of M tests` summary and preserve all failures, including `FAIL` and named directory-suite failures before later successful suites. Keep test and file counts separate. One command log requires a configured `target`; multiple targets require separate fresh `format: kof` reports tagged with each target, using repository-native logs/configuration. Do not infer targets from output that does not identify them or add another test invocation to get metrics. Unknown suite identity/counts remain unknown.
- **PIT:** Parse mutation XML into metrics and individual identities/statuses, with report path, class, method/descriptor, line, mutator, indexes, description and killing test when supplied. Every `SURVIVED` and `NO_COVERAGE` contributes to `unclassified_mutants` and requires chat classification. Unsupported/incomplete states are execution errors or collection errors, never accepted killed mutants. Keep focal scope, one invocation per attempt, complete classifications and fingerprint/reuse rules unchanged. HTML remains available for directed review.
- **Habit:** Adapt only a standalone canonical `habit-hooks` invocation (including its executable path and native arguments). Resolve native sibling `habit-sensors` and `habit-mapper`; execute sensors once, store their JSON, feed it to mapper once, and forward `--config` to both exactly as the native wrapper does. Preserve raw findings, guide output and both stage codes. Mapper exit one is enforcement; a failed sensor, mapper tool-error code or `incomplete-run` is tooling failure. Exit zero with findings is `guidance`, not clean. Even zero raw findings require inspecting native output for no configured/scanned files. Do not infer active counts or modify snooze state. Custom shell commands, wrappers and pipelines use generic execution without a second scan.
- **Generic:** Preserve exit observations, elapsed duration, complete log, compact diagnostics and the bounded `conclusion` excerpt. Only declared additional opaque artifacts are accepted. Unavailable metrics stay `null`; chat interpretation remains mandatory.

## Measure efficiency from actual evidence

Compare `duration_seconds`, `command_invocations`, stage invocation counts, `log_bytes`, report sizes and the UTF-8 byte length of the returned JSON. Keep full logs for the comparison. Do not convert bytes into an alleged measured token count or token cost. Collector checks against already available consumer reports are read-only compatibility evidence; they do not establish report freshness, run a consumer build, or authorize a ledger gate.
