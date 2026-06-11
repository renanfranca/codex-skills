#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="${SEED4J_REPO_ROOT:-/home/renanfranca/projects/seed4j-cli}"
WORKTREE_ROOT="${SEED4J_WORKTREE_ROOT:-/home/renanfranca/projects/seed4j-cli-worktree}"
BASE_BRANCH="${SEED4J_BASE_BRANCH:-main}"

usage() {
  cat <<'USAGE'
Usage:
  seed4j_worktree_flow.sh status
  seed4j_worktree_flow.sh start <branch>
  seed4j_worktree_flow.sh finish <branch>

Environment overrides:
  SEED4J_REPO_ROOT       Default: /home/renanfranca/projects/seed4j-cli
  SEED4J_WORKTREE_ROOT   Default: /home/renanfranca/projects/seed4j-cli-worktree
  SEED4J_BASE_BRANCH     Default: main
USAGE
}

fail() {
  printf 'ERROR: %s\n' "$*" >&2
  exit 1
}

require_repo() {
  [[ -d "$REPO_ROOT/.git" || -f "$REPO_ROOT/.git" ]] || fail "Repository not found at $REPO_ROOT"
  git -C "$REPO_ROOT" rev-parse --is-inside-work-tree >/dev/null
  git -C "$REPO_ROOT" show-ref --verify --quiet "refs/heads/$BASE_BRANCH" || fail "Base branch '$BASE_BRANCH' does not exist locally"
}

require_branch_name() {
  local branch="${1:-}"

  [[ -n "$branch" ]] || fail "Missing branch name"
  [[ "$branch" != "$BASE_BRANCH" ]] || fail "Refusing to operate on base branch '$BASE_BRANCH'"
  git check-ref-format --branch "$branch" >/dev/null || fail "Invalid branch name: $branch"
}

worktree_path_for() {
  local branch="$1"

  printf '%s/%s\n' "$WORKTREE_ROOT" "$branch"
}

branch_exists() {
  local branch="$1"

  git -C "$REPO_ROOT" show-ref --verify --quiet "refs/heads/$branch"
}

branch_checked_out() {
  local branch="$1"

  git -C "$REPO_ROOT" worktree list --porcelain | grep -Fxq "branch refs/heads/$branch"
}

known_worktree_path() {
  local path="$1"

  git -C "$REPO_ROOT" worktree list --porcelain | grep -Fxq "worktree $path"
}

worktree_branch() {
  local path="$1"

  git -C "$path" branch --show-current
}

dirty_state() {
  local path="$1"

  if [[ -n "$(git -C "$path" status --porcelain)" ]]; then
    printf 'dirty'
  else
    printf 'clean'
  fi
}

merged_into_base() {
  local branch="$1"

  git -C "$REPO_ROOT" merge-base --is-ancestor "$branch" "$BASE_BRANCH"
}

ahead_count() {
  local branch="$1"

  git -C "$REPO_ROOT" rev-list --count "$BASE_BRANCH..$branch"
}

print_status() {
  require_repo

  printf 'Repository: %s\n' "$REPO_ROOT"
  printf 'Worktree root: %s\n' "$WORKTREE_ROOT"
  printf 'Base branch: %s\n\n' "$BASE_BRANCH"

  printf 'Worktrees:\n'
  git -C "$REPO_ROOT" worktree list
  printf '\n'

  while IFS= read -r path; do
    [[ -n "$path" ]] || continue

    local branch
    local state
    branch="$(worktree_branch "$path")"
    state="$(dirty_state "$path")"

    if [[ -n "$branch" && "$branch" != "$BASE_BRANCH" ]]; then
      if merged_into_base "$branch"; then
        printf '%s -> %s, %s, merged into %s\n' "$path" "$branch" "$state" "$BASE_BRANCH"
      else
        printf '%s -> %s, %s, %s commits ahead of %s\n' "$path" "$branch" "$state" "$(ahead_count "$branch")" "$BASE_BRANCH"
      fi
    else
      printf '%s -> %s, %s\n' "$path" "${branch:-detached}" "$state"
    fi
  done < <(git -C "$REPO_ROOT" worktree list --porcelain | awk '/^worktree / { sub(/^worktree /, ""); print }')
}

start_worktree() {
  local branch="$1"
  local target

  require_repo
  require_branch_name "$branch"
  target="$(worktree_path_for "$branch")"

  [[ ! -e "$target" ]] || fail "Target path already exists: $target"
  branch_checked_out "$branch" && fail "Branch '$branch' is already checked out in another worktree"

  mkdir -p "$WORKTREE_ROOT"

  if branch_exists "$branch"; then
    printf '+ git -C %s worktree add %s %s\n' "$REPO_ROOT" "$target" "$branch"
    git -C "$REPO_ROOT" worktree add "$target" "$branch"
  else
    printf '+ git -C %s worktree add -b %s %s %s\n' "$REPO_ROOT" "$branch" "$target" "$BASE_BRANCH"
    git -C "$REPO_ROOT" worktree add -b "$branch" "$target" "$BASE_BRANCH"
  fi

  printf '\nCreated worktree: %s\n' "$target"
  printf 'Next step: cd %s\n' "$target"
}

finish_worktree() {
  local branch="$1"
  local target
  local active_branch

  require_repo
  require_branch_name "$branch"
  target="$(worktree_path_for "$branch")"

  known_worktree_path "$target" || fail "Path is not a known worktree: $target"
  active_branch="$(worktree_branch "$target")"
  [[ "$active_branch" == "$branch" ]] || fail "Expected '$target' to be on '$branch', found '${active_branch:-detached}'"
  [[ "$(dirty_state "$target")" == "clean" ]] || fail "Worktree is dirty: $target"
  branch_exists "$branch" || fail "Branch '$branch' does not exist locally"
  merged_into_base "$branch" || fail "Branch '$branch' is not merged into '$BASE_BRANCH'"

  printf '+ git -C %s worktree remove %s\n' "$REPO_ROOT" "$target"
  git -C "$REPO_ROOT" worktree remove "$target"

  printf '+ git -C %s branch -d %s\n' "$REPO_ROOT" "$branch"
  git -C "$REPO_ROOT" branch -d "$branch"

  printf '\nRemoved worktree and local branch: %s\n' "$branch"
}

main() {
  local command="${1:-}"

  case "$command" in
    status)
      print_status
      ;;
    start)
      start_worktree "${2:-}"
      ;;
    finish)
      finish_worktree "${2:-}"
      ;;
    -h|--help|help)
      usage
      ;;
    *)
      usage >&2
      exit 2
      ;;
  esac
}

main "$@"
