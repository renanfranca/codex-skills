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
    'Validated promotion',
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

test('a validated promotion explains qualification and recorded effort', async ({ page }, testInfo) => {
  await page.goto('skills/');

  const card = page.locator('article.skill-card').filter({ hasText: 'restructure-documentation' });
  const trigger = card.getByRole('button', { name: /Explain evidence for restructure-documentation/ });
  if (testInfo.project.name === 'mobile') {
    await trigger.tap();
  } else {
    await trigger.click();
  }

  const panel = page.getByRole('dialog', { name: 'restructure-documentation evidence status' });
  await expect(panel.locator('header').getByText('Validated promotion', { exact: true })).toBeVisible();
  await expect(panel.getByText('Qualification gates', { exact: true })).toBeVisible();
  await expect(panel.getByText('Valid RED', { exact: true })).toBeVisible();
  await expect(panel.getByText('Three stable GREEN results per affected case', { exact: true })).toBeVisible();
  await expect(panel.getByText('Proportional regression when required', { exact: true })).toBeVisible();
  await expect(panel.getByText('Current source fingerprint', { exact: true })).toBeVisible();

  await expect(panel.getByText('Recorded effort', { exact: true })).toBeVisible();
  await expect(panel.getByText('Executor sessions', { exact: true })).toBeVisible();
  await expect(panel.getByText('Judge sessions', { exact: true })).toBeVisible();
  await expect(panel.getByText('Total sessions', { exact: true })).toBeVisible();
  await expect(panel.getByText('Total tokens', { exact: true })).toBeVisible();
  await expect(panel.getByText('Cached input tokens', { exact: true })).toBeVisible();
  await expect(panel.getByText('Duration', { exact: true })).toBeVisible();
  await expect(panel.getByText('Runtime telemetry', { exact: true })).toBeVisible();
  await expect(panel.getByText('Token telemetry', { exact: true })).toBeVisible();
  await expect(panel.getByText(/one isolated executor or judge invocation recorded by qualification/i)).toBeVisible();
  await expect(panel.getByText(/Deterministic checks can consume zero sessions/)).toBeVisible();
  await expect(panel.getByText(/not an observed financial charge/)).toBeVisible();
  await expect(panel.getByRole('link', { name: 'Inspect promotion report' })).toHaveAttribute(
    'href',
    /\/evaluations\/restructure-documentation\/20260727T233326\.147750Z-48228593ef91$/,
  );
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

test('report vocabulary is learnable in context and in the complete guide', async ({ page }, testInfo) => {
  const report = archiveManifest.reports.find(item => item.status === 'PASS');
  await page.goto(`evaluations/${report.skill}/${report.operation_id}`);

  const factGrid = page.locator('.fact-grid').first();
  const executorHelp = factGrid.getByRole('button', { name: /Executor model/ });
  const targetSize = await executorHelp.boundingBox();
  expect(targetSize.height).toBeGreaterThanOrEqual(44);
  await executorHelp.focus();
  await page.keyboard.press('Enter');

  const fieldPanel = page.getByRole('dialog', { name: 'Executor model help' });
  await expect(fieldPanel.getByText('Current value', { exact: true })).toBeVisible();
  await expect(fieldPanel.getByText(/schema accepts an open string/i)).toBeVisible();
  if (testInfo.project.name === 'mobile') {
    await expect(fieldPanel).toHaveClass(/evaluation-help-sheet/);
  } else {
    await expect(fieldPanel).toHaveClass(/evaluation-help-popover/);
  }
  await expect(page).toHaveScreenshot('execution-facts-help.png', { maxDiffPixelRatio: 0.01 });

  await page.keyboard.press('Escape');
  await expect(fieldPanel).toBeHidden();
  await expect(executorHelp).toBeFocused();

  await page.getByRole('button', { name: 'Learn how to read this report' }).click();
  const guide = page.getByRole('dialog', { name: 'Learn how to read this report' });
  await expect(guide.getByText(/program run_skill_evals\.py/)).toBeVisible();
  await expect(guide.locator('dt').filter({ hasText: 'RED/GREEN check' })).toBeVisible();
  await expect(guide.getByText('verify-change', { exact: true })).toBeVisible();
  await expect(guide.locator('dt').filter({ hasText: 'Invalid RED' })).toBeVisible();
  await expect(guide.locator('dt').filter({ hasText: 'No evaluation yet' })).toBeVisible();
  await expect(guide.getByText(/answer different questions/i)).toBeVisible();
  await expect(page).toHaveScreenshot('evaluation-vocabulary-guide.png', { maxDiffPixelRatio: 0.01 });
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);

  await guide.getByRole('button', { name: 'Close evaluation help' }).click();
  await expect(page.getByRole('button', { name: 'Learn how to read this report' })).toBeFocused();
});

test('contextual help stays inside the desktop viewport while the document scrolls', async ({ page }, testInfo) => {
  test.skip(testInfo.project.name !== 'desktop', 'Desktop popovers use anchored positioning; mobile uses a bottom sheet.');
  const report = archiveManifest.reports.find(item => item.status === 'PASS');
  await page.goto(`evaluations/${report.skill}/${report.operation_id}`);

  const failureCategory = page.getByRole('button', { name: /Failure category/ }).first();
  await failureCategory.evaluate(element => element.scrollIntoView({ block: 'end' }));
  await failureCategory.click();
  const tallPanel = page.getByRole('dialog', { name: 'Failure category help' });
  const tallBounds = await tallPanel.evaluate(element => {
    const bounds = element.getBoundingClientRect();
    return {
      top: bounds.top,
      bottom: bounds.bottom,
      viewportHeight: window.innerHeight,
      scrollHeight: element.scrollHeight,
      clientHeight: element.clientHeight,
    };
  });

  expect(tallBounds.top).toBeGreaterThanOrEqual(16);
  expect(tallBounds.bottom).toBeLessThanOrEqual(tallBounds.viewportHeight - 16);
  expect(tallBounds.scrollHeight).toBeGreaterThan(tallBounds.clientHeight);
  await page.keyboard.press('Escape');

  const executorModel = page.getByRole('button', { name: /Executor model/ }).first();
  await executorModel.evaluate(element => element.scrollIntoView({ block: 'center' }));
  await executorModel.click();
  const anchoredPanel = page.getByRole('dialog', { name: 'Executor model help' });
  const initialTop = await anchoredPanel.evaluate(element => element.getBoundingClientRect().top);
  await page.evaluate(async () => {
    window.scrollBy(0, 160);
    await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));
  });
  const scrolledBounds = await anchoredPanel.evaluate(element => {
    const bounds = element.getBoundingClientRect();
    return { top: bounds.top, bottom: bounds.bottom, viewportHeight: window.innerHeight };
  });

  expect(scrolledBounds.top).not.toBe(initialTop);
  expect(scrolledBounds.top).toBeGreaterThanOrEqual(16);
  expect(scrolledBounds.bottom).toBeLessThanOrEqual(scrolledBounds.viewportHeight - 16);
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
