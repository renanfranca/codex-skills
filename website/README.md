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
