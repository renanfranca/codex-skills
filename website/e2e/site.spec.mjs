import { expect, test } from '@playwright/test';
import { readFileSync } from 'node:fs';

const archiveManifest = JSON.parse(readFileSync(new URL('../../evaluation-reports/manifest.json', import.meta.url), 'utf8'));

async function contrastRatio(locator) {
  return locator.evaluate(element => {
    const parseColor = value => {
      const channels = value.match(/[\d.]+/g)?.map(Number);
      if (!channels || channels.length < 3) throw new Error(`Unsupported computed color: ${value}`);
      return [channels[0], channels[1], channels[2], channels[3] ?? 1];
    };
    const composite = (foreground, background) => {
      const alpha = foreground[3] + background[3] * (1 - foreground[3]);
      return [
        (foreground[0] * foreground[3] + background[0] * background[3] * (1 - foreground[3])) / alpha,
        (foreground[1] * foreground[3] + background[1] * background[3] * (1 - foreground[3])) / alpha,
        (foreground[2] * foreground[3] + background[2] * background[3] * (1 - foreground[3])) / alpha,
        alpha,
      ];
    };
    const backgrounds = [];
    for (let current = element; current; current = current.parentElement) {
      backgrounds.push(parseColor(getComputedStyle(current).backgroundColor));
    }
    const background = backgrounds.reverse().reduce((result, layer) => composite(layer, result), [255, 255, 255, 1]);
    const foreground = composite(parseColor(getComputedStyle(element).color), background);
    const luminance = color => {
      const linearChannels = color.slice(0, 3).map(channel => {
        const value = channel / 255;
        return value <= 0.04045 ? value / 12.92 : ((value + 0.055) / 1.055) ** 2.4;
      });
      return linearChannels[0] * 0.2126 + linearChannels[1] * 0.7152 + linearChannels[2] * 0.0722;
    };
    const lighter = Math.max(luminance(foreground), luminance(background));
    const darker = Math.min(luminance(foreground), luminance(background));
    return (lighter + 0.05) / (darker + 0.05);
  });
}

async function expectModelSessionDefinition(container) {
  await expect(container.getByText(/isolated, ephemeral codex exec --json invocation started by the evaluation runner/i)).toBeVisible();
  await expect(
    container.getByText(/executor performs the evaluated task.*optional judge evaluates the result in a separate invocation/i),
  ).toBeVisible();
  await expect(container.getByText(/not a message, conversational turn, deterministic check, or complete promotion/i)).toBeVisible();
  await expect(container.getByText(/Deterministic checks consume zero model sessions/)).toBeVisible();
  await expect(container.getByText('codex exec --json', { exact: true })).toHaveCount(1);
  await expect(container.getByText('codex exec --json', { exact: true })).toHaveJSProperty('tagName', 'CODE');
}

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
    'Complete current suite evidence',
    'Partial current suite evidence',
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
  await expect(panel.getByText('Input tokens', { exact: true })).toBeVisible();
  await expect(panel.getByText('Cached input tokens', { exact: true })).toBeVisible();
  await expect(panel.getByText('Output tokens', { exact: true })).toBeVisible();
  await expect(panel.getByText('Reasoning output tokens', { exact: true })).toBeVisible();
  await expect(panel.getByText('Total tokens', { exact: true })).toBeVisible();
  await expect(panel.getByText('Duration', { exact: true })).toBeVisible();
  await expect(panel.getByText('Usage events', { exact: true })).toBeVisible();
  await expect(panel.getByText('API reference estimate', { exact: true })).toBeVisible();
  await expect(panel.getByText('Runtime telemetry', { exact: true })).toBeVisible();
  await expect(panel.getByText('Token telemetry', { exact: true })).toBeVisible();
  await expectModelSessionDefinition(panel);
  await expect(panel.getByText(/Aggregate workload telemetry.*not an observed financial charge/i)).toBeVisible();
  const reportLink = panel.getByRole('link', { name: 'Inspect promotion report' });
  await expect(reportLink).toHaveAttribute('href', /\/evaluations\/restructure-documentation\/20260727T233326\.147750Z-48228593ef91$/);
  await reportLink.click();

  await expect(page).toHaveURL(/\/evaluations\/restructure-documentation\/20260727T233326\.147750Z-48228593ef91$/);
  await expect(page.getByRole('heading', { level: 2, name: 'Token usage' })).toBeVisible();
  await expect(page.getByRole('heading', { level: 2, name: 'API reference estimate' })).toBeVisible();
  await expect(page.getByRole('heading', { level: 2, name: 'Observations' })).toBeVisible();
  const usageEvents = page.getByText(/Normalized usage events \(\d+\)/).first();
  await expect(usageEvents).toBeVisible();
  expect(await usageEvents.evaluate(summary => summary.parentElement.open)).toBe(false);
  const estimateDetails = page.getByText('View API reference estimate details', { exact: true });
  await expect(estimateDetails).toBeVisible();
  expect(await estimateDetails.evaluate(summary => summary.parentElement.open)).toBe(false);
  await expect(page.getByText(/not an observed charge or invoice/i)).toBeHidden();
  if (testInfo.project.name === 'mobile') {
    await estimateDetails.tap();
  } else {
    await estimateDetails.focus();
    await estimateDetails.press('Enter');
  }
  expect(await estimateDetails.evaluate(summary => summary.parentElement.open)).toBe(true);
  await expect(page.getByText(/not an observed charge or invoice/i)).toBeVisible();
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
  await expect(panel.getByText('Historical runs', { exact: true })).toBeVisible();
  await expect(panel.getByText('Suite evidence', { exact: true })).toBeVisible();
  await expect(panel.getByText('0 of 11 declared cases have a current pass.')).toBeVisible();
  await expect(panel.getByText('No matching promotion')).toBeVisible();
  await expect(panel.getByText('No archived report matches the current source fingerprint.')).toBeVisible();
  await expect(panel.getByRole('link', { name: 'View evaluation history →' })).toBeVisible();
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

