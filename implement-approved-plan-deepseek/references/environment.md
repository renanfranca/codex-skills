# Standalone DSH environment

## Installation and model

The official launcher is installed in `/home/renanfranca/.local/share/deepseek-harness` with its existing npm lockfile. Launcher package `@deepseek-ai/dsh` is pinned to `0.1.5-rc.1`; installed runtime components are `0.1.5-rc.2`. The official Web frontend is included. This is a prerelease runtime; upgrades require repeating the session, approval and recovery tests.

The `deepseek-web` profile uses an authored `deepseek-standard` preset copied from the official standard preset. It retains filesystem skills, terminal, files, native Plan Mode, compaction and questions. Delegation tools are removed because this workflow uses ordinary persistent sessions. The Host plugin calls the official SessionController and WorkspaceController APIs. Its console endpoint is a custom authenticated operator convenience, not an upstream SDK endpoint.

Connection, credentials and default model are configured in `~/.dsh/settings.yaml`;
profile overrides live in `~/.dsh/profiles/deepseek-web/cordis.patch.yml`. The Web
model picker remains available. Specialist efforts come from the Host plugin's
`roleReasoningEfforts` configuration: `implementer`, `committer` and
`structural-reviewer` at `low`, and `validator`, `habit-curator` and
`mutation-analyst` at `off`. The DSH default model also uses `low`. Selections
are recorded in the ledger.
Changing a configured selection is not an instruction to replace session IDs.
Output per call is capped at 16384 tokens. Auxiliary title generation and the
separate search provider remain disabled. HTTP web fetch remains available;
built-in web search has no configured provider and must not be claimed as working.

The native permission preset is `danger-full-access`, with `sandbox: danger-full-access` and `approval: never`. It runs as Unix user `renanfranca`, with that user's filesystem/network privileges. It does not grant Linux root automatically. Workflow leases and identity checks enforce cooperation through DSH tools; sessions share a trusted Unix account and Full Access is not OS isolation between them.

## API key

`DEEPSEEK_API_KEY` is read from the process environment. The existing private `~/.loadenv/deepseek.env` is loaded through `loadenv deepseek` by the launcher when the environment does not already supply it; the value is never copied to settings, skills, repository files or command logs. An already configured key is reused without requesting it again.

To insert or replace it manually, edit `/home/renanfranca/.loadenv/deepseek.env` in your local editor and set this one line, replacing the placeholder locally:

```text
DEEPSEEK_API_KEY=YOUR_DEEPSEEK_KEY
```

Keep the directory private and file mode `600`; it is outside tracked project files and explicitly excluded in the home Git worktree. Do not paste the key into a chat, command argument or Git file. Then run `dsh-env restart`. For a foreground process you can instead read it without echo:

```bash
read -rsp 'DeepSeek key: ' DEEPSEEK_API_KEY
export DEEPSEEK_API_KEY
~/.local/bin/dsh-web-launch
```

The foreground environment does not change the systemd service's key source.

## Lifecycle and remote access

```bash
dsh-env start
dsh-env stop
dsh-env restart
dsh-env status
dsh-env doctor
dsh-env open
dsh-env open --local
dsh-env workspaces
dsh-env sessions
dsh-env resume SESSION_ID
```

`dsh-env open` explicitly displays a DSH launch URL containing an access token. Keep it private. It exchanges the token for DSH's native host-only HttpOnly/SameSite cookie and redirects to the clean URL. Cookies survive service restarts through the private DSH credentials store; the launch token changes on restart. Do not publish that URL. The Android browser can retain its cookie and reopen the clean URL.

`dsh-web.service` runs independently from Codex, starts with systemd and restarts on failure. DSH binds only `127.0.0.1:3080`. Tailscale Serve provides private HTTPS and forwards HTTP/WebSockets to that loopback address. Funnel is not enabled. Stop disables the DSH HTTPS handler and stops DSH; the VPN daemon remains available. A service restart stops running tools, so prefer it when sessions are idle and use the recovery procedure afterwards.

Android: install the official Tailscale app, log into the same tailnet, connect the VPN, and open `https://renan-dsh.taileb74b9.ts.net/`. On first access, use the private remote launch URL from `dsh-env open`. Choose a workspace in the sidebar, create a session with the DeepSeek Full Access preset, and open any saved session by its title. Repositories remain on this computer; it must be awake and connected. Tailscale account login/HTTPS enablement and a real Android browser test require the user and are tracked separately from local checks.

