import { copyFileSync, mkdirSync, readFileSync, readdirSync, rmSync, statSync, writeFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { dirname, isAbsolute, join, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { evaluationGlossary, knownObservationRoles, operationDisplay } from './evaluation-glossary.mjs';

const websiteRoot = join(dirname(fileURLToPath(import.meta.url)), '..');
const contentConfig = JSON.parse(readFileSync(join(websiteRoot, 'content-config.json'), 'utf8'));
const evidenceStates = Object.freeze(
  Object.fromEntries(
    Object.entries(evaluationGlossary.evidenceStatuses).map(([key, definition]) => [key, Object.freeze({ key, ...definition })]),
  ),
);
const siteBase = contentConfig.base.replace(/\/$/, '');

function siteRoute(path = '/') {
  return `${siteBase}${path}`;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;');
}

function tableCell(value) {
  return escapeHtml(value ?? 'Not recorded')
    .replaceAll('|', '\\|')
    .replaceAll('\n', '<br>');
}

function parseArguments(argumentsList) {
  const values = {};
  for (let index = 0; index < argumentsList.length; index += 2) {
    const key = argumentsList[index];
    const value = argumentsList[index + 1];
    if (!key?.startsWith('--') || value === undefined) {
      throw new Error(`Invalid argument near ${key ?? 'end of command'}`);
    }
    values[key.slice(2)] = resolve(value);
  }
  for (const required of ['repository-root', 'archive', 'output']) {
    if (!values[required]) {
      throw new Error(`Missing required argument --${required}`);
    }
  }
  return values;
}

function readJson(path) {
  try {
    return JSON.parse(readFileSync(path, 'utf8'));
  } catch (error) {
    throw new Error(`Cannot read valid JSON from ${path}: ${error.message}`);
  }
}

function assertTaxonomy(name, actualValues, glossaryValues) {
  const actual = [...actualValues].sort();
  const documented = [...glossaryValues].sort();
  if (JSON.stringify(actual) !== JSON.stringify(documented)) {
    throw new Error(`${name} glossary is out of sync: schema has [${actual.join(', ')}], glossary has [${documented.join(', ')}]`);
  }
}

function validateEvaluationGlossary() {
  const references = join(websiteRoot, '..', 'develop-skill-with-evals', 'references');
  const reportSchema = readJson(join(references, 'eval-report.schema.json'));
  const resultSchema = readJson(join(references, 'eval-result.schema.json'));

  assertTaxonomy('Operation', reportSchema.properties.operation.properties.type.enum, Object.keys(evaluationGlossary.operations));
  assertTaxonomy('Recorded result', reportSchema.properties.operation.properties.status.enum, Object.keys(evaluationGlossary.results));
  assertTaxonomy('Observation kind', resultSchema.properties.results.items.properties.kind.enum, Object.keys(evaluationGlossary.kinds));
  assertTaxonomy(
    'Judge verdict',
    resultSchema.properties.results.items.properties.judge.properties.verdict.enum,
    Object.keys(evaluationGlossary.judgeVerdicts),
  );
  assertTaxonomy(
    'Failure category',
    reportSchema.properties.operation.properties.failure_category.enum.map(value => value ?? 'none'),
    Object.keys(evaluationGlossary.failureCategories).filter(value => value !== 'not-recorded'),
  );
  assertTaxonomy('Observation role', knownObservationRoles, Object.keys(evaluationGlossary.roles));
}

function readSkill(path) {
  const source = readFileSync(path, 'utf8');
  const frontmatter = source.match(/^---\n([\s\S]*?)\n---/);
  if (!frontmatter) {
    throw new Error(`Skill frontmatter is missing from ${path}`);
  }
  const metadata = {};
  for (const line of frontmatter[1].split('\n')) {
    const separator = line.indexOf(':');
    if (separator > 0) {
      metadata[line.slice(0, separator).trim()] = line
        .slice(separator + 1)
        .trim()
        .replace(/^(['"])(.*)\1$/, '$2');
    }
  }
  if (!metadata.name || !metadata.description) {
    throw new Error(`Skill name or description is missing from ${path}`);
  }
  return metadata;
}

function sha256(value) {
  return createHash('sha256').update(value).digest('hex');
}

function canonicalFingerprintPayload(value) {
  return JSON.stringify(value).replaceAll(/[\u0080-\uffff]/g, character => {
    return `\\u${character.charCodeAt(0).toString(16).padStart(4, '0')}`;
  });
}

function compareUnicodeCodePoints(left, right) {
  const leftPoints = [...left].map(character => character.codePointAt(0));
  const rightPoints = [...right].map(character => character.codePointAt(0));
  for (let index = 0; index < Math.min(leftPoints.length, rightPoints.length); index += 1) {
    if (leftPoints[index] !== rightPoints[index]) {
      return leftPoints[index] - rightPoints[index];
    }
  }
  return leftPoints.length - rightPoints.length;
}

function fingerprintFiles(root) {
  const files = [];
  function visit(directory) {
    for (const entry of readdirSync(directory, { withFileTypes: true })) {
      const path = join(directory, entry.name);
      const relativePath = relative(root, path).split('\\').join('/');
      const parts = relativePath.split('/');
      if (parts.includes('.git') || parts.includes('__pycache__') || entry.name.endsWith('.pyc')) {
        continue;
      }
      if (entry.isDirectory()) {
        visit(path);
      } else if (entry.isFile() || (entry.isSymbolicLink() && statSync(path).isFile())) {
        files.push([relativePath, path]);
      }
    }
  }
  visit(root);
  return Object.fromEntries(
    files
      .sort(([left], [right]) => compareUnicodeCodePoints(left, right))
      .map(([relativePath, path]) => [
        relativePath,
        {
          mode: readFileMode(path),
          sha256: sha256(readFileSync(path)),
        },
      ]),
  );
}

function readFileMode(path) {
  return statSync(path).mode & 0o7777;
}

function treeFingerprint(root) {
  return sha256(canonicalFingerprintPayload(fingerprintFiles(root)));
}

function readSuiteCases(skillRoot) {
  try {
    const suite = readJson(join(skillRoot, 'evals', 'suite.json'));
    if (
      suite.version !== 1
      || !Array.isArray(suite.cases)
      || suite.cases.some(caseId => typeof caseId !== 'string')
      || new Set(suite.cases).size !== suite.cases.length
    ) {
      throw new Error(`Evaluation suite is invalid for ${skillRoot}`);
    }
    return suite.cases;
  } catch (error) {
    if (error.cause?.code === 'ENOENT' || error.code === 'ENOENT') {
      return null;
    }
    if (error.message.startsWith('Cannot read valid JSON') && error.message.includes('ENOENT')) {
      return null;
    }
    throw error;
  }
}

function findSkills(repositoryRoot) {
  const disabledSkills = new Set(contentConfig.disabledSkills ?? []);
  return readdirSync(repositoryRoot, { withFileTypes: true })
    .filter(
      entry =>
        entry.isDirectory()
        && !entry.name.startsWith('.')
        && !entry.name.startsWith('_')
        && entry.name !== 'website'
        && !disabledSkills.has(entry.name),
    )
    .flatMap(entry => {
      const skillPath = join(repositoryRoot, entry.name, 'SKILL.md');
      try {
        const metadata = readSkill(skillPath);
        return [
          {
            slug: entry.name,
            name: metadata.name,
            description: metadata.description,
            sourcePath: `${entry.name}/SKILL.md`,
          },
        ];
      } catch (error) {
        if (error.code === 'ENOENT') {
          return [];
        }
        throw error;
      }
    })
    .sort((left, right) => left.name.localeCompare(right.name));
}

function normalizeObservation(observation) {
  for (const [taxonomy, value, definitions] of [
    ['result', observation.status, evaluationGlossary.results],
    ['kind', observation.kind, evaluationGlossary.kinds],
    ['role', observation.role, evaluationGlossary.roles],
    ['judge verdict', observation.judge?.verdict, evaluationGlossary.judgeVerdicts],
  ]) {
    if (value !== undefined && !Object.hasOwn(definitions, value)) {
      throw new Error(`Archived observation has unknown ${taxonomy} "${value}"`);
    }
  }
  const judgeState = observation.judge?.enabled === false ? 'not-used' : observation.judge?.executed === true ? 'executed' : 'skipped';
  const judgeDisplay =
    judgeState === 'not-used' ? 'Not used' : judgeState === 'skipped' ? 'Skipped' : (observation.judge?.verdict ?? 'Not recorded');
  return {
    caseId: observation.case_id ?? 'Not recorded',
    status: observation.status ?? 'Not recorded',
    kind: observation.kind ?? 'Not recorded',
    role: observation.role ?? 'Not recorded',
    judgeVerdict: observation.judge?.verdict ?? 'Not recorded',
    judgeState,
    judgeDisplay,
    judgeRationale: observation.judge?.rationale ?? 'Not recorded',
    judgeEvidence: observation.judge?.evidence ?? [],
    mechanicalPassed: observation.mechanical?.passed ?? null,
    checks: observation.mechanical?.checks ?? [],
    commands: observation.mechanical?.commands ?? [],
    changedFiles: observation.evidence?.changed_files ?? [],
    diff: observation.evidence?.diff ?? '',
    fragments: observation.evidence?.fragments ?? [],
  };
}

function normalizeSessionCounts(sessions) {
  return {
    executor: typeof sessions === 'object' && sessions !== null ? (sessions.executor ?? null) : null,
    judge: typeof sessions === 'object' && sessions !== null ? (sessions.judge ?? null) : null,
    total: typeof sessions === 'object' && sessions !== null ? (sessions.total ?? null) : (sessions ?? null),
  };
}

function normalizeReport(entry, archiveRoot) {
  if (!entry.path || !entry.skill || !entry.operation_id) {
    throw new Error('Archive manifest contains a report without path, skill, or operation_id');
  }
  const sourcePath = resolve(archiveRoot, entry.path);
  const archiveRelativePath = relative(archiveRoot, sourcePath);
  if (
    archiveRelativePath === '..'
    || archiveRelativePath.startsWith(`..${process.platform === 'win32' ? '\\' : '/'}`)
    || isAbsolute(archiveRelativePath)
  ) {
    throw new Error(`Report path ${entry.path} resolves outside the evaluation archive`);
  }
  const report = readJson(sourcePath);
  const operation = report.operation ?? {};
  const operationType = entry.operation ?? operation.type;
  if (operationType !== undefined && !Object.hasOwn(evaluationGlossary.operations, operationType)) {
    throw new Error(`Archived report has unknown operation "${operationType}"`);
  }
  const operationStatus = entry.status ?? operation.status;
  if (operationStatus !== undefined && !Object.hasOwn(evaluationGlossary.results, operationStatus)) {
    throw new Error(`Archived report has unknown result "${operationStatus}"`);
  }
  if (
    Object.hasOwn(operation, 'failure_category')
    && operation.failure_category !== null
    && !Object.hasOwn(evaluationGlossary.failureCategories, operation.failure_category)
  ) {
    throw new Error(`Archived report has unknown failure category "${operation.failure_category}"`);
  }
  const executedSessions = report.sessions?.executed;
  const plannedSessions = report.sessions?.planned;
  const observations = (report.observations ?? []).map(normalizeObservation);
  const judgeApplicable =
    report.runtime?.judge?.required === true || observations.some(observation => observation.judgeState !== 'not-used');
  const failureCategory = Object.hasOwn(operation, 'failure_category')
    ? operation.failure_category === null
      ? 'None'
      : operation.failure_category
    : 'Not recorded';
  return {
    id: entry.operation_id,
    skill: entry.skill,
    status: operationStatus ?? 'Not recorded',
    operation: operationType ?? 'Not recorded',
    operationLabel: evaluationGlossary.operations[operationType]?.label ?? 'Not recorded',
    operationDisplay: operationType ? operationDisplay(operationType) : 'Not recorded',
    workflow: operation.workflow ?? 'Not recorded',
    promotionEligible: operation.promotion_eligible ?? null,
    failureCategory,
    provenance: report.provenance ?? 'Not recorded',
    startedAt: report.started_at ?? 'Not recorded',
    finishedAt: report.finished_at ?? 'Not recorded',
    durationMs: entry.duration_ms ?? report.duration_ms ?? null,
    model: entry.model ?? report.runtime?.executor?.model ?? report.runtime?.executor?.requested_model ?? 'Not recorded',
    reasoningEffort: entry.reasoning_effort ?? report.runtime?.executor?.reasoning_effort ?? 'Not recorded',
    sessions: entry.sessions ?? report.sessions?.executed ?? null,
    totalTokens: report.usage?.total_tokens ?? entry.tokens?.total ?? null,
    runtimeByRole: {
      executor: {
        model: report.runtime?.executor?.model ?? entry.model ?? 'Not recorded',
        reasoningEffort: report.runtime?.executor?.reasoning_effort ?? entry.reasoning_effort ?? 'Not recorded',
      },
      judge: {
        applicable: judgeApplicable,
        model: judgeApplicable ? (report.runtime?.judge?.model ?? 'Not recorded') : 'Not used',
        reasoningEffort: judgeApplicable ? (report.runtime?.judge?.reasoning_effort ?? 'Not recorded') : 'Not used',
      },
    },
    sessionsByRole: {
      planned: normalizeSessionCounts(plannedSessions),
      executed: normalizeSessionCounts(executedSessions),
    },
    judgeState: judgeApplicable
      ? observations.some(observation => observation.judgeState === 'executed')
        ? 'Executed'
        : 'Skipped'
      : 'Not used',
    promotionEffort: {
      sessions: normalizeSessionCounts(executedSessions),
      tokens: {
        total: report.usage?.total_tokens ?? null,
        cachedInput: report.usage?.cached_input_tokens ?? null,
      },
      durationMs: report.duration_ms ?? null,
      telemetry: {
        runtimeComplete: report.runtime?.complete ?? null,
        usageComplete: report.usage?.complete ?? null,
      },
    },
    limitations: report.limitations ?? [],
    observations,
    fingerprints: report.fingerprints ?? null,
    archivePath: entry.path,
  };
}

function evaluatedSourceFingerprint(report) {
  const sources = report.fingerprints?.sources;
  if (!sources || typeof sources !== 'object') return null;
  if (Object.hasOwn(sources, 'baseline')) {
    return typeof sources.candidate === 'string' ? sources.candidate : null;
  }
  return typeof sources.evaluated === 'string' ? sources.evaluated : null;
}

function groupCurrentReports(reports) {
  return Object.fromEntries(
    [...new Set(reports.map(report => report.status))].sort().map(status => [
      status,
      reports
        .filter(report => report.status === status)
        .map(report => ({
          id: report.id,
          operation: report.operation,
          operationDisplay: report.operationDisplay,
          status: report.status,
          href: reportRoute(report),
        })),
    ]),
  );
}

function promotionSummary(report) {
  if (!report) return null;
  return {
    report: {
      id: report.id,
      href: reportRoute(report),
    },
    ...report.promotionEffort,
  };
}

function deriveEvidence(skillRoot, reports) {
  const currentFingerprint = treeFingerprint(skillRoot);
  const suiteCases = readSuiteCases(skillRoot);
  const currentReports = reports.filter(report => evaluatedSourceFingerprint(report) === currentFingerprint);
  const currentReportIds = new Set(currentReports.map(report => report.id));
  const historicalReports = reports.filter(report => !currentReportIds.has(report.id));
  const coveredCases = [
    ...new Set(
      currentReports.flatMap(report =>
        report.observations
          .filter(observation => observation.role !== 'baseline' && observation.status === 'PASS')
          .map(observation => observation.caseId),
      ),
    ),
  ].sort();
  const promotionReport = currentReports.find(report => report.status === 'PASS' && report.promotionEligible === true) ?? null;
  const currentReportGroups = groupCurrentReports(currentReports);
  const hasCurrentPass = coveredCases.length > 0 || currentReports.some(report => report.status === 'PASS');
  const hasCompleteCoverage = suiteCases !== null && suiteCases.length > 0 && suiteCases.every(caseId => coveredCases.includes(caseId));
  let state;
  if (promotionReport) {
    state = evidenceStates.promotion;
  } else if (hasCompleteCoverage) {
    state = evidenceStates.complete;
  } else if (hasCurrentPass) {
    state = evidenceStates.partial;
  } else if (currentReports.length > 0) {
    state = evidenceStates['no-current-pass'];
  } else if (reports.length > 0) {
    state = evidenceStates.historical;
  } else {
    state = evidenceStates['no-evaluation'];
  }

  return {
    ...state,
    currentFingerprint,
    promotionReport,
    promotionSummary: promotionSummary(promotionReport),
    currentReports,
    currentReportGroups,
    currentResults: Object.fromEntries(
      Object.entries(currentReportGroups).map(([status, groupedReports]) => [status, groupedReports.length]),
    ),
    coveredCases,
    coveredCaseCount: coveredCases.length,
    suiteCases,
    suiteCaseCount: suiteCases?.length ?? null,
    historicalReportCount: historicalReports.length,
  };
}

function formatDuration(durationMs) {
  if (durationMs === null || durationMs === undefined) return 'Not recorded';
  if (durationMs < 1000) return `${durationMs} ms`;
  const seconds = durationMs / 1000;
  if (seconds < 60) return `${seconds.toFixed(1)} s`;
  return `${Math.floor(seconds / 60)}m ${Math.round(seconds % 60)}s`;
}

function formatNumber(value) {
  return value === null || value === undefined ? 'Not recorded' : new Intl.NumberFormat('en').format(value);
}

function formatSessions(sessions) {
  const { executor, judge, total } = sessions;
  return `${formatNumber(total)} total · ${formatNumber(executor)} executor · ${formatNumber(judge)} judge`;
}

function renderHelpFact(field, value, { detail = '', status = '' } = {}) {
  return `<div><EvaluationHelp field="${field}" current="${escapeHtml(value)}"${detail ? ` detail="${escapeHtml(detail)}"` : ''}></EvaluationHelp><strong${status ? ` class="${status}"` : ''}>${escapeHtml(value)}</strong></div>`;
}

function formatDate(value) {
  if (value === 'Not recorded') return value;
  const date = new Date(value);
  if (Number.isNaN(date.valueOf())) return value;
  return new Intl.DateTimeFormat('en', {
    dateStyle: 'medium',
    timeStyle: 'short',
    timeZone: 'UTC',
  }).format(date);
}

function formatStarted(value) {
  return value === 'Not recorded' ? value : `${formatDate(value)} UTC`;
}

function codeBlock(source, language = '') {
  const longestFence = Math.max(3, ...[...source.matchAll(/`+/g)].map(match => match[0].length + 1));
  const fence = '`'.repeat(longestFence);
  return `${fence}${language}\n${source.replace(/\n?$/, '\n')}${fence}`;
}

function yamlString(value) {
  return JSON.stringify(String(value)).replaceAll('<', '\\u003c').replaceAll('>', '\\u003e').replaceAll('&', '\\u0026');
}

function statusClass(status) {
  return String(status)
    .toLowerCase()
    .replaceAll(/[^a-z0-9]+/g, '-');
}

function reportRoute(report) {
  return siteRoute(`/evaluations/${encodeURIComponent(report.skill)}/${encodeURIComponent(report.id)}`);
}

function evidenceComponentData(skill) {
  return encodeURIComponent(
    JSON.stringify({
      skill: skill.name,
      key: skill.evidence.key,
      label: skill.evidence.label,
      description: skill.evidence.description,
      variant: skill.evidence.variant,
      qualificationGates: skill.evidence.qualificationGates ?? [],
      currentResults: skill.evidence.currentResults,
      currentReportGroups: skill.evidence.currentReportGroups,
      coveredCaseCount: skill.evidence.coveredCaseCount,
      suiteCaseCount: skill.evidence.suiteCaseCount,
      promotion: skill.evidence.promotionReport !== null,
      promotionSummary: skill.evidence.promotionSummary,
      historicalReportCount: skill.evidence.historicalReportCount,
      historyHref: siteRoute(`/skills/${skill.slug}#evaluation-history`),
    }),
  );
}

function renderEvidenceSummary(skill, { compact = false } = {}) {
  return `<EvidenceStatus data="${escapeHtml(evidenceComponentData(skill))}"${compact ? ' compact' : ''}></EvidenceStatus>`;
}

function renderEvidenceLegend() {
  const items = Object.values(evidenceStates)
    .sort((left, right) => left.priority - right.priority)
    .map(
      state => `<li class="evidence-state evidence-state-${state.variant}">
  <span class="evidence-state-indicator" aria-hidden="true"></span>
  <div><strong>${escapeHtml(state.label)}</strong><p>${escapeHtml(state.description)}</p></div>
</li>`,
    )
    .join('\n');
  return `<details class="evidence-legend">
<summary>How to read evidence status</summary>
<p>Each status describes the strongest evidence tied to the current skill source. Color is only a secondary cue.</p>
<ol>
${items}
</ol>
</details>`;
}

function renderFragment(fragment) {
  if (fragment.binary) {
    return `<div class="fragment-card"><strong>${escapeHtml(fragment.path ?? 'Not recorded')}</strong><p>Binary content was recorded without a text excerpt.</p></div>`;
  }
  const before = typeof fragment.before === 'string' ? codeBlock(fragment.before) : 'Not recorded';
  const after = typeof fragment.after === 'string' ? codeBlock(fragment.after) : 'Not recorded';
  return `<div class="fragment-card">
<strong>${escapeHtml(fragment.path ?? 'Not recorded')}</strong>
<div class="fragment-versions">
<section><span>Before</span>

${before}

</section>
<section><span>After</span>

${after}

</section>
</div>
</div>`;
}

function renderObservation(observation) {
  const checks = observation.checks.length
    ? observation.checks
        .map(check => `| ${check.passed ? 'Pass' : 'Fail'} | ${tableCell(check.name)} | ${tableCell(check.detail)} |`)
        .join('\n')
    : '| — | No mechanical checks recorded | — |';
  const judgeEvidence = observation.judgeEvidence.length
    ? observation.judgeEvidence.map(item => `- ${escapeHtml(item)}`).join('\n')
    : 'No judge evidence recorded.';
  const changedFiles = observation.changedFiles.length
    ? observation.changedFiles.map(path => `<code>${escapeHtml(path)}</code>`).join(', ')
    : 'Not recorded';
  const diff = observation.diff
    ? `\n\n<details class="evidence-details">\n<summary>View code diff</summary>\n\n${codeBlock(observation.diff, 'diff')}\n\n</details>`
    : '';
  const fragments = observation.fragments.length
    ? `\n\n<details class="evidence-details">\n<summary>Code fragments</summary>\n\n${observation.fragments.map(renderFragment).join('\n')}\n\n</details>`
    : '';

  return `### ${escapeHtml(observation.caseId)}

<div class="fact-grid">
  ${renderHelpFact('result', observation.status, { status: `status status-${statusClass(observation.status)}` })}
  ${renderHelpFact('kind', observation.kind)}
  ${renderHelpFact('role', observation.role)}
  ${renderHelpFact('judge', observation.judgeDisplay)}
</div>

${escapeHtml(observation.judgeRationale)}

<details class="evidence-details">
<summary>Why the judge reached this verdict</summary>

${judgeEvidence}

</details>

<details class="evidence-details">
<summary>Mechanical checks</summary>

| Result | Check | Detail |
| --- | --- | --- |
${checks}

</details>

**Changed files:** ${changedFiles}${diff}${fragments}`;
}

function renderReport(report) {
  const observations = report.observations.length
    ? report.observations.map(renderObservation).join('\n\n')
    : 'No observations were recorded.';
  const limitations = report.limitations.length
    ? report.limitations.map(item => `- ${escapeHtml(item)}`).join('\n')
    : 'No limitations were recorded.';

  return `---
title: ${yamlString(report.id)}
description: ${yamlString(`${report.skill} evaluation evidence with status ${report.status}.`)}
outline: [2, 3]
---

<a class="eyebrow" href="${siteRoute('/evaluations/')}">Evaluation evidence</a>

# ${escapeHtml(report.skill)}

<p class="lede">A recorded <strong>${escapeHtml(report.operationLabel)}</strong> operation (<code>${escapeHtml(report.operation)}</code>) for <code>${escapeHtml(report.id)}</code>.</p>

<div class="report-hero status-panel status-${statusClass(report.status)}">
  <div>
    <span class="label">Recorded result</span>
    <strong>${escapeHtml(report.status)}</strong>
  </div>
  <p>This page projects the archived report. Missing information remains explicitly unrecorded.</p>
</div>

<div class="report-section-heading">
  <h2 id="execution-facts" tabindex="-1">Execution facts</h2>
  <EvaluationHelp guide></EvaluationHelp>
</div>

<div class="fact-grid">
  ${renderHelpFact('startedAt', formatStarted(report.startedAt))}
  ${renderHelpFact('duration', formatDuration(report.durationMs))}
  ${renderHelpFact('executorModel', report.runtimeByRole.executor.model)}
  ${renderHelpFact('executorReasoningEffort', report.runtimeByRole.executor.reasoningEffort)}
  ${renderHelpFact('judgeModel', report.runtimeByRole.judge.model)}
  ${renderHelpFact('judgeReasoningEffort', report.runtimeByRole.judge.reasoningEffort)}
  ${renderHelpFact('sessions', formatSessions(report.sessionsByRole.executed), {
    detail: `Planned maximum: ${formatSessions(report.sessionsByRole.planned)}`,
  })}
  ${renderHelpFact('totalTokens', formatNumber(report.totalTokens))}
  ${renderHelpFact('failureCategory', report.failureCategory)}
</div>

## Observations

${observations}

## Limitations

${limitations}

<p class="source-link"><a href="https://github.com/renanfranca/codex-skills/blob/main/evaluation-reports/${report.archivePath}">Inspect the canonical report on GitHub →</a></p>
`;
}

function renderSkill(skill) {
  const reports = skill.reports.length
    ? skill.reports
        .map(
          report =>
            `<a class="history-row" href="${reportRoute(report)}">
  <span><strong>${escapeHtml(report.operationDisplay)}</strong><small>${escapeHtml(formatStarted(report.startedAt))}</small></span>
  <span class="status status-${statusClass(report.status)}">${escapeHtml(report.status)}</span>
</a>`,
        )
        .join('\n')
    : '<div class="empty-state">No archived evaluation reports are available for this skill yet.</div>';

  return `---
title: ${yamlString(skill.name)}
description: ${yamlString(skill.description)}
---

<a class="eyebrow" href="${siteRoute('/skills/')}">Skill catalog</a>

# ${escapeHtml(skill.name)}

<p class="lede">${escapeHtml(skill.description)}</p>

<div class="evidence-callout evidence-state evidence-state-${skill.evidence.variant}">
  <span class="evidence-state-indicator" aria-hidden="true"></span>
  <div>
    <span>Evidence status</span>
    <strong>${escapeHtml(skill.evidence.label)}</strong>
    <p>${escapeHtml(skill.evidence.description)}</p>
  </div>
  ${renderEvidenceSummary(skill)}
</div>

## Evaluation history

<p>Operation type describes how evidence was produced. It does not determine the result or evidence strength by itself.</p>

<div class="history-list">
${reports}
</div>

<p class="source-link"><a href="https://github.com/renanfranca/codex-skills/blob/main/${skill.sourcePath}">Read the canonical SKILL.md on GitHub →</a></p>
`;
}

function renderSkillIndex(skills) {
  const cards = skills
    .map(
      skill =>
        `<article class="skill-card evidence-state evidence-state-${skill.evidence.variant}">
  <span class="skill-index">${String(skills.indexOf(skill) + 1).padStart(2, '0')}</span>
  <a class="skill-card-main" href="${siteRoute(`/skills/${skill.slug}`)}">
    <h2>${escapeHtml(skill.name)}</h2>
    <p>${escapeHtml(skill.description)}</p>
  </a>
  <footer>
    <span class="skill-evidence-label"><span class="evidence-state-indicator" aria-hidden="true"></span>${escapeHtml(skill.evidence.label)}</span>
    <div class="skill-card-actions">
      ${renderEvidenceSummary(skill, { compact: true })}
      <a class="skill-history-link" href="${siteRoute(`/skills/${skill.slug}#evaluation-history`)}">${skill.reports.length} reports →</a>
    </div>
  </footer>
</article>`,
    )
    .join('\n');
  return `---
title: Skill catalog
description: Reusable Codex workflows and the evidence currently archived for them.
---

<span class="eyebrow">Skill catalog</span>

# Reusable workflows,<br>with inspectable evidence.

<p class="lede">Each skill packages a focused way of working. Its page distinguishes the instructions from the evidence recorded by previous evaluation runs.</p>

${renderEvidenceLegend()}

<div class="skill-grid">
${cards}
</div>
`;
}

function renderEvaluationIndex(reports) {
  const rows = reports
    .map(
      report =>
        `<a class="history-row" href="${reportRoute(report)}">
  <span><strong>${escapeHtml(report.skill)}</strong><small>${escapeHtml(report.operationDisplay)} · ${escapeHtml(formatStarted(report.startedAt))}</small></span>
  <span class="status status-${statusClass(report.status)}">${escapeHtml(report.status)}</span>
</a>`,
    )
    .join('\n');
  return `---
title: Evaluation evidence
description: Recorded evaluation operations, including passing and failing results.
---

<span class="eyebrow">Evaluation archive</span>

# Evidence is useful<br>when it remains inspectable.

<p class="lede">This history includes successful, failed, and incomplete operations. Each entry links claims to mechanical checks, judge evidence, and code changes retained in the canonical report.</p>

<p>Operation type describes how evidence was produced. It does not determine the result or evidence strength by itself.</p>

<div class="history-list">
${rows}
</div>
`;
}

function renderHome(skills, reports) {
  const passed = reports.filter(report => report.status === 'PASS').length;
  const otherOutcomes = reports.length - passed;
  const featured = ['develop-skill-with-evals', 'refactor-design', 'restructure-documentation']
    .map(slug => skills.find(skill => skill.slug === slug))
    .filter(Boolean)
    .map(
      skill => `<a href="${siteRoute(`/skills/${skill.slug}`)}">
  <span>${escapeHtml(skill.evidenceLabel)}</span>
  <strong>${escapeHtml(skill.name)}</strong>
  <p>${escapeHtml(skill.description)}</p>
</a>`,
    )
    .join('\n');

  return `---
title: Evaluating Codex Skills
description: Evidence of how effectively skills guide Codex behavior.
layout: page
---

<div class="home-hero">
  <div class="hero-copy">
    <span class="eyebrow">Open workflows · Recorded evidence</span>
    <h1>Evaluating<br>Codex Skills</h1>
    <p>Evidence of how effectively skills guide Codex behavior.</p>
    <div class="hero-actions">
      <a class="primary-action" href="${siteRoute('/skills/')}">Explore the skills <span>→</span></a>
      <a class="secondary-action" href="${siteRoute('/evaluations/')}">Inspect evaluation evidence</a>
    </div>
  </div>
  <div class="evidence-ledger" aria-label="Archive summary">
    <span>Archive snapshot</span>
    <strong>${reports.length}</strong>
    <p>archived operations</p>
    <dl>
      <div><dt>Skills</dt><dd>${skills.length}</dd></div>
      <div><dt>Pass</dt><dd>${passed}</dd></div>
      <div><dt>Other outcomes</dt><dd>${otherOutcomes}</dd></div>
    </dl>
  </div>
</div>

<section class="home-section">
  <header>
    <span class="eyebrow">How to read this project</span>
    <h2>Instructions are claims.<br>Evaluations are evidence.</h2>
  </header>
  <div class="process-grid">
    <article><span>01</span><h3>Choose a workflow</h3><p>A skill packages instructions, scripts, and references for one repeatable kind of work.</p></article>
    <article><span>02</span><h3>Exercise behavior</h3><p>An evaluation gives the skill a bounded task and records mechanical checks, judge findings, and runtime facts.</p></article>
    <article><span>03</span><h3>Inspect the record</h3><p>The archive preserves successes, failures, code changes, and limitations instead of reducing the result to a badge.</p></article>
  </div>
</section>

<section class="home-section featured-section">
  <header>
    <span class="eyebrow">Evidence available now</span>
    <h2>Start with the skills<br>that have a recorded history.</h2>
  </header>
  <div class="featured-grid">
${featured}
  </div>
</section>

<section class="archive-note">
  <span>What this site does not claim</span>
  <p>An archived pass describes one recorded execution. Changes to a skill, model, Codex CLI, fixture, or runtime require new evidence.</p>
  <a href="${siteRoute('/evaluations/')}">Read all ${reports.length} archived operations →</a>
</section>
`;
}

function writeOutput(path, content) {
  mkdirSync(dirname(path), { recursive: true });
  writeFileSync(path, content.endsWith('\n') ? content : `${content}\n`);
}

export function generateContent({ repositoryRoot, archiveRoot, outputRoot }) {
  validateEvaluationGlossary();
  const manifest = readJson(join(archiveRoot, 'manifest.json'));
  if (!Array.isArray(manifest.reports)) {
    throw new Error('Archive manifest reports must be an array');
  }
  if (manifest.report_count !== undefined && manifest.report_count !== manifest.reports.length) {
    throw new Error(`Archive manifest declares ${manifest.report_count} reports but lists ${manifest.reports.length}`);
  }

  const reports = manifest.reports.map(entry => normalizeReport(entry, archiveRoot)).sort((left, right) => right.id.localeCompare(left.id));
  const skills = findSkills(repositoryRoot).map(skill => {
    const skillReports = reports.filter(report => report.skill === skill.slug);
    const evidence = deriveEvidence(join(repositoryRoot, skill.slug), skillReports);
    return {
      ...skill,
      evidence,
      evidenceLabel: evidence.label,
      evidenceExplanation: evidence.description,
      reports: skillReports,
    };
  });

  rmSync(outputRoot, { recursive: true, force: true });
  for (const asset of ['mark-light.svg', 'mark-dark.svg']) {
    const destination = join(outputRoot, 'public', asset);
    mkdirSync(dirname(destination), { recursive: true });
    copyFileSync(join(websiteRoot, 'public', asset), destination);
  }
  writeOutput(
    join(outputRoot, 'data.json'),
    `${JSON.stringify({ generatedFrom: relative(repositoryRoot, archiveRoot), evaluationGlossary, skills, reports }, null, 2)}\n`,
  );
  writeOutput(join(outputRoot, 'index.md'), renderHome(skills, reports));
  writeOutput(join(outputRoot, 'skills', 'index.md'), renderSkillIndex(skills));
  for (const skill of skills) {
    writeOutput(join(outputRoot, 'skills', `${skill.slug}.md`), renderSkill(skill));
  }
  writeOutput(join(outputRoot, 'evaluations', 'index.md'), renderEvaluationIndex(reports));
  for (const report of reports) {
    writeOutput(join(outputRoot, 'evaluations', report.skill, `${report.id}.md`), renderReport(report));
  }
  return { skills: skills.length, reports: reports.length };
}

const currentFile = fileURLToPath(import.meta.url);
if (process.argv[1] && resolve(process.argv[1]) === currentFile) {
  const argumentsMap = parseArguments(process.argv.slice(2));
  const result = generateContent({
    repositoryRoot: argumentsMap['repository-root'],
    archiveRoot: argumentsMap.archive,
    outputRoot: argumentsMap.output,
  });
  process.stdout.write(`Generated ${result.skills} skills and ${result.reports} reports.\n`);
}
