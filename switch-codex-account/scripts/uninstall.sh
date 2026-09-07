#!/usr/bin/env bash
set -euo pipefail

die() {
  printf 'Error: %s\n' "$1" >&2
  exit 1
}

if (($#)); then
  case "$1" in
    -h|--help)
      printf '%s\n' 'Usage: uninstall.sh'
      exit 0
      ;;
    *) die "Unknown option: $1" ;;
  esac
fi

if [[ -z "${WSL_DISTRO_NAME:-}" ]] && ! grep -qi microsoft /proc/sys/kernel/osrelease 2>/dev/null; then
  die 'This uninstaller must run inside WSL.'
fi

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
powershell="${SWITCHER_POWERSHELL:-/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe}"
[[ -x "$powershell" ]] || die 'Windows PowerShell was not found from WSL.'
command -v wslpath >/dev/null 2>&1 || die 'Required command not found: wslpath'

windows_profile="$($powershell -NoLogo -NoProfile -NonInteractive -Command '[Environment]::GetFolderPath("UserProfile")' | tr -d '\r')"
local_app_data_windows="$($powershell -NoLogo -NoProfile -NonInteractive -Command '[Environment]::GetFolderPath("LocalApplicationData")' | tr -d '\r')"
[[ -n "$windows_profile" && -n "$local_app_data_windows" ]] || die 'Windows user directories could not be resolved.'

codex_home_windows="${SWITCHER_CODEX_HOME_WINDOWS:-${windows_profile}\\.codex}"
codex_home_linux="$(wslpath -u "$codex_home_windows")"
runtime_dir_windows="${local_app_data_windows}\\CodexAccountSwitcher"
runtime_dir_linux="$(wslpath -u "$runtime_dir_windows")"
rules_path="$codex_home_linux/rules/switch-codex-account.rules"
registration_source="$script_dir/windows/Register-CodexAccountSwitcher.ps1"

"$powershell" -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File "$(wslpath -w "$registration_source")" -Mode Uninstall >/dev/null
rm -f -- "$rules_path"

[[ "$(basename -- "$runtime_dir_linux")" == 'CodexAccountSwitcher' ]] || die 'Refusing to remove an unexpected runtime path.'
rm -rf -- "$runtime_dir_linux"

printf '%s\n' '{"status":"uninstalled","credentials_preserved":true,"source_preserved":true,"restart_required":true}'
