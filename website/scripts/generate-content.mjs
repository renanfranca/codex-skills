import { copyFileSync, mkdirSync, readFileSync, readdirSync, rmSync, writeFileSync } from 'node:fs';
import { dirname, isAbsolute, join, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const websiteRoot = join(dirname(fileURLToPath(import.meta.url)), '..');
const contentConfig = JSON.parse(readFileSync(join(websiteRoot, 'content-config.json'), 'utf8'));
const evidenceLabels = new Map([
  ['restructure-documentation', 'Current promotion'],
  ['refactor-design', 'Current observations'],
  ['develop-skill-with-evals', 'Historical evidence'],
]);
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
  return {
    caseId: observation.case_id ?? 'Not recorded',
    status: observation.status ?? 'Not recorded',
    kind: observation.kind ?? 'Not recorded',
    role: observation.role ?? 'Not recorded',
    judgeVerdict: observation.judge?.verdict ?? 'Not recorded',
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
  return {
    id: entry.operation_id,
    skill: entry.skill,
    status: entry.status ?? operation.status ?? 'Not recorded',
    operation: entry.operation ?? operation.type ?? 'Not recorded',
    workflow: operation.workflow ?? 'Not recorded',
    promotionEligible: operation.promotion_eligible ?? null,
    failureCategory: operation.failure_category ?? 'Not recorded',
    provenance: report.provenance ?? 'Not recorded',
    startedAt: report.started_at ?? 'Not recorded',
    finishedAt: report.finished_at ?? 'Not recorded',
    durationMs: entry.duration_ms ?? report.duration_ms ?? null,
    model: entry.model ?? report.runtime?.executor?.model ?? report.runtime?.executor?.requested_model ?? 'Not recorded',
    reasoningEffort: entry.reasoning_effort ?? report.runtime?.executor?.reasoning_effort ?? 'Not recorded',
    sessions: entry.sessions ?? report.sessions?.executed ?? null,
    totalTokens: report.usage?.total_tokens ?? entry.tokens?.total ?? null,
    limitations: report.limitations ?? [],
    observations: (report.observations ?? []).map(normalizeObservation),
    archivePath: entry.path,
  };
}

function formatDuration(durationMs) {
  if (durationMs === null || durationMs === undefined) return 'Not recorded';
  if (durationMs < 1000) return `${durationMs} ms`;
  const seconds = durationMs / 1000;
  if (seconds < 60) return `${seconds.toFixed(1)} s`;
  return `${Math.floor(seconds / 60)}m ${Math.round(seconds % 60)}s`;
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
  <div><span>Result</span><strong class="status status-${statusClass(observation.status)}">${escapeHtml(observation.status)}</strong></div>
  <div><span>Kind</span><strong>${escapeHtml(observation.kind)}</strong></div>
  <div><span>Role</span><strong>${escapeHtml(observation.role)}</strong></div>
  <div><span>Judge</span><strong>${escapeHtml(observation.judgeVerdict)}</strong></div>
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

<p class="lede">A recorded <strong>${escapeHtml(report.operation)}</strong> operation for <code>${escapeHtml(report.id)}</code>.</p>

<div class="report-hero status-panel status-${statusClass(report.status)}">
  <div>
    <span class="label">Recorded result</span>
    <strong>${escapeHtml(report.status)}</strong>
  </div>
  <p>This page projects the archived report. Missing information remains explicitly unrecorded.</p>
</div>

## Execution facts

<div class="fact-grid">
  <div><span>Started</span><strong>${escapeHtml(formatStarted(report.startedAt))}</strong></div>
  <div><span>Duration</span><strong>${formatDuration(report.durationMs)}</strong></div>
  <div><span>Model</span><strong>${escapeHtml(report.model)}</strong></div>
  <div><span>Reasoning effort</span><strong>${escapeHtml(report.reasoningEffort)}</strong></div>
  <div><span>Sessions</span><strong>${escapeHtml(report.sessions ?? 'Not recorded')}</strong></div>
  <div><span>Total tokens</span><strong>${escapeHtml(report.totalTokens ?? 'Not recorded')}</strong></div>
  <div><span>Failure category</span><strong>${escapeHtml(report.failureCategory)}</strong></div>
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
  <span><strong>${escapeHtml(report.operation)}</strong><small>${escapeHtml(formatStarted(report.startedAt))}</small></span>
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

<div class="evidence-callout">
  <span>Evidence status</span>
  <strong>${escapeHtml(skill.evidenceLabel)}</strong>
  <p>${escapeHtml(skill.evidenceExplanation)}</p>
</div>

## Evaluation history

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
        `<a class="skill-card" href="${siteRoute(`/skills/${skill.slug}`)}">
  <span class="skill-index">${String(skills.indexOf(skill) + 1).padStart(2, '0')}</span>
  <h2>${escapeHtml(skill.name)}</h2>
  <p>${escapeHtml(skill.description)}</p>
  <footer><span>${escapeHtml(skill.evidenceLabel)}</span><strong>${skill.reports.length} reports →</strong></footer>
</a>`,
    )
    .join('\n');
  return `---
title: Skill catalog
description: Reusable Codex workflows and the evidence currently archived for them.
---

<span class="eyebrow">Skill catalog</span>

# Reusable workflows,<br>with inspectable evidence.

<p class="lede">Each skill packages a focused way of working. Its page distinguishes the instructions from the evidence recorded by previous evaluation runs.</p>

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
  <span><strong>${escapeHtml(report.skill)}</strong><small>${escapeHtml(report.operation)} · ${escapeHtml(formatStarted(report.startedAt))}</small></span>
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

function evidenceExplanation(skill, reportCount) {
  if (reportCount === 0) {
    return 'The skill is available, but this archive does not currently contain an evaluation report for it.';
  }
  if (skill === 'restructure-documentation') {
    return 'The archive contains the promotion campaign currently used as direct evidence for this skill.';
  }
  if (skill === 'refactor-design') {
    return 'The archive contains recent observation runs that demonstrate and calibrate this skill.';
  }
  return 'The archive preserves historical runs. They describe past executions, not a guarantee about a changed skill or runtime.';
}

function writeOutput(path, content) {
  mkdirSync(dirname(path), { recursive: true });
  writeFileSync(path, content.endsWith('\n') ? content : `${content}\n`);
}

export function generateContent({ repositoryRoot, archiveRoot, outputRoot }) {
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
    return {
      ...skill,
      evidenceLabel: evidenceLabels.get(skill.slug) ?? (skillReports.length ? 'Historical evidence' : 'No archived evidence'),
      evidenceExplanation: evidenceExplanation(skill.slug, skillReports.length),
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
    `${JSON.stringify({ generatedFrom: relative(repositoryRoot, archiveRoot), skills, reports }, null, 2)}\n`,
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
