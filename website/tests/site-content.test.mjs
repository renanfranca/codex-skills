import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { mkdtempSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
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
        },
        sessions: { executed: 1 },
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
  assert.match(reportPage, /The observable behavior matched the contract\./);
  assert.match(reportPage, /--- a\/example\.py\n\+\+\+ b\/example\.py/);
  assert.match(reportPage, /Code fragments/);
  assert.match(reportPage, /print\("before"\)/);
  assert.match(reportPage, /print\("after"\)/);
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
        failure_category: 'runtime_configuration',
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
  assert.match(reportPage, /Failure category[\s\S]*runtime_configuration/);
  assert.match(reportPage, /The executor did not start\./);
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

  assert.match(homePage, /Codex Skills/);
  assert.match(homePage, /44 archived operations/);
  assert.match(homePage, /href="\/codex-skills\/skills\/"/);
  assert.match(homePage, /href="\/codex-skills\/evaluations\/"/);
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

  assert.equal(model.skills.length, 9);
  assert.equal(
    model.skills.some(skill => skill.slug === 'tdd-strict-autonomous'),
    false,
  );
  assert.equal(
    model.skills.some(skill => skill.slug === 'tdd-strict-cycle-confirmation'),
    false,
  );
});
