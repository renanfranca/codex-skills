import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { mkdtempSync, mkdirSync, readFileSync, rmSync, symlinkSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import test from 'node:test';

const websiteDirectory = join(dirname(fileURLToPath(import.meta.url)), '..');

test('generates a factual skill history from an archived evaluation', () => {
  const workspace = mkdtempSync(join(tmpdir(), 'codex-skills-content-'));
  const repository = join(workspace, 'repository');
  const archive = join(repository, 'evaluation-reports');
  const operationId = '20260728T120000.000000Z-example';
  const reportDirectory = join(archive, 'example-skill', 'operations', operationId);
  const output = join(workspace, 'generated');

  mkdirSync(join(repository, 'example-skill'), { recursive: true });
  mkdirSync(reportDirectory, { recursive: true });
  writeFileSync(
    join(repository, 'example-skill', 'SKILL.md'),
    ['---', 'name: example-skill', 'description: Explain an example behavior with evidence.', '---', '', '# Example skill', ''].join('\n'),
  );
  writeFileSync(
    join(archive, 'manifest.json'),
    `${JSON.stringify(
      {
        version: 1,
        canonical_format: 'report.json',
        report_count: 1,
        reports: [
          {
            skill: 'example-skill',
            operation_id: operationId,
            operation: 'run',
            status: 'PASS',
            model: 'gpt-example',
            reasoning_effort: 'medium',
            sessions: 1,
            duration_ms: 1200,
            path: `example-skill/operations/${operationId}/report.json`,
          },
        ],
      },
      null,
      2,
    )}\n`,
  );
  writeFileSync(
    join(reportDirectory, 'report.json'),
    `${JSON.stringify(
      {
        schema_version: 1,
        operation: {
          id: operationId,
          type: 'run',
          status: 'PASS',
          workflow: 'run',
          promotion_eligible: true,
          failure_category: null,
        },
        provenance: 'executed',
        started_at: '2026-07-28T12:00:00Z',
        finished_at: '2026-07-28T12:00:01Z',
        duration_ms: 1200,
        skill: { path: './example-skill', name: 'example-skill' },
        runtime: {
          executor: { model: 'gpt-example', reasoning_effort: 'medium' },
          judge: { required: true, model: 'gpt-judge', reasoning_effort: 'high' },
        },
        sessions: {
          planned: { executor: 1, judge: 1, total: 2 },
          executed: { executor: 1, judge: 1, total: 2 },
        },
        usage: { total_tokens: 42 },
        observations: [
          {
            case_id: 'example-case',
            status: 'PASS',
            kind: 'behavioral',
            role: 'candidate',
            mechanical: {
              passed: true,
              checks: [{ name: 'public command', passed: true, detail: 'exit 0' }],
              commands: [],
            },
            judge: {
              enabled: true,
              executed: true,
              verdict: 'PASS',
              rationale: 'The observable behavior matched the contract.',
              evidence: ['The public command exited successfully.'],
            },
            evidence: {
              changed_files: ['example.py'],
              diff: '--- a/example.py\n+++ b/example.py\n',
              fragments: [
                {
                  path: 'example.py',
                  before: 'print("before")\n',
                  after: 'print("after")\n',
                  binary: false,
                },
              ],
            },
          },
        ],
        limitations: [],
      },
      null,
      2,
    )}\n`,
  );

  execFileSync(
    process.execPath,
    [join(websiteDirectory, 'scripts', 'generate-content.mjs'), '--repository-root', repository, '--archive', archive, '--output', output],
    { stdio: 'pipe' },
  );

  const model = JSON.parse(readFileSync(join(output, 'data.json'), 'utf8'));
  const reportPage = readFileSync(join(output, 'evaluations', 'example-skill', `${operationId}.md`), 'utf8');

  assert.equal(model.skills[0].name, 'example-skill');
  assert.equal(model.skills[0].description, 'Explain an example behavior with evidence.');
  assert.equal(model.skills[0].reports[0].status, 'PASS');
  assert.deepEqual(model.reports[0].runtimeByRole, {
    executor: { model: 'gpt-example', reasoningEffort: 'medium' },
    judge: { applicable: true, model: 'gpt-judge', reasoningEffort: 'high' },
  });
  assert.deepEqual(model.reports[0].sessionsByRole.executed, { executor: 1, judge: 1, total: 2 });
  assert.deepEqual(model.reports[0].sessionsByRole.planned, { executor: 1, judge: 1, total: 2 });
  assert.equal(model.reports[0].judgeState, 'Executed');
  assert.match(reportPage, /The observable behavior matched the contract\./);
  assert.match(reportPage, /--- a\/example\.py\n\+\+\+ b\/example\.py/);
  assert.match(reportPage, /Code fragments/);
  assert.match(reportPage, /print\("before"\)/);
  assert.match(reportPage, /print\("after"\)/);
  assert.match(reportPage, /Exploratory evaluation[\s\S]*<code>run<\/code>/);
  assert.match(reportPage, /<EvaluationHelp guide>/);
  assert.match(reportPage, /<EvaluationHelp[\s\S]*field="executorModel"/);
  assert.match(reportPage, /field="executorModel"/);
  assert.match(reportPage, /field="judgeModel"/);
  assert.match(reportPage, /field="sessions"/);
  assert.match(reportPage, /None/);

  const reportPath = join(reportDirectory, 'report.json');
  const report = JSON.parse(readFileSync(reportPath, 'utf8'));
  for (const [judge, displayedState] of [
    [{ enabled: false, executed: false, verdict: 'PASS' }, 'Not used'],
    [{ enabled: true, executed: false, verdict: 'SKIPPED' }, 'Skipped'],
  ]) {
    Object.assign(report.observations[0].judge, judge);
    writeFileSync(reportPath, `${JSON.stringify(report)}\n`);
    execFileSync(
      process.execPath,
      [
        join(websiteDirectory, 'scripts', 'generate-content.mjs'),
        '--repository-root',
        repository,
        '--archive',
        archive,
        '--output',
        output,
      ],
      { stdio: 'pipe' },
    );
    const updatedModel = JSON.parse(readFileSync(join(output, 'data.json'), 'utf8'));
    assert.equal(updatedModel.reports[0].observations[0].judgeDisplay, displayedState);
  }
});

test('keeps a failed operation and explains its recorded failure category', () => {
  const workspace = mkdtempSync(join(tmpdir(), 'codex-skills-failure-'));
  const repository = join(workspace, 'repository');
  const archive = join(repository, 'evaluation-reports');
  const operationId = '20260728T130000.000000Z-failure';
  const reportDirectory = join(archive, 'example-skill', 'operations', operationId);
  const output = join(workspace, 'generated');

  mkdirSync(join(repository, 'example-skill'), { recursive: true });
  mkdirSync(reportDirectory, { recursive: true });
  writeFileSync(join(repository, 'example-skill', 'SKILL.md'), '---\nname: example-skill\ndescription: Explain failures honestly.\n---\n');
  writeFileSync(
    join(archive, 'manifest.json'),
    `${JSON.stringify({
      version: 1,
      report_count: 1,
      reports: [
        {
          skill: 'example-skill',
          operation_id: operationId,
          operation: 'run',
          status: 'ERROR',
          path: `example-skill/operations/${operationId}/report.json`,
        },
      ],
    })}\n`,
  );
  writeFileSync(
    join(reportDirectory, 'report.json'),
    `${JSON.stringify({
      schema_version: 1,
      operation: {
        id: operationId,
        type: 'run',
        status: 'ERROR',
        failure_category: 'infrastructure',
      },
      skill: { name: 'example-skill' },
      observations: [],
      limitations: ['The executor did not start.'],
    })}\n`,
  );

  execFileSync(
    process.execPath,
    [join(websiteDirectory, 'scripts', 'generate-content.mjs'), '--repository-root', repository, '--archive', archive, '--output', output],
    { stdio: 'pipe' },
  );

  const reportPage = readFileSync(join(output, 'evaluations', 'example-skill', `${operationId}.md`), 'utf8');

  assert.match(reportPage, /Recorded result[\s\S]*ERROR/);
  assert.match(reportPage, /field="failureCategory" current="infrastructure"/);
  assert.match(reportPage, /The executor did not start\./);

  const reportPath = join(reportDirectory, 'report.json');
  const report = JSON.parse(readFileSync(reportPath, 'utf8'));
  for (const [recordedValue, displayedValue] of [
    ['contract', 'contract'],
    [null, 'None'],
  ]) {
    report.operation.failure_category = recordedValue;
    writeFileSync(reportPath, `${JSON.stringify(report)}\n`);
    execFileSync(
      process.execPath,
      [
        join(websiteDirectory, 'scripts', 'generate-content.mjs'),
        '--repository-root',
        repository,
        '--archive',
        archive,
        '--output',
        output,
      ],
      { stdio: 'pipe' },
    );
    assert.match(
      readFileSync(join(output, 'evaluations', 'example-skill', `${operationId}.md`), 'utf8'),
      new RegExp(`field="failureCategory" current="${displayedValue}"`),
    );
  }

  delete report.operation.failure_category;
  writeFileSync(reportPath, `${JSON.stringify(report)}\n`);
  execFileSync(
    process.execPath,
    [join(websiteDirectory, 'scripts', 'generate-content.mjs'), '--repository-root', repository, '--archive', archive, '--output', output],
    { stdio: 'pipe' },
  );
  assert.match(
    readFileSync(join(output, 'evaluations', 'example-skill', `${operationId}.md`), 'utf8'),
    /field="failureCategory" current="Not recorded"/,
  );
});

test('rejects a manifest report path outside the evaluation archive', () => {
  const workspace = mkdtempSync(join(tmpdir(), 'codex-skills-invalid-'));
  const repository = join(workspace, 'repository');
  const archive = join(repository, 'evaluation-reports');
  const output = join(workspace, 'generated');

  mkdirSync(join(repository, 'example-skill'), { recursive: true });
  mkdirSync(archive, { recursive: true });
  writeFileSync(join(repository, 'example-skill', 'SKILL.md'), '---\nname: example-skill\ndescription: Reject invalid evidence.\n---\n');
  writeFileSync(join(repository, 'outside.json'), '{"operation":{"status":"PASS"}}\n');
  writeFileSync(
    join(archive, 'manifest.json'),
    `${JSON.stringify({
      version: 1,
      report_count: 1,
      reports: [
        {
          skill: 'example-skill',
          operation_id: 'outside',
          status: 'PASS',
          path: '../outside.json',
        },
      ],
    })}\n`,
  );

  assert.throws(
    () =>
      execFileSync(
        process.execPath,
        [
          join(websiteDirectory, 'scripts', 'generate-content.mjs'),
          '--repository-root',
          repository,
          '--archive',
          archive,
          '--output',
          output,
        ],
        { stdio: 'pipe' },
      ),
    error => {
      assert.match(error.stderr.toString(), /outside the evaluation archive/);
      return true;
    },
  );
});

test('generates a project landing page that leads readers to evidence', () => {
  const output = mkdtempSync(join(tmpdir(), 'codex-skills-home-'));
  const repository = join(websiteDirectory, '..');
  const manifest = JSON.parse(readFileSync(join(repository, 'evaluation-reports', 'manifest.json'), 'utf8'));

  execFileSync(
    process.execPath,
    [
      join(websiteDirectory, 'scripts', 'generate-content.mjs'),
      '--repository-root',
      repository,
      '--archive',
      join(repository, 'evaluation-reports'),
      '--output',
      output,
    ],
    { stdio: 'pipe' },
  );

  const homePage = readFileSync(join(output, 'index.md'), 'utf8');

  assert.match(homePage, /Evaluating<br>Codex Skills/);
  assert.match(homePage, /Evidence of how effectively skills guide Codex behavior\./);
  assert.match(homePage, new RegExp(`${manifest.report_count} archived operations`));
  assert.match(homePage, /href="\/codex-skills\/skills\/"/);
  assert.match(homePage, /href="\/codex-skills\/evaluations\/"/);
});

test('publishes the complete evaluation vocabulary as independent concepts', () => {
  const output = mkdtempSync(join(tmpdir(), 'codex-skills-glossary-'));
  const repository = join(websiteDirectory, '..');

  execFileSync(
    process.execPath,
    [
      join(websiteDirectory, 'scripts', 'generate-content.mjs'),
      '--repository-root',
      repository,
      '--archive',
      join(repository, 'evaluation-reports'),
      '--output',
      output,
    ],
    { stdio: 'pipe' },
  );

  const model = JSON.parse(readFileSync(join(output, 'data.json'), 'utf8'));

  assert.equal(model.evaluationGlossary.concepts.evidenceStatus.label, 'Evidence status');
  assert.equal(model.evaluationGlossary.concepts.operationType.label, 'Operation type');
  assert.equal(model.evaluationGlossary.concepts.recordedResult.label, 'Recorded result');
  assert.deepEqual(Object.keys(model.evaluationGlossary.operations), [
    'run',
    'verify-change',
    'stability',
    'probe-change',
    'validate-change',
  ]);
  assert.deepEqual(Object.keys(model.evaluationGlossary.results), ['PASS', 'FAIL', 'ERROR', 'INCONCLUSIVE', 'INVALID_RED', 'UNSTABLE']);
  assert.match(model.evaluationGlossary.runner.description, /run_skill_evals\.py/);
  assert.match(model.evaluationGlossary.executor.description, /performs the evaluated task/);
  assert.match(model.evaluationGlossary.judge.description, /optional.*evaluates the result.*separate invocation/i);
  assert.equal(model.evaluationGlossary.modelSession.description, model.evaluationGlossary.fields.sessions.description);
  assert.match(model.evaluationGlossary.modelSession.description, /isolated, ephemeral codex exec --json invocation/);
  assert.match(model.evaluationGlossary.modelSession.description, /started by the evaluation runner/);
  assert.match(model.evaluationGlossary.modelSession.description, /executor performs the evaluated task/);
  assert.match(model.evaluationGlossary.modelSession.description, /optional judge evaluates the result in a separate invocation/);
  assert.match(
    model.evaluationGlossary.modelSession.description,
    /not a message, conversational turn, deterministic check, or complete promotion/,
  );
  assert.match(model.evaluationGlossary.modelSession.description, /Deterministic checks consume zero model sessions/);
  assert.deepEqual(
    model.evaluationGlossary.modelSession.segments.filter(segment => segment.type === 'code'),
    [{ type: 'code', text: 'codex exec --json' }],
  );
  assert.match(model.evaluationGlossary.fields.cachedInputTokens.description, /subset of recorded input tokens/i);
  assert.match(model.evaluationGlossary.fields.reasoningOutputTokens.description, /subset of output tokens/i);
  assert.match(model.evaluationGlossary.fields.usageEvents.description, /normalized telemetry event/i);
  assert.match(model.evaluationGlossary.fields.usageEvents.description, /origin and scope/i);
  assert.match(model.evaluationGlossary.fields.apiReferenceEstimate.description, /dated API price/i);
  assert.match(model.evaluationGlossary.fields.apiReferenceEstimate.description, /not an observed charge or invoice/i);
});

test('rejects archived operations and roles without glossary definitions', () => {
  const workspace = mkdtempSync(join(tmpdir(), 'codex-skills-undocumented-taxonomy-'));
  const repository = join(workspace, 'repository');
  const archive = join(repository, 'evaluation-reports');
  const operationId = '20260730T120000.000000Z-unknown';
  const reportDirectory = join(archive, 'example-skill', 'operations', operationId);
  const output = join(workspace, 'generated');
  const reportPath = `example-skill/operations/${operationId}/report.json`;

  mkdirSync(join(repository, 'example-skill'), { recursive: true });
  mkdirSync(reportDirectory, { recursive: true });
  writeFileSync(join(repository, 'example-skill', 'SKILL.md'), '---\nname: example-skill\ndescription: Reject undocumented values.\n---\n');
  writeFileSync(
    join(archive, 'manifest.json'),
    `${JSON.stringify({
      report_count: 1,
      reports: [{ skill: 'example-skill', operation_id: operationId, operation: 'future-operation', path: reportPath }],
    })}\n`,
  );
  writeFileSync(join(reportDirectory, 'report.json'), '{"operation":{"type":"future-operation"},"observations":[]}\n');

  const generate = () =>
    execFileSync(
      process.execPath,
      [
        join(websiteDirectory, 'scripts', 'generate-content.mjs'),
        '--repository-root',
        repository,
        '--archive',
        archive,
        '--output',
        output,
      ],
      { stdio: 'pipe' },
    );

  assert.throws(generate, error => {
    assert.match(error.stderr.toString(), /unknown operation "future-operation"/);
    return true;
  });

  writeFileSync(
    join(archive, 'manifest.json'),
    `${JSON.stringify({
      report_count: 1,
      reports: [{ skill: 'example-skill', operation_id: operationId, operation: 'run', path: reportPath }],
    })}\n`,
  );
  writeFileSync(
    join(reportDirectory, 'report.json'),
    '{"operation":{"type":"run"},"observations":[{"case_id":"example","role":"future-role"}]}\n',
  );

  assert.throws(generate, error => {
    assert.match(error.stderr.toString(), /unknown role "future-role"/);
    return true;
  });
});

test('renders archived text as evidence instead of executable markup', () => {
  const workspace = mkdtempSync(join(tmpdir(), 'codex-skills-safe-evidence-'));
  const repository = join(workspace, 'repository');
  const archive = join(repository, 'evaluation-reports');
  const operationId = '20260728T140000.000000Z-safe';
  const reportDirectory = join(archive, 'example-skill', 'operations', operationId);
  const output = join(workspace, 'generated');

  mkdirSync(join(repository, 'example-skill'), { recursive: true });
  mkdirSync(reportDirectory, { recursive: true });
  writeFileSync(
    join(repository, 'example-skill', 'SKILL.md'),
    '---\nname: example-skill\ndescription: Explain <img src=x onerror=alert(1)> safely.\n---\n',
  );
  writeFileSync(
    join(archive, 'manifest.json'),
    `${JSON.stringify({
      report_count: 1,
      reports: [
        {
          skill: 'example-skill',
          operation_id: operationId,
          status: 'PASS',
          path: `example-skill/operations/${operationId}/report.json`,
        },
      ],
    })}\n`,
  );
  writeFileSync(
    join(reportDirectory, 'report.json'),
    `${JSON.stringify({
      operation: { id: operationId, status: 'PASS' },
      observations: [
        {
          case_id: 'safe-case',
          status: 'PASS',
          judge: {
            rationale: '<script>globalThis.compromised = true</script>',
          },
        },
      ],
    })}\n`,
  );

  execFileSync(
    process.execPath,
    [join(websiteDirectory, 'scripts', 'generate-content.mjs'), '--repository-root', repository, '--archive', archive, '--output', output],
    { stdio: 'pipe' },
  );

  const skillPage = readFileSync(join(output, 'skills', 'example-skill.md'), 'utf8');
  const reportPage = readFileSync(join(output, 'evaluations', 'example-skill', `${operationId}.md`), 'utf8');

  assert.doesNotMatch(skillPage, /<img src=x/);
  assert.match(skillPage, /&lt;img src=x onerror=alert\(1\)&gt;/);
  assert.doesNotMatch(reportPage, /<script>/);
  assert.match(reportPage, /&lt;script&gt;globalThis\.compromised = true&lt;\/script&gt;/);
});

test('keeps disabled compatibility skills out of the public catalog', () => {
  const output = mkdtempSync(join(tmpdir(), 'codex-skills-active-catalog-'));
  const repository = join(websiteDirectory, '..');

  execFileSync(
    process.execPath,
    [
      join(websiteDirectory, 'scripts', 'generate-content.mjs'),
      '--repository-root',
      repository,
      '--archive',
      join(repository, 'evaluation-reports'),
      '--output',
      output,
    ],
    { stdio: 'pipe' },
  );

  const model = JSON.parse(readFileSync(join(output, 'data.json'), 'utf8'));

  assert.equal(model.skills.length, 10);
  assert.equal(
    model.skills.some(skill => skill.slug === 'execplan-tdd'),
    true,
  );
  assert.equal(
    model.skills.some(skill => skill.slug === 'tdd-strict-autonomous'),
    false,
  );
  assert.equal(
    model.skills.some(skill => skill.slug === 'tdd-strict-cycle-confirmation'),
    false,
  );
});

function createEvidenceWorkspace(prefix = 'codex-skills-derived-evidence-') {
  const workspace = mkdtempSync(join(tmpdir(), prefix));
  const repository = join(workspace, 'repository');
  const archive = join(repository, 'evaluation-reports');
  const skill = join(repository, 'example-skill');
  const output = join(workspace, 'generated');

  mkdirSync(join(skill, 'evals'), { recursive: true });
  mkdirSync(archive, { recursive: true });
  writeFileSync(join(skill, 'SKILL.md'), '---\nname: example-skill\ndescription: Explain derived evidence truthfully.\n---\n');
  writeFileSync(join(skill, 'evals', 'suite.json'), `${JSON.stringify({ version: 1, cases: ['first-case', 'second-case'] }, null, 2)}\n`);
  return { workspace, repository, archive, skill, output };
}

function runnerFingerprint(skill) {
  const runner = join(websiteDirectory, '..', 'develop-skill-with-evals', 'scripts', 'run_skill_evals.py');
  return execFileSync(
    'python3',
    [
      '-c',
      'import importlib.util,pathlib,sys;p=pathlib.Path(sys.argv[1]);s=importlib.util.spec_from_file_location("runner",p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);print(m.tree_fingerprint(pathlib.Path(sys.argv[2])))',
      runner,
      skill,
    ],
    { encoding: 'utf8' },
  ).trim();
}

function writeEvidenceArchive({ archive, reports }) {
  for (const report of reports) {
    const reportDirectory = join(archive, 'example-skill', 'operations', report.operation.id);
    mkdirSync(reportDirectory, { recursive: true });
    writeFileSync(join(reportDirectory, 'report.json'), `${JSON.stringify(report, null, 2)}\n`);
  }
  writeFileSync(
    join(archive, 'manifest.json'),
    `${JSON.stringify(
      {
        version: 1,
        report_count: reports.length,
        reports: reports.map(report => ({
          skill: 'example-skill',
          operation_id: report.operation.id,
          operation: report.operation.type,
          status: report.operation.status,
          path: `example-skill/operations/${report.operation.id}/report.json`,
        })),
      },
      null,
      2,
    )}\n`,
  );
}

function generateEvidenceModel(context) {
  execFileSync(
    process.execPath,
    [
      join(websiteDirectory, 'scripts', 'generate-content.mjs'),
      '--repository-root',
      context.repository,
      '--archive',
      context.archive,
      '--output',
      context.output,
    ],
    { stdio: 'pipe' },
  );
  return JSON.parse(readFileSync(join(context.output, 'data.json'), 'utf8'));
}

test('preserves every recorded token usage field and normalized event exactly', () => {
  const context = createEvidenceWorkspace('codex-skills-token-usage-');
  writeEvidenceArchive({
    archive: context.archive,
    reports: [
      {
        operation: {
          id: '20260730T120000.000000Z-token-usage',
          type: 'run',
          status: 'PASS',
        },
        usage: {
          input_tokens: 1_001,
          cached_input_tokens: 502,
          output_tokens: 203,
          reasoning_output_tokens: 104,
          total_tokens: 1_204,
          complete: true,
          reasoning_output_tokens_complete: false,
          events: [
            {
              sequence: 7,
              source_event_type: 'turn.completed',
              scope: 'turn',
              input_tokens: 701,
              cached_input_tokens: 302,
              output_tokens: 103,
              reasoning_output_tokens: 54,
              total_tokens: 804,
              complete: false,
              reasoning_output_tokens_complete: true,
            },
          ],
          event_count: 9,
          events_complete: false,
        },
        observations: [],
      },
    ],
  });

  const report = generateEvidenceModel(context).reports[0];

  assert.deepEqual(report.usage, {
    inputTokens: 1_001,
    cachedInputTokens: 502,
    outputTokens: 203,
    reasoningOutputTokens: 104,
    totalTokens: 1_204,
    complete: true,
    reasoningOutputTokensComplete: false,
    events: [
      {
        sequence: 7,
        sourceEventType: 'turn.completed',
        scope: 'turn',
        inputTokens: 701,
        cachedInputTokens: 302,
        outputTokens: 103,
        reasoningOutputTokens: 54,
        totalTokens: 804,
        complete: false,
        reasoningOutputTokensComplete: true,
      },
    ],
    eventCount: 9,
    eventsComplete: false,
  });
});

test('preserves every recorded API reference estimate field exactly', () => {
  const context = createEvidenceWorkspace('codex-skills-api-estimate-');
  writeEvidenceArchive({
    archive: context.archive,
    reports: [
      {
        operation: {
          id: '20260730T121000.000000Z-api-estimate',
          type: 'run',
          status: 'PASS',
        },
        pricing: {
          applied: true,
          snapshot: {
            version: 3,
            effective_date: '2026-07-26',
            source: 'https://example.test/pricing',
            currency: 'USD',
            unit: 'per_million_tokens',
            models: {
              'gpt-example': {
                input: 2.5,
                cached_input: 0.25,
                output: 15,
                long_context: {
                  input_token_threshold: 272_000,
                  input_multiplier: 2,
                  output_multiplier: 1.5,
                  applies_per: 'request',
                },
              },
            },
            limitations: ['Snapshot limitation.'],
          },
          limitations: ['Applied pricing limitation.'],
        },
        api_reference_estimate: {
          available: true,
          status: 'complete',
          currency: 'USD',
          amount: 0.123456,
          base_rate_amount: 0.123456,
          actual_charge: false,
          billing_mode: 'chatgpt-plan',
          calculation: {
            model: 'gpt-example',
            unit: 'per_million_tokens',
            tokens: {
              uncached_input: 101,
              cached_input: 202,
              output: 303,
              reasoning_output: 104,
            },
            rates: {
              input: 2.5,
              cached_input: 0.25,
              output: 15,
              long_context: {
                input_token_threshold: 272_000,
                input_multiplier: 2,
                output_multiplier: 1.5,
                applies_per: 'request',
              },
            },
            components: {
              input: 0.0002525,
              cached_input: 0.0000505,
              output: 0.004545,
            },
            reasoning_note: 'Reasoning is already part of output.',
          },
          long_context_assessment: {
            input_token_threshold: 272_000,
            applies_per: 'request',
            triggering_event_sequences: [],
            observed_event_scopes: ['request'],
          },
          limitations: ['Estimate limitation.'],
        },
        observations: [],
      },
    ],
  });

  const report = generateEvidenceModel(context).reports[0];

  assert.deepEqual(report.pricing, {
    applied: true,
    snapshot: {
      version: 3,
      effectiveDate: '2026-07-26',
      source: 'https://example.test/pricing',
      currency: 'USD',
      unit: 'per_million_tokens',
      models: {
        'gpt-example': {
          input: 2.5,
          cachedInput: 0.25,
          output: 15,
          longContext: {
            inputTokenThreshold: 272_000,
            inputMultiplier: 2,
            outputMultiplier: 1.5,
            appliesPer: 'request',
          },
        },
      },
      limitations: ['Snapshot limitation.'],
    },
    limitations: ['Applied pricing limitation.'],
  });
  assert.deepEqual(report.apiReferenceEstimate, {
    available: true,
    status: 'complete',
    currency: 'USD',
    amount: 0.123456,
    baseRateAmount: 0.123456,
    actualCharge: false,
    billingMode: 'chatgpt-plan',
    calculation: {
      model: 'gpt-example',
      unit: 'per_million_tokens',
      tokens: {
        uncachedInput: 101,
        cachedInput: 202,
        output: 303,
        reasoningOutput: 104,
      },
      rates: {
        input: 2.5,
        cachedInput: 0.25,
        output: 15,
        longContext: {
          inputTokenThreshold: 272_000,
          inputMultiplier: 2,
          outputMultiplier: 1.5,
          appliesPer: 'request',
        },
      },
      components: {
        input: 0.0002525,
        cachedInput: 0.0000505,
        output: 0.004545,
      },
      reasoningNote: 'Reasoning is already part of output.',
    },
    longContextAssessment: {
      inputTokenThreshold: 272_000,
      appliesPer: 'request',
      triggeringEventSequences: [],
      observedEventScopes: ['request'],
    },
    limitations: ['Estimate limitation.'],
  });
});

test('renders complete token usage and API reference estimate details on a report page', () => {
  const context = createEvidenceWorkspace('codex-skills-report-telemetry-');
  const operationId = '20260730T122000.000000Z-report-telemetry';
  writeEvidenceArchive({
    archive: context.archive,
    reports: [
      {
        operation: {
          id: operationId,
          type: 'run',
          status: 'PASS',
        },
        usage: {
          input_tokens: 1_001,
          cached_input_tokens: 502,
          output_tokens: 203,
          reasoning_output_tokens: 104,
          total_tokens: 1_204,
          complete: true,
          reasoning_output_tokens_complete: true,
          events: [
            {
              sequence: 1,
              source_event_type: 'turn.completed',
              scope: 'turn',
              input_tokens: 1_001,
              cached_input_tokens: 502,
              output_tokens: 203,
              reasoning_output_tokens: 104,
              total_tokens: 1_204,
              complete: true,
              reasoning_output_tokens_complete: true,
            },
          ],
          event_count: 1,
          events_complete: true,
        },
        pricing: {
          applied: true,
          snapshot: {
            version: 1,
            effective_date: '2026-07-26',
            source: 'https://example.test/pricing',
            currency: 'USD',
            unit: 'per_million_tokens',
            models: {},
            limitations: ['Snapshot limitation.'],
          },
          limitations: ['Pricing limitation.'],
        },
        api_reference_estimate: {
          available: true,
          status: 'complete',
          currency: 'USD',
          amount: 0.123456,
          base_rate_amount: 0.123456,
          actual_charge: false,
          billing_mode: 'chatgpt-plan',
          calculation: {
            model: 'gpt-example',
            unit: 'per_million_tokens',
            tokens: {
              uncached_input: 499,
              cached_input: 502,
              output: 203,
              reasoning_output: 104,
            },
            rates: {
              input: 2.5,
              cached_input: 0.25,
              output: 15,
              long_context: {
                input_token_threshold: 272_000,
                input_multiplier: 2,
                output_multiplier: 1.5,
                applies_per: 'request',
              },
            },
            components: {
              input: 0.0012475,
              cached_input: 0.0001255,
              output: 0.003045,
            },
            reasoning_note: 'Reasoning output is already included in output.',
          },
          long_context_assessment: {
            input_token_threshold: 272_000,
            applies_per: 'request',
            triggering_event_sequences: [],
            observed_event_scopes: ['turn'],
          },
          limitations: ['Estimate limitation.'],
        },
        observations: [],
      },
    ],
  });

  generateEvidenceModel(context);
  const reportPage = readFileSync(join(context.output, 'evaluations', 'example-skill', `${operationId}.md`), 'utf8');

  assert.match(reportPage, /## Token usage/);
  assert.match(reportPage, /Input tokens[\s\S]*1,001/);
  assert.match(reportPage, /Cached input tokens[\s\S]*502/);
  assert.match(reportPage, /Output tokens[\s\S]*203/);
  assert.match(reportPage, /Reasoning output tokens[\s\S]*104/);
  assert.match(reportPage, /Total tokens[\s\S]*1,204/);
  assert.match(reportPage, /<details class="evidence-details usage-events">/);
  assert.match(reportPage, /<summary>Normalized usage events \(1\)<\/summary>/);
  assert.doesNotMatch(reportPage, /<details class="evidence-details usage-events" open>/);
  assert.match(reportPage, /\| 1 \| turn\.completed \| turn \| 1,001 \| 502 \| 203 \| 104 \| 1,204 \| Complete \| Complete \|/);
  assert.match(reportPage, /## API reference estimate/);
  assert.match(reportPage, /USD 0\.123456/);
  assert.match(reportPage, /not an observed charge/i);
  assert.match(reportPage, /Input component[\s\S]*USD 0\.0012475/);
  assert.match(reportPage, /Input price[\s\S]*USD 2\.5 per million tokens/);
  assert.match(reportPage, /Long context threshold[\s\S]*272,000 input tokens per request/);
  assert.match(reportPage, /Estimate limitation\./);
});

test('labels a long context base-rate amount as reference while withholding an exact estimate', () => {
  const context = createEvidenceWorkspace('codex-skills-long-context-estimate-');
  const operationId = '20260730T123000.000000Z-long-context';
  writeEvidenceArchive({
    archive: context.archive,
    reports: [
      {
        operation: {
          id: operationId,
          type: 'run',
          status: 'PASS',
        },
        usage: {
          input_tokens: 400_000,
          cached_input_tokens: 300_000,
          output_tokens: 10_000,
          reasoning_output_tokens: 2_000,
          total_tokens: 410_000,
          complete: true,
          reasoning_output_tokens_complete: true,
          events: [],
          event_count: 0,
          events_complete: true,
        },
        api_reference_estimate: {
          available: false,
          status: 'indeterminate-long-context',
          currency: 'USD',
          amount: null,
          base_rate_amount: 1.884085,
          actual_charge: false,
          billing_mode: 'chatgpt-plan',
          calculation: null,
          long_context_assessment: {
            input_token_threshold: 272_000,
            applies_per: 'request',
            triggering_event_sequences: [1],
            observed_event_scopes: ['turn'],
          },
          limitations: ['The exact multiplier cannot be audited.'],
        },
        observations: [],
      },
    ],
  });

  generateEvidenceModel(context);
  const reportPage = readFileSync(join(context.output, 'evaluations', 'example-skill', `${operationId}.md`), 'utf8');

  assert.match(reportPage, /Base-rate reference[\s\S]*USD 1\.884085/);
  assert.match(reportPage, /Exact estimate unavailable\./);
  assert.match(reportPage, /request-level long-context multiplier/);
  assert.match(reportPage, /Triggering event sequences[\s\S]*1/);
  assert.match(reportPage, /Observed event scopes[\s\S]*turn/);
  assert.doesNotMatch(reportPage, /<span class="label">Exact estimate<\/span><strong>USD/);
});

test('explains when an archived API reference estimate is unavailable', () => {
  const context = createEvidenceWorkspace('codex-skills-unavailable-estimate-');
  const operationId = '20260730T124000.000000Z-unavailable-estimate';
  writeEvidenceArchive({
    archive: context.archive,
    reports: [
      {
        operation: {
          id: operationId,
          type: 'run',
          status: 'ERROR',
        },
        usage: {
          input_tokens: null,
          cached_input_tokens: null,
          output_tokens: null,
          reasoning_output_tokens: null,
          total_tokens: null,
          complete: false,
          reasoning_output_tokens_complete: false,
          events: [],
          event_count: 0,
          events_complete: false,
        },
        api_reference_estimate: {
          available: false,
          status: 'unavailable',
          currency: 'USD',
          amount: null,
          base_rate_amount: null,
          actual_charge: false,
          billing_mode: 'chatgpt-plan-or-unknown',
          calculation: null,
          long_context_assessment: null,
          limitations: ['Observed token usage is incomplete.'],
        },
        observations: [],
      },
    ],
  });

  generateEvidenceModel(context);
  const reportPage = readFileSync(join(context.output, 'evaluations', 'example-skill', `${operationId}.md`), 'utf8');

  assert.match(reportPage, /Status[\s\S]*Unavailable/);
  assert.match(reportPage, /Reference value[\s\S]*Not recorded/);
  assert.match(reportPage, /No exact or base-rate value is available from this report\./);
  assert.match(reportPage, /Observed token usage is incomplete\./);
  assert.doesNotMatch(reportPage, /USD 0(?:\\.0+)?/);
});

test('does not infer missing token or estimate fields for a legacy report', () => {
  const context = createEvidenceWorkspace('codex-skills-legacy-telemetry-');
  const operationId = '20260730T125000.000000Z-legacy-telemetry';
  writeEvidenceArchive({
    archive: context.archive,
    reports: [
      {
        operation: {
          id: operationId,
          type: 'run',
          status: 'PASS',
        },
        usage: {
          total_tokens: 42,
          events: [
            {
              input_tokens: 40,
              output_tokens: 2,
            },
          ],
        },
        observations: [],
      },
    ],
  });

  generateEvidenceModel(context);
  const reportPage = readFileSync(join(context.output, 'evaluations', 'example-skill', `${operationId}.md`), 'utf8');

  assert.match(reportPage, /Input tokens<\/span><strong>Not recorded/);
  assert.match(reportPage, /Cached input tokens<\/span><strong>Not recorded/);
  assert.match(reportPage, /Output tokens<\/span><strong>Not recorded/);
  assert.match(reportPage, /Reasoning output tokens<\/span><strong>Not recorded/);
  assert.match(reportPage, /Total tokens<\/span><strong>42/);
  assert.match(reportPage, /Usage events<\/span><strong>Not recorded/);
  assert.match(reportPage, /Normalized usage events \(Not recorded\)/);
  assert.match(reportPage, /API reference estimate[\s\S]*Not recorded/);
  assert.match(reportPage, /The website does not calculate one\./);
  assert.doesNotMatch(reportPage, /Input tokens<\/span><strong>40/);
  assert.doesNotMatch(reportPage, /Output tokens<\/span><strong>2/);
});

test('identifies an eligible passing promotion for the current candidate source', () => {
  const context = createEvidenceWorkspace();
  const currentFingerprint = runnerFingerprint(context.skill);
  const promotionId = '20260729T200000.000000Z-promotion';

  writeEvidenceArchive({
    archive: context.archive,
    reports: [
      {
        operation: {
          id: promotionId,
          type: 'validate-change',
          status: 'PASS',
          workflow: 'promotion',
          promotion_eligible: true,
        },
        fingerprints: {
          sources: {
            baseline: 'baseline-does-not-establish-current-evidence',
            candidate: currentFingerprint,
          },
        },
        duration_ms: 125_000,
        runtime: { complete: true },
        sessions: {
          executed: {
            executor: 4,
            judge: 3,
            total: 7,
          },
        },
        usage: {
          input_tokens: 333_333,
          total_tokens: 345_678,
          cached_input_tokens: 234_567,
          output_tokens: 12_345,
          reasoning_output_tokens: 4_321,
          complete: true,
          reasoning_output_tokens_complete: true,
          event_count: 7,
          events_complete: true,
        },
        api_reference_estimate: {
          available: true,
          status: 'complete',
          currency: 'USD',
          amount: 1.234567,
          base_rate_amount: 1.234567,
        },
        observations: [
          { case_id: 'first-case', status: 'FAIL', role: 'baseline' },
          { case_id: 'first-case', status: 'PASS', role: 'candidate' },
        ],
      },
    ],
  });

  const skill = generateEvidenceModel(context).skills[0];

  assert.equal(skill.evidence.key, 'promotion');
  assert.equal(skill.evidence.label, 'Validated promotion');
  assert.equal(skill.evidence.currentFingerprint, currentFingerprint);
  assert.equal(skill.evidence.promotionReport.id, promotionId);
  assert.deepEqual(skill.evidence.promotionSummary, {
    report: {
      id: promotionId,
      href: `/codex-skills/evaluations/example-skill/${promotionId}`,
    },
    sessions: {
      executor: 4,
      judge: 3,
      total: 7,
    },
    tokens: {
      input: 333_333,
      cachedInput: 234_567,
      output: 12_345,
      reasoningOutput: 4_321,
      total: 345_678,
    },
    eventCount: 7,
    durationMs: 125_000,
    apiReferenceEstimate: {
      status: 'complete',
      currency: 'USD',
      amount: 1.234567,
      baseRateAmount: 1.234567,
    },
    telemetry: {
      runtimeComplete: true,
      usageComplete: true,
      reasoningOutputTokensComplete: true,
      eventsComplete: true,
    },
  });
  assert.deepEqual(skill.evidence.currentResults, { PASS: 1 });
  assert.equal(skill.evidence.historicalReportCount, 0);
});

test('treats a promotion as historical after the skill source changes', () => {
  const context = createEvidenceWorkspace();
  const promotionFingerprint = runnerFingerprint(context.skill);
  writeEvidenceArchive({
    archive: context.archive,
    reports: [
      {
        operation: {
          id: '20260729T201000.000000Z-old-promotion',
          type: 'validate-change',
          status: 'PASS',
          promotion_eligible: true,
        },
        fingerprints: { sources: { baseline: 'old-baseline', candidate: promotionFingerprint } },
        observations: [{ case_id: 'first-case', status: 'PASS', role: 'candidate' }],
      },
    ],
  });
  writeFileSync(join(context.skill, 'new-guidance.md'), 'The source changed after promotion.\n');

  const evidence = generateEvidenceModel(context).skills[0].evidence;

  assert.equal(evidence.key, 'historical');
  assert.notEqual(evidence.currentFingerprint, promotionFingerprint);
  assert.equal(evidence.promotionReport, null);
  assert.equal(evidence.promotionSummary, null);
  assert.equal(evidence.historicalReportCount, 1);
});

test('preserves missing promotion effort as unrecorded telemetry', () => {
  const context = createEvidenceWorkspace();
  const currentFingerprint = runnerFingerprint(context.skill);
  const promotionId = '20260729T201500.000000Z-missing-telemetry';
  writeEvidenceArchive({
    archive: context.archive,
    reports: [
      {
        operation: {
          id: promotionId,
          type: 'validate-change',
          status: 'PASS',
          promotion_eligible: true,
        },
        fingerprints: { sources: { baseline: 'baseline', candidate: currentFingerprint } },
        observations: [{ case_id: 'first-case', status: 'PASS', role: 'candidate' }],
      },
    ],
  });

  const evidence = generateEvidenceModel(context).skills[0].evidence;

  assert.deepEqual(evidence.promotionSummary, {
    report: {
      id: promotionId,
      href: `/codex-skills/evaluations/example-skill/${promotionId}`,
    },
    sessions: {
      executor: null,
      judge: null,
      total: null,
    },
    tokens: {
      input: null,
      cachedInput: null,
      output: null,
      reasoningOutput: null,
      total: null,
    },
    eventCount: null,
    durationMs: null,
    apiReferenceEstimate: {
      status: null,
      currency: null,
      amount: null,
      baseRateAmount: null,
    },
    telemetry: {
      runtimeComplete: null,
      usageComplete: null,
      reasoningOutputTokensComplete: null,
      eventsComplete: null,
    },
  });
});

test('does not infer session roles from a legacy total', () => {
  const context = createEvidenceWorkspace();
  const currentFingerprint = runnerFingerprint(context.skill);
  writeEvidenceArchive({
    archive: context.archive,
    reports: [
      {
        operation: {
          id: '20260729T201600.000000Z-legacy-sessions',
          type: 'validate-change',
          status: 'PASS',
          promotion_eligible: true,
        },
        fingerprints: { sources: { baseline: 'baseline', candidate: currentFingerprint } },
        sessions: { executed: 4 },
        observations: [{ case_id: 'first-case', status: 'PASS', role: 'candidate' }],
      },
    ],
  });

  const sessions = generateEvidenceModel(context).skills[0].evidence.promotionSummary.sessions;

  assert.deepEqual(sessions, {
    executor: null,
    judge: null,
    total: 4,
  });
});

test('never treats a matching baseline as evidence for the current source', () => {
  const context = createEvidenceWorkspace();
  const currentFingerprint = runnerFingerprint(context.skill);
  writeEvidenceArchive({
    archive: context.archive,
    reports: [
      {
        operation: {
          id: '20260729T202000.000000Z-baseline-only',
          type: 'validate-change',
          status: 'PASS',
          promotion_eligible: true,
        },
        fingerprints: { sources: { baseline: currentFingerprint, candidate: 'different-candidate' } },
        observations: [{ case_id: 'first-case', status: 'PASS', role: 'baseline' }],
      },
    ],
  });

  const evidence = generateEvidenceModel(context).skills[0].evidence;

  assert.equal(evidence.key, 'historical');
  assert.deepEqual(evidence.currentResults, {});
  assert.deepEqual(evidence.coveredCases, []);
});

test('combines current passing cases across operations into complete suite coverage', () => {
  const context = createEvidenceWorkspace();
  const currentFingerprint = runnerFingerprint(context.skill);
  writeEvidenceArchive({
    archive: context.archive,
    reports: [
      {
        operation: { id: '20260729T203000.000000Z-first', type: 'run', status: 'PASS' },
        fingerprints: { sources: { evaluated: currentFingerprint } },
        observations: [{ case_id: 'first-case', status: 'PASS', role: 'observation' }],
      },
      {
        operation: { id: '20260729T204000.000000Z-second', type: 'run', status: 'FAIL' },
        fingerprints: { sources: { evaluated: currentFingerprint } },
        observations: [
          { case_id: 'second-case', status: 'PASS', role: 'observation' },
          { case_id: 'first-case', status: 'FAIL', role: 'observation' },
        ],
      },
    ],
  });

  const evidence = generateEvidenceModel(context).skills[0].evidence;

  assert.equal(evidence.key, 'complete');
  assert.equal(evidence.label, 'Complete current coverage');
  assert.equal(evidence.promotionSummary, null);
  assert.deepEqual(evidence.coveredCases, ['first-case', 'second-case']);
  assert.equal(evidence.coveredCaseCount, 2);
  assert.equal(evidence.suiteCaseCount, 2);
  assert.deepEqual(evidence.currentResults, { FAIL: 1, PASS: 1 });
});

test('limits a current pass without complete declared coverage to partial coverage', () => {
  const context = createEvidenceWorkspace();
  const currentFingerprint = runnerFingerprint(context.skill);
  writeEvidenceArchive({
    archive: context.archive,
    reports: [
      {
        operation: { id: '20260729T205000.000000Z-partial', type: 'run', status: 'PASS' },
        fingerprints: { sources: { evaluated: currentFingerprint } },
        observations: [{ case_id: 'first-case', status: 'PASS', role: 'observation' }],
      },
    ],
  });

  const evidence = generateEvidenceModel(context).skills[0].evidence;

  assert.equal(evidence.key, 'partial');
  assert.equal(evidence.coveredCaseCount, 1);
  assert.equal(evidence.suiteCaseCount, 2);
});

test('limits a current pass without a declared suite to partial coverage', () => {
  const context = createEvidenceWorkspace();
  rmSync(join(context.skill, 'evals', 'suite.json'));
  const currentFingerprint = runnerFingerprint(context.skill);
  writeEvidenceArchive({
    archive: context.archive,
    reports: [
      {
        operation: { id: '20260729T206000.000000Z-no-suite', type: 'run', status: 'PASS' },
        fingerprints: { sources: { evaluated: currentFingerprint } },
        observations: [{ case_id: 'unlisted-case', status: 'PASS', role: 'observation' }],
      },
    ],
  });

  const evidence = generateEvidenceModel(context).skills[0].evidence;

  assert.equal(evidence.key, 'partial');
  assert.equal(evidence.suiteCases, null);
  assert.equal(evidence.suiteCaseCount, null);
});

test('distinguishes current reports without a pass from historical and absent evidence', () => {
  const context = createEvidenceWorkspace();
  const currentFingerprint = runnerFingerprint(context.skill);
  writeEvidenceArchive({
    archive: context.archive,
    reports: [
      {
        operation: { id: '20260729T207000.000000Z-error', type: 'run', status: 'ERROR' },
        fingerprints: { sources: { evaluated: currentFingerprint } },
        observations: [{ case_id: 'first-case', status: 'ERROR', role: 'observation' }],
      },
    ],
  });

  const evidence = generateEvidenceModel(context).skills[0].evidence;

  assert.equal(evidence.key, 'no-current-pass');
  assert.equal(evidence.label, 'No current pass');
  assert.deepEqual(evidence.currentResults, { ERROR: 1 });
  assert.equal(evidence.historicalReportCount, 0);
});

test('keeps reports without a comparable fingerprint as historical', () => {
  const context = createEvidenceWorkspace();
  writeEvidenceArchive({
    archive: context.archive,
    reports: [
      {
        operation: { id: '20260729T208000.000000Z-no-fingerprint', type: 'run', status: 'PASS' },
        observations: [{ case_id: 'first-case', status: 'PASS', role: 'observation' }],
      },
    ],
  });

  const evidence = generateEvidenceModel(context).skills[0].evidence;

  assert.equal(evidence.key, 'historical');
  assert.deepEqual(evidence.currentResults, {});
  assert.equal(evidence.historicalReportCount, 1);
});

test('identifies a skill with no archived reports as not evaluated yet', () => {
  const context = createEvidenceWorkspace();
  writeEvidenceArchive({ archive: context.archive, reports: [] });

  const evidence = generateEvidenceModel(context).skills[0].evidence;

  assert.equal(evidence.key, 'no-evaluation');
  assert.equal(evidence.label, 'No evaluation yet');
  assert.equal(evidence.historicalReportCount, 0);
});

test('gives current promotion precedence without hiding conflicting current results', () => {
  const context = createEvidenceWorkspace();
  const currentFingerprint = runnerFingerprint(context.skill);
  writeEvidenceArchive({
    archive: context.archive,
    reports: [
      {
        operation: {
          id: '20260729T209000.000000Z-promotion',
          type: 'validate-change',
          status: 'PASS',
          promotion_eligible: true,
        },
        fingerprints: { sources: { baseline: 'baseline', candidate: currentFingerprint } },
        observations: [{ case_id: 'first-case', status: 'PASS', role: 'candidate' }],
      },
      {
        operation: { id: '20260729T210000.000000Z-conflict', type: 'run', status: 'UNSTABLE' },
        fingerprints: { sources: { evaluated: currentFingerprint } },
        observations: [{ case_id: 'second-case', status: 'FAIL', role: 'observation' }],
      },
    ],
  });

  const evidence = generateEvidenceModel(context).skills[0].evidence;

  assert.equal(evidence.key, 'promotion');
  assert.deepEqual(evidence.currentResults, { PASS: 1, UNSTABLE: 1 });
  assert.equal(evidence.currentReports.length, 2);
  assert.equal(evidence.currentReportGroups.PASS[0].id, '20260729T209000.000000Z-promotion');
  assert.equal(evidence.currentReportGroups.UNSTABLE[0].id, '20260729T210000.000000Z-conflict');
});

test('matches the runner fingerprint contract and expected real catalog states', () => {
  const output = mkdtempSync(join(tmpdir(), 'codex-skills-real-evidence-'));
  const repository = join(websiteDirectory, '..');
  const archive = join(repository, 'evaluation-reports');
  const model = generateEvidenceModel({ repository, archive, output });
  const bySlug = Object.fromEntries(model.skills.map(skill => [skill.slug, skill]));

  for (const slug of ['execplan-tdd', 'implement-execplan', 'restructure-documentation', 'refactor-design', 'develop-skill-with-evals']) {
    assert.equal(bySlug[slug].evidence.currentFingerprint, runnerFingerprint(join(repository, slug)));
  }
  assert.equal(bySlug['execplan-tdd'].evidence.key, 'promotion');
  assert.equal(bySlug['implement-execplan'].evidence.key, 'promotion');
  assert.equal(bySlug['restructure-documentation'].evidence.key, 'promotion');
  assert.equal(bySlug['refactor-design'].evidence.key, 'partial');
  assert.equal(bySlug['refactor-design'].evidence.coveredCaseCount, 3);
  assert.equal(bySlug['refactor-design'].evidence.suiteCaseCount, 12);
  assert.equal(bySlug['develop-skill-with-evals'].evidence.key, 'historical');
});

test('matches the runner fingerprint contract for a linked skill file', () => {
  const context = createEvidenceWorkspace('codex-skills-linked-fingerprint-');
  writeFileSync(join(context.workspace, 'shared-guidance.md'), 'Shared guidance.\n');
  symlinkSync(join(context.workspace, 'shared-guidance.md'), join(context.skill, 'linked-guidance.md'));
  writeEvidenceArchive({ archive: context.archive, reports: [] });

  const evidence = generateEvidenceModel(context).skills[0].evidence;

  assert.equal(evidence.currentFingerprint, runnerFingerprint(context.skill));
});

test('matches the runner Unicode path ordering in the fingerprint contract', () => {
  const context = createEvidenceWorkspace('codex-skills-unicode-fingerprint-');
  writeFileSync(join(context.skill, '\u{e000}.md'), 'Basic multilingual plane.\n');
  writeFileSync(join(context.skill, '\u{1f600}.md'), 'Astral plane.\n');
  writeEvidenceArchive({ archive: context.archive, reports: [] });

  const evidence = generateEvidenceModel(context).skills[0].evidence;

  assert.equal(evidence.currentFingerprint, runnerFingerprint(context.skill));
});
