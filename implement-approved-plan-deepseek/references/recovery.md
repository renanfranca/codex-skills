# Recovery

Start the environment with `dsh-env start`, open the authenticated Web URL and
select the original Coordinator by workflow prefix and session ID. Send a resume
request; Coordinator calls `workflow_resume`, then `workflow_status`.

The ledger retains its immutable base SHA, phases, accepted gates and lease.
Ignored `<slug>.dsh-orchestration.json` retains Coordinator identity, six reserved
session IDs, assignments, prompt IDs, collection snapshots and notifications.
The DSH home retains authoritative compressed session logs and workspace state.

If a dispatched prompt is found in durable history, do not send it again. If the
worker completed, collect and inspect its response and actual checkout before
recording a gate or releasing its lease. A cold unfinished assignment is marked
interrupted and keeps the lease: inspect HEAD, tracked/untracked changes and
active processes, and write a diagnostic report under ignored `.agent/tmp`.
Call `workflow_recover` with the interrupted assignment ID, diagnostic path and
Coordinator decision. It cancels that assignment without claiming success or
replaying its prompt; the original lease remains held. Record failure/correction
evidence as applicable, then explicitly release or send a new scoped assignment
to the same session. Inspect existing commits/PRs before any new side effect.
Never infer a successful command or commit from prompt acknowledgement.

A collected assignment can release its lease only after the worker is idle and
its changed paths are within the approved assignment. Unexpected changes block
the gate; preserve them and ask for direction instead of reverting silently.

Use the original Coordinator session. A different session cannot adopt authority
by supplying its ID in an operator request. Keep plan/ledger/logs until a later
explicit invocation confirms GitHub's exact recorded PR is MERGED.
Use `workflow_cleanup` for this reconciliation. It independently queries GitHub,
requires the exact recorded PR URL and a valid merge timestamp, and deletes only
the native plan/ledger pair. Native transcripts, sessions, reports, transport
journal and branches remain. Archived sessions still allow conversation but do
not regain checkout authority.