test('card, evidence, and operation navigation remain independent', async ({ page }) => {
  await page.goto('skills/');

  const card = page.locator('article.skill-card').filter({ hasText: 'refactor-design' });
  await expect(card.locator('a button, button a')).toHaveCount(0);
  await card.locator('a.skill-card-main').click();
  await expect(page).toHaveURL(/\/skills\/refactor-design$/);

  await page.goBack();
  await page.locator('article.skill-card').filter({ hasText: 'refactor-design' }).locator('a.skill-history-link').click();
  await expect(page).toHaveURL(/\/skills\/refactor-design#operation-history$/);
  await expect(page.getByRole('heading', { level: 2, name: 'Operations' })).toBeVisible();
});

test('evaluation pages separate current evidence, case results, and complete operations', async ({ page }) => {
  await page.goto('skills/refactor-design');

  const hiddenState = page.locator('.evaluation-card').filter({ hasText: 'Hidden invocation state' });
  await expect(hiddenState.getByText('Historical runs', { exact: true })).toBeVisible();
  await hiddenState.click();

  await expect(page).toHaveURL(/\/skills\/refactor-design\/evaluations\/hidden-invocation-state$/);
  await page.evaluate(() => {
    document.documentElement.style.scrollBehavior = 'auto';
  });
  await expect(page.getByText('Historical runs', { exact: true }).first()).toBeVisible();
  await expect(
    page.locator('.operation-summary > div').filter({ hasText: 'Case result' }).getByText('PASS', { exact: true }),
  ).toBeVisible();
  await expect(
    page.locator('.operation-summary > div').filter({ hasText: 'Complete operation result' }).getByText('FAIL', { exact: true }),
  ).toBeVisible();
  const flow = page.locator('.definition-flow');
  await expect(flow.getByRole('link')).toHaveCount(6);
  await expect(flow.locator('.definition-step-result')).toHaveCount(1);
  await expect(flow.getByText('Independent checks outside the executor workspace', { exact: true })).toBeVisible();
  for (const status of ['PASS', 'FAIL', 'ERROR', 'SKIPPED']) {
    await expect(flow.getByText(status, { exact: true })).toBeVisible();
  }
  const firstListItem = flow.locator('.definition-step').first();
  expect(await firstListItem.evaluate(element => getComputedStyle(element).listStyleType)).toBe('none');
  expect(await firstListItem.evaluate(element => getComputedStyle(element, '::marker').content)).toBe('""');
  const firstStage = flow.getByRole('link').first();
  await flow.scrollIntoViewIfNeeded();
  const flowBox = await flow.boundingBox();
  expect(flowBox).not.toBeNull();
  const viewport = await page.evaluate(() => ({ width: window.innerWidth, height: window.innerHeight }));
  const pointerPosition = [
    { x: 1, y: 1 },
    { x: viewport.width - 2, y: 1 },
    { x: 1, y: viewport.height - 2 },
    { x: viewport.width - 2, y: viewport.height - 2 },
  ].find(({ x, y }) => x < flowBox.x || x > flowBox.x + flowBox.width || y < flowBox.y || y > flowBox.y + flowBox.height);
  expect(pointerPosition).toBeDefined();
  await page.mouse.move(pointerPosition.x, pointerPosition.y);
  await expect(flow.locator('a:hover')).toHaveCount(0);
  const connectorAlignment = await firstListItem.evaluate(element => {
    const itemBox = element.getBoundingClientRect();
    const nodeBox = element.querySelector('.definition-step-node').getBoundingClientRect();
    const nextNodeBox = element.nextElementSibling.querySelector('.definition-step-node').getBoundingClientRect();
    const lineStyle = getComputedStyle(element, '::after');
    const arrowStyle = getComputedStyle(element, '::before');
    const pixels = value => Number.parseFloat(value) || 0;
    const vertical = Math.abs(nextNodeBox.left - nodeBox.left) < Math.abs(nextNodeBox.top - nodeBox.top);
    const axis = vertical ? 'left' : 'top';
    const size = vertical ? 'width' : 'height';
    const startBorder = vertical ? 'borderLeftWidth' : 'borderTopWidth';
    const endBorder = vertical ? 'borderRightWidth' : 'borderBottomWidth';
    const nodeCenter = vertical ? nodeBox.left - itemBox.left + nodeBox.width / 2 : nodeBox.top - itemBox.top + nodeBox.height / 2;
    const pseudoCenter = style => {
      const renderedSize =
        pixels(style[size]) + (style.boxSizing === 'border-box' ? 0 : pixels(style[startBorder]) + pixels(style[endBorder]));
      return pixels(style[axis]) + renderedSize / 2;
    };
    return {
      lineOffset: Math.abs(pseudoCenter(lineStyle) - nodeCenter),
      arrowOffset: Math.abs(pseudoCenter(arrowStyle) - nodeCenter),
    };
  });
  expect(connectorAlignment.lineOffset).toBeLessThanOrEqual(0.01);
  expect(connectorAlignment.arrowOffset).toBeLessThanOrEqual(0.01);
  await expect(flow).toHaveScreenshot('evaluation-flow.png');

  const themeSwitch = page.getByRole('switch', { name: 'Switch to dark theme' });
  const mobileNavigation = page.getByRole('button', { name: 'mobile navigation' });
  let openedMobileNavigation = false;
  if (!(await themeSwitch.isVisible())) {
    await mobileNavigation.click();
    openedMobileNavigation = true;
  }
  await themeSwitch.click();
  await expect(page.locator('html')).toHaveClass(/dark/);
  if (openedMobileNavigation) await mobileNavigation.click();
  await expect(flow).toHaveScreenshot('evaluation-flow-dark.png');

  await firstStage.focus();
  await page.keyboard.press('Shift+Tab');
  await page.keyboard.press('Tab');
  await expect(firstStage).toBeFocused();
  expect(await firstStage.evaluate(element => getComputedStyle(element).outlineStyle)).not.toBe('none');
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);

  await page.goto('skills/execplan-tdd/evaluations/documentation-only-boundary');
  const judgeDisabledFlow = page.locator('.definition-flow');
  await expect(judgeDisabledFlow.getByRole('link')).toHaveCount(5);
  await expect(judgeDisabledFlow.getByText('Judge', { exact: true })).toHaveCount(0);
  await expect(judgeDisabledFlow.getByText('Independent checks outside the executor workspace', { exact: true })).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);

  await page.goto('skills/develop-skill-with-evals/evaluations/global-target-skill-isolation');
  await expect(page.getByText('Not evaluated yet', { exact: true }).first()).toBeVisible();

  await page.goto('skills/develop-skill-with-evals/evaluations/load-skill-creator-first');
  await expect(page.getByText('Historical', { exact: true }).first()).toBeVisible();
  await expect(page.getByText(/current definition is not available/i)).toBeVisible();
  await expect(page.locator('.definition-flow')).toHaveCount(0);

  const operationsNav = page.getByRole('link', { name: 'Operations', exact: true });
  if (!(await operationsNav.isVisible())) {
    await page.getByRole('button', { name: 'mobile navigation' }).click();
  }
  await expect(operationsNav).toHaveAttribute('href', /\/evaluations\/$/);
});

