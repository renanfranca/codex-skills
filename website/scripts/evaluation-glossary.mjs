const entry = (label, description, applicability = 'All evaluation reports') => Object.freeze({ label, description, applicability });

export const knownObservationRoles = Object.freeze(['baseline', 'candidate', 'regression', 'observation']);

export const evaluationGlossary = Object.freeze({
  concepts: Object.freeze({
    evidenceStatus: entry(
      'Evidence status',
      'The strength and currency of evidence for the current skill source. It is independent of operation type and recorded result.',
      'Skill catalog and skill pages',
    ),
    operationType: entry(
      'Operation type',
      'How the evidence was produced. It does not determine the result or evidence strength by itself.',
    ),
    recordedResult: entry(
      'Recorded result',
      'What happened in one operation. A result does not by itself establish current or promotion evidence.',
    ),
  }),
  runner: entry(
    'Evaluation runner',
    'The program run_skill_evals.py that coordinates gates, isolated workspaces, the executor, the judge, deterministic checks, and report archiving.',
  ),
  evidenceStatuses: Object.freeze({
    promotion: Object.freeze({
      ...entry(
        'Validated promotion',
        'A current qualification records valid RED, three stable GREEN results per affected case, and proportional regression when required.',
        'Current skill evidence',
      ),
      qualificationGates: Object.freeze([
        'Valid RED',
        'Three stable GREEN results per affected case',
        'Proportional regression when required',
        'Current source fingerprint',
      ]),
      variant: 'promotion',
      priority: 1,
    }),
    complete: Object.freeze({
      ...entry(
        'Complete current coverage',
        'Every declared case has one current nonbaseline pass; RED, repetition, stability, and promotion are not established.',
        'Current skill evidence',
      ),
      variant: 'complete',
      priority: 2,
    }),
    partial: Object.freeze({
      ...entry(
        'Partial current coverage',
        'Current evidence includes a pass, but it does not cover every declared suite case.',
        'Current skill evidence',
      ),
      variant: 'partial',
      priority: 3,
    }),
    'no-current-pass': Object.freeze({
      ...entry('No current pass', 'Reports match the current skill source, but none records a current pass.', 'Current skill evidence'),
      variant: 'no-current-pass',
      priority: 4,
    }),
    historical: Object.freeze({
      ...entry(
        'Historical runs',
        'Archived reports exist, but none has a comparable fingerprint matching the current skill source.',
        'Historical skill evidence',
      ),
      variant: 'historical',
      priority: 5,
    }),
    'no-evaluation': Object.freeze({
      ...entry('No evaluation yet', 'No archived evaluation report is available for this skill yet.', 'Skills without reports'),
      variant: 'no-evaluation',
      priority: 6,
    }),
  }),
  operations: Object.freeze({
    run: entry('Exploratory evaluation', 'Evaluates selected cases without establishing promotion qualification.'),
    'verify-change': entry('RED/GREEN check', 'Compares baseline RED with candidate GREEN behavior.'),
    stability: entry('Stability check', 'Repeats evaluation to detect inconsistent outcomes.'),
    'probe-change': entry('Diagnostic change probe', 'Diagnoses a proposed change once per selected execution and reports defects.'),
    'validate-change': entry('Promotion validation', 'Runs the full promotion workflow and its required qualification gates.'),
  }),
  results: Object.freeze({
    PASS: entry('Pass', 'The operation satisfied its recorded checks.'),
    FAIL: entry('Fail', 'The evaluated behavior did not satisfy the contract.'),
    ERROR: entry('Error', 'The operation could not complete normally.'),
    INCONCLUSIVE: entry('Inconclusive', 'The available evidence could not establish the contract.'),
    INVALID_RED: entry('Invalid RED', 'The baseline did not demonstrate the required failing behavior.'),
    UNSTABLE: entry('Unstable', 'Repeated outcomes did not produce a stable result.'),
  }),
  kinds: Object.freeze({
    behavioral: entry('Behavioral', 'Checks user visible or public contract behavior.'),
    non_behavioral: entry('Nonbehavioral', 'Checks a change that does not require semantic task execution.'),
    trigger: entry('Trigger', 'Checks whether the skill is selected and invoked appropriately.'),
    deterministic: entry('Deterministic', 'Uses deterministic checks and consumes zero model sessions.'),
  }),
  roles: Object.freeze({
    baseline: entry('Baseline', 'The unchanged comparison input expected to demonstrate RED.'),
    candidate: entry('Candidate', 'The changed input being evaluated for the affected case.'),
    regression: entry('Regression', 'A case outside the affected set used to detect unintended behavior changes.'),
    observation: entry('Observation', 'A direct evaluation without a baseline or candidate comparison.'),
  }),
  judgeStates: Object.freeze({
    'not-used': entry('Not used', 'The judge was disabled for this observation.'),
    skipped: entry('Skipped', 'The judge was enabled but did not run, usually because an earlier check failed.'),
    executed: entry('Executed', 'The judge ran and its archived verdict is displayed.'),
  }),
  judgeVerdicts: Object.freeze({
    PASS: entry('Pass', 'The judge found that the evaluated result satisfied the contract.'),
    FAIL: entry('Fail', 'The judge found that the evaluated result did not satisfy the contract.'),
    INCONCLUSIVE: entry('Inconclusive', 'The judge could not establish whether the contract was satisfied.'),
    SKIPPED: entry('Skipped', 'The enabled judge did not execute.'),
  }),
  failureCategories: Object.freeze({
    contract: entry('Contract', 'The evaluated behavior or evidence contract failed.'),
    infrastructure: entry('Infrastructure', 'Authentication, quota, process launch, or another execution dependency failed.'),
    none: entry('None', 'The canonical report explicitly records no failure category.'),
    'not-recorded': entry('Not recorded', 'The report does not contain a failure category property.'),
  }),
  fields: Object.freeze({
    startedAt: entry('Started', 'The archived UTC start time for this operation.'),
    duration: entry('Duration', 'Elapsed wall clock time recorded for the operation.'),
    executorModel: entry(
      'Executor model',
      'The model used by the executor. The schema accepts an open string and does not define an exhaustive model list.',
    ),
    executorReasoningEffort: entry(
      'Executor reasoning effort',
      'The reasoning effort recorded for the executor. The schema does not define a closed list of values.',
    ),
    judgeModel: entry(
      'Judge model',
      'The model used by the judge, or Not used when judging was not applicable. The schema accepts an open string.',
    ),
    judgeReasoningEffort: entry(
      'Judge reasoning effort',
      'The reasoning effort recorded for the judge, or Not used when judging was not applicable. Values are not a closed taxonomy.',
    ),
    sessions: entry(
      'Executed sessions',
      'One session is one isolated executor or judge invocation recorded by qualification. Deterministic checks can consume zero sessions.',
    ),
    plannedSessions: entry(
      'Planned maximum sessions',
      'The maximum executor and judge invocations authorized by the plan; skipped judge work can make execution lower.',
    ),
    totalTokens: entry(
      'Total tokens',
      'Aggregate workload telemetry from recorded model events. It is not an observed financial charge, and missing telemetry is not inferred.',
    ),
    failureCategory: entry('Failure category', 'Whether a recorded failure belongs to the behavior contract or infrastructure.'),
  }),
  observationFields: Object.freeze({
    result: entry('Result', 'The recorded result for this case observation.'),
    kind: entry('Kind', 'The evaluation mechanism used for this case.'),
    role: entry('Role', 'The observation’s place in the evaluation workflow.'),
    judge: entry('Judge', 'Whether judging was used, skipped, or executed with an archived verdict.'),
  }),
});

export function operationDisplay(operation) {
  const definition = evaluationGlossary.operations[operation];
  return definition ? `${definition.label} — ${operation}` : operation;
}