## Plan and implementation

In an ordinary Web session, submit `/plan`, describe the behavior, review the plan, and approve through the official plan panel. Approval stops the assistant turn; it does not implement. The plugin captures the exact approved Markdown and commits the native plan exit at idle, including recovery after restart. Explicitly reentering `/plan` later is respected.

Then submit:

```text
/implement-approved-plan-deepseek
Execute the approved plan. Use slug MY-SLUG, feature branch MY-BRANCH and base main.
```

Use kebab-case slug/branch names. The initial session becomes Coordinator and keeps its original session ID. Six specialist sessions are created in the same workspace, checkout and branch, with titles `<slug> · <role>`. They appear in the ordinary sidebar and can be opened and discussed from Android. Their conversation persists; only Coordinator assignments authorize checkout work. New requested changes must be routed through Coordinator.

The Coordinator sends assignments with `workflow_dispatch`, waits with `workflow_wait`, collects with `workflow_collect` and operates the guarded ledger with `workflow_control`. Worker completion resumes the same Coordinator through an official queued prompt. Follow-ups reuse the same worker ID. Native session creation/resume/listing are supported; there are no Codex tasks or external coding backends in the runtime.

## Persistence and recovery

DSH transcripts and projections live under `~/.dsh/sessions`; workspace registrations live in native DSH storage. `~/.dsh/workflow-registry.json` indexes roles/approvals. Each checkout keeps ignored `.agent/tmp/<slug>.md`, `.dsh-workflow.json` and `.dsh-orchestration.json`, plus reports/logs. Back up both DSH home and the checkout's ignored artifacts to preserve an execution.

After `dsh-env start`, open the original Coordinator. Ask it to call `workflow_resume`, inspect the journal, native histories, checkout and processes, and continue the existing approved workflow. Resume reconciles the original six reserved IDs and does not create replacements. Interrupted assignments retain their leases and require explicit diagnosis; no timeout releases authority and no restart blindly replays a commit, push or PR. See [recovery.md](recovery.md).

The private seed4j-cli fixture uses unique Sonar containers on loopback9002. Its workflow leaves its PR open for review. No release/synchronization workflow is installed. Baseline provisioning is separate from the seven-session implementation, so the workflow's immutable base SHA contains the tools and CI configuration.

## Official sources

- [Official DeepSeek Harness repository](https://github.com/deepseek-ai/DeepSeek-Harness)
- [Official launcher documentation](https://github.com/deepseek-ai/DeepSeek-Harness/tree/master/apps/cli)
- [Tailscale Serve](https://tailscale.com/kb/1242/tailscale-serve)
- [DeepSeek API configuration](https://api-docs.deepseek.com/)

Installed package README files and public declaration files are the authority for this pinned runtime. Newer upstream interfaces must not be assumed present.

## Windows startup and shutdown

Windows Task Scheduler task `DSH WSL Keepalive` starts at the current user's login and keeps Ubuntu-Seed4J running through a foreground `sleep infinity`. Its trusted scripts are `C:\Users\renan\.dsh\keepalive.ps1` and `install-keepalive.ps1`. systemd then starts DSH and Tailscale without Codex. No administrator principal, user password or API key is stored in the task. This keeps WSL active; it does not prevent Windows sleep or survive a Windows shutdown.

To stop the keepalive from PowerShell, run `Stop-ScheduledTask -TaskName 'DSH WSL Keepalive'`. To prevent the next login startup, run `Disable-ScheduledTask -TaskName 'DSH WSL Keepalive'`. Enable/start with the corresponding `Enable-ScheduledTask` and `Start-ScheduledTask`. This is independent of `dsh-env stop`, which stops the Web service and private HTTPS handler.

## Skill compatibility

The existing shared skills root `~/.agents/skills` is officially discovered by DSH. TDD, commit-the-changes, commit-staged-change and refactor-design use filesystem references and Git/terminal operations and can be loaded natively without migrating the originals. The new workflow skill uses native DSH invocation controls `disable-model-invocation` and `user-invocable`; Codex's older quick_validate rejects these two DSH fields. That validator is left unchanged. Actual DSH catalog/invocation tests are authoritative for native compatibility; Markdown links and ledger tests are validated independently.