test.describe('narrow evaluation layout', () => {
  test.use({ viewport: { width: 390, height: 844 } });

  test('active evaluation pages keep long commands visible inside the viewport', async ({ page }, testInfo) => {
    test.skip(testInfo.project.name !== 'desktop', 'This regression is covered by the deterministic desktop project.');

    await page.goto('skills/restructure-documentation/evaluations/documentation-system-restructure#judge-verification');

    await expect(page.locator('.mechanism-section#judge-verification')).toBeVisible();
    const commandRow = page.locator('.command-list li').filter({ hasText: 'check_markdown_links.py' });
    await expect(commandRow.locator('code')).toBeVisible();
    await expect(commandRow.getByText('Expected exit: 0', { exact: true })).toBeVisible();
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
  });
});

test('active evaluation guidance omits retired traceability while historical cases remain accessible', async ({ page }, testInfo) => {
  await page.goto('skills/refactor-design');
  await expect(page.locator('.evaluation-card-grid').first().locator('.evaluation-card')).toHaveCount(11);
  await expect(page.getByRole('heading', { level: 2, name: 'Historical evaluations' })).toBeVisible();
  const retiredCase = page.locator('.historical-evaluation-card').filter({ hasText: 'Coverage contract' });
  await expect(retiredCase).toBeVisible();
  await expect(page.getByText('Execution and traceability', { exact: true })).toHaveCount(0);
  await expect(page.getByText(/skill contracts and .*mappings/i)).toHaveCount(0);
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);

  await page.goto('skills/refactor-design/evaluations/hidden-invocation-state');

  await expect(page.getByText('How to read this page', { exact: true })).toBeVisible();
  await expect(page.getByText(/An evaluation is the persistent case definition/)).toBeVisible();
  await expect(page.getByText(/traceability|coverage level|mapping label/i)).toHaveCount(0);
  await expect(page.getByRole('heading', { level: 2, name: 'Skill contracts mapped to this case' })).toHaveCount(0);
  await expect(page.getByRole('heading', { level: 2, name: 'Rubric families sampled by this case' })).toHaveCount(0);
  await expect(page.getByText('Hidden invocation state', { exact: true }).first()).toBeVisible();
  await expect(page.getByRole('dialog')).toHaveCount(0);

  for (const name of ['Current evidence', 'Latest recorded result', 'Suite state', 'Kind']) {
    await expect(page.getByRole('button', { name, exact: true }).first()).toBeVisible();
  }
  await expect(page.getByRole('button', { name: 'Coverage level', exact: true })).toHaveCount(0);
  await expect(page.getByRole('button', { name: 'Mapping label', exact: true })).toHaveCount(0);

  const evidenceTrigger = page.getByRole('button', { name: 'Current evidence', exact: true });
  await evidenceTrigger.focus();
  await page.keyboard.press('Enter');
  const evidenceHelp = page.getByRole('dialog', { name: 'Current evidence help' });
  await expect(evidenceHelp).toBeVisible();
  await expect(evidenceHelp.getByText('Evaluation term', { exact: true })).toBeVisible();
  await expect(evidenceHelp.getByText('Possible values', { exact: true })).toBeVisible();
  if (testInfo.project.name === 'mobile') {
    await expect(evidenceHelp).toHaveClass(/evaluation-help-sheet/);
  } else {
    await expect(evidenceHelp).toHaveClass(/evaluation-help-popover/);
  }
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
  await page.keyboard.press('Escape');
  await expect(evidenceHelp).toBeHidden();
  await expect(evidenceTrigger).toBeFocused();

  await page.goto('skills/refactor-design/evaluations/coverage-contract');
  await expect(page.getByText('Historical', { exact: true }).first()).toBeVisible();
  await expect(page.getByText(/current definition is not available/i)).toBeVisible();
  await expect(page.locator('.definition-flow')).toHaveCount(0);
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
});

