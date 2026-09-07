#!/usr/bin/env bash
set -euo pipefail

readonly CODEX_AUTH_VERSION='0.2.10'
readonly PACKAGE_NAME='@loongphy/codex-auth'

reconfigure=0
dry_run=0
prefer_device_auth=0

usage() {
  printf '%s\n' 'Usage: install.sh [--reconfigure] [--device-auth] [--dry-run]'
}

die() {
  printf 'Error: %s\n' "$1" >&2
  exit 1
}

require_command() {
  command -v "$1" >/dev/null 2>&1 || die "Required command not found: $1"
}

strip_cr() {
  tr -d '\r'
}

while (($#)); do
  case "$1" in
    --reconfigure) reconfigure=1 ;;
    --device-auth) prefer_device_auth=1 ;;
    --dry-run) dry_run=1 ;;
    -h|--help) usage; exit 0 ;;
    *) usage >&2; die "Unknown option: $1" ;;
  esac
  shift
done

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
skill_root="$(cd -- "$script_dir/.." && pwd -P)"
expected_skill_root="$(realpath -m -- "$HOME/.agents/skills/switch-codex-account")"

if [[ "$skill_root" != "$expected_skill_root" && "${SWITCHER_ALLOW_NON_DISCOVERY_ROOT:-0}" != '1' ]]; then
  die "Place this skill at $expected_skill_root before running the installer."
fi

if ((dry_run)) && [[ "${SWITCHER_TEST_MODE:-0}" == '1' ]]; then
  printf '{"status":"dry_run_ok","dependency":"%s@%s","accounts":2,"skill_installations":1}\n' "$PACKAGE_NAME" "$CODEX_AUTH_VERSION"
  exit 0
fi

if [[ -z "${WSL_DISTRO_NAME:-}" ]] && ! grep -qi microsoft /proc/sys/kernel/osrelease 2>/dev/null; then
  die 'This installer must run inside WSL.'
fi

powershell="${SWITCHER_POWERSHELL:-/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe}"
schtasks="${SWITCHER_SCHTASKS:-/mnt/c/Windows/System32/schtasks.exe}"
[[ -x "$powershell" ]] || die 'Windows PowerShell was not found from WSL.'
[[ -x "$schtasks" ]] || die 'Windows Task Scheduler was not found from WSL.'
require_command node
require_command npm
require_command wslpath

windows_profile="$($powershell -NoLogo -NoProfile -NonInteractive -Command '[Environment]::GetFolderPath("UserProfile")' | strip_cr)"
local_app_data_windows="$($powershell -NoLogo -NoProfile -NonInteractive -Command '[Environment]::GetFolderPath("LocalApplicationData")' | strip_cr)"
[[ -n "$windows_profile" && -n "$local_app_data_windows" ]] || die 'Windows user directories could not be resolved.'

codex_home_windows="${SWITCHER_CODEX_HOME_WINDOWS:-${windows_profile}\\.codex}"
codex_home_linux="$(wslpath -u "$codex_home_windows")"
runtime_dir_windows="${local_app_data_windows}\\CodexAccountSwitcher"
runtime_dir_linux="$(wslpath -u "$runtime_dir_windows")"
registry_path="$codex_home_linux/accounts/registry.json"
rules_dir="$codex_home_linux/rules"
rules_path="$rules_dir/switch-codex-account.rules"
default_rules_path="$rules_dir/default.rules"
legacy_skill_root="$codex_home_linux/skills/switch-codex-account"
distro="${SWITCHER_DISTRO:-${WSL_DISTRO_NAME:-}}"
[[ -n "$distro" ]] || die 'The WSL distribution name could not be resolved.'

node_linux="$(command -v node)"
for runtime_argument in "$distro" "$codex_home_linux" "$node_linux"; do
  [[ "$runtime_argument" =~ ^[A-Za-z0-9_%@./:=+-]+$ ]] || die 'A runtime path contains unsupported characters.'
