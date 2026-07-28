# Evaluation evidence: 20260727T233326.147750Z-48228593ef91

- Operation: `validate-change`
- Status: `PASS`
- Provenance: `executed`
- Started: `2026-07-27T23:33:26.147750Z`
- Finished: `2026-07-27T23:47:04.226005Z`
- Duration: `818663 ms`
- Executor model: `gpt-5.6-terra`
- Executor effort: `medium`
- Codex CLI: `codex-cli 0.145.0`
- Authentication: `chatgpt`
- Runner SHA-256: `30f579584ba4eb2c9d21a68786aaae41f336a012c01cad35f4079e72a1e640e5`

## Consumption

- Tokens: input `1047864`, cached input `844032`, output `38571`, reasoning output `8933`
- Normalized usage events: `7`, complete `true`, scopes `turn`
- Sessions: planned `8`, executed `7`

## API reference estimate

- Reference amount: `1.299153000000 USD`
- Billing mode: `chatgpt-plan`
- This is not an actual charge.
- Estimate status: `complete`
- Limitation: This is an API reference estimate, not an observed charge.
- Limitation: This dated table is an API reference and is not an observed ChatGPT charge.
- Limitation: Prompts above 272,000 input tokens use the documented higher rates; an exact estimate is unavailable when normalized telemetry does not expose request scoped input.
- Limitation: Cache write charges are not estimated because Codex JSONL usage does not identify cache writes.
- Limitation: Reasoning output tokens are reported separately but are already included in output tokens.

## Observation 1: documentation-system-restructure

- Status: `FAIL`
- Role: `baseline`
- Repetition: `1`
- Duration: `171271 ms`
- Workspace retention: `removed`
- Tokens: input `261599`, cached input `219648`, output `7870`, reasoning output `1714`
- Normalized usage events: `1`, complete `true`, scopes `turn`

### Executor account

Diagnosis: Configuration and procedures had been duplicated across documents, and the conceptual guide used `workspace` before defining it.

Approach:
- Separated landing, conceptual, procedural, and normative-reference roles.
- Preserved required paths, anchors, commands, variable, and schema version.

Decisions:
- Kept README as the newcomer landing page, Concepts as conceptual owner, Cookbook as procedural owner, and Reference as configuration owner.
- Did not invent an installation command because the repository provides no verified installation mechanism.

Rejected Alternatives:
- Adding an unverified package manager installation command.

Key Changes:
- Added explicit audience routes from README.
- Removed duplicated configuration facts outside the Reference.
- Recorded validation and decisions in the living ExecPlan.

Validation:
- `python3 /home/renanfranca/.codex/skills/restructure-documentation/scripts/check_markdown_links.py README.md docs documentation-restructure-execplan.md` exited 0.
- `git diff --check` exited 0.

### Mechanical facts

- Mechanical result: `FAIL`
- Oracle result: `PASS`
- Judge verdict: `SKIPPED`
- `executor exit code`: `PASS`
- `executor response schema`: `PASS`
- `required path: README.md`: `PASS`
- `required path: docs/concepts.md`: `PASS`
- `required path: docs/cookbook.md`: `PASS`
- `required path: docs/reference.md`: `PASS`
- `required path: documentation-restructure-execplan.md`: `PASS`
- `required path: AGENTS.md`: `PASS`
- `forbidden changed path: AGENTS.md`: `PASS`
- `forbidden changed path: .agents/skills/**`: `PASS`
- `evaluated skill remained unchanged`: `PASS`
- `command: python3 .agents/skills/restructure-documentation/scripts/check_markdown_links.py README.md docs`: `FAIL`

### Changed files

- `README.md`
- `docs/concepts.md`
- `docs/cookbook.md`
- `docs/reference.md`
- `documentation-restructure-execplan.md`

### Sanitized diff

