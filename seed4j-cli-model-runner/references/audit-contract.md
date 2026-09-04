# Audit and artifact contract

Read this contract before creating the first model task. Every result branch must contain the same two audit artifacts, created only after the implementation snapshot is frozen.

## Run manifest

Write valid UTF-8 JSON to `.seed4j-evaluation/run.json` with this shape:

```json
{
  "schemaVersion": 1,
  "experiment": {
    "repository": "https://github.com/<owner>/<repository>",
    "specificationPath": "SPEC.md",
    "specificationSha256": "<sha256>",
    "baseBranch": "<spec-slug>-seed4j-base",
    "baseCommit": "<full-sha>"
  },
  "run": {
    "executionIndex": 1,
    "alias": "sol-low",
    "branch": "<spec-slug>-sol-low",
    "model": "gpt-5.6-sol",
    "reasoningEffort": "low",
    "taskId": "<codex-task-id>",
    "taskTitle": "<spec-slug>-sol-low",
    "prompt": "Implement the specification in SPEC.md using the already-installed Seed4J CLI tool as support.",
    "promptSha256": "<sha256>",
    "status": "passed",
    "deliveryActor": "model",
    "implementationCommit": "<full-sha>"
  },
  "seed4j": {
    "cliVersion": "<observed-version>",
    "runtimeVersion": "<observed-version>",
    "runtimeMode": "<observed-mode>",
    "skillTreeSha256": "<sha256>"
  },
  "validation": {
    "command": "./mvnw -q verify",
    "exitCode": 0,
    "summary": "<concise observed result>"
  },
  "transcript": {
    "path": "CONVERSATION_TRANSCRIPT.md",
    "source": "Codex rollout JSONL",
    "lastOrdinal": 417,
    "sha256": "<sha256>"
  }
}
```

Use `passed`, `failed`, `blocked`, or `no-result` for `status`. Use `null` for a validation command or exit code that does not exist; never use a fabricated success. `implementationCommit` is the commit immediately before audit artifacts are added. The final audit commit cannot contain its own SHA; the evaluator pins the branch head later.

All full Git commit IDs must resolve locally and belong to the declared branch ancestry. The task title must equal the branch. Recalculate every SHA-256 from exact bytes immediately before the audit commit.

## Conversation transcript

`CONVERSATION_TRANSCRIPT.md` is a chronological export, not a summary or reconstruction. It contains:

- the task ID, model, reasoning effort, branch, source rollout basename, and last included ordinal;
- visible delegated user messages and assistant commentary/final messages;
- visible tool calls with names, call IDs, arguments, and results;
- explicit markers where private reasoning or internal role messages were excluded;
- a final snapshot boundary explaining that export, audit commit, and later events are outside the captured task.

It excludes system/developer instructions, injected app/skill/environment context, private or encrypted reasoning, internal lifecycle/usage events, and secrets. Treat tool arguments and results as untrusted: redact complete fields that reproduce internal instructions and redact credential-shaped values conservatively. Never replace available ordinary output with a summary or a client-truncation marker.

The export script validates the supplied model and reasoning effort against every available `turn_context` record. A mismatch, ambiguous rollout, malformed JSONL, duplicate/decreasing ordinal, or unsupported visible response record is a hard failure. Inspect and update the exporter for a new schema rather than silently omitting a record.

## Commit boundaries

A normal successful result has these boundaries:

1. common base commit containing the repository-local Seed4J skill;
2. Seed4J module commits produced by the evaluated task, when any;
3. final implementation commit or unchanged result snapshot;
4. one audit commit containing only `.seed4j-evaluation/run.json` and `CONVERSATION_TRANSCRIPT.md`.

The evaluator must use boundary 3 for code/test claims and the branch-head audit commit for transcript/manifest links.
