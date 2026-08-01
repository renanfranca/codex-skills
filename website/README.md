# Codex Skills

The documentation site for the repository's reusable Codex workflows, declared evaluation cases, and archived operation evidence. VitePress renders the site at the GitHub Pages base path `/codex-skills/`; generated pages remain projections of canonical skill evaluation sources and `evaluation-reports/**/report.json` files.

## Prerequisites

- Node.js 24 or newer
- npm 11.7.0
- Python 3 for evaluation archive validation
- Docker Engine for the Playwright visual checkpoint

```bash
npm ci
```

## Local environment

<!-- seed4j-needle-localEnvironment -->

The content generator reads the repository one directory above `website/`. It validates the archive before each development server or production build and writes disposable pages to `.generated/`.

```bash
npm run dev
```

Open `http://localhost:5173/codex-skills/`.

## Evaluation vocabulary and evidence status

The website keeps one `evaluationGlossary` in `scripts/evaluation-glossary.mjs`. Generated reports use it for complete label contextual help, human operation names, evidence status, and the broad “Learn how to read this report” guide. Evaluation pages use the same component with evaluation context for current evidence, latest recorded result, suite state, and kind. The guide defines the evaluation runner as `run_skill_evals.py` and keeps three questions separate:

- Evidence status describes the strength and currency of evidence.
- Operation type describes how the evidence was produced.
- Recorded result describes what happened in that operation.

The generator validates closed glossary taxonomies against `eval-report.schema.json` and `eval-result.schema.json`. It also rejects archived observation roles outside the runner's known role set. Model and reasoning effort remain open strings because their schemas do not define exhaustive lists.

The skill catalog derives evidence status from the current skill source, the archived report fingerprints, and the case IDs in the current `evals/suite.json`. Labels are not maintained by hand.

Each skill page also publishes an evaluation catalog. Active evaluations come only from the ordered IDs in `evals/suite.json` and their current `evals/cases/<case-id>/` directories. The generator reads `case.json`, a public prompt when the case uses an executor, and public fixture paths. It computes current skill and case fingerprints with the runner's canonical tree algorithm and does not modify those sources.

An **evaluation** is the persistent case contract, an **observation** is one case result inside an archived invocation, and an **operation** is the complete runner invocation that can contain several observations. Public `/evaluations/` and report URLs remain stable, but the site labels that archive **Operations**. Skill pages link new operation navigation to `#operation-history` and retain `#evaluation-history` as an empty compatibility target.

Active case routes use `/skills/<skill-id>/evaluations/<case-id>`. An always visible introduction defines an evaluation as the persistent case definition, an observation as one recorded case result, and an operation as the complete runner invocation. Concise guidance beneath each section explains how to interpret the current definition and archived operation facts without opening contextual help.

The pages show current evidence, suite membership, a linked current definition flow, public prompt and fixture paths, mechanical, oracle, and judge details, the latest related operation flow, and one history row per related operation.

**Kind** is visible with definitions for `behavioral`, `non_behavioral`, `trigger`, and `deterministic`, and the same taxonomy is available through contextual help. Semantic flows include the executor and applicable semantic verification. Deterministic flows omit the executor, judge, and expected executor exit code because executor configuration is forbidden for that kind. The flow is static semantic HTML and CSS with visible focus, text labels, responsive stacking, and reduced motion behavior.

Archived observation IDs absent from the current suite become separate historical evaluations at the same route shape. Historical pages explain locally that operation history remains because archived operations contain observations for the case, while the current suite no longer provides a definition. They retain only durable operation facts and do not reconstruct or present a current prompt, fixture, flow, case fingerprint, suite evidence claim, or verification contract as a former definition.

Case evidence requires both the current skill source fingerprint and current case fingerprint. Its closed states, in priority order, are:

1. **Validated promotion** means a promotion eligible `PASS` matches both fingerprints and includes passing `candidate` observations for the case. A passing `regression` observation does not establish this state.
2. **Current pass** means both fingerprints match at least one passing nonbaseline observation without a qualifying promotion.
3. **No current pass** means compatible observations exist without a passing nonbaseline observation.
4. **Historical runs** means related observations exist, but none matches both current fingerprints.
5. **Not evaluated yet** means no archived observation exists for the case.

Related observations are grouped under their one operation in report order. The latest operation is selected by recorded `started_at`, then operation ID. When one operation records different statuses for a case, the site displays counts for every status instead of selecting one observation. Case results remain separate from the complete operation result, so a passing case inside a failed operation is not presented as an operation pass.

For operations that compare a baseline with a candidate, only the candidate fingerprint can establish current evidence. For direct runs, the evaluated fingerprint is used. A matching baseline never establishes evidence for the current source, and reports without a comparable fingerprint remain historical.

