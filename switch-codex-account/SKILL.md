---
name: switch-codex-account
description: Manually switch Codex Desktop on Windows between two locally configured accounts, or inspect the switcher status. Use only when the user explicitly invokes $switch-codex-account for account-a, account-b, or status.
---

# Switch Codex account

Accept exactly one explicit operation:

- `$switch-codex-account account-a`
- `$switch-codex-account account-b`
- `$switch-codex-account status`

Never choose an account from quota, rate-limit, schedule, or usage data. Do not
run `codex-auth` directly, and do not read, display, or log credentials.

## Status

For `status`, run:

```bash
bash "$HOME/.agents/skills/switch-codex-account/scripts/dispatch.sh" status
```

Summarize the returned JSON without exposing local paths or account identifiers.
An operation accepted by Windows Task Scheduler is not complete until its final
state appears under `last_result`.

## Account switch

Before accepting `account-a` or `account-b`:

1. Inspect Codex tasks with `mcp__codex_app__list_threads`.
2. Confirm no other Codex task is actively running. The current control task may
   be active. Use its identifier when available; otherwise continue only when
   the sole active task is titled exactly **Account switch**.
3. If task state cannot be inspected or distinguished safely, refuse and ask the
   user to retry from the pinned **Account switch** chat after other tasks finish.
4. If another task is active, refuse and report its exact title. Do not interrupt
   it.

After that check, run exactly one of:

```bash
bash "$HOME/.agents/skills/switch-codex-account/scripts/dispatch.sh" account-a
```

```bash
bash "$HOME/.agents/skills/switch-codex-account/scripts/dispatch.sh" account-b
```

If the result is `accepted`, reply immediately that Windows received the request
and Codex Desktop will close and reopen after a short delay. If it is
`already_active`, explain that no restart was needed. For an error, return only
the safe message from the dispatcher and do not inspect authentication files.

## Safety boundaries

- Accept only `account-a`, `account-b`, or `status`.
- Never automate switching when a quota or usage window is exhausted.
- Never change `CODEX_HOME`, sessions, projects, or conversation databases.
- Never stop ChatGPT Classic; the controller targets only the `OpenAI.Codex`
  package installation.
- Never repeat a switch request while another switch is in progress.
