# Native DSH orchestration

The official DSH SessionController is the lifecycle owner. The persistent Cordis
Host plugin calls `create({workspaceId,cwd,sessionId,agentPreset})`,
`selectModel`, `rename`, `prompt({sessionId,requestId,mode:'queue',content})`,
`resolveAgent`, `list` and `inspect`. These are ordinary top-level sessions with
no subagent origin, parent or delegation ownership.

The Host mints the six IDs before creation and saves them in ignored transport
state. Explicit-ID creation is idempotent. Every prompt has a stable request ID.
After the session is created its exact route and Full Access state are checked,
and its ID is registered in the behavioral ledger. Titles identify one workflow
and role. The model, prompt admission, terminal and filesystem remain DSH-owned.

## Tools

- `workflow_start`: resolve approved plan, clean feature branch and immutable
  base; initialize ledger and reconcile exactly six registered sessions.
- `workflow_status`: inspect workflow, sessions, lease and assignments.
- `workflow_dispatch`: Coordinator-only; authorize role, files and expected
  evidence under its lease; journal the assignment before native prompt admission.
- `workflow_collect`: Coordinator-only; require the worker to be idle and the
  assignment to have a durable response; return evidence and checkout scope.
- `workflow_control`: Coordinator-only; run the guarded ledger CLI with an argv
  array. There is no shell interpolation. A release requires an idle worker and
  a collected, scope-checked assignment.
- `workflow_wait`: conclude this Coordinator turn until worker completion. A
  queued notification resumes the same Coordinator. No external model is used.
- `workflow_resume`: reconcile existing IDs and interrupted assignments. It
  never creates replacement specialists or releases leases by elapsed time.
  An active worker or background job defers model configuration; its existing
  selection and completion monitor remain in place until idle reconciliation.

Every checkout tool call in a managed session must have the matching lease. Skill
loading, user questions and workflow status are available without checkout work.
Coordinator management tools do not grant checkout access to other sessions.
Model calls use DSH adapters and configured selections; the plugin does not
restrict a global provider or reasoning level. Specialist model configuration
uses the DSH default plus per-role effort, and restores the global default after
selection, including failures. Role and file contracts are checked again against
actual Git deltas after the specialist is idle.

Full Access is official unrestricted tool execution at the OS user's existing
privilege level. Trusted sessions share that identity; contracts and leases are
workflow controls rather than OS isolation from malicious processes.

## Plan approval

`/plan` uses the official plan-mode plugin and Web review channel. An agent-local
wrapper preserves the original exit tool schema, implementation and UI, captures
only a successful approved Markdown plan, and calls the official execution's
`concludeTurn`. The workflow starts only on an explicit human skill invocation.
An external plan file without a captured approval uses native Web plan review.
The native exit selection ordinarily commits on the next pre-step. After the
approval concludes its turn, the Host uses public PlanModeController.set at idle
to make that exit durable. On resume it repairs only an older approved exit;
an explicit later `/plan` selection is preserved.

Upstream Plan Mode changes guidance and durable mode state, not sandbox rights.
Full Access is retained. Workflow start refuses active Plan Mode.

## Interfaces and differences

The authenticated `/api/dsh-workflow/console` endpoint is this plugin's small
operator interface, registered through official Connection Fetch routes. It
delegates workspace/session operations to official Host controllers and exposes
read-only workflow status. Orchestration runs through model-facing tools in the
Coordinator, not operator-supplied session identities. DSH's launch-token cookie
exchange authenticates this endpoint as it does native Remote/WebSocket routes.

No ACP or SDK-only substitute is used: installed ACP deliberately omits native
plan review and the installed SDK does not provide faithful multi-session resume.
The plugin adds the cross-session capability that `SKILL.md` alone cannot add.

Operator `workflow.configure-models` updates the existing seven idle sessions
without prompts, introductions, phase changes or lease release. It accepts the
Coordinator `sessionId`, checks active jobs and records the accepted specialist
selections. `session.model` forwards the requested native selection unchanged.
