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

  const skillWithoutEvidence = page.locator('article.skill-card').filter({ hasText: 'No evaluation yet' }).first();
  const skillName = await skillWithoutEvidence.getByRole('heading', { level: 2 }).textContent();
  await skillWithoutEvidence.locator('a.skill-card-main').click();

  await expect(page.getByRole('heading', { level: 1, name: skillName })).toBeVisible();
  await expect(page.getByText('No evaluation yet')).toBeVisible();
  await expect(page.getByText('No archived evaluation report is available for this skill yet.')).toBeVisible();
  await expect(page.getByText('No archived evaluation reports are available for this skill yet.')).toBeVisible();
});

test('the evidence legend explains all six statuses without relying on color', async ({ page }) => {
  await page.goto('skills/');

  await page.getByText('How to read evidence status').click();
  const legend = page.locator('.evidence-legend');
  for (const label of [
    'Promotion evidence',
    'Complete current coverage',
    'Partial current coverage',
    'No current pass',
    'Historical runs',
    'No evaluation yet',
  ]) {
    await expect(legend.getByText(label, { exact: true })).toBeVisible();
  }
  await expect(legend.locator('.evidence-state-indicator')).toHaveCount(6);
  await expect(legend.getByText('Color is only a secondary cue.')).toBeVisible();
});

test('a reader can inspect current evidence in the viewport appropriate panel', async ({ page }, testInfo) => {
  await page.goto('skills/');

  const card = page.locator('article.skill-card').filter({ hasText: 'refactor-design' });
  const trigger = card.getByRole('button', { name: /Explain evidence for refactor-design/ });
  if (testInfo.project.name === 'mobile') {
    await trigger.tap();
  } else {
    await trigger.click();
  }

  const panel = page.getByRole('dialog', { name: 'refactor-design evidence status' });
  await expect(panel).toBeVisible();
  await expect(panel.getByText('Partial current coverage', { exact: true })).toBeVisible();
  await expect(panel.getByText('3 of 12 declared cases have a current pass.')).toBeVisible();
  await expect(panel.getByText('No matching promotion')).toBeVisible();
  await expect(panel.getByText('PASS', { exact: true })).toBeVisible();
  await expect(panel.getByText('4', { exact: true })).toBeVisible();
  await expect(panel.getByRole('link', { name: /run · 2026/ }).first()).toBeVisible();
  if (testInfo.project.name === 'mobile') {
    await expect(panel).toHaveClass(/evidence-status-sheet/);
    await expect(page.getByTestId('evidence-backdrop')).toBeVisible();
  } else {
    await expect(panel).toHaveClass(/evidence-status-popover/);
    await expect(page.getByTestId('evidence-backdrop')).toHaveCount(0);
  }

  await panel.getByRole('button', { name: 'Close evidence status' }).click();
  await expect(panel).toBeHidden();
  await expect(trigger).toBeFocused();
});

test('the evidence panel supports keyboard opening, escape, and outside dismissal', async ({ page }, testInfo) => {
  await page.goto('skills/');

  const trigger = page
    .locator('article.skill-card')
    .filter({ hasText: 'execplan-tdd' })
    .getByRole('button', { name: /Explain evidence for execplan-tdd/ });
  await trigger.focus();
  await page.keyboard.press('Enter');
  const panel = page.getByRole('dialog', { name: 'execplan-tdd evidence status' });
  await expect(panel).toBeVisible();
  await page.keyboard.press('Escape');
  await expect(panel).toBeHidden();
  await expect(trigger).toBeFocused();

  await page.keyboard.press('Space');
  await expect(panel).toBeVisible();
  if (testInfo.project.name === 'mobile') {
    await page.getByTestId('evidence-backdrop').tap({ position: { x: 10, y: 10 } });
  } else {
    await page.getByRole('heading', { level: 1, name: /Reusable workflows/ }).click();
  }
  await expect(panel).toBeHidden();
  await expect(trigger).toBeFocused();
});

test('card, evidence, and history navigation remain independent', async ({ page }) => {
  await page.goto('skills/');

  const card = page.locator('article.skill-card').filter({ hasText: 'refactor-design' });
  await expect(card.locator('a button, button a')).toHaveCount(0);
  await card.locator('a.skill-card-main').click();
  await expect(page).toHaveURL(/\/skills\/refactor-design$/);

  await page.goBack();
  await page.locator('article.skill-card').filter({ hasText: 'refactor-design' }).locator('a.skill-history-link').click();
  await expect(page).toHaveURL(/\/skills\/refactor-design#evaluation-history$/);
  await expect(page.getByRole('heading', { level: 2, name: 'Evaluation history' })).toBeVisible();
});

test('evidence remains readable in light and dark themes', async ({ page }) => {
  await page.goto('skills/');

  const card = page.locator('article.skill-card').filter({ hasText: 'refactor-design' });
  const lightBorder = await card.evaluate(element => getComputedStyle(element).borderTopColor);
  await expect(card.getByText('Partial current coverage', { exact: true })).toBeVisible();

  const themeSwitch = page.getByRole('switch', { name: 'Switch to dark theme' });
  if (!(await themeSwitch.isVisible())) {
    await page.getByRole('button', { name: 'mobile navigation' }).click();
  }
  await themeSwitch.click();

  const darkBorder = await card.evaluate(element => getComputedStyle(element).borderTopColor);
  expect(darkBorder).not.toBe(lightBorder);
  await expect(card.getByText('Partial current coverage', { exact: true })).toBeVisible();
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
  await page
    .locator('article.skill-card')
    .first()
    .getByRole('button', { name: /Explain evidence/ })
    .click();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
});
