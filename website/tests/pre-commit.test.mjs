import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { mkdtempSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import test from 'node:test';

const websiteDirectory = join(dirname(fileURLToPath(import.meta.url)), '..');

test('formats staged website sources without touching staged root files', () => {
  const repository = mkdtempSync(join(tmpdir(), 'codex-skills-hook-'));
  const nestedWebsite = join(repository, 'website');
  const rootDocument = join(repository, 'ROOT.md');
  const websiteSource = join(nestedWebsite, 'example.js');

  mkdirSync(nestedWebsite);
  writeFileSync(rootDocument, '# Root  title\n');
  writeFileSync(websiteSource, 'const answer=42\n');
  execFileSync('git', ['init', '--quiet'], { cwd: repository });
  execFileSync('git', ['add', 'ROOT.md', 'website/example.js'], { cwd: repository });

  execFileSync(join(websiteDirectory, 'node_modules', '.bin', 'lint-staged'), ['--config', join(websiteDirectory, '.lintstagedrc.cjs')], {
    cwd: nestedWebsite,
    env: { ...process.env, FORCE_COLOR: '0' },
    stdio: 'pipe',
  });

  assert.equal(readFileSync(websiteSource, 'utf8'), 'const answer = 42;\n');
  assert.equal(readFileSync(rootDocument, 'utf8'), '# Root  title\n');
});
