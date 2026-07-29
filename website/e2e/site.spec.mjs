import { expect, test } from '@playwright/test';
import { readFileSync } from 'node:fs';

const archiveManifest = JSON.parse(readFileSync(new URL('../../evaluation-reports/manifest.json', import.meta.url), 'utf8'));

test('a reader can move from the project purpose to the skill catalog', async ({ page }) => {
  const consoleErrors = [];
  page.on('console', message => {
    if (message.type() === 'error') consoleErrors.push(message.text());
  });

  await page.goto('./');

  await expect(page.getByRole('heading', { level: 1, name: 'Evaluating Codex Skills' })).toBeVisible();
  await expect(page.getByText('Evidence of how effectively skills guide Codex behavior.')).toBeVisible();
  await expect(page.getByText(`${archiveManifest.report_count} archived operations`)).toBeVisible();
  await page.getByRole('link', { name: /Explore the skills/ }).click();
  await expect(page).toHaveURL(/\/codex-skills\/skills\/?$/);
  await expect(
    page.getByRole('heading', {
      level: 1,
      name: /Reusable workflows/,
    }),
  ).toBeVisible();
  expect(consoleErrors).toEqual([]);
});

test('the public mark matches the approved evidence identity in both themes', async ({ page }) => {
  await page.goto('./');

  const mark = page.getByRole('img', { name: 'Evaluating Codex Skills' });
  await expect(mark).toHaveScreenshot('evidence-mark-light.png');

  const themeSwitch = page.getByRole('switch', { name: 'Switch to dark theme' });
  if (!(await themeSwitch.isVisible())) {
    await page.getByRole('button', { name: 'mobile navigation' }).click();
  }
  await themeSwitch.click();
  await expect(mark).toHaveScreenshot('evidence-mark-dark.png');
});

test('a reader can inspect a failed operation instead of seeing only passes', async ({ page }) => {
  await page.goto('evaluations/');

  const failedOperation = page.getByRole('link', { name: /develop-skill-with-evals[\s\S]*ERROR/ }).first();
  await expect(failedOperation).toBeVisible();
  await failedOperation.click();

  await expect(page.getByText('Recorded result')).toBeVisible();
  await expect(page.getByText('ERROR', { exact: true }).first()).toBeVisible();
  await expect(page.getByText('Failure category')).toBeVisible();
});

test('a skill without archived runs says that evidence is unavailable', async ({ page }) => {
  await page.goto('skills/');

  const skillWithoutEvidence = page.locator('a.skill-card').filter({ hasText: 'No archived evidence' }).first();
  const skillName = await skillWithoutEvidence.getByRole('heading', { level: 2 }).textContent();
  await skillWithoutEvidence.click();

  await expect(page.getByRole('heading', { level: 1, name: skillName })).toBeVisible();
  await expect(page.getByText('No archived evidence')).toBeVisible();
  await expect(page.getByText('No archived evaluation reports are available for this skill yet.')).toBeVisible();
});

test('a reader can expand the retained code diff for an observation', async ({ page }) => {
  await page.goto('skills/refactor-design');
  await page
    .getByRole('link', { name: /run[\s\S]*PASS/ })
    .first()
    .click();

  const diffSummary = page.getByText('View code diff').first();
  await expect(diffSummary).toBeVisible();
  await diffSummary.click();

  await expect(page.locator('code').filter({ hasText: '--- a/' }).first()).toBeVisible();
  const fragmentSummary = page.getByText('Code fragments').first();
  await expect(fragmentSummary).toBeVisible();
  await fragmentSummary.click();
  await expect(page.getByText('Before', { exact: true }).first()).toBeVisible();
  await expect(page.getByText('After', { exact: true }).first()).toBeVisible();
});

test('the project and skill catalog fit the available viewport', async ({ page }) => {
  await page.goto('./');

  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
  await page.getByRole('link', { name: /Explore the skills/ }).click();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
});
