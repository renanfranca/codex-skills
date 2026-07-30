import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import test from 'node:test';

const websiteDirectory = join(dirname(fileURLToPath(import.meta.url)), '..');
const repositoryDirectory = join(websiteDirectory, '..');

test('keeps local and CI visual checkpoints on the packaged Playwright version and image', () => {
  const packageJson = JSON.parse(readFileSync(join(websiteDirectory, 'package.json'), 'utf8'));
  const localRunner = readFileSync(join(websiteDirectory, 'scripts', 'run-playwright-container.sh'), 'utf8');
  const workflow = readFileSync(join(repositoryDirectory, '.github', 'workflows', 'deploy-website.yml'), 'utf8');

  const playwrightVersion = packageJson.devDependencies['@playwright/test'];
  const localImage = localRunner.match(/^readonly PLAYWRIGHT_IMAGE="([^"]+)"$/m)?.[1];
  const workflowImage = workflow.match(/^\s+image:\s+(\S+)$/m)?.[1];
  const imageVersion = localImage?.match(/\/playwright:v([^-@]+)-jammy@sha256:[a-f0-9]{64}$/)?.[1];

  assert.equal(packageJson.scripts['test:e2e'], 'bash scripts/run-playwright-container.sh');
  assert.equal(packageJson.scripts['test:e2e:direct'], 'playwright test');
  assert.equal(localImage, workflowImage);
  assert.equal(imageVersion, playwrightVersion);
  assert.match(localRunner, /docker run --rm --init --ipc=host/);
  assert.match(workflow, /npm run test:e2e:direct --prefix website/);
  assert.doesNotMatch(workflow, /playwright install/);
});