The catalog selects the strongest applicable status in this order:

1. **Validated promotion** means a promotion eligible `PASS` matches the current source and records an integrated qualification: valid RED, three stable GREEN results for each affected case, proportional regression when the declared impact requires it, and the current candidate fingerprint.
2. **Complete current suite evidence** means every case declared by the current suite has one matching nonbaseline `PASS`, possibly across several operations.
3. **Partial current suite evidence** means there is at least one matching `PASS`, but not every declared suite case has one or no suite is declared.
4. **No current pass** means matching reports exist without a current `PASS`.
5. **Historical runs** means reports exist, but none matches the current source with a comparable fingerprint.
6. **No evaluation yet** means no report is archived for the skill.

Complete current suite evidence does not establish RED, repetition, stability, regression, or promotion. Each evidence panel presents the passing case count as **Suite evidence** and retains current results by their recorded status so failures and inconclusive or unstable operations remain visible even when stronger evidence takes precedence.

A validated promotion panel projects recorded effort exclusively from its archived report: executed executor, judge, and total sessions; input, cached input, output, reasoning output, and total tokens; duration; normalized usage event count; API reference estimate value or status; and runtime and token telemetry completeness.

A model session is one isolated, ephemeral `codex exec --json` invocation started by the evaluation runner. The executor performs the evaluated task; an optional judge evaluates the result in a separate invocation. A model session is not a message, conversational turn, deterministic check, or complete promotion. Deterministic checks consume zero model sessions.

Token totals measure recorded workload, not an observed financial charge. Cached input is a subset of input tokens. Reasoning output is a subset of output tokens, so it is displayed separately but never added to the total again.

Each report page preserves the archived usage decomposition, completeness fields, event count, event completeness, and every normalized event with its recorded origin, scope, and token fields. The event table is collapsed by default. An empty or legacy report remains explicit: missing archived telemetry appears as `Not recorded`, and the website does not derive event counts, cache ratios, token subtotals, or costs.

An **API reference estimate** applies an archived dated API price table to recorded usage. It is never an observed charge, ChatGPT billing statement, or invoice. Report pages show the archived status, currency, amount, base rate amount, calculation tokens, prices, components, long context assessment, and limitations. Monetary values retain their recorded decimal value without scientific notation. When request scoped long context pricing cannot be audited from event scope, the page labels the base rate amount as reference only and states that the exact estimate is unavailable.

Report execution facts retain compatibility fields in generated `data.json` and add `runtimeByRole`, `sessionsByRole`, and `judgeState`. Explicit `failure_category: null` renders as `None`; an absent property renders as `Not recorded`. A disabled judge renders as `Not used`, an enabled judge that did not execute renders as `Skipped`, and an executed judge renders its archived verdict.

On desktop, a complete fact label opens an anchored popover. On narrow viewports it opens a scrollable bottom sheet. The complete guide uses the same responsive component and includes canonical values that may be absent from the current report.

## Validation

```bash
npm test
npm run prettier:check
npm run build
npm run test:e2e
```

The browser suite runs the same journeys with desktop Chromium and a fully emulated Pixel 7 profile. `npm run test:e2e` builds the site first and starts a local preview automatically.

The public E2E command runs Playwright in the same digest-pinned official Playwright 1.62.0 Jammy container used by GitHub Actions. The runner forwards additional Playwright arguments, so update all existing visual baselines in that environment with:

```bash
npm run test:e2e -- --update-snapshots
```

The container uses `--init`, host IPC, the invoking user, and an isolated temporary volume for `node_modules`. Its first execution downloads the pinned image. `npm run test:e2e:direct` is an internal command for GitHub Actions or a shell already running inside that exact container; do not use it to create host baselines.

## Content and publication

- `content-config.json` records website-only catalog decisions such as compatibility skills excluded from the active catalog.
- `scripts/evaluation-catalog.mjs` loads current case definitions, groups archived observations by operation, and derives case evidence.
- `scripts/generate-content.mjs` creates the home page, skill pages, active and historical evaluation pages, the operation archive, and report evidence pages.
- `scripts/telemetry-format.mjs` keeps API reference values and statuses consistent between generated reports and interactive promotion panels.
- `.vitepress/` contains the GitHub Pages base path, navigation, and visual theme.
- `.github/workflows/deploy-website.yml` validates, tests, builds, and deploys the static artifact after changes reach `main`. Its build job uses the same pinned visual-test container as the local runner.

GitHub Pages must use **GitHub Actions** as its publishing source. The workflow publishes `website/.vitepress/dist` to `https://renanfranca.github.io/codex-skills/`.

<!-- seed4j-needle-startupCommand -->
<!-- seed4j-needle-documentation -->
