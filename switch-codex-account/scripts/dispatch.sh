#!/usr/bin/env bash
set -euo pipefail

operation="${1:-}"
powershell="${SWITCHER_POWERSHELL:-/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe}"
schtasks="${SWITCHER_SCHTASKS:-/mnt/c/Windows/System32/schtasks.exe}"

if [[ -n "${SWITCHER_CONTROLLER_WINDOWS:-}" ]]; then
  controller_windows="$SWITCHER_CONTROLLER_WINDOWS"
else
  local_app_data="$($powershell -NoLogo -NoProfile -NonInteractive -Command '[Environment]::GetFolderPath("LocalApplicationData")' | tr -d '\r')"
  controller_windows="${local_app_data}\\CodexAccountSwitcher\\Switch-CodexAccount.ps1"
fi

case "$operation" in
  status)
    "$powershell" -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File "$controller_windows" -StatusOnly | tr -d '\r'
    ;;
  account-a|account-b)
    validation="$("$powershell" -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File "$controller_windows" -Target "$operation" -ValidateTargetOnly | tr -d '\r')"
    if [[ "$validation" == *'"status":"already_active"'* ]]; then
      printf '%s\n' "$validation"
      exit 0
    fi
    if [[ "$operation" == 'account-a' ]]; then
      task_name='\Codex Account Switch\Account A'
    else
      task_name='\Codex Account Switch\Account B'
    fi
    "$schtasks" /Run /TN "$task_name" >/dev/null
    printf '{"status":"accepted","target":"%s","message":"The request was handed to the detached Windows controller."}\n' "$operation"
    ;;
  *)
    printf '{"status":"error","message":"Use only account-a, account-b, or status."}\n' >&2
    exit 2
    ;;
esac
