import { readFileSync } from 'node:fs';
import { defineConfig } from 'vitepress';

const contentConfig = JSON.parse(readFileSync(new URL('../content-config.json', import.meta.url), 'utf8'));

export default defineConfig({
  lang: 'en-US',
  title: 'Codex Skills',
  description: 'Reusable Codex workflows with inspectable evaluation evidence.',
  base: contentConfig.base,
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
        href: `${contentConfig.base}mark-light.svg`,
      },
    ],
  ],
  themeConfig: {
    logo: {
      light: '/mark-light.svg',
      dark: '/mark-dark.svg',
      alt: 'Codex Skills',
    },
    nav: [
      { text: 'Skills', link: '/skills/' },
      { text: 'Evaluations', link: '/evaluations/' },
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
