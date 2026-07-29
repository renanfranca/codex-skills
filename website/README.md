# Codex Skills

The documentation site for the repository's reusable Codex workflows and archived evaluation evidence. VitePress renders the site at the GitHub Pages base path `/codex-skills/`; generated pages remain projections of canonical `SKILL.md` and `evaluation-reports/**/report.json` files.

## Prerequisites

- Node.js 24 or newer
- npm 11.7.0
- Python 3 for evaluation archive validation

```bash
npm ci
npm exec -- playwright install chromium
```

## Local environment

<!-- seed4j-needle-localEnvironment -->

The content generator reads the repository one directory above `website/`. It validates the archive before each development server or production build and writes disposable pages to `.generated/`.

```bash
npm run dev
```

Open `http://localhost:5173/codex-skills/`.

## Derived evidence status

The skill catalog derives evidence status from the current skill source, the archived report fingerprints, and the case IDs in the current `evals/suite.json`. Labels are not maintained by hand.

For operations that compare a baseline with a candidate, only the candidate fingerprint can establish current evidence. For direct runs, the evaluated fingerprint is used. A matching baseline never establishes evidence for the current source, and reports without a comparable fingerprint remain historical.

The catalog selects the strongest applicable status in this order:

1. **Promotion evidence** means an eligible passing promotion matches the current source.
2. **Complete current coverage** means every case declared by the current suite has at least one matching nonbaseline `PASS`, possibly across several operations.
3. **Partial current coverage** means there is at least one matching `PASS`, but the declared suite is not completely covered or no suite is declared.
4. **No current pass** means matching reports exist without a current `PASS`.
5. **Historical runs** means reports exist, but none matches the current source with a comparable fingerprint.
6. **No evaluation yet** means no report is archived for the skill.

Complete current coverage does not mean promotion, repeatability, or stability. Promotion remains governed by the runner contract, including valid RED, three stable GREEN results, and the required regression gates. Each evidence panel retains current results by their recorded status so failures and inconclusive or unstable operations remain visible even when stronger evidence takes precedence.

## Validation

```bash
npm test
npm run prettier:check
npm run build
npm run test:e2e
```

The browser suite runs the same journeys with desktop Chromium and a fully emulated Pixel 7 profile. `npm run test:e2e` builds the site first and starts a local preview automatically.

## Content and publication

- `content-config.json` records website-only catalog decisions such as compatibility skills excluded from the active catalog.
- `scripts/generate-content.mjs` creates the home page, skill pages, evaluation history, and report evidence pages.
- `.vitepress/` contains the GitHub Pages base path, navigation, and visual theme.
- `.github/workflows/deploy-website.yml` validates, tests, builds, and deploys the static artifact after changes reach `main`.

GitHub Pages must use **GitHub Actions** as its publishing source. The workflow publishes `website/.vitepress/dist` to `https://renanfranca.github.io/codex-skills/`.

<!-- seed4j-needle-startupCommand -->
<!-- seed4j-needle-documentation -->
