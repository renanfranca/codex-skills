import { expect, test } from '@playwright/test';

test('a reader can move from the project purpose to the skill catalog', async ({ page }) => {
  const consoleErrors = [];
  page.on('console', message => {
    if (message.type() === 'error') consoleErrors.push(message.text());
  });

  await page.goto('./');

  await expect(page.getByRole('heading', { level: 1, name: 'Codex Skills' })).toBeVisible();
  await expect(page.getByText('44 archived operations')).toBeVisible();
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

  await page.getByRole('link', { name: /implement-execplan[\s\S]*No archived evidence/ }).click();

  await expect(page.getByRole('heading', { level: 1, name: 'implement-execplan' })).toBeVisible();
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