```diff
--- a/README.md
+++ b/README.md
@@ -1,24 +1,26 @@
 # Lantern CLI

-Lantern scans workspaces.
-
-Set `LANTERN_CACHE_DIR` if you do not want `.lantern-cache`. Configuration schema version 3 is current. A workspace is a folder with `lantern.toml`, although the examples below already use that term.
+Lantern scans directories using a Lantern configuration file.

 ## Getting started

-Run:
+### Install Lantern
+
+Install the `lantern` command through the approved distribution for your environment. This documentation set does not prescribe a package manager or installation command.
+
+### Initialize and scan
+
+From the directory you want Lantern to scan, run:

 ```console
 lantern init
 lantern scan --format json
 ```

-The scan command emits JSON. For more concepts see [concepts](docs/concepts.md), for commands see [recipes](docs/cookbook.md), and for every exact setting see [configuration](docs/reference.md#config-file).
+The scan command emits JSON. To understand the directory Lantern initializes, read [Workspace](docs/concepts.md#workspace).

-## Configuration
+## Documentation routes

-The `cache_dir` setting defaults to `.lantern-cache`. `LANTERN_CACHE_DIR` overrides it. Schema version 3 is current.
-
-## Recipes
-
-To create a workspace run `lantern init`. To scan it run `lantern scan --format json`.
+- Operators: use the outcome based [Cookbook](docs/cookbook.md#initialize-and-scan) for command recipes.
+- Contributors: use the normative [Configuration reference](docs/reference.md#config-file) for exact configuration facts.
+- Readers new to Lantern's model: start with [Concepts](docs/concepts.md#workspace).
--- a/docs/concepts.md
+++ b/docs/concepts.md
@@ -1,13 +1,11 @@
 # Concepts
-
-Run `lantern scan --format json` inside a workspace.

 ## Workspace

-A workspace is a folder containing `lantern.toml`.
+A workspace is a directory containing `lantern.toml`.

 ## Configuration

-Lantern uses configuration schema version 3. Set `LANTERN_CACHE_DIR` to override `.lantern-cache`.
+Lantern reads configuration from `lantern.toml`. The [configuration reference](reference.md#config-file) is the canonical source for schema compatibility, defaults, and environment overrides.

-See the [README configuration](../README.md#configuration).
+For command procedures, use the [Cookbook](cookbook.md#initialize-and-scan).
--- a/docs/cookbook.md
+++ b/docs/cookbook.md
@@ -1,14 +1,14 @@
 # Cookbook
+
+Use these recipes to operate Lantern. For exact configuration values, see the [configuration reference](reference.md#config-file).

 ## Initialize and scan

-A workspace is a folder containing `lantern.toml`.
+Create a workspace, then scan it:

 ```console
 lantern init
 lantern scan --format json
 ```

-Schema version 3 is current. `LANTERN_CACHE_DIR` changes the cache.
-
-See [all configuration](reference.md#config-file).
+The scan command emits JSON. For the definition of the directory being initialized, see [Workspace](concepts.md#workspace).
--- a/docs/reference.md
+++ b/docs/reference.md
@@ -1,8 +1,10 @@
 # Reference
+
+This reference is the canonical source for exact Lantern configuration facts.

 ## Config file

-A workspace contains `lantern.toml`. Configuration schema version 3 is current.
+Lantern reads its configuration from `lantern.toml`. Configuration schema version 3 is current.

 | Name | Default |
 | --- | --- |
@@ -10,6 +12,6 @@

 `LANTERN_CACHE_DIR` overrides `cache_dir`.

-Initialize with `lantern init` and scan with `lantern scan --format json`.
+For command procedures, use the [Initialize and scan recipe](cookbook.md#initialize-and-scan). For the directory model, see [Workspace](concepts.md#workspace).

-Return to the [README](../README.md#getting-started).
+Return to [Getting started](../README.md#getting-started).
--- /dev/null
+++ b/documentation-restructure-execplan.md
@@ -0,0 +1,134 @@
+# Restructure Lantern documentation journeys
+
+This ExecPlan is a living document. Keep `Progress`, `Decisions`, `Risks and Mitigations`, and `Lessons Learned` current as work advances.
+
+## Purpose / Big Picture
+
+Lantern documentation will route three readers to the material they need: a newcomer to an installation and first scan, an operator to repeatable recipes, and a contributor to exact configuration facts. The resulting Markdown will keep the public README and reference anchors working while separating concepts, procedures, and normative configuration details.
+
+## Scope
+
+In scope: `README.md`, `docs/concepts.md`, `docs/cookbook.md`, `docs/reference.md`, and this plan. Preserve the existing paths, `README.md#getting-started`, `docs/reference.md#config-file`, `lantern init`, `lantern scan --format json`, `LANTERN_CACHE_DIR`, and schema version 3. Do not edit `AGENTS.md`. Out of scope: changing Lantern behavior or adding documentation tooling.
+
+## Definitions
+
+Audience route: the ordered links a reader follows from a starting page to the information needed for an outcome. Canonical owner: the one document responsible for complete guidance on a subject; other documents link to it rather than repeat its details. Local navigation: Markdown links and fragments that resolve to files and headings in this repository.
+
+## Existing Context
+
+The README currently repeats configuration facts and recipes. The cookbook repeats the concept definition and configuration facts. The reference mixes the configuration record with procedural commands. `docs/concepts.md` mentions `workspace` before its `## Workspace` definition. There are no repository commits or project documentation checks; the available validation will be a local Markdown link check plus content and diff inspections.
+
+## Desired End State
+
+`README.md` is the newcomer landing page with `## Getting started` retained. `docs/concepts.md` owns conceptual definitions and defines `workspace` at its first lexical occurrence. `docs/cookbook.md` owns operator procedures. `docs/reference.md` owns configuration facts and retains `## Config file`. Each audience can select a clear canonical destination from the README or its relevant document.
+
+## Milestones
+
+### Milestone 1 - Inventory and plan routes
+
+#### Goal
+
+Protect public interfaces and assign one canonical owner to each kind of information.
+
+#### Changes
+
+- [x] Inventory paths, headings, links, commands, and required facts in the four documentation files.
+- [x] Record audience routes and the target ownership model in this plan.
+
+#### Validation
+
+- [x] Command: `rg -n "workspace|LANTERN_CACHE_DIR|schema version|lantern init|lantern scan --format json|config-file|getting-started" README.md docs/*.md`
+- [x] Expected result: all existing copies and preserved interfaces are identified before edits.
+
+#### Acceptance Criteria
+
+- [x] The public anchors and mandatory facts are explicitly protected.
+- [x] Concepts, procedures, and configuration facts each have a planned canonical owner.
+
+### Milestone 2 - Restructure pages and routes
+
+#### Goal
+
+Put each audience on an ordered journey without duplicated normative content.
+
+#### Changes
+
+- [x] Edit the landing page, conceptual guide, cookbook, and reference according to their canonical roles.
+- [x] Keep the conceptual guide's `## Workspace` heading and definition before every other use of `workspace` or `workspaces` in that file.
+
+#### Validation
+
+- [x] Command: `python3 /home/renanfranca/.codex/skills/restructure-documentation/scripts/check_markdown_links.py README.md docs`
+- [x] Result: exit 0 with no output, meaning every local path and fragment resolved.
+
+#### Acceptance Criteria
+
+- [x] Each audience has an explicit route to its outcome.
+- [x] The protected anchors, commands, variable, and version remain in their designated owners.
+
+### Milestone 3 - Verify and finalize evidence
+
+#### Goal
+
+Check navigation, concept order, interfaces, and scope before handoff.
+
+#### Changes
+
+- [x] Record final validation evidence, decisions, and lessons in this plan.
+
+#### Validation
+
+- [x] Command: `rg -n "^#{1,3} |workspace|workspaces|LANTERN_CACHE_DIR|schema version 3|lantern init|lantern scan --format json" README.md docs/*.md`
+- [x] Result: `docs/concepts.md:3` is `## Workspace`; its definition at line 5 is the next and first body occurrence. Required commands are in README and Cookbook; the environment override and schema version are in the reference.
+- [x] Command: `git diff --check`
+- [x] Result: exit 0 with no whitespace errors. The initial repository state is entirely untracked, so `git diff` cannot show a tracked-file diff; direct file inspection was used for scope review.
+- [x] Final navigation command: `python3 /home/renanfranca/.codex/skills/restructure-documentation/scripts/check_markdown_links.py README.md docs documentation-restructure-execplan.md`
+- [x] Result: exit 0 with all local Markdown paths and fragments, including those in this plan, resolved.
+
+#### Acceptance Criteria
+
+- [x] Local navigation and required interfaces have concrete evidence.
+- [x] No change touches `AGENTS.md`.
+
+## Progress
+
+- [x] Milestone 1 started
+- [x] Milestone 1 completed
+- [x] Milestone 2 started
+- [x] Milestone 2 completed
+- [x] Milestone 3 started
+- [x] Milestone 3 completed
+
+## Decisions
+
+- Decision: Make README the newcomer landing page, concepts the conceptual owner, cookbook the procedural owner, and reference the configuration owner.
+  Rationale: This directly separates the three requested audiences and removes the documented overlap.
+  Date/Author: 2026-07-27 / Codex
+- Decision: Do not add an installation command.
+  Rationale: The repository documents no verified installation mechanism or package manager.
+  Date/Author: 2026-07-27 / Codex
+
+## Risks and Mitigations
+
+- Risk: Retitling headings could break incoming links.
+  Mitigation: Retain `## Getting started` and `## Config file` exactly, then run the local link validator.
+- Risk: A configuration fact may remain duplicated and drift.
+  Mitigation: Keep exact defaults, environment override, and schema version only in the reference; other pages link there.
+- Risk: `workspace` may appear before its definition in the conceptual guide.
+  Mitigation: Start that file with `## Workspace` and inspect every occurrence after editing.
+
+## Validation Strategy
+
+1. Inspect the required facts and headings with `rg`.
+2. Run the bundled local Markdown link validator against the README and `docs` directory.
+3. Review the scoped diff and whitespace check.
+4. Walk the newcomer, operator, and contributor routes using their actual headings and destinations.
+
+## Rollout and Recovery
+
+This is a documentation-only change: publish the edited Markdown with the repository. If a route proves confusing or an external link depends on a changed heading, revert the affected documentation file while retaining the protected anchors; no runtime data or migration is involved.
+
+## Lessons Learned
+
+- The repository has no commits and no project documentation check configuration, so validation must use the bundled local link checker and direct interface inspection.
+- The repository's documentation files are untracked at baseline; `git diff` cannot display their content changes, but `git diff --check` still completed without whitespace errors.
```

## Observation 2: documentation-system-restructure

- Status: `PASS`
- Role: `candidate`
- Repetition: `1`
- Duration: `186401 ms`
- Workspace retention: `removed`
- Tokens: input `267603`, cached input `215808`, output `9241`, reasoning output `1637`
- Normalized usage events: `2`, complete `true`, scopes `turn`

### Executor account

Diagnosis: Commands and configuration facts were duplicated across files, and the conceptual guide used `workspace` before defining it.

Approach:
- Separated landing, conceptual, procedural, and normative-reference responsibilities.
- Replaced noncanonical detail with direct local links to the canonical owner.

Decisions:
- README retains the smallest newcomer success path; cookbook owns the full operator procedure.
- Reference owns exact configuration facts; concepts owns definitions.

Rejected Alternatives:
- None recorded.

Key Changes:
- Added audience routing from README.
- Preserved required anchors and facts.
- Maintained the completed living ExecPlan.

Validation:
- `python3 .agents/skills/restructure-documentation/scripts/check_markdown_links.py .` exited 0.
- `git diff --check` exited 0.
- Targeted lexical check confirmed `## Workspace` is the first singular or plural occurrence in `docs/concepts.md`.

