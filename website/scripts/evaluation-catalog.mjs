import { existsSync, readFileSync, readdirSync, realpathSync } from 'node:fs';
import { isAbsolute, join, relative, resolve } from 'node:path';

function readJson(path) {
  try {
    return JSON.parse(readFileSync(path, 'utf8'));
  } catch (error) {
    throw new Error(`Cannot read valid JSON from ${path}: ${error.message}`);
  }
}

export function humanizeIdentifier(value) {
  const words = String(value).split(/[-_]+/).filter(Boolean);
  if (!words.length) return String(value);
  return `${words[0][0].toUpperCase()}${words[0].slice(1)}${words.length > 1 ? ` ${words.slice(1).join(' ')}` : ''}`;
}

function resolveInside(root, path, label) {
  const target = resolve(root, path);
  const relativePath = relative(root, target);
  if (relativePath === '..' || relativePath.startsWith(`..${process.platform === 'win32' ? '\\' : '/'}`) || isAbsolute(relativePath)) {
    throw new Error(`${label} ${path} resolves outside ${root}`);
  }
  return target;
}

function fixturePaths(caseRoot) {
  const fixtureRoot = join(caseRoot, 'fixture');
  if (!existsSync(fixtureRoot)) return [];
  const paths = [];
  function visit(directory) {
    for (const entry of readdirSync(directory, { withFileTypes: true })) {
      const path = join(directory, entry.name);
      if (entry.isDirectory()) visit(path);
      else if (entry.isFile()) paths.push(relative(caseRoot, path).split('\\').join('/'));
    }
  }
  visit(fixtureRoot);
  return paths.sort();
}

function normalizeCommand(command) {
  return {
    argv: Array.isArray(command?.argv) ? command.argv.map(String) : [],
    exitCode: command?.exit_code ?? 'Not recorded',
  };
}

function readCoverage(skillRoot) {
  const path = join(skillRoot, 'evals', 'coverage.json');
  if (!existsSync(path)) return null;
  const coverage = readJson(path);
  if (coverage.version !== 1 || !Array.isArray(coverage.contracts)) {
    throw new Error(`Evaluation coverage is invalid for ${skillRoot}`);
  }
  return coverage;
}

function mappingsForCase(entries, caseId) {
  return entries.flatMap(entry => {
    const mappings = (entry.mappings ?? []).filter(mapping => mapping.case_id === caseId);
    return mappings.map(mapping => ({
      id: entry.id ?? 'Not recorded',
      statement: entry.statement ?? null,
      source: entry.source ?? null,
      sections: entry.sections ?? [],
      guarantee: entry.guarantee ?? 'Not recorded',
      limitation: entry.limitation ?? null,
      dimension: mapping.dimension ?? 'Not recorded',
      evidence: mapping.evidence ?? [],
    }));
  });
}

function coverageForCase(coverage, caseId) {
  return coverage ? mappingsForCase(coverage.contracts, caseId) : [];
}

function rubricCoverageForCase(coverage, caseId) {
  return coverage ? mappingsForCase(coverage.rubric_families ?? [], caseId) : [];
}

function summarizeTraceability(coverage, executableCaseCount) {
  if (!coverage) return null;
  const rubricFamilies = coverage.rubric_families ?? [];
  return {
    declared: true,
    executableCaseCount,
    skillContractCount: coverage.contracts.length,
    skillContractMappingCount: coverage.contracts.reduce((count, contract) => count + (contract.mappings ?? []).length, 0),
    rubricFamilyCount: rubricFamilies.length,
    rubricFamilyMappingCount: rubricFamilies.reduce((count, family) => count + (family.mappings ?? []).length, 0),
  };
}

function reportCaseFingerprint(report, caseId) {
  return report.fingerprints?.cases?.[caseId] ?? null;
}

function evaluatedSourceFingerprint(report) {
  const sources = report.fingerprints?.sources;
  if (!sources || typeof sources !== 'object') return null;
  if (Object.hasOwn(sources, 'baseline')) return typeof sources.candidate === 'string' ? sources.candidate : null;
  return typeof sources.evaluated === 'string' ? sources.evaluated : null;
}

function summarizeObservationResults(observations) {
  if (!observations.length) return 'Not recorded';
  const counts = new Map();
  for (const observation of observations) counts.set(observation.status, (counts.get(observation.status) ?? 0) + 1);
  if (counts.size === 1) return counts.keys().next().value;
  return [...counts].map(([status, count]) => `${status}: ${count}`).join(' · ');
}

function relatedOperation(report, caseId, currentSourceFingerprint, currentCaseFingerprint) {
  const observations = report.observations.filter(observation => observation.caseId === caseId);
  if (!observations.length) return null;
  return {
    id: report.id,
    href: report.href,
    status: report.status,
    operation: report.operation,
    operationDisplay: report.operationDisplay,
    promotionEligible: report.promotionEligible,
    startedAt: report.startedAt,
    sourceCompatible: evaluatedSourceFingerprint(report) === currentSourceFingerprint,
    caseCompatible: reportCaseFingerprint(report, caseId) === currentCaseFingerprint,
    resultSummary: summarizeObservationResults(observations),
    observations,
  };
}

function compareOperations(left, right) {
  const byStartedAt = String(right.startedAt).localeCompare(String(left.startedAt));
  return byStartedAt || right.id.localeCompare(left.id);
}

