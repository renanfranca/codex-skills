# Codex Skills

The documentation site for the repository's reusable Codex workflows and archived evaluation evidence. VitePress renders the site at the GitHub Pages base path `/codex-skills/`; generated pages remain projections of canonical `SKILL.md` and `evaluation-reports/**/report.json` files.

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

The website keeps one `evaluationGlossary` in `scripts/evaluation-glossary.mjs`. Generated reports use it for complete label contextual help, human operation names, evidence status, and the broad “Learn how to read this report” guide. The guide defines the evaluation runner as `run_skill_evals.py` and keeps three questions separate:

- Evidence status describes the strength and currency of evidence.
- Operation type describes how the evidence was produced.
- Recorded result describes what happened in that operation.

The generator validates closed glossary taxonomies against `eval-report.schema.json` and `eval-result.schema.json`. It also rejects archived observation roles outside the runner's known role set. Model and reasoning effort remain open strings because their schemas do not define exhaustive lists.

The skill catalog derives evidence status from the current skill source, the archived report fingerprints, and the case IDs in the current `evals/suite.json`. Labels are not maintained by hand.

For operations that compare a baseline with a candidate, only the candidate fingerprint can establish current evidence. For direct runs, the evaluated fingerprint is used. A matching baseline never establishes evidence for the current source, and reports without a comparable fingerprint remain historical.

The catalog selects the strongest applicable status in this order:

1. **Validated promotion** means a promotion eligible `PASS` matches the current source and records an integrated qualification: valid RED, three stable GREEN results for each affected case, proportional regression when the declared impact requires it, and the current candidate fingerprint.
2. **Complete current coverage** means every case declared by the current suite has one matching nonbaseline `PASS`, possibly across several operations.
3. **Partial current coverage** means there is at least one matching `PASS`, but the declared suite is not completely covered or no suite is declared.
4. **No current pass** means matching reports exist without a current `PASS`.
5. **Historical runs** means reports exist, but none matches the current source with a comparable fingerprint.
6. **No evaluation yet** means no report is archived for the skill.

Complete current coverage does not establish RED, repetition, stability, regression, or promotion. Each evidence panel retains current results by their recorded status so failures and inconclusive or unstable operations remain visible even when stronger evidence takes precedence.

A validated promotion panel projects recorded effort exclusively from its archived report: executed executor, judge, and total sessions; total and cached input tokens; duration; and runtime and token telemetry completeness.

A model session is one isolated, ephemeral `codex exec --json` invocation started by the evaluation runner. The executor performs the evaluated task; an optional judge evaluates the result in a separate invocation. A model session is not a message, conversational turn, deterministic check, or complete promotion. Deterministic checks consume zero model sessions.

Token totals measure recorded workload, not an observed financial charge. Missing archived telemetry remains `Not recorded`; the website does not infer values or reconstruct cost.

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
- `scripts/generate-content.mjs` creates the home page, skill pages, evaluation history, and report evidence pages.
- `.vitepress/` contains the GitHub Pages base path, navigation, and visual theme.
- `.github/workflows/deploy-website.yml` validates, tests, builds, and deploys the static artifact after changes reach `main`. Its build job uses the same pinned visual-test container as the local runner.

GitHub Pages must use **GitHub Actions** as its publishing source. The workflow publishes `website/.vitepress/dist` to `https://renanfranca.github.io/codex-skills/`.

<!-- seed4j-needle-startupCommand -->
<!-- seed4j-needle-documentation -->