done

if ((dry_run)); then
  printf '{"status":"dry_run_ok","dependency":"%s@%s","accounts":2,"skill_installations":1}\n' "$PACKAGE_NAME" "$CODEX_AUTH_VERSION"
  exit 0
fi

current_version=''
if command -v codex-auth >/dev/null 2>&1; then
  current_version="$(codex-auth --version 2>/dev/null | sed -n '1p' || true)"
fi
if [[ "$current_version" != "codex-auth $CODEX_AUTH_VERSION" ]]; then
  npm install -g "${PACKAGE_NAME}@${CODEX_AUTH_VERSION}"
fi

codex_auth_command="$(command -v codex-auth)"
codex_auth_js_linux="$(readlink -f -- "$codex_auth_command")"
[[ -f "$codex_auth_js_linux" ]] || die 'The installed codex-auth entrypoint could not be resolved.'
[[ "$codex_auth_js_linux" =~ ^[A-Za-z0-9_%@./:=+-]+$ ]] || die 'The codex-auth path contains unsupported characters.'

run_codex_auth() {
  CODEX_HOME="$codex_home_linux" "$codex_auth_command" "$@"
}

run_codex_auth config auto disable >/dev/null
run_codex_auth config api disable >/dev/null
run_codex_auth list >/dev/null 2>&1 || true

initial_active_row=''
if [[ -f "$registry_path" ]]; then
  initial_active_row="$(node "$script_dir/registry-helper.mjs" active "$registry_path" 2>/dev/null || true)"
fi

account_count=0
if [[ -f "$registry_path" ]]; then
  account_count="$(node "$script_dir/registry-helper.mjs" list "$registry_path" | wc -l)"
fi

login_attempts=0
while ((account_count < 2)); do
  ((login_attempts += 1))
  ((login_attempts <= 2)) || die 'Two distinct accounts were not registered; correct the login and rerun the installer.'
  printf 'A second registered Codex account is required (%d/2 currently available).\n' "$account_count"
  if ((prefer_device_auth)); then
    run_codex_auth login --device-auth
  elif ! run_codex_auth login; then
    printf '%s\n' 'Browser authentication did not complete; trying device authentication.'
    run_codex_auth login --device-auth
  fi
  run_codex_auth list >/dev/null
  account_count="$(node "$script_dir/registry-helper.mjs" list "$registry_path" | wc -l)"
done

pair_output=''
adopted=0
existing_config="$runtime_dir_linux/config.json"
existing_mapping_kind='none'
if [[ -f "$existing_config" ]]; then
  if node -e 'const c=require(process.argv[1]); process.exit(c.accounts?.["account-a"] && c.accounts?.["account-b"] ? 0 : 1)' "$existing_config"; then
    existing_mapping_kind='english'
  elif node -e 'const c=require(process.argv[1]); process.exit(c.accounts?.["conta-a"] && c.accounts?.["conta-b"] ? 0 : 1)' "$existing_config"; then
    existing_mapping_kind='legacy'
  fi
fi
if ((!reconfigure)) && [[ -f "$existing_config" ]]; then
  if pair_output="$(node "$script_dir/registry-helper.mjs" existing-pair "$registry_path" "$existing_config" 2>/dev/null)"; then
    adopted=1
  fi
fi

if [[ -z "$pair_output" ]]; then
  if ((account_count == 2)); then
    pair_output="$(node "$script_dir/registry-helper.mjs" suggested-pair "$registry_path")"
  else
    printf '%s\n' 'Registered accounts:'
    node "$script_dir/registry-helper.mjs" list "$registry_path"
    read -r -p 'Number for Account A: ' account_a_number
    read -r -p 'Number for Account B: ' account_b_number
    pair_output="$(node "$script_dir/registry-helper.mjs" selected-pair "$registry_path" "$account_a_number" "$account_b_number")"
  fi
fi