function deriveCaseEvidence(operations, definitions) {
  if (!operations.length) return definitions['not-evaluated-yet'];
  const compatible = operations.filter(operation => operation.sourceCompatible && operation.caseCompatible);
  if (!compatible.length) return definitions['historical-runs'];
  if (
    compatible.some(
      operation =>
        operation.promotionEligible === true
        && operation.status === 'PASS'
        && operation.observations.some(observation => observation.role === 'candidate' && observation.status === 'PASS'),
    )
  ) {
    return definitions['validated-promotion'];
  }
  if (
    compatible.some(operation =>
      operation.observations.some(observation => observation.role !== 'baseline' && observation.status === 'PASS'),
    )
  ) {
    return definitions['current-pass'];
  }
  return definitions['no-current-pass'];
}

function activeEvaluation({ skill, skillRoot, caseId, reports, sourceFingerprint, caseEvidenceStatuses, treeFingerprint, coverage }) {
  const caseRoot = join(skillRoot, 'evals', 'cases', caseId);
  const manifestPath = join(caseRoot, 'case.json');
  if (!existsSync(manifestPath)) throw new Error(`Evaluation case ${caseId} is missing ${manifestPath}`);
  const manifest = readJson(manifestPath);
  if (manifest.id !== caseId || typeof manifest.kind !== 'string') {
    throw new Error(`Evaluation case ${caseId} is invalid for ${skillRoot}`);
  }
  const promptPath = manifest.prompt_file ? resolveInside(caseRoot, manifest.prompt_file, 'Prompt path') : null;
  if (promptPath && !realpathSync(promptPath).startsWith(`${realpathSync(caseRoot)}/`)) {
    throw new Error(`Prompt path ${manifest.prompt_file} resolves outside ${caseRoot}`);
  }
  const caseFingerprint = treeFingerprint(caseRoot);
  const operations = reports
    .map(report => relatedOperation(report, caseId, sourceFingerprint, caseFingerprint))
    .filter(Boolean)
    .sort(compareOperations);
  return {
    skillId: skill.slug,
    caseId,
    title: humanizeIdentifier(caseId),
    route: `/skills/${skill.slug}/evaluations/${caseId}`,
    active: true,
    state: 'active',
    kind: manifest.kind,
    caseFingerprint,
    prompt: promptPath ? readFileSync(promptPath, 'utf8') : null,
    fixturePaths: fixturePaths(caseRoot),
    mechanical: {
      expectedExitCode: manifest.mechanical?.expected_exit_code ?? 'Not recorded',
      requiredPaths: manifest.mechanical?.required_paths ?? [],
      protectedChangedPaths: manifest.mechanical?.forbidden_changed_paths ?? [],
      commands: (manifest.mechanical?.commands ?? []).map(normalizeCommand),
    },
    oracle: {
      applicable: (manifest.oracle?.commands ?? []).length > 0,
      commands: (manifest.oracle?.commands ?? []).map(normalizeCommand),
    },
    judge: {
      applicable: manifest.judge?.enabled === true,
      criteria: manifest.judge?.criteria ?? [],
      noActionAcceptable: manifest.judge?.no_action_acceptable ?? 'Not recorded',
    },
    coverage: coverageForCase(coverage, caseId),
    rubricCoverage: rubricCoverageForCase(coverage, caseId),
    traceabilityDeclared: coverage !== null,
    evidence: deriveCaseEvidence(operations, caseEvidenceStatuses),
    latestRecordedResult: operations[0]?.resultSummary ?? 'Not recorded',
    latestOperation: operations[0] ?? null,
    operations,
  };
}

function historicalEvaluation(skill, caseId, reports) {
  const operations = reports
    .map(report => {
      const observations = report.observations.filter(observation => observation.caseId === caseId);
      return observations.length
        ? {
            id: report.id,
            href: report.href,
            status: report.status,
            operation: report.operation,
            operationDisplay: report.operationDisplay,
            promotionEligible: report.promotionEligible,
            startedAt: report.startedAt,
            resultSummary: summarizeObservationResults(observations),
            observations,
          }
        : null;
    })
    .filter(Boolean)
    .sort(compareOperations);
  return {
    skillId: skill.slug,
    caseId,
    title: humanizeIdentifier(caseId),
    route: `/skills/${skill.slug}/evaluations/${caseId}`,
    active: false,
    state: 'historical',
    latestRecordedResult: operations[0]?.resultSummary ?? 'Not recorded',
    latestOperation: operations[0] ?? null,
    operations,
  };
}

export function buildEvaluationCatalog({
  skill,
  skillRoot,
  caseIds = [],
  reports,
  sourceFingerprint,
  caseEvidenceStatuses,
  treeFingerprint,
}) {
  const coverage = readCoverage(skillRoot);
  const activeIds = new Set(caseIds);
  const archivedIds = [...new Set(reports.flatMap(report => report.observations.map(observation => observation.caseId)))].filter(
    caseId => caseId !== 'Not recorded' && !activeIds.has(caseId),
  );
  return {
    traceability: summarizeTraceability(coverage, caseIds.length),
    evaluations: caseIds.map(caseId =>
      activeEvaluation({
        skill,
        skillRoot,
        caseId,
        reports,
        sourceFingerprint,
        caseEvidenceStatuses,
        treeFingerprint,
        coverage,
      }),
    ),
    historicalEvaluations: archivedIds.sort().map(caseId => historicalEvaluation(skill, caseId, reports)),
  };
}