### Mechanical facts

- Mechanical result: `PASS`
- Oracle result: `PASS`
- Judge verdict: `PASS`
- `executor exit code`: `PASS`
- `executor response schema`: `PASS`
- `required path: README.md`: `PASS`
- `required path: docs/concepts.md`: `PASS`
- `required path: docs/cookbook.md`: `PASS`
- `required path: docs/reference.md`: `PASS`
- `required path: documentation-restructure-execplan.md`: `PASS`
- `required path: AGENTS.md`: `PASS`
- `forbidden changed path: AGENTS.md`: `PASS`
- `forbidden changed path: .agents/skills/**`: `PASS`
- `evaluated skill remained unchanged`: `PASS`
- `command: python3 .agents/skills/restructure-documentation/scripts/check_markdown_links.py README.md docs`: `PASS`

### Changed files

- `README.md`
- `docs/concepts.md`
- `docs/cookbook.md`
- `docs/reference.md`
- `documentation-restructure-execplan.md`

### Sanitized diff

```diff
--- a/README.md
+++ b/README.md
@@ -1,24 +1,20 @@
 # Lantern CLI

-Lantern scans workspaces.
-
-Set `LANTERN_CACHE_DIR` if you do not want `.lantern-cache`. Configuration schema version 3 is current. A workspace is a folder with `lantern.toml`, although the examples below already use that term.
+Lantern scans project files and emits results for local tooling.

 ## Getting started

-Run:
+For a first successful scan, initialize Lantern and request JSON output:

 ```console
 lantern init
 lantern scan --format json
 ```

-The scan command emits JSON. For more concepts see [concepts](docs/concepts.md), for commands see [recipes](docs/cookbook.md), and for every exact setting see [configuration](docs/reference.md#config-file).
+The scan command emits JSON. Read [Workspace](docs/concepts.md#workspace) to understand the project directory created by the first command.

-## Configuration
+## Choose your path

-The `cache_dir` setting defaults to `.lantern-cache`. `LANTERN_CACHE_DIR` overrides it. Schema version 3 is current.
-
-## Recipes
-
-To create a workspace run `lantern init`. To scan it run `lantern scan --format json`.
+* **Newcomer:** start above, then read [Workspace](docs/concepts.md#workspace).
+* **Operator:** use the [Initialize and scan](docs/cookbook.md#initialize-and-scan) recipe and its expected result.
+* **Contributor:** consult the [Config file](docs/reference.md#config-file) reference for exact configuration facts.
--- a/docs/concepts.md
+++ b/docs/concepts.md
@@ -1,13 +1,13 @@
 # Concepts
-
-Run `lantern scan --format json` inside a workspace.

 ## Workspace

-A workspace is a folder containing `lantern.toml`.
+A workspace is a project directory containing `lantern.toml`. It is the scope Lantern initializes and scans.

-## Configuration
+## Configuration model

-Lantern uses configuration schema version 3. Set `LANTERN_CACHE_DIR` to override `.lantern-cache`.
+The configuration file controls how Lantern operates in a workspace. For the complete schema, defaults, and environment overrides, see [Config file](reference.md#config-file).

-See the [README configuration](../README.md#configuration).
+## Recipes
+
+For the commands and expected result of a scan, use [Initialize and scan](cookbook.md#initialize-and-scan).
--- a/docs/cookbook.md
+++ b/docs/cookbook.md
@@ -1,14 +1,16 @@
 # Cookbook
+
+Goal based procedures for operating Lantern.

 ## Initialize and scan

-A workspace is a folder containing `lantern.toml`.
+Before starting, read [Workspace](concepts.md#workspace) to understand the directory Lantern will create and scan.
+
+Run these commands from the directory you want Lantern to initialize:

 ```console
 lantern init
 lantern scan --format json
 ```

-Schema version 3 is current. `LANTERN_CACHE_DIR` changes the cache.
-
-See [all configuration](reference.md#config-file).
+The scan command emits JSON. To change configuration such as the cache location, use the exact facts in [Config file](reference.md#config-file).
--- a/docs/reference.md
+++ b/docs/reference.md
@@ -1,15 +1,15 @@
 # Reference
+
+Exact configuration facts for contributors and maintainers.

 ## Config file

-A workspace contains `lantern.toml`. Configuration schema version 3 is current.
+Lantern reads configuration from `lantern.toml`. Configuration schema version 3 is current.

-| Name | Default |
-| --- | --- |
-| `cache_dir` | `.lantern-cache` |
+| Name | Default | Environment override |
+| --- | --- | --- |
+| `cache_dir` | `.lantern-cache` | `LANTERN_CACHE_DIR` |

 `LANTERN_CACHE_DIR` overrides `cache_dir`.

-Initialize with `lantern init` and scan with `lantern scan --format json`.
-
-Return to the [README](../README.md#getting-started).
+For the directory concept, see [Workspace](concepts.md#workspace). For operational commands, use [Initialize and scan](cookbook.md#initialize-and-scan). Return to [Getting started](../README.md#getting-started).
--- /dev/null
+++ b/documentation-restructure-execplan.md
@@ -0,0 +1,149 @@
+# Restructure Lantern Documentation by Audience
+
+This ExecPlan is a living document. Keep `Progress`, `Decisions`, `Risks and Mitigations`, and `Lessons Learned` up to date as work advances.
+
+## Purpose / Big Picture
+
+Restructure the existing Lantern documentation so a newcomer can install and begin, an operator can find task based recipes, and a contributor can locate exact configuration facts. The outcome is observable through clear routes from `README.md`, unambiguous canonical owners, preserved public anchors and facts, and valid local Markdown navigation.
+
+## Scope
+
+In scope: `README.md`, `docs/concepts.md`, `docs/cookbook.md`, `docs/reference.md`, and this plan. Preserve existing paths, `README.md#getting-started`, `docs/reference.md#config-file`, `lantern init`, `lantern scan --format json`, `LANTERN_CACHE_DIR`, and configuration schema version 3. `AGENTS.md` is protected and out of scope.
+
+## Definitions
+
+* **Canonical owner**: the one document that contains the complete authoritative explanation for a subject; other documents link to it rather than restating details.
+* **Local navigation**: a Markdown link or fragment that resolves to a file and heading within this repository.
+* **Workspace**: the Lantern project directory and its configuration context. Its formal definition will occur in the conceptual guide before procedural use.
+
+## Existing Context
+
+The documentation consists of the repository README and three documents under `docs/`. Before the restructure, the README, cookbook, and reference repeated commands and configuration facts. `docs/concepts.md` used `workspace` in its opening command before `## Workspace` defined it. There is no repository specific documentation check; the bundled local link validator is the repository validation available for this set.
+
+Audience inventory:
+
+| Audience | Start | Outcome | Required concept | Canonical destination | Former obstacle |
+| --- | --- | --- | --- | --- | --- |
+| Newcomer | `README.md#Getting started` | Initialize and complete a JSON scan | Workspace | `docs/concepts.md#Workspace` | The README mixed start, configuration, and recipes. |
+| Operator | `docs/cookbook.md#Initialize and scan` | Run the initialization and JSON scan procedure | Workspace | `docs/cookbook.md#Initialize and scan` | Commands and configuration were mixed across three files. |
+| Contributor | `docs/reference.md#Config file` | Find exact configuration facts | Config file | `docs/reference.md#Config file` | Exact configuration facts were duplicated. |
+
+Subject inventory: concepts are owned by `docs/concepts.md`; commands and expected operational result are owned by `docs/cookbook.md`; schema version, `cache_dir`, `.lantern-cache`, and `LANTERN_CACHE_DIR` are owned by `docs/reference.md`. The required public interfaces are `README.md#getting-started`, `docs/reference.md#config-file`, `lantern init`, `lantern scan --format json`, `LANTERN_CACHE_DIR`, and schema version 3.
+
+## Desired End State
+
+`README.md` is the newcomer landing path, `docs/concepts.md` owns conceptual definitions, `docs/cookbook.md` owns goal based operator procedures, and `docs/reference.md` owns exact configuration facts. Existing paths and stated anchors remain resolvable, while the required commands, environment variable, and schema version remain exact.
+
+## Milestones
+
+### Milestone 1 - Audit the Current Documentation
+
+#### Goal
+
+Inventory document roles, navigation, facts, and concept ordering without modifying protected files.
+
+#### Changes
+
+* [x] Inspect the documentation files, repository checks, and documentation role guidance.
+* [x] Record source evidence, overlap, audience obstacles, and protected interfaces in this plan.
+
+#### Validation
+
+* [x] Command: `rg -n "lantern init|lantern scan --format json|LANTERN_CACHE_DIR|schema version 3|workspace" README.md docs`
+* [x] Expected result: current occurrences are identified before content moves.
+
+#### Acceptance Criteria
+
+* [x] Each audience has a starting point, intended outcome, and current obstacle.
+* [x] Each protected fact and public anchor has a known source location.
+
+### Milestone 2 - Establish Audience Routes and Owners
+
+#### Goal
+
+Restructure the four documentation files around their intended primary roles without changing the documented interfaces.
+
+#### Changes
+
+* [x] Edit `README.md` as the newcomer landing route while retaining `#getting-started`.
+* [x] Edit `docs/concepts.md` so its `## Workspace` heading and definition precede every lexical occurrence of workspace or workspaces.
+* [x] Edit `docs/cookbook.md` as the operator recipe collection.
+* [x] Edit `docs/reference.md` as the exact configuration source while retaining `#config-file`.
+
+#### Validation
+
+* [x] Command: `python3 .agents/skills/restructure-documentation/scripts/check_markdown_links.py README.md docs`
+* [x] Expected result: every local Markdown link and fragment resolves.
+
+#### Acceptance Criteria
+
+* [x] Each audience can follow a direct non-circular route from its entry point to its outcome.
+* [x] Every subject has a single canonical owner and other documents link to it.
+
+### Milestone 3 - Validate Interfaces and Finalize Evidence
+
+#### Goal
+
+Confirm navigation, term ordering, required facts, repository checks, and the final diff.
+
+#### Changes
+
+* [x] Update this plan with completed validation, concise decisions, and lessons learned.
+
+#### Validation
+
+* [x] Command: `python3 .agents/skills/restructure-documentation/scripts/check_markdown_links.py .`
+* [x] Command: `git diff --check`
+* [x] Command: targeted `rg` checks for protected headings, commands, variable, version, and first workspace occurrence
+* [x] Expected result: all checks exit successfully and inspection confirms the stated interfaces.
+
+#### Acceptance Criteria
+
+* [x] No changes affect `AGENTS.md`.
+* [x] The final evidence cites actual headings, destinations, canonical owners, concept ordering, and preserved interfaces.
+
+## Progress
+
+* [x] Milestone 1 started
+* [x] Milestone 1 completed
+* [x] Milestone 2 started
+* [x] Milestone 2 completed
+* [x] Milestone 3 started
+* [x] Milestone 3 completed
+
+## Decisions
+
+* Decision: Use the README as landing page, concepts guide for definitions, cookbook for operator procedures, and reference for configuration facts.
+  Rationale: These roles directly match the three requested audiences and prevent the current overlap.
+  Date/Author: 2026-07-27 / Codex
+* Decision: Keep the newcomer quick start in the README and make the cookbook the canonical owner of the full procedure.
+  Rationale: A smallest successful start belongs on the landing page, while the cookbook provides the procedural destination and configuration handoff.
+  Date/Author: 2026-07-27 / Codex
+
+## Risks and Mitigations
+
+* Risk: Moving duplicate content can break inbound anchors or lose required facts.
+  Mitigation: Preserve stated headings and facts exactly, then validate all local navigation and inspect the final diff.
+* Risk: The concept term can be introduced before its required definition.
+  Mitigation: Search the conceptual guide for singular and plural occurrences and inspect the first match before finalizing.
+
+## Validation Strategy
+
+1. Compare protected commands, configuration facts, variable, version, paths, and anchors with the final documentation.
+2. Run the bundled local link validator across the README and `docs/`.
+3. Run any repository documentation check found during the audit.
+4. Walk the three routes from their actual entry headings and inspect the final diff.
+
+Validation completed on 2026-07-27:
+
+* `python3 .agents/skills/restructure-documentation/scripts/check_markdown_links.py .` exited 0 with no broken local links or fragments across the repository Markdown set.
+* `git diff --check` exited 0. This repository is an uncommitted fixture, so `git diff` has no baseline to display; `git status --short` confirmed the expected documentation files are untracked and did not identify a modified tracked `AGENTS.md`.
+* Targeted `rg` inspection confirmed `docs/concepts.md` first uses the term at `## Workspace`, then defines it in the following paragraph. It also confirmed both required commands remain in the README and cookbook, and the schema version and environment variable remain in `docs/reference.md`.
+
+## Rollout and Recovery
+
+These Markdown only changes take effect when merged. If an audience route proves unclear or a link fails, revert the affected documentation hunk and retain the stable paths and anchors while correcting the route.
+
+## Lessons Learned
+
+* The repository has no project specific check script or build manifest. The bundled local link validator is therefore the full repository documentation check for this Markdown only fixture.
```

## Observation 3: documentation-system-restructure

- Status: `PASS`
- Role: `candidate`
- Repetition: `2`
- Duration: `247615 ms`
- Workspace retention: `removed`
- Tokens: input `251041`, cached input `184832`, output `10740`, reasoning output `2770`
- Normalized usage events: `2`, complete `true`, scopes `turn`

### Executor account

Diagnosis: The prior set duplicated procedures and configuration facts across all documents and used `workspace` before defining it in the conceptual guide. Installation mechanics are absent from the repository source material.

Approach:
- Separated landing, conceptual, procedural, and normative-reference roles.
- Replaced noncanonical details with direct links to canonical owners.
- Maintained the living ExecPlan through implementation and validation.

Decisions:
- README is the landing page; concepts owns vocabulary; cookbook owns procedures; reference owns configuration facts.
- The quick start is explicitly post-installation because no installation method is documented.
- The required commands remain in README’s minimal quick start and the canonical cookbook recipe.

Rejected Alternatives:
- Inventing an installation command or distribution method.

Key Changes:
- Added audience-specific routes from README.
- Made `## Workspace` and its definition the first `workspace` occurrences in the conceptual guide.
- Centralized exact configuration facts in `docs/reference.md#config-file`.

