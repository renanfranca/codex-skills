import { readFileSync } from 'node:fs';
import { defineConfig } from 'vitepress';
import { resolveSiteBase } from '../scripts/site-base.mjs';

const contentConfig = JSON.parse(readFileSync(new URL('../content-config.json', import.meta.url), 'utf8'));
const siteBase = resolveSiteBase(contentConfig.base);

export default defineConfig({
  lang: 'en-US',
  title: 'Evaluating Codex Skills',
  description: 'Evidence of how effectively skills guide Codex behavior.',
  base: siteBase,
  srcDir: '.generated',
  cleanUrls: true,
  sitemap: {
    hostname: 'https://renanfranca.github.io/codex-skills/',
  },
  head: [
    ['meta', { name: 'theme-color', content: '#171713' }],
    ['meta', { name: 'author', content: 'Renan Franca' }],
    [
      'link',
      {
        rel: 'icon',
        type: 'image/svg+xml',
        href: `${siteBase}mark-light.svg`,
      },
    ],
  ],
  themeConfig: {
    logo: {
      light: '/mark-light.svg',
      dark: '/mark-dark.svg',
      alt: 'Evaluating Codex Skills',
    },
    nav: [
      { text: 'Skills', link: '/skills/' },
      { text: 'Operations', link: '/evaluations/' },
      {
        text: 'Method',
        link: 'https://github.com/renanfranca/codex-skills/blob/main/EVALUATIONS.md',
      },
    ],
    search: {
      provider: 'local',
    },
    socialLinks: [
      {
        icon: 'github',
        link: 'https://github.com/renanfranca/codex-skills',
      },
    ],
    outline: {
      level: [2, 3],
      label: 'On this page',
    },
    footer: {
      message: 'Evidence is historical, inspectable, and explicit about limits.',
      copyright: 'Released under the repository license.',
    },
  },
});