test('evidence remains readable in light and dark themes', async ({ page }) => {
  await page.goto('skills/');

  const card = page.locator('article.skill-card').filter({ hasText: 'refactor-design' });
  const lightBorder = await card.evaluate(element => getComputedStyle(element).borderTopColor);
  await expect(card.getByText('Historical runs', { exact: true })).toBeVisible();

  const themeSwitch = page.getByRole('switch', { name: 'Switch to dark theme' });
  if (!(await themeSwitch.isVisible())) {
    await page.getByRole('button', { name: 'mobile navigation' }).click();
  }
  await themeSwitch.click();

  const darkBorder = await card.evaluate(element => getComputedStyle(element).borderTopColor);
  expect(darkBorder).not.toBe(lightBorder);
  await expect(card.getByText('Historical runs', { exact: true })).toBeVisible();
});

test('retained report code is readable and expandable in both themes', async ({ page }) => {
  await page.goto('evaluations/execplan-tdd/20260729T181620.575049Z-cc3d76bb204a');

  const operation = page.locator('.lede code').nth(0);
  const operationId = page.locator('.lede code').nth(1);

  const diffSummary = page.getByText('View code diff').first();
  await expect(diffSummary).toBeVisible();
  await diffSummary.click();

  const diffBlock = page.locator('.language-diff').first();
  await expect(diffBlock.locator('code').filter({ hasText: '--- /dev/null' })).toBeVisible();
  const contextLine = diffBlock.locator('.line > span').filter({ hasText: 'unittest.main()' });
  const language = diffBlock.locator('.lang');

  const fragmentSummary = page.getByText('Code fragments').first();
  await expect(fragmentSummary).toBeVisible();
  await fragmentSummary.click();
  await expect(page.getByText('Before', { exact: true }).first()).toBeVisible();
  await expect(page.getByText('After', { exact: true }).first()).toBeVisible();

  for (const code of [operation, operationId, contextLine, language]) {
    expect(await contrastRatio(code)).toBeGreaterThanOrEqual(4.5);
  }
  const lightBlockBackground = await diffBlock.evaluate(element => getComputedStyle(element).backgroundColor);

  const themeSwitch = page.getByRole('switch', { name: 'Switch to dark theme' });
  if (!(await themeSwitch.isVisible())) {
    await page.getByRole('button', { name: 'mobile navigation' }).click();
  }
  await themeSwitch.click();
  await expect(page.locator('html')).toHaveClass(/dark/);

  for (const code of [operation, operationId, contextLine, language]) {
    expect(await contrastRatio(code)).toBeGreaterThanOrEqual(4.5);
  }
  expect(await diffBlock.evaluate(element => getComputedStyle(element).backgroundColor)).toBe(lightBlockBackground);
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
});