Validation:
- `python3 .agents/skills/restructure-documentation/scripts/check_markdown_links.py .` completed successfully for all local documentation navigation.
- `python3 .agents/skills/restructure-documentation/scripts/tests/test_check_markdown_links.py` passed: 6 tests.
- Whitespace checks across changed documentation found no errors.

### Mechanical facts

- Mechanical result: `PASS`
- Oracle result: `PASS`
- Judge verdict: `PASS`
- `executor exit code`: `PASS`
- `executor response schema`: `PASS`
- `required path: README.md`: `PASS`
- `required path: docs/concepts.md`: `PASS`
- `required path: docs/cookbook.md`: `PASS`
- `required path: docs/reference.md`: `PASS`
- `required path: documentation-restructure-execplan.md`: `PASS`
- `required path: AGENTS.md`: `PASS`
- `forbidden changed path: AGENTS.md`: `PASS`
- `forbidden changed path: .agents/skills/**`: `PASS`
- `evaluated skill remained unchanged`: `PASS`
- `command: python3 .agents/skills/restructure-documentation/scripts/check_markdown_links.py README.md docs`: `PASS`

### Changed files

- `README.md`
- `docs/concepts.md`
- `docs/cookbook.md`
- `docs/reference.md`
- `documentation-restructure-execplan.md`