mapfile -t pair_rows <<< "$pair_output"
[[ ${#pair_rows[@]} -eq 2 ]] || die 'Exactly two account mappings are required.'
IFS=$'\t' read -r account_a_key account_a_email _ <<< "${pair_rows[0]}"
IFS=$'\t' read -r account_b_key account_b_email _ <<< "${pair_rows[1]}"
[[ -n "$account_a_key" && -n "$account_b_key" && "$account_a_key" != "$account_b_key" ]] || die 'The two account mappings must be different.'
[[ "$account_a_email" =~ ^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+$ ]] || die 'Account A has an unsupported email selector.'
[[ "$account_b_email" =~ ^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+$ ]] || die 'Account B has an unsupported email selector.'
[[ "${account_a_email,,}" != "${account_b_email,,}" ]] || die 'Duplicate account emails cannot be switched unambiguously.'

backup_root="$(mktemp -d)"
runtime_existed=0
rules_existed=0
mutation_started=0
install_succeeded=0

rollback_installation() {
  local exit_code=$?
  trap - EXIT
  if ((mutation_started)) && ((!install_succeeded)); then
    "$powershell" -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File "$(wslpath -w "$script_dir/windows/Register-CodexAccountSwitcher.ps1")" -Mode Uninstall >/dev/null 2>&1 || true
    rm -rf -- "$runtime_dir_linux"
    if ((runtime_existed)); then
      mkdir -p -- "$runtime_dir_linux"
      cp -a -- "$backup_root/runtime/." "$runtime_dir_linux/"
      if [[ "$existing_mapping_kind" == 'english' && -f "$runtime_dir_linux/Switch-CodexAccount.ps1" ]]; then
        "$powershell" -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File "$(wslpath -w "$script_dir/windows/Register-CodexAccountSwitcher.ps1")" -Mode Install -ControllerPath "${runtime_dir_windows}\\Switch-CodexAccount.ps1" >/dev/null 2>&1 || true
      fi
    fi
    if ((rules_existed)); then
      mkdir -p -- "$rules_dir"
      cp -- "$backup_root/switch-codex-account.rules" "$rules_path"
    else
      rm -f -- "$rules_path"
    fi
  fi
  rm -rf -- "$backup_root"
  exit "$exit_code"
}
trap rollback_installation EXIT

if [[ -d "$runtime_dir_linux" ]]; then
  runtime_existed=1
  mkdir -p -- "$backup_root/runtime"
  cp -a -- "$runtime_dir_linux/." "$backup_root/runtime/"
fi
if [[ -f "$rules_path" ]]; then
  rules_existed=1
  cp -- "$rules_path" "$backup_root/switch-codex-account.rules"
fi

mutation_started=1
mkdir -p -- "$runtime_dir_linux" "$rules_dir"
install -m 0644 "$script_dir/windows/Switch-CodexAccount.ps1" "$runtime_dir_linux/Switch-CodexAccount.ps1"
install -m 0644 "$script_dir/windows/Register-CodexAccountSwitcher.ps1" "$runtime_dir_linux/Register-CodexAccountSwitcher.ps1"

export SWITCHER_CONFIG_DISTRO="$distro"
export SWITCHER_CONFIG_CODEX_HOME_LINUX="$codex_home_linux"
export SWITCHER_CONFIG_CODEX_HOME_WINDOWS="$codex_home_windows"
export SWITCHER_CONFIG_NODE_LINUX="$node_linux"
export SWITCHER_CONFIG_CODEX_AUTH_JS_LINUX="$codex_auth_js_linux"
export SWITCHER_CONFIG_ACCOUNT_A_EMAIL="$account_a_email"
export SWITCHER_CONFIG_ACCOUNT_A_KEY="$account_a_key"
export SWITCHER_CONFIG_ACCOUNT_B_EMAIL="$account_b_email"
export SWITCHER_CONFIG_ACCOUNT_B_KEY="$account_b_key"
node "$script_dir/write-config.mjs" "$runtime_dir_linux/config.json"

dispatch_command_prefix='bash "$HOME/.agents/skills/switch-codex-account/scripts/dispatch.sh"'
SWITCHER_RULE_COMMAND_PREFIX="$dispatch_command_prefix" node --input-type=module - "$rules_path" <<'NODE'
import fs from "node:fs";
const output = process.argv[2];
const prefix = process.env.SWITCHER_RULE_COMMAND_PREFIX;
const lines = ["status", "account-a", "account-b"].map((operation) => {
  const command = `${prefix} ${operation}`;
  return `prefix_rule(pattern=["/bin/bash", "-lc", ${JSON.stringify(command)}], decision="allow")`;
});
const temporary = `${output}.${process.pid}.tmp`;
fs.writeFileSync(temporary, `${lines.join("\n")}\n`, { encoding: "utf8", mode: 0o600 });
fs.renameSync(temporary, output);
NODE

controller_windows="${runtime_dir_windows}\\Switch-CodexAccount.ps1"
registration_windows="${runtime_dir_windows}\\Register-CodexAccountSwitcher.ps1"
"$powershell" -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File "$registration_windows" -Mode Install -ControllerPath "$controller_windows" >/dev/null

status_json="$("$powershell" -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File "$controller_windows" -StatusOnly | strip_cr)"
STATUS_JSON="$status_json" node -e 'const value=JSON.parse(process.env.STATUS_JSON); if (!value.accounts?.["account-a"] || !value.accounts?.["account-b"]) process.exit(1);'

if [[ -n "$initial_active_row" ]]; then
  IFS=$'\t' read -r initial_active_key initial_active_email _ <<< "$initial_active_row"
  current_active_row="$(node "$script_dir/registry-helper.mjs" active "$registry_path")"
  IFS=$'\t' read -r current_active_key _ <<< "$current_active_row"
  if [[ "$current_active_key" != "$initial_active_key" ]]; then
    run_codex_auth switch "$initial_active_email" >/dev/null
    restored_active_row="$(node "$script_dir/registry-helper.mjs" active "$registry_path")"
    IFS=$'\t' read -r restored_active_key _ <<< "$restored_active_row"
    [[ "$restored_active_key" == "$initial_active_key" ]] || die 'The initially active account could not be restored.'
  fi
fi

"$powershell" -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File "$registration_windows" -Mode RemoveLegacy >/dev/null

legacy_dispatch="$legacy_skill_root/scripts/dispatch.sh"
if [[ -f "$default_rules_path" ]] && grep -Fq -- "$legacy_dispatch" "$default_rules_path"; then
  rules_temporary="${default_rules_path}.switcher.$$.tmp"
  awk -v needle="$legacy_dispatch" 'index($0, needle) == 0' "$default_rules_path" > "$rules_temporary"
  mv -f -- "$rules_temporary" "$default_rules_path"
fi

if [[ -d "$legacy_skill_root" && "$(realpath -m -- "$legacy_skill_root")" != "$skill_root" ]]; then
  [[ "$(basename -- "$legacy_skill_root")" == 'switch-codex-account' ]] || die 'Refusing to remove an unexpected legacy skill path.'
  rm -rf -- "$legacy_skill_root"
fi

rm -f -- "$runtime_dir_linux/Install-CodexAccountSwitcher.ps1" "$runtime_dir_linux/README.md"
rm -rf -- "$runtime_dir_linux/tests"
if [[ "$existing_mapping_kind" == 'legacy' ]]; then
  rm -f -- "$runtime_dir_linux/last-result.json" "$runtime_dir_linux/switch.log"
fi

install_succeeded=1
if ((adopted)); then
  install_mode='adopted'
else
  install_mode='configured'
fi
printf '{"status":"installed","mode":"%s","dependency":"%s@%s","skill_installations":1,"restart_required":true}\n' "$install_mode" "$PACKAGE_NAME" "$CODEX_AUTH_VERSION"