test('report vocabulary is learnable in context and in the complete guide', async ({ page }, testInfo) => {
  const report = archiveManifest.reports.find(item => item.status === 'PASS');
  await page.goto(`evaluations/${report.skill}/${report.operation_id}`);
  await page.evaluate(() => {
    document.documentElement.style.scrollBehavior = 'auto';
  });

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
  await expect(page).toHaveScreenshot('execution-facts-help.png');

  await page.keyboard.press('Escape');
  await expect(fieldPanel).toBeHidden();
  await expect(executorHelp).toBeFocused();

  const sessionsHelp = factGrid.getByRole('button', { name: /Executed sessions/ });
  await sessionsHelp.focus();
  await page.keyboard.press('Enter');
  const sessionsPanel = page.getByRole('dialog', { name: 'Executed sessions help' });
  await expectModelSessionDefinition(sessionsPanel);
  await page.keyboard.press('Escape');
  await expect(sessionsPanel).toBeHidden();
  await expect(sessionsHelp).toBeFocused();

  await page.getByRole('button', { name: 'Learn how to read this report' }).click();
  const guide = page.getByRole('dialog', { name: 'Learn how to read this report' });
  await expect(guide.getByText(/program run_skill_evals\.py/)).toBeVisible();
  const modelSessionEntry = guide.locator('dl > div').filter({ hasText: 'Executed sessions' });
  await expect(modelSessionEntry).toHaveCount(1);
  await expectModelSessionDefinition(modelSessionEntry);
  await expect(guide.locator('dt').filter({ hasText: 'RED/GREEN check' })).toBeVisible();
  await expect(guide.getByText('verify-change', { exact: true })).toBeVisible();
  await expect(guide.locator('dt').filter({ hasText: 'Invalid RED' })).toBeVisible();
  await expect(guide.locator('dt').filter({ hasText: 'No evaluation yet' })).toBeVisible();
  await expect(guide.getByText(/answer different questions/i)).toBeVisible();
  if (testInfo.project.name === 'mobile') {
    await page.evaluate(async () => {
      window.scrollTo({
        top: 0,
        behavior: 'instant',
      });
      await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));
    });
    await expect.poll(() => page.evaluate(() => Math.round(window.scrollY))).toBe(0);
  }
  await expect(page).toHaveScreenshot('evaluation-vocabulary-guide.png');
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
    window.scrollBy({ top: 160, behavior: 'instant' });
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