### Sanitized diff

```diff
--- a/README.md
+++ b/README.md
@@ -1,24 +1,22 @@
 # Lantern CLI

-Lantern scans workspaces.
-
-Set `LANTERN_CACHE_DIR` if you do not want `.lantern-cache`. Configuration schema version 3 is current. A workspace is a folder with `lantern.toml`, although the examples below already use that term.
+Lantern initializes a project and scans it.

 ## Getting started

-Run:
+After installing Lantern, run:

 ```console
 lantern init
 lantern scan --format json
 ```

-The scan command emits JSON. For more concepts see [concepts](docs/concepts.md), for commands see [recipes](docs/cookbook.md), and for every exact setting see [configuration](docs/reference.md#config-file).
+The scan command emits JSON.

-## Configuration
+## Choose a path

-The `cache_dir` setting defaults to `.lantern-cache`. `LANTERN_CACHE_DIR` overrides it. Schema version 3 is current.
+- Newcomers who need the model behind the first scan: [Concepts: Workspace](docs/concepts.md#workspace).
+- Operators completing the initialization and scan task: [Cookbook: Initialize and scan](docs/cookbook.md#initialize-and-scan).
+- Contributors checking exact configuration behavior: [Reference: Config file](docs/reference.md#config-file).

-## Recipes
-
-To create a workspace run `lantern init`. To scan it run `lantern scan --format json`.
+Installation instructions are not specified in this repository; use the distribution method provided for your environment before starting.
--- a/docs/concepts.md
+++ b/docs/concepts.md
@@ -1,6 +1,4 @@
 # Concepts
-
-Run `lantern scan --format json` inside a workspace.

 ## Workspace

@@ -8,6 +6,6 @@

 ## Configuration

-Lantern uses configuration schema version 3. Set `LANTERN_CACHE_DIR` to override `.lantern-cache`.
+Lantern reads its configuration from the file in the Workspace definition. The [configuration reference](reference.md#config-file) owns the exact schema version, default values, and environment override.

-See the [README configuration](../README.md#configuration).
+For the task that creates and scans a Workspace, follow the [initialize and scan recipe](cookbook.md#initialize-and-scan).
--- a/docs/cookbook.md
+++ b/docs/cookbook.md
@@ -2,13 +2,13 @@

 ## Initialize and scan

-A workspace is a folder containing `lantern.toml`.
+Before starting, read [Workspace](concepts.md#workspace) for the directory Lantern initializes.

 ```console
 lantern init
 lantern scan --format json
 ```

-Schema version 3 is current. `LANTERN_CACHE_DIR` changes the cache.
+The scan command emits JSON. For exact configuration behavior, including the cache location, environment override, and schema version, see [Config file](reference.md#config-file).

-See [all configuration](reference.md#config-file).
+Return to [Getting started](../README.md#getting-started) to choose another path.
--- a/docs/reference.md
+++ b/docs/reference.md
@@ -2,7 +2,7 @@

 ## Config file

-A workspace contains `lantern.toml`. Configuration schema version 3 is current.
+Lantern configuration is stored in `lantern.toml`. Configuration schema version 3 is current.

 | Name | Default |
 | --- | --- |
@@ -10,6 +10,6 @@

 `LANTERN_CACHE_DIR` overrides `cache_dir`.

-Initialize with `lantern init` and scan with `lantern scan --format json`.
+For the initialization and scan procedure, use [Initialize and scan](cookbook.md#initialize-and-scan).

 Return to the [README](../README.md#getting-started).
--- /dev/null
+++ b/documentation-restructure-execplan.md
@@ -0,0 +1,141 @@
+# Restructure Lantern documentation journeys
+
+This ExecPlan is a living document. Keep `Progress`, `Decisions`, `Risks and Mitigations`, and `Lessons Learned` up to date as work advances.
+
+## Purpose / Big Picture
+
+Reorganize the existing Lantern documentation so a newcomer can start after installing Lantern, an operator can find a task focused recipe, and a contributor can find exact configuration facts without reconciling duplicates. The result is observable through the landing page routes, the ordered concepts guide, goal based cookbook, and configuration reference, with all local Markdown links resolving.
+
+## Scope
+
+In scope: `README.md`, `docs/concepts.md`, `docs/cookbook.md`, `docs/reference.md`, and this ExecPlan. Preserve those existing document paths, `README.md#getting-started`, `docs/reference.md#config-file`, the commands `lantern init` and `lantern scan --format json`, `LANTERN_CACHE_DIR`, and the current configuration schema version of 3.
+
+Out of scope: `AGENTS.md`, product behavior, installation instructions not supported by a repository source, and external links. Safety boundary: This task is limited to authorized, defensive maintenance of this repository documentation.
+
+## Definitions
+
+Landing page: the short entry document that routes a reader to the right journey. Canonical owner: the one document responsible for a subject's complete current guidance. Workspace: a Lantern folder containing `lantern.toml`; the public conceptual definition will be in `docs/concepts.md`.
+
+## Existing Context
+
+`README.md` currently mixes the quick start, configuration defaults, and recipe commands. `docs/concepts.md` runs a command in a workspace before its `## Workspace` definition. `docs/cookbook.md` repeats the definition and configuration facts, while `docs/reference.md` repeats commands that are procedural guidance. No file provides an authoritative installation method, package source, or installation command. All repository files are initially untracked, so the baseline content is treated as user supplied and protected except for the authorized documentation changes.
+
+Subject inventory: Workspace terminology is duplicated in all four documents and will be owned by `docs/concepts.md#workspace`; task commands are duplicated in the README, cookbook, and reference and will be owned procedurally by `docs/cookbook.md#initialize-and-scan` while the README retains the required quick start; configuration version, file name, default, and environment override are duplicated and will be owned by `docs/reference.md#config-file`.
+
+## Desired End State
+
+`README.md#getting-started` gives an installed Lantern user the smallest successful scan and routes the three audiences to their canonical destinations. `docs/concepts.md` defines Workspace as the first lexical use of that term, before any procedure. `docs/cookbook.md` owns the initialize and scan procedure, and `docs/reference.md#config-file` owns exact configuration facts. Local navigation is valid.
+
+## Milestones
+
+### Milestone 1 - Establish the documentation map
+
+#### Goal
+
+Record the current overlap, preserved interfaces, and canonical owners before changing prose.
+
+#### Changes
+
+- [x] Create `documentation-restructure-execplan.md` with the audit, scope, and subject inventory.
+- [x] Record the selected document roles and audience routes in this plan.
+
+#### Validation
+
+- [x] Command: `rg -n '(lantern init|lantern scan --format json|LANTERN_CACHE_DIR|schema version 3|^## Getting started|^## Config file)' README.md docs/*.md`
+- [x] Expected result: all protected commands, facts, and anchors are present after the restructure.
+
+#### Acceptance Criteria
+
+- [x] Every requested audience has a documented entry point and canonical destination.
+
+### Milestone 2 - Restructure canonical documents
+
+#### Goal
+
+Give each document one primary role and remove noncanonical duplication.
+
+#### Changes
+
+- [x] Edit `README.md` as landing page and retain `## Getting started`.
+- [x] Edit `docs/concepts.md` so `## Workspace` and its definition are the first uses of the term.
+- [x] Edit `docs/cookbook.md` as a task focused procedure.
+- [x] Edit `docs/reference.md` as the configuration facts owner and retain `## Config file`.
+
+#### Validation
+
+- [x] Command: `python3 .agents/skills/restructure-documentation/scripts/check_markdown_links.py .`
+- [x] Expected result: exit status 0 with no broken local paths or fragments.
+
+#### Acceptance Criteria
+
+- [x] The three audience routes are direct, noncircular, and use the intended owners.
+- [x] Configuration facts appear canonically in the reference and procedural steps in the cookbook.
+
+### Milestone 3 - Verify and finalize
+
+#### Goal
+
+Check protected interfaces, navigation, lexical ordering, and repository documentation checks.
+
+#### Changes
+
+- [x] Update this ExecPlan with executed validation evidence and final lessons.
+
+#### Validation
+
+- [x] Command: `python3 .agents/skills/restructure-documentation/scripts/check_markdown_links.py .`
+- [x] Command: `python3 .agents/skills/restructure-documentation/scripts/tests/test_check_markdown_links.py`
+- [x] Command: `for f in README.md docs/concepts.md docs/cookbook.md docs/reference.md documentation-restructure-execplan.md; do git diff --no-index --check /dev/null "$f"; test $? -le 1 || exit $?; done`
+- [x] Expected result: navigation validation exited 0; six validator tests passed; whitespace checks found no errors; the lexical audit shows the `## Workspace` heading and definition precede all other occurrences in `docs/concepts.md`.
+
+#### Acceptance Criteria
+
+- [x] Final evidence can name the exact routing headings and destinations, canonical owners, lexical definition order, and preserved interfaces.
+
+## Progress
+
+- [x] Milestone 1 started
+- [x] Milestone 1 completed
+- [x] Milestone 2 started
+- [x] Milestone 2 completed
+- [x] Milestone 3 started
+- [x] Milestone 3 completed
+
+## Decisions
+
+- Decision: Use `README.md` as the landing page, `docs/concepts.md` for vocabulary, `docs/cookbook.md` for procedures, and `docs/reference.md` for normative configuration facts.
+  Rationale: These roles match the requested audiences and eliminate the existing cross document duplication.
+  Date/Author: 2026-07-27 / Codex
+- Decision: Describe the quick start as following installation, without adding an installation command.
+  Rationale: The repository provides no authoritative installation mechanism, so adding one would create unsupported product guidance.
+  Date/Author: 2026-07-27 / Codex
+- Decision: Keep the two required commands in the README quick start as well as in the cookbook recipe.
+  Rationale: The landing page must retain its smallest successful start; the cookbook remains the canonical task procedure with prerequisites and follow up links.
+  Date/Author: 2026-07-27 / Codex
+
+## Risks and Mitigations
+
+- Risk: Moving headings could break public fragments.
+  Mitigation: Retain `## Getting started` and `## Config file`, then validate all local links.
+- Risk: Configuration facts could remain duplicated and drift.
+  Mitigation: Keep their complete statement only in `docs/reference.md#config-file`; other documents link there.
+- Risk: The concepts guide could use Workspace before defining it.
+  Mitigation: Begin its body with `## Workspace` and audit all occurrences after editing.
+- Risk: A newcomer may need installation guidance unavailable in this repository.
+  Mitigation: Do not invent a mechanism; make the quick start's installed binary prerequisite explicit.
+
+## Validation Strategy
+
+1. Search for all protected commands, facts, and required headings.
+2. Run the bundled local Markdown link validator over the landing page and docs directory.
+3. Run the validator's repository test suite and whitespace check.
+4. Inspect every occurrence of `workspace` and walk each audience route from the README.
+
+## Rollout and Recovery
+
+These are documentation only edits with no deployment step. Review the diff before merging. If a route is unsuitable, revert the affected documentation file and this plan together, retaining the required public headings and facts.
+
+## Lessons Learned
+
+- The repository has no committed history and no authoritative installation instructions; the restructure must not infer either.
+- The bundled navigation validator is directly executable; its six tests passed when run as the test script.
```

## Observation 4: documentation-system-restructure

- Status: `PASS`
- Role: `candidate`
- Repetition: `3`
- Duration: `213256 ms`
- Workspace retention: `removed`
- Tokens: input `267621`, cached input `223744`, output `10720`, reasoning output `2812`
- Normalized usage events: `2`, complete `true`, scopes `turn`

### Executor account

Diagnosis: The original landing page, cookbook, and reference duplicated procedures and configuration facts; the conceptual guide used `workspace` before defining it.

Approach:
- Separated landing, conceptual, procedural, and normative-reference roles.
- Validated all local Markdown paths and fragments, protected facts, anchors, and term ordering.

Decisions:
- README is the shared audience landing page.
- Concepts, Cookbook, and Reference are the canonical owners for vocabulary, procedures, and configuration facts.
- `lantern init` is not presented as an installation command.

Rejected Alternatives:
- Inventing installation guidance without a documented installer or distribution source.

Key Changes:
- Added explicit audience routing from README.
- Moved configuration authority to the preserved Config file reference.
- Moved operational command guidance to the cookbook.
- Put the Workspace definition before every conceptual-guide use of the term.

Validation:
- `git diff --check` returned 0.
- `python3 .agents/skills/restructure-documentation/scripts/check_markdown_links.py README.md docs` returned 0.
- Case-insensitive workspace search reports `## Workspace` first at concepts line 3, followed by its definition at line 5.
- The living validation record is in [documentation-restructure-execplan.md](/tmp/skill-eval-artifacts/validate-change-saqr0le6/documentation-system-restructure-k1s4o6pj/documentation-restructure-execplan.md:136).

