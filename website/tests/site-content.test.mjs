import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { mkdtempSync, mkdirSync, readFileSync, rmSync, symlinkSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import test from 'node:test';

const websiteDirectory = join(dirname(fileURLToPath(import.meta.url)), '..');

test('publishes every active evaluation including cases without archived observations', () => {
  const workspace = mkdtempSync(join(tmpdir(), 'codex-skills-evaluation-catalog-'));
  const repository = join(workspace, 'repository');
  const archive = join(repository, 'evaluation-reports');
  const skill = join(repository, 'example-skill');
  const output = join(workspace, 'generated');

  mkdirSync(join(skill, 'evals', 'cases', 'semantic-case', 'fixture'), { recursive: true });
  mkdirSync(join(skill, 'evals', 'cases', 'deterministic-case'), { recursive: true });
  mkdirSync(join(skill, 'evals', 'cases', 'executor-case'), { recursive: true });
  mkdirSync(archive, { recursive: true });
  writeFileSync(join(skill, 'SKILL.md'), '---\nname: example-skill\ndescription: Publish declared evaluations.\n---\n');
  writeFileSync(
    join(skill, 'evals', 'suite.json'),
    `${JSON.stringify({ version: 1, cases: ['semantic-case', 'deterministic-case', 'executor-case'] }, null, 2)}\n`,
  );
  writeFileSync(
    join(skill, 'evals', 'cases', 'semantic-case', 'case.json'),
    `${JSON.stringify(
      {
        id: 'semantic-case',
        kind: 'behavioral',
        prompt_file: 'prompt.md',
        mechanical: {
          expected_exit_code: 0,
          required_paths: ['result.txt'],
          forbidden_changed_paths: ['private/**'],
          commands: [{ argv: ['python3', '-m', 'unittest'], exit_code: 0 }],
        },
        oracle: { commands: [{ argv: ['python3', '{oracle_dir}/check.py'], exit_code: 0 }] },
        judge: { enabled: true, criteria: ['The result is useful.'], no_action_acceptable: true },
      },
      null,
      2,
    )}\n`,
  );
  writeFileSync(join(skill, 'evals', 'cases', 'semantic-case', 'prompt.md'), 'Create a useful result.\n');
  writeFileSync(join(skill, 'evals', 'cases', 'semantic-case', 'fixture', 'input.txt'), 'public input\n');
  writeFileSync(
    join(skill, 'evals', 'cases', 'deterministic-case', 'case.json'),
    `${JSON.stringify(
      {
        id: 'deterministic-case',
        kind: 'deterministic',
        mechanical: { commands: [{ argv: ['python3', 'check.py'], exit_code: 0 }] },
        judge: { enabled: false, criteria: [] },
      },
      null,
      2,
    )}\n`,
  );
  writeFileSync(
    join(skill, 'evals', 'cases', 'executor-case', 'case.json'),
    `${JSON.stringify(
      {
        id: 'executor-case',
        kind: 'trigger',
        prompt_file: 'prompt.md',
        mechanical: { expected_exit_code: 0 },
        judge: { enabled: false, criteria: [] },
      },
      null,
      2,
    )}\n`,
  );
  writeFileSync(join(skill, 'evals', 'cases', 'executor-case', 'prompt.md'), 'Choose the matching skill.\n');
  writeFileSync(join(archive, 'manifest.json'), '{"version":1,"report_count":0,"reports":[]}\n');

  execFileSync(
    process.execPath,
    [join(websiteDirectory, 'scripts', 'generate-content.mjs'), '--repository-root', repository, '--archive', archive, '--output', output],
    { stdio: 'pipe' },
  );

  const skillModel = JSON.parse(readFileSync(join(output, 'data.json'), 'utf8')).skills[0];
  const semanticPage = readFileSync(join(output, 'skills', 'example-skill', 'evaluations', 'semantic-case.md'), 'utf8');
  const deterministicPage = readFileSync(join(output, 'skills', 'example-skill', 'evaluations', 'deterministic-case.md'), 'utf8');
  const executorPage = readFileSync(join(output, 'skills', 'example-skill', 'evaluations', 'executor-case.md'), 'utf8');

  assert.deepEqual(
    skillModel.evaluations.map(evaluation => [evaluation.caseId, evaluation.kind, evaluation.evidence.label]),
    [
      ['semantic-case', 'behavioral', 'Not evaluated yet'],
      ['deterministic-case', 'deterministic', 'Not evaluated yet'],
      ['executor-case', 'trigger', 'Not evaluated yet'],
    ],
  );
  assert.equal(skillModel.evaluations[0].prompt, 'Create a useful result.\n');
  assert.deepEqual(skillModel.evaluations[0].fixturePaths, ['fixture/input.txt']);
  assert.equal(skillModel.evaluations[0].mechanical.expectedExitCode, 0);
  assert.deepEqual(skillModel.evaluations[0].mechanical.requiredPaths, ['result.txt']);
  assert.deepEqual(skillModel.evaluations[0].mechanical.protectedChangedPaths, ['private/**']);
  assert.equal(skillModel.evaluations[0].oracle.applicable, true);
  assert.equal(skillModel.evaluations[0].judge.applicable, true);
  assert.equal(skillModel.evaluations[1].prompt, null);
  assert.equal(skillModel.evaluations[1].judge.applicable, false);
  assert.equal(skillModel.evaluations[2].prompt, 'Choose the matching skill.\n');
  assert.deepEqual(skillModel.evaluations[2].fixturePaths, []);
  assert.deepEqual(skillModel.historicalEvaluations, []);
  assert.match(semanticPage, /class="definition-flow definition-stepper" style="--flow-stages: 6"/);
  assert.match(deterministicPage, /class="definition-flow definition-stepper" style="--flow-stages: 3"/);
  assert.match(executorPage, /class="definition-flow definition-stepper" style="--flow-stages: 4"/);
  assert.doesNotMatch(deterministicPage, /href="#judge-verification"/);
  assert.doesNotMatch(deterministicPage, />Judge</);
  assert.match(deterministicPage, /This deterministic case does not use an executor prompt or a starting repository\./);
  assert.match(deterministicPage, /## Oracle verification[\s\S]*Not used in this case/);
  assert.match(deterministicPage, /## Judge verification[\s\S]*Not used in this case/);
  assert.match(
    semanticPage,
    /repository-controlled code kept outside the workspace visible to the executor[\s\S]*another process against the workspace left by the executor/,
  );
  assert.match(semanticPage, /Oracle process[\s\S]*python3 \{oracle_dir\}\/check\.py/);
  assert.match(semanticPage, /The judge may accept a response without workspace changes when the declared criteria are satisfied\./);
  assert.match(executorPage, /## Prompt\n/);
  assert.doesNotMatch(executorPage, /Prompt and starting repository|Starting repository files/);
  assert.match(deterministicPage, /Case decision[\s\S]*PASS[\s\S]*FAIL/);
  assert.doesNotMatch(deterministicPage, /<span>ERROR<\/span>|<span>INCONCLUSIVE<\/span>|<span>SKIPPED<\/span>/);
  assert.match(executorPage, /Case decision[\s\S]*PASS[\s\S]*FAIL[\s\S]*ERROR/);
  assert.doesNotMatch(executorPage, /<span>INCONCLUSIVE<\/span>|<span>SKIPPED<\/span>/);
  assert.match(semanticPage, /Case decision[\s\S]*PASS[\s\S]*FAIL[\s\S]*ERROR[\s\S]*INCONCLUSIVE/);
  assert.doesNotMatch(semanticPage, /<span>SKIPPED<\/span>/);
  assert.match(semanticPage, /SKIPPED<\/code> is a possible judge state after an earlier failure, not a final observation result\./);
  assert.match(semanticPage, /<EvaluationHelp context="evaluation" field="kind" current="behavioral"/);
  assert.match(semanticPage, /<strong>Behavioral<\/strong> <code>behavioral<\/code>[\s\S]*user visible or public contract behavior/);
  assert.match(semanticPage, /<strong>Nonbehavioral<\/strong> <code>non_behavioral<\/code>[\s\S]*does not require semantic task execution/);
  assert.match(semanticPage, /<strong>Trigger<\/strong> <code>trigger<\/code>[\s\S]*selected and invoked appropriately/);
  assert.match(semanticPage, /<strong>Deterministic<\/strong> <code>deterministic<\/code>[\s\S]*zero model sessions/);
  assert.match(semanticPage, /Executor process[\s\S]*Expected exit: 0/);
  assert.doesNotMatch(deterministicPage, /Executor process/);
});

test('renders an active evaluation card and a linked current-definition page', () => {
  const workspace = mkdtempSync(join(tmpdir(), 'codex-skills-evaluation-page-'));
  const repository = join(workspace, 'repository');
  const archive = join(repository, 'evaluation-reports');
  const caseRoot = join(repository, 'example-skill', 'evals', 'cases', 'safe-case');
  const output = join(workspace, 'generated');

  mkdirSync(join(caseRoot, 'fixture'), { recursive: true });
  mkdirSync(archive, { recursive: true });
  writeFileSync(
    join(repository, 'example-skill', 'SKILL.md'),
    '---\nname: example-skill\ndescription: Explain declared evaluations.\n---\n',
  );
  writeFileSync(
    join(repository, 'example-skill', 'evals', 'suite.json'),
    `${JSON.stringify({ version: 1, cases: ['safe-case'] }, null, 2)}\n`,
  );
  writeFileSync(
    join(caseRoot, 'case.json'),
    `${JSON.stringify(
      {
        id: 'safe-case',
        kind: 'behavioral',
        prompt_file: 'prompt.md',
        mechanical: {
          expected_exit_code: 0,
          required_paths: ['result.txt'],
          commands: [{ argv: ['python3', 'check.py'], exit_code: 1 }],
        },
        oracle: { commands: [{ argv: ['python3', '{oracle_dir}/check.py'], exit_code: 0 }] },
        judge: { enabled: true, criteria: ['Reject <script>alert(1)</script>.'], no_action_acceptable: false },
      },
      null,
      2,
    )}\n`,
  );
  writeFileSync(join(caseRoot, 'prompt.md'), 'Treat <img src=x onerror=alert(1)> as text.\n');
  writeFileSync(join(caseRoot, 'fixture', 'input.txt'), 'input\n');
  writeFileSync(join(archive, 'manifest.json'), '{"version":1,"report_count":0,"reports":[]}\n');

  execFileSync(
    process.execPath,
    [join(websiteDirectory, 'scripts', 'generate-content.mjs'), '--repository-root', repository, '--archive', archive, '--output', output],
    { stdio: 'pipe' },
  );

  const skillPage = readFileSync(join(output, 'skills', 'example-skill.md'), 'utf8');
  const evaluationPage = readFileSync(join(output, 'skills', 'example-skill', 'evaluations', 'safe-case.md'), 'utf8');

  assert.match(skillPage, /## Active evaluations/);
  assert.match(skillPage, /Each card links a current case definition to its current evidence and recorded operation history\./);
  assert.match(skillPage, /href="\/codex-skills\/skills\/example-skill\/evaluations\/safe-case"/);
  assert.match(skillPage, /Safe case[\s\S]*Not evaluated yet[\s\S]*Behavioral/);
  assert.match(skillPage, /id="operation-history"/);
  assert.match(skillPage, /id="evaluation-history"/);
  assert.match(evaluationPage, /# Safe case/);
  assert.match(
    evaluationPage,
    /An evaluation is the persistent case definition\. An observation is one case result recorded inside an operation, and an operation is the complete runner invocation\./,
  );
  assert.match(evaluationPage, /<EvaluationHelp context="evaluation" field="currentEvidence"/);
  assert.match(evaluationPage, /<EvaluationHelp context="evaluation" field="latestRecordedResult"/);
  assert.match(evaluationPage, /<EvaluationHelp context="evaluation" field="suiteState"/);
  assert.match(evaluationPage, /field="currentEvidence" current="Not evaluated yet"/);
  assert.doesNotMatch(evaluationPage, /Skill contracts mapped to this case/);
  assert.doesNotMatch(evaluationPage, /Rubric families sampled by this case/);
  assert.doesNotMatch(evaluationPage, /coverage map|traceability manifest/i);
  assert.match(evaluationPage, /## How this evaluation runs/);
  assert.match(
    evaluationPage,
    /Follow the current evaluation from its public input through each declared verification mechanism to its possible result\./,
  );
  assert.match(evaluationPage, /class="definition-flow definition-stepper" style="--flow-stages: 6"/);
  assert.doesNotMatch(evaluationPage, /class="[^"]*evaluation-flow[^"]*definition-flow/);
  assert.equal((evaluationPage.match(/class="definition-step(?: definition-step-result)?"/g) ?? []).length, 6);
  assert.equal((evaluationPage.match(/class="definition-step-node" aria-hidden="true"/g) ?? []).length, 6);
  assert.match(evaluationPage, /href="#public-input"/);
  assert.match(evaluationPage, /Prompt and starting repository[\s\S]*Prompt and initial workspace copied for the executor/);
  assert.match(evaluationPage, /Executor[\s\S]*Isolated model invocation/);
  assert.match(evaluationPage, /href="#mechanical-checks"/);
  assert.match(evaluationPage, /Runner checks[\s\S]*Automatic and case-declared checks/);
  assert.match(evaluationPage, /href="#oracle-verification"/);
  assert.match(evaluationPage, /Oracle[\s\S]*Independent checks outside the executor workspace/);
  assert.match(evaluationPage, /href="#judge-verification"/);
  assert.match(evaluationPage, /Judge[\s\S]*Semantic evaluation in a separate model invocation/);
  assert.match(evaluationPage, /class="definition-step definition-step-result"/);
  assert.match(evaluationPage, /Case decision[\s\S]*PASS[\s\S]*FAIL[\s\S]*ERROR[\s\S]*INCONCLUSIVE/);
  assert.doesNotMatch(evaluationPage, /<span>SKIPPED<\/span>/);
  assert.match(evaluationPage, /## Prompt and starting repository/);
  assert.match(
    evaluationPage,
    /The fixture is the starting repository copied into the disposable executor workspace\. It is input to the evaluation, not an evaluation result\./,
  );
  assert.match(evaluationPage, /Treat <img src=x onerror=alert\(1\)> as text\./);
  assert.doesNotMatch(evaluationPage, /<script>alert\(1\)<\/script>/);
  assert.match(evaluationPage, /&lt;script&gt;alert\(1\)&lt;\/script&gt;/);
  assert.match(evaluationPage, /## Runner checks/);
  assert.match(evaluationPage, /Automatic runner checks/);
  assert.match(evaluationPage, /Executor process[\s\S]*Expected exit: 0/);
  assert.match(evaluationPage, /Structured executor response/);
  assert.match(evaluationPage, /Evaluated skill integrity/);
  assert.match(evaluationPage, /Case-declared requirements/);
  assert.match(evaluationPage, /Required paths[\s\S]*result\.txt/);
  assert.match(evaluationPage, /Workspace checks[\s\S]*Workspace check[\s\S]*python3 check\.py[\s\S]*Expected exit: 1/);
  assert.match(evaluationPage, /Exit code 1 is the success condition for this command\./);
  assert.match(evaluationPage, /The oracle is repository-controlled code kept outside the workspace visible to the executor/);
  assert.match(evaluationPage, /Judge verification applies the declared semantic criteria after earlier checks allow it to run\./);
  assert.match(
    evaluationPage,
    /A response without workspace changes is not sufficient by itself; the declared criteria still determine the verdict\./,
  );
  assert.doesNotMatch(evaluationPage, /No action acceptable:[\s\S]*(?:true|false)/);
  assert.doesNotMatch(evaluationPage, /The latest operation is the newest archived runner invocation related to this case/);
  assert.match(evaluationPage, /Operation history lists complete runner invocations that contain observations for this case/);
});

test('ignores a coverage manifest when publishing executable suite evidence', () => {
  const workspace = mkdtempSync(join(tmpdir(), 'codex-skills-evaluation-coverage-'));
  const repository = join(workspace, 'repository');
  const archive = join(repository, 'evaluation-reports');
  const skill = join(repository, 'example-skill');
  const caseRoot = join(skill, 'evals', 'cases', 'mapped-case');
  const output = join(workspace, 'generated');

  mkdirSync(caseRoot, { recursive: true });
  mkdirSync(archive, { recursive: true });
  writeFileSync(join(skill, 'SKILL.md'), '---\nname: example-skill\ndescription: Explain coverage declarations.\n---\n');
  writeFileSync(join(skill, 'evals', 'suite.json'), `${JSON.stringify({ version: 1, cases: ['mapped-case'] }, null, 2)}\n`);
  writeFileSync(
    join(caseRoot, 'case.json'),
    `${JSON.stringify(
      {
        id: 'mapped-case',
        kind: 'deterministic',
        mechanical: { commands: [{ argv: ['python3', 'check.py'], exit_code: 0 }] },
        judge: { enabled: false, criteria: [] },
      },
      null,
      2,
    )}\n`,
  );
  writeFileSync(
    join(skill, 'evals', 'coverage.json'),
    `${JSON.stringify(
      {
        version: 1,
        contracts: [
          {
            id: 'complete-contract',
            statement: 'Protect the complete public contract.',
            guarantee: 'complete',
            mappings: [{ case_id: 'mapped-case', dimension: 'public-result', evidence: ['mechanical', 'oracle'] }],
          },
          {
            id: 'partial-contract',
            statement: 'Sample a context-sensitive contract.',
            guarantee: 'partial',
            limitation: 'The fixture samples one supported context.',
            mappings: [{ case_id: 'mapped-case', dimension: 'context-sample', evidence: ['judge', 'executor_response'] }],
          },
        ],
        rubric_families: [
          {
            id: 'safe-boundaries',
            source: 'references/rubric.md',
            guarantee: 'partial',
            limitation: 'The fixture samples one boundary.',
            sections: ['Boundary ownership'],
            mappings: [
              {
                case_id: 'mapped-case',
                dimension: 'boundary-sample',
                evidence: ['mechanical', 'changed_paths'],
              },
            ],
          },
        ],
      },
      null,
      2,
    )}\n`,
  );
  writeFileSync(join(archive, 'manifest.json'), '{"version":1,"report_count":0,"reports":[]}\n');

  execFileSync(
    process.execPath,
    [join(websiteDirectory, 'scripts', 'generate-content.mjs'), '--repository-root', repository, '--archive', archive, '--output', output],
    { stdio: 'pipe' },
  );

  const model = JSON.parse(readFileSync(join(output, 'data.json'), 'utf8'));
  const skillPage = readFileSync(join(output, 'skills', 'example-skill.md'), 'utf8');
  const evaluationPage = readFileSync(join(output, 'skills', 'example-skill', 'evaluations', 'mapped-case.md'), 'utf8');

  assert.equal(Object.hasOwn(model.skills[0], 'traceability'), false);
  assert.equal(Object.hasOwn(model.skills[0].evaluations[0], 'coverage'), false);
  assert.equal(Object.hasOwn(model.skills[0].evaluations[0], 'rubricCoverage'), false);
  assert.equal(Object.hasOwn(model.skills[0].evaluations[0], 'traceabilityDeclared'), false);
  assert.doesNotMatch(skillPage, /traceability|skill contracts|rubric famil|mapping/i);
  assert.doesNotMatch(evaluationPage, /traceability|coverage level|skill contracts|rubric famil|mapping label/i);
  assert.match(evaluationPage, /This deterministic case does not use an executor prompt or a starting repository\./);
});

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

test('generates root-relative catalog links for Netlify', () => {
  const output = mkdtempSync(join(tmpdir(), 'codex-skills-netlify-home-'));
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
    { stdio: 'pipe', env: { ...process.env, NETLIFY: 'true' } },
  );

  const homePage = readFileSync(join(output, 'index.md'), 'utf8');

  assert.match(homePage, /href="\/skills\/"/);
  assert.match(homePage, /href="\/evaluations\/"/);
  assert.doesNotMatch(homePage, /href="\/codex-skills\/skills\/"/);
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
  assert.equal(model.evaluationGlossary.evaluationPage.concepts.evaluation.label, 'Evaluation');
  assert.equal(model.evaluationGlossary.evaluationPage.concepts.observation.label, 'Observation');
  assert.equal(model.evaluationGlossary.evaluationPage.concepts.operation.label, 'Operation');
  assert.equal(Object.hasOwn(model.evaluationGlossary.evaluationPage, 'coverageLevels'), false);
  assert.equal(Object.hasOwn(model.evaluationGlossary.evaluationPage, 'evidenceMechanisms'), false);
  assert.equal(Object.hasOwn(model.evaluationGlossary.evaluationPage.fields, 'coverageLevel'), false);
  assert.equal(Object.hasOwn(model.evaluationGlossary.evaluationPage.fields, 'mappingLabel'), false);
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

  mkdirSync(join(skill, 'evals', 'cases', 'first-case'), { recursive: true });
  mkdirSync(join(skill, 'evals', 'cases', 'second-case'), { recursive: true });
  mkdirSync(archive, { recursive: true });
  writeFileSync(join(skill, 'SKILL.md'), '---\nname: example-skill\ndescription: Explain derived evidence truthfully.\n---\n');
  writeFileSync(join(skill, 'evals', 'suite.json'), `${JSON.stringify({ version: 1, cases: ['first-case', 'second-case'] }, null, 2)}\n`);
  for (const caseId of ['first-case', 'second-case']) {
    writeFileSync(
      join(skill, 'evals', 'cases', caseId, 'case.json'),
      `${JSON.stringify(
        {
          id: caseId,
          kind: 'deterministic',
          mechanical: { commands: [{ argv: ['python3', 'check.py'], exit_code: 0 }] },
          judge: { enabled: false, criteria: [] },
        },
        null,
        2,
      )}\n`,
    );
  }
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

test('publishes a documentary promotion qualification map before active evaluations', () => {
  const context = createEvidenceWorkspace('codex-skills-promotion-qualification-map-');
  writeEvidenceArchive({ archive: context.archive, reports: [] });

  generateEvidenceModel(context);
  const skillPage = readFileSync(join(context.output, 'skills', 'example-skill.md'), 'utf8');
  const mapStart = skillPage.indexOf('<section class="promotion-qualification-map"');
  const activeEvaluationsStart = skillPage.indexOf('## Active evaluations');

  assert.ok(mapStart > skillPage.indexOf('<div class="evidence-callout'));
  assert.ok(activeEvaluationsStart > mapStart);
  assert.equal((skillPage.match(/<section class="promotion-qualification-map"/g) ?? []).length, 1);
  assert.match(skillPage, /<h2 id="promotion-qualification-map">How promotion qualification works<\/h2>/);
  assert.match(
    skillPage,
    /Required evidence depends on the impact of the proposed change\. This map explains qualification; it does not track a live run\./,
  );
  assert.deepEqual(
    [
      ...skillPage.matchAll(
        /<h3>(Prepare comparable sources|Classify and plan|Run the required evidence path|Review the qualification)<\/h3>/g,
      ),
    ].map(match => match[1]),
    ['Prepare comparable sources', 'Classify and plan', 'Run the required evidence path', 'Review the qualification'],
  );
  assert.deepEqual(
    [...skillPage.matchAll(/<h4>(Static|Deterministic|Scoped|Cross-cutting)<\/h4>/g)].map(match => match[1]),
    ['Static', 'Deterministic', 'Scoped', 'Cross-cutting'],
  );
  assert.match(skillPage, /Static[\s\S]*Structural validation only[\s\S]*does not produce the <code>Validated promotion<\/code> status/);
  assert.match(
    skillPage,
    /Deterministic[\s\S]*baseline fails once[\s\S]*candidate passes three times with a stable result[\s\S]*zero model sessions/,
  );
  assert.match(
    skillPage,
    /Scoped[\s\S]*RED for affected semantic cases[\s\S]*three stable GREEN results[\s\S]*No unrelated-case regression/,
  );
  assert.match(skillPage, /Cross-cutting[\s\S]*RED and GREEN 1[\s\S]*one regression of every remaining case[\s\S]*GREEN 2 and 3/);
  assert.match(
    skillPage,
    /Any result other than <code>PASS<\/code> blocks qualification[\s\S]*current fingerprint establishes <code>Validated promotion<\/code>[\s\S]*source change makes that evidence historical/,
  );
  assert.match(
    skillPage,
    /Validated promotion means that one specific source satisfied its declared contracts\. It does not prove correctness, completeness, or deterministic model output, and it does not publish or apply the change\./,
  );
  assert.doesNotMatch(skillPage.slice(mapStart, activeEvaluationsStart), /live progress|current progress|running now/i);
});

test('derives case evidence from compatible observations while grouping each operation once', () => {
  const context = createEvidenceWorkspace('codex-skills-case-evidence-');
  const sourceFingerprint = runnerFingerprint(context.skill);
  const caseFingerprint = runnerFingerprint(join(context.skill, 'evals', 'cases', 'first-case'));
  writeEvidenceArchive({
    archive: context.archive,
    reports: [
      {
        operation: {
          id: '20260730T120000.000000Z-promotion',
          type: 'validate-change',
          status: 'PASS',
          promotion_eligible: true,
        },
        started_at: '2026-07-30T12:00:00Z',
        fingerprints: {
          sources: { baseline: 'baseline-fingerprint', candidate: sourceFingerprint },
          cases: { 'first-case': caseFingerprint },
        },
        observations: [
          { case_id: 'first-case', kind: 'deterministic', role: 'baseline', repetition: 1, status: 'FAIL' },
          { case_id: 'first-case', kind: 'deterministic', role: 'candidate', repetition: 1, status: 'PASS' },
          { case_id: 'first-case', kind: 'deterministic', role: 'candidate', repetition: 2, status: 'PASS' },
        ],
      },
      {
        operation: {
          id: '20260730T130000.000000Z-latest',
          type: 'run',
          status: 'FAIL',
          promotion_eligible: false,
        },
        started_at: '2026-07-30T13:00:00Z',
        fingerprints: {
          sources: { evaluated: sourceFingerprint },
          cases: { 'first-case': caseFingerprint },
        },
        observations: [
          { case_id: 'first-case', kind: 'deterministic', role: 'observation', repetition: 1, status: 'PASS' },
          { case_id: 'first-case', kind: 'deterministic', role: 'observation', repetition: 2, status: 'FAIL' },
        ],
      },
    ],
  });

  const evaluation = generateEvidenceModel(context).skills[0].evaluations[0];

  assert.equal(evaluation.evidence.label, 'Validated promotion');
  assert.equal(evaluation.latestRecordedResult, 'PASS: 1 · FAIL: 1');
  assert.equal(evaluation.latestOperation.id, '20260730T130000.000000Z-latest');
  assert.equal(evaluation.latestOperation.status, 'FAIL');
  assert.equal(evaluation.operations.length, 2);
  assert.deepEqual(
    evaluation.operations[1].observations.map(observation => [observation.role, observation.repetition, observation.status]),
    [
      ['baseline', 1, 'FAIL'],
      ['candidate', 1, 'PASS'],
      ['candidate', 2, 'PASS'],
    ],
  );
  const evaluationPage = readFileSync(join(context.output, 'skills', 'example-skill', 'evaluations', 'first-case.md'), 'utf8');
  assert.doesNotMatch(evaluationPage, /## Latest operation flow/);
  assert.doesNotMatch(evaluationPage, /class="evaluation-flow operation-flow"/);
  assert.match(evaluationPage, /## Operation history/);
});

test('separates archived-only case IDs as historical evaluations without inventing a current definition', () => {
  const context = createEvidenceWorkspace('codex-skills-historical-evaluation-');
  writeEvidenceArchive({
    archive: context.archive,
    reports: [
      {
        operation: { id: '20260730T140000.000000Z-historical', type: 'run', status: 'PASS' },
        started_at: '2026-07-30T14:00:00Z',
        observations: [{ case_id: 'retired-case', kind: 'behavioral', role: 'observation', status: 'PASS' }],
      },
    ],
  });

  const skill = generateEvidenceModel(context).skills[0];
  const historicalPage = readFileSync(join(context.output, 'skills', 'example-skill', 'evaluations', 'retired-case.md'), 'utf8');

  assert.equal(skill.evaluations[0].state, 'active');
  assert.equal(skill.historicalEvaluations.length, 1);
  assert.deepEqual(skill.historicalEvaluations[0], {
    skillId: 'example-skill',
    caseId: 'retired-case',
    title: 'Retired case',
    route: '/skills/example-skill/evaluations/retired-case',
    active: false,
    state: 'historical',
    latestRecordedResult: 'PASS',
    latestOperation: skill.historicalEvaluations[0].latestOperation,
    operations: skill.historicalEvaluations[0].operations,
  });
  assert.equal(Object.hasOwn(skill.historicalEvaluations[0], 'prompt'), false);
  assert.equal(Object.hasOwn(skill.historicalEvaluations[0], 'caseFingerprint'), false);
  assert.equal(Object.hasOwn(skill.historicalEvaluations[0], 'mechanical'), false);
  assert.match(
    historicalPage,
    /An evaluation is the persistent case definition\. An observation is one case result recorded inside an operation, and an operation is the complete runner invocation\./,
  );
  assert.match(historicalPage, /<EvaluationHelp context="evaluation" field="suiteState" current="Historical"/);
  assert.match(historicalPage, /<EvaluationHelp context="evaluation" field="latestRecordedResult" current="PASS"/);
  assert.match(
    historicalPage,
    /Operation history remains available because archived operations contain observations for this case\. The current suite no longer provides a definition to display\./,
  );
  assert.match(historicalPage, /This history lists complete archived runner invocations, not a reconstructed case definition\./);
});

test('publishes stable case evidence keys with candidate, regression, baseline, and fingerprint precedence', () => {
  const scenarios = [
    { role: 'candidate', caseMatches: true, expected: ['validated-promotion', 'Validated promotion'] },
    { role: 'regression', caseMatches: true, expected: ['current-pass', 'Current pass'] },
    { role: 'baseline', caseMatches: true, expected: ['no-current-pass', 'No current pass'] },
    { role: 'candidate', caseMatches: false, expected: ['historical-runs', 'Historical runs'] },
  ];
  const actual = scenarios.map(({ role, caseMatches }) => {
    const context = createEvidenceWorkspace(`codex-skills-case-state-${role}-`);
    const sourceFingerprint = runnerFingerprint(context.skill);
    const currentCaseFingerprint = runnerFingerprint(join(context.skill, 'evals', 'cases', 'first-case'));
    writeEvidenceArchive({
      archive: context.archive,
      reports: [
        {
          operation: {
            id: `20260730T150000.000000Z-${role}`,
            type: 'validate-change',
            status: 'PASS',
            promotion_eligible: true,
          },
          started_at: '2026-07-30T15:00:00Z',
          fingerprints: {
            sources: { baseline: 'baseline-fingerprint', candidate: sourceFingerprint },
            cases: { 'first-case': caseMatches ? currentCaseFingerprint : 'historical-case-fingerprint' },
          },
          observations: [{ case_id: 'first-case', kind: 'deterministic', role, repetition: 1, status: 'PASS' }],
        },
      ],
    });
    const evidence = generateEvidenceModel(context).skills[0].evaluations[0].evidence;
    return [evidence.key, evidence.label];
  });

  assert.deepEqual(
    actual,
    scenarios.map(scenario => scenario.expected),
  );
});

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
  assert.match(reportPage, /<details class="evidence-details api-reference-estimate">/);
  assert.match(reportPage, /<summary>View API reference estimate details<\/summary>/);
  assert.doesNotMatch(reportPage, /<details class="evidence-details api-reference-estimate" open>/);
  assert.match(reportPage, /USD 0\.123456/);
  assert.match(reportPage, /not an observed charge/i);
  assert.match(reportPage, /Input component[\s\S]*USD 0\.0012475/);
  assert.match(reportPage, /Input price[\s\S]*USD 2\.5 per million tokens/);
  assert.match(reportPage, /Long context threshold[\s\S]*272,000 input tokens per request/);
  assert.match(reportPage, /Estimate limitation\./);
  assert.match(reportPage, /<\/details>\n\n## Observations/);
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
  assert.doesNotMatch(reportPage, /api-reference-estimate/);
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
  assert.deepEqual(evidence.passingCases, []);
  assert.equal(Object.hasOwn(evidence, 'coveredCases'), false);
  assert.equal(Object.hasOwn(evidence, 'coveredCaseCount'), false);
});

test('combines current passing cases across operations into complete current suite evidence', () => {
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
  assert.equal(evidence.label, 'Complete current suite evidence');
  assert.equal(evidence.promotionSummary, null);
  assert.deepEqual(evidence.passingCases, ['first-case', 'second-case']);
  assert.equal(evidence.passingCaseCount, 2);
  assert.equal(evidence.suiteCaseCount, 2);
  assert.deepEqual(evidence.currentResults, { FAIL: 1, PASS: 1 });
});

test('limits a current pass without complete suite evidence to partial current suite evidence', () => {
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
  assert.equal(evidence.label, 'Partial current suite evidence');
  assert.equal(evidence.passingCaseCount, 1);
  assert.equal(evidence.suiteCaseCount, 2);
});

test('limits a current pass without a declared suite to partial current suite evidence', () => {
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
  assert.equal(bySlug['refactor-design'].evidence.key, 'historical');
  assert.equal(bySlug['refactor-design'].evidence.passingCaseCount, 0);
  assert.equal(bySlug['refactor-design'].evidence.suiteCaseCount, 11);
  assert.equal(bySlug['refactor-design'].evaluations.length, 11);
  assert.equal(
    bySlug['refactor-design'].evaluations.some(evaluation => evaluation.caseId === 'coverage-contract'),
    false,
  );
  assert.equal(
    bySlug['refactor-design'].historicalEvaluations.some(evaluation => evaluation.caseId === 'coverage-contract'),
    true,
  );
  assert.equal(Object.hasOwn(bySlug['refactor-design'], 'traceability'), false);
  const refactorSkillPage = readFileSync(join(output, 'skills', 'refactor-design.md'), 'utf8');
  assert.match(refactorSkillPage, /Historical runs/);
  assert.match(refactorSkillPage, /## Historical evaluations[\s\S]*Coverage contract/);
  assert.doesNotMatch(refactorSkillPage, /traceability|coverage level|mapping label/i);
  assert.equal(bySlug['develop-skill-with-evals'].evidence.key, 'historical');
  assert.equal(Object.hasOwn(bySlug['develop-skill-with-evals'], 'traceability'), false);
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
