# Codex Account Switcher

`switch-codex-account` manually switches the account used by Codex Desktop on
Windows while preserving one shared `CODEX_HOME`, including its projects,
sessions, skills, and conversation index.

It is designed for Codex Desktop running commands through WSL. The switch is
always explicit: this package does not inspect quotas, monitor usage windows, or
rotate accounts automatically.

## Requirements

- Windows with WSL and Codex Desktop installed as the `OpenAI.Codex` Appx package.
- A WSL distribution used by Codex Desktop.
- Node.js and npm available inside that distribution.
- Two ChatGPT accounts that you are authorized to use.
- The skill placed at `$HOME/.agents/skills/switch-codex-account` inside WSL.

The installer pins the third-party
[`@loongphy/codex-auth`](https://github.com/Loongphy/codex-auth) package to
version `0.2.10`. Its source is not vendored here and remains governed by its own
license and security model.

## Installation

If this repository itself is checked out at `$HOME/.agents/skills`, the skill is
already in its final discovery location and is the only skill copy:

```bash
cd "$HOME/.agents/skills"
bash switch-codex-account/scripts/install.sh
```

For a selective installation, first place only this directory at
`$HOME/.agents/skills/switch-codex-account`, then run the same installer from
inside that directory:

```bash
bash scripts/install.sh
```

The guided installer:

1. Detects the current WSL distribution and Windows profile paths.
2. Installs `@loongphy/codex-auth@0.2.10` when that exact version is absent.
3. Disables codex-auth automatic switching and API modes.
4. Adopts an existing A/B mapping or guides account login and selection.
5. Generates the detached Windows runtime and two on-demand scheduled tasks.
6. Installs three exact command rules for status, Account A, and Account B.
7. Validates safe status before removing an older Windows-hosted skill copy.

Browser authentication is attempted first when another account is needed. Use
device authentication directly when local browser callbacks are unsuitable:

```bash
bash scripts/install.sh --device-auth
```

Restart Codex after installation so it reloads the skill and command rules.

## Source and runtime locations

| Purpose | Location | Stored in Git |
| --- | --- | --- |
| Discoverable skill and canonical source | `$HOME/.agents/skills/switch-codex-account` | Yes |
| Detached Windows controller and generated state | `%LOCALAPPDATA%\CodexAccountSwitcher` | No |
| Codex and codex-auth authentication | `%USERPROFILE%\.codex` | No |

The Windows and WSL spellings of a path under `/mnt/c` refer to the same files.
The AppData directory is not a second skill installation: it contains only the
Windows controller copy required to finish restarting Codex after the Desktop
process closes.

Generated `config.json` contains account selectors and account keys but no
access or refresh tokens. Actual authentication remains in `auth.json` and the
codex-auth account registry under the existing Windows `CODEX_HOME`. Never add
any of those generated files to a repository, including a private repository.

## Usage

Invoke the explicit-only skill from Codex:

```text
$switch-codex-account status
$switch-codex-account account-a
$switch-codex-account account-b
```

The skill refuses a switch while another Codex task is active. A dedicated
pinned chat titled **Account switch** is recommended so the control task can be
distinguished from other work.

The same dispatcher is available directly from WSL:

```bash
bash "$HOME/.agents/skills/switch-codex-account/scripts/dispatch.sh" status
bash "$HOME/.agents/skills/switch-codex-account/scripts/dispatch.sh" account-a
bash "$HOME/.agents/skills/switch-codex-account/scripts/dispatch.sh" account-b
```

A switch request is handed to Windows Task Scheduler. The controller waits five
seconds, closes only processes whose executable belongs to the installed
`OpenAI.Codex` package, updates authentication through codex-auth, verifies the
target account, and reopens Codex Desktop. It does not stop ChatGPT Classic.

## Updating and reconfiguring

Pull or replace the repository source, then rerun the installer:

```bash
bash scripts/install.sh
```

An ordinary rerun adopts the current A/B mapping and updates only files owned by
the switcher. To select the two accounts again:

```bash
bash scripts/install.sh --reconfigure
```

When exactly two accounts are registered, the active account becomes Account A.
When more accounts exist, the installer asks which two to use. codex-auth 0.2.10
receives an email query, so the installer verifies that each selected email
matches exactly one registry record across email, alias, and account name. An
ambiguous selector is rejected instead of opening an interactive prompt in a
background task.

## Uninstalling

```bash
bash scripts/uninstall.sh
```

This removes the scheduled tasks, generated rule file, controller, local
configuration, and sanitized logs. It deliberately preserves:

- The Git-tracked skill source.
- `auth.json`, the codex-auth registry, and saved account credentials.
- Codex projects, sessions, and conversation databases.
- The global codex-auth installation, which may be used independently.

Because this repository checkout is also the discovery location, removing the
source directory would create a Git deletion. Move or remove the directory
yourself only if you also want to remove the skill from the repository checkout.
The skill is explicit-only and cannot switch after its runtime is uninstalled.

Restart Codex after uninstalling so it reloads skills and rules.

## Failure recovery

The installer backs up the previous generated runtime before replacing it. If
task registration or status validation fails, it restores that runtime and
leaves the older installed skill untouched.

For every account switch, the controller copies `auth.json` and
`accounts/registry.json` to a temporary rollback directory inside the existing
codex-auth account store. If switching or verification fails, both files are
restored atomically. A rollback directory is retained only when automatic
restoration itself fails.

Safe operational state is available through `status`. `last-result.json` and
`switch.log` contain aliases, stages, and result messages only; they never log
emails or tokens.

## Troubleshooting

- **The skill is not visible:** verify the directory and `SKILL.md`, then restart
  Codex.
- **The scheduled task is missing:** rerun `bash scripts/install.sh`.
- **The browser login callback fails:** rerun with `--device-auth`.
- **The installer rejects duplicate emails:** codex-auth 0.2.10 cannot switch
  those records non-interactively; register two accounts with distinct emails.
- **A switch is already in progress:** wait for `status` to show a terminal
  result. Do not submit the task again.
- **The account switched but Codex did not reopen:** open Codex Desktop manually;
  status will report `launch_failed` rather than rolling back a verified switch.

After installation, perform one explicit smoke test when no other Codex work is
running: switch A to B, verify an existing project and conversation, then switch
back to A and verify them again.