### Mechanical facts

- Mechanical result: `PASS`
- Oracle result: `PASS`
- Judge verdict: `PASS`
- `executor exit code`: `PASS`
- `executor response schema`: `PASS`
- `required path: README.md`: `PASS`
- `required path: docs/concepts.md`: `PASS`
- `required path: docs/cookbook.md`: `PASS`
- `required path: docs/reference.md`: `PASS`
- `required path: documentation-restructure-execplan.md`: `PASS`
- `required path: AGENTS.md`: `PASS`
- `forbidden changed path: AGENTS.md`: `PASS`
- `forbidden changed path: .agents/skills/**`: `PASS`
- `evaluated skill remained unchanged`: `PASS`
- `command: python3 .agents/skills/restructure-documentation/scripts/check_markdown_links.py README.md docs`: `PASS`

### Changed files

- `README.md`
- `docs/concepts.md`
- `docs/cookbook.md`
- `docs/reference.md`
- `documentation-restructure-execplan.md`

### Sanitized diff

```diff
--- a/README.md
+++ b/README.md
@@ -1,24 +1,28 @@
 # Lantern CLI

-Lantern scans workspaces.
+Lantern scans folders and helps you establish a repeatable scan setup.

-Set `LANTERN_CACHE_DIR` if you do not want `.lantern-cache`. Configuration schema version 3 is current. A workspace is a folder with `lantern.toml`, although the examples below already use that term.
+## Choose a path
+
+### Newcomer: first scan
+
+Start with [Getting started](#getting-started), then learn the [Workspace](docs/concepts.md#workspace) concept behind the files Lantern uses.
+
+### Operator: repeat a task
+
+Use the goal based [Initialize and scan recipe](docs/cookbook.md#initialize-and-scan).
+
+### Contributor: verify configuration
+
+Consult the exact [Config file reference](docs/reference.md#config-file), including the current schema and cache setting.

 ## Getting started

-Run:
+In the folder you want Lantern to initialize, run:

 ```console
 lantern init
 lantern scan --format json
 ```

-The scan command emits JSON. For more concepts see [concepts](docs/concepts.md), for commands see [recipes](docs/cookbook.md), and for every exact setting see [configuration](docs/reference.md#config-file).
-
-## Configuration
-
-The `cache_dir` setting defaults to `.lantern-cache`. `LANTERN_CACHE_DIR` overrides it. Schema version 3 is current.
-
-## Recipes
-
-To create a workspace run `lantern init`. To scan it run `lantern scan --format json`.
+The scan command emits JSON. Next, see [Workspace](docs/concepts.md#workspace) for the directory model, use the [cookbook](docs/cookbook.md#initialize-and-scan) for operations, or consult the [configuration reference](docs/reference.md#config-file) for exact settings.
--- a/docs/concepts.md
+++ b/docs/concepts.md
@@ -1,6 +1,4 @@
 # Concepts
-
-Run `lantern scan --format json` inside a workspace.

 ## Workspace

@@ -8,6 +6,6 @@

 ## Configuration

-Lantern uses configuration schema version 3. Set `LANTERN_CACHE_DIR` to override `.lantern-cache`.
+Lantern reads configuration from `lantern.toml`. For the current schema, cache setting, and environment override, see the [Config file reference](reference.md#config-file).

-See the [README configuration](../README.md#configuration).
+For the commands that initialize and scan this folder, see [Initialize and scan](cookbook.md#initialize-and-scan).
--- a/docs/cookbook.md
+++ b/docs/cookbook.md
@@ -2,13 +2,15 @@

 ## Initialize and scan

-A workspace is a folder containing `lantern.toml`.
+Before starting, read [Workspace](concepts.md#workspace) to understand the folder Lantern uses.
+
+In the directory you want Lantern to initialize, run:

 ```console
 lantern init
 lantern scan --format json
 ```

-Schema version 3 is current. `LANTERN_CACHE_DIR` changes the cache.
+The scan command emits JSON. For cache behavior, environment overrides, and the current schema, use the [Config file reference](reference.md#config-file).

-See [all configuration](reference.md#config-file).
+Return to [Getting started](../README.md#getting-started) for the newcomer route.
--- a/docs/reference.md
+++ b/docs/reference.md
@@ -2,7 +2,7 @@

 ## Config file

-A workspace contains `lantern.toml`. Configuration schema version 3 is current.
+Configuration is stored in `lantern.toml`. Configuration schema version 3 is current.

 | Name | Default |
 | --- | --- |
@@ -10,6 +10,6 @@

 `LANTERN_CACHE_DIR` overrides `cache_dir`.

-Initialize with `lantern init` and scan with `lantern scan --format json`.
+For the initialization and scan procedure, use [Initialize and scan](cookbook.md#initialize-and-scan).

 Return to the [README](../README.md#getting-started).
--- /dev/null
+++ b/documentation-restructure-execplan.md
@@ -0,0 +1,153 @@
+# Restructure Lantern documentation journeys
+
+This ExecPlan is a living document. Keep `Progress`, `Decisions`, `Risks and Mitigations`, and `Lessons Learned` up to date as work advances.
+
+## Purpose / Big Picture
+
+Lantern readers need separate, direct routes for a first installation and scan, operational recipes, and exact configuration facts. This change gives each route one primary document while retaining the established public paths, anchors, commands, environment variable, and current schema version. A reader can observe the result by beginning at the README and following the relevant local link without encountering duplicated configuration authority or an undefined `workspace` in the conceptual guide.
+
+## Scope
+
+In scope: restructure `README.md`, `docs/concepts.md`, `docs/cookbook.md`, and `docs/reference.md`; add and maintain this ExecPlan; and validate all local Markdown navigation. Out of scope: CLI behavior, configuration semantics, generated documentation, and `AGENTS.md`.
+
+Safety boundary: This task is limited to authorized, defensive maintenance of this repository documentation.
+
+## Definitions
+
+Landing page: the short starting document that routes a reader to the appropriate journey.
+
+Canonical owner: the one document responsible for complete, maintained guidance about a subject; other documents link there instead of duplicating it.
+
+Workspace: a folder containing `lantern.toml`. The conceptual guide must define this term before it uses it.
+
+## Existing Context
+
+`README.md` mixes newcomer orientation, recipes, and configuration details. `docs/concepts.md` runs a command inside a workspace before its `## Workspace` definition. `docs/cookbook.md` repeats configuration facts, while `docs/reference.md` repeats procedures. The repository has no committed history or product source files that supersede the user supplied facts: configuration schema version 3 is current, `LANTERN_CACHE_DIR` controls the cache location, and the commands are `lantern init` and `lantern scan --format json`.
+
+Protected interfaces are the existing file paths, `README.md#getting-started`, `docs/reference.md#config-file`, both documented commands, `LANTERN_CACHE_DIR`, and schema version 3. `AGENTS.md` must not change.
+
+## Desired End State
+
+The README starts newcomers at `## Getting started`, gives a smallest successful scan, and routes them to concepts, recipes, and configuration. Concepts owns vocabulary and begins its body with `## Workspace` and its definition. The cookbook owns task procedures, organized by an operator outcome. The reference owns complete configuration facts under its preserved `## Config file` anchor. Every local link and fragment resolves.
+
+## Milestones
+
+### Milestone 1 - Record the documentation architecture
+
+#### Goal
+
+Capture the current overlap, protected interfaces, roles, and validation plan before editing public documentation.
+
+#### Changes
+
+- [x] Create `documentation-restructure-execplan.md` with the audit, scope, and constraints.
+- [x] Assign the README, concepts guide, cookbook, and reference distinct primary roles.
+
+#### Validation
+
+- [x] Command: `rg -n -i 'workspace|lantern init|lantern scan --format json|LANTERN_CACHE_DIR|schema version' README.md docs`
+- [x] Expected result: inventory identifies all preserved interfaces and duplicated ownership.
+
+#### Acceptance Criteria
+
+- [x] The plan names exact files, interfaces, and audience outcomes.
+
+### Milestone 2 - Establish audience routes and canonical owners
+
+#### Goal
+
+Give each audience a direct, ordered route and remove noncanonical detail.
+
+#### Changes
+
+- [x] Edit `README.md` as the newcomer landing page while preserving `## Getting started`.
+- [x] Edit `docs/concepts.md` so `## Workspace` is the first occurrence and definition of the term.
+- [x] Edit `docs/cookbook.md` as the operator recipe owner.
+- [x] Edit `docs/reference.md` as the exact configuration owner while preserving `## Config file`.
+
+#### Validation
+
+- [x] Command: `python3 .agents/skills/restructure-documentation/scripts/check_markdown_links.py README.md docs`
+- [x] Expected result: exit 0 and every local path and fragment resolves.
+- [x] Command: `rg -n -i 'workspace' docs/concepts.md`
+- [x] Expected result: the first match is `## Workspace`, followed immediately by its definition.
+
+#### Acceptance Criteria
+
+- [x] Newcomers, operators, and contributors can select a path from the README.
+- [x] Procedures and configuration facts each have one canonical owner.
+
+### Milestone 3 - Verify the finished documentation system
+
+#### Goal
+
+Confirm facts, public interfaces, routes, and scope are intact.
+
+#### Changes
+
+- [x] Update this ExecPlan with completed progress, validation results, and lessons.
+
+#### Validation
+
+- [x] Command: `git diff --check`
+- [x] Expected result: no whitespace errors.
+- [x] Command: `git diff --check && python3 .agents/skills/restructure-documentation/scripts/check_markdown_links.py README.md docs && rg -n -i 'workspace' docs/concepts.md && rg -n 'lantern init|lantern scan --format json|LANTERN_CACHE_DIR|schema version 3|^## Getting started|^## Config file' README.md docs/*.md`
+- [x] Expected result: checks pass; preserved facts and anchors remain in their canonical destinations.
+
+#### Acceptance Criteria
+
+- [x] All local Markdown navigation is valid.
+- [x] The final diff changes only authorized documentation and the ExecPlan.
+
+## Progress
+
+- [x] Milestone 1 started
+- [x] Milestone 1 completed
+- [x] Milestone 2 started
+- [x] Milestone 2 completed
+- [x] Milestone 3 started
+- [x] Milestone 3 completed
+
+## Decisions
+
+- Decision: Keep `README.md` as the single landing page for all three audiences.
+  Rationale: It is the existing public entry point and can route readers without duplicating the canonical guides.
+  Date/Author: 2026-07-27 / Codex
+
+- Decision: Make `docs/concepts.md`, `docs/cookbook.md`, and `docs/reference.md` the canonical owners for concepts, procedures, and configuration facts respectively.
+  Rationale: These roles align each document with its audience and remove the current overlap.
+  Date/Author: 2026-07-27 / Codex
+
+- Decision: Do not present `lantern init` as an installation command.
+  Rationale: The repository supplies no authoritative installation command or distribution guidance; the newcomer route starts with the first documented Lantern action.
+  Date/Author: 2026-07-27 / Codex
+
+## Risks and Mitigations
+
+- Risk: Renaming headings could break inbound public fragments.
+  Mitigation: Retain `## Getting started` and `## Config file` exactly and run the local link validator.
+
+- Risk: Moving repeated facts could lose a required interface.
+  Mitigation: Search for every preserved command, variable, and schema fact after editing and retain them in their canonical documents.
+
+- Risk: The conceptual guide may still use `workspace` before defining it.
+  Mitigation: Search the complete file case insensitively and inspect the first match.
+
+## Validation Strategy
+
+1. Search the changed documents for protected anchors, terms, commands, and configuration facts.
+2. Run `git diff --check`.
+3. Run `python3 .agents/skills/restructure-documentation/scripts/check_markdown_links.py README.md docs`.
+4. Manually follow the README routes for newcomer, operator, and contributor outcomes.
+5. Inspect the final diff and status to confirm `AGENTS.md` remains unchanged.
+
+Result on 2026-07-27: `git diff --check` returned 0; the local link validator returned 0; the concept search reported `## Workspace` at line 3 and its definition at line 5; and the protected anchors, commands, variable, and schema fact were found at their intended destinations.
+
+## Rollout and Recovery
+
+Publish the four documentation files and this plan together. If an external consumer reports a broken link, restore the preserved heading or add a compatible explicit ID, then rerun the local link validator. Reverting this documentation-only change restores the previous navigation without affecting Lantern behavior.
+
+## Lessons Learned
+
+- The repository contains no implementation or schema source files, so the supplied preservation requirements are the authority for current configuration facts.
+- The repository also has no installation source. Installation documentation needs an authoritative package or distribution owner before it can be added safely.
```

## Integrity

- Report digest: `sha256:5dd644befd9ba19b763d7bb241404a1c875d6f19f2ec651186650968ccb0f0fd`
