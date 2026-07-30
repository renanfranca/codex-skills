#!/usr/bin/env bash

set -euo pipefail

readonly PLAYWRIGHT_IMAGE="mcr.microsoft.com/playwright:v1.62.0-jammy@sha256:b012874f829d298730411256666afcaeaeebaf505a0cf4c2f668d6dedb3d1e80"
readonly SCRIPT_DIRECTORY="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly WEBSITE_DIRECTORY="$(cd "${SCRIPT_DIRECTORY}/.." && pwd)"
readonly REPOSITORY_DIRECTORY="$(cd "${WEBSITE_DIRECTORY}/.." && pwd)"
readonly LOCAL_USER_ID="$(id -u)"
readonly LOCAL_GROUP_ID="$(id -g)"
readonly NODE_MODULES_VOLUME="codex-skills-playwright-node-modules-${LOCAL_USER_ID}-$$"

cleanup() {
  docker volume rm "${NODE_MODULES_VOLUME}" >/dev/null 2>&1 || true
}

cd "${WEBSITE_DIRECTORY}"
npm run build

docker volume create "${NODE_MODULES_VOLUME}" >/dev/null
trap cleanup EXIT

docker run --rm \
  --user root \
  --mount "type=volume,source=${NODE_MODULES_VOLUME},target=${WEBSITE_DIRECTORY}/node_modules" \
  "${PLAYWRIGHT_IMAGE}" \
  chown "${LOCAL_USER_ID}:${LOCAL_GROUP_ID}" "${WEBSITE_DIRECTORY}/node_modules"

docker run --rm --init --ipc=host \
  --user "${LOCAL_USER_ID}:${LOCAL_GROUP_ID}" \
  --workdir "${WEBSITE_DIRECTORY}" \
  --env HUSKY=0 \
  --env npm_config_cache=/tmp/codex-skills-npm-cache \
  --mount "type=bind,source=${REPOSITORY_DIRECTORY},target=${REPOSITORY_DIRECTORY}" \
  --mount "type=volume,source=${NODE_MODULES_VOLUME},target=${WEBSITE_DIRECTORY}/node_modules" \
  "${PLAYWRIGHT_IMAGE}" \
  bash -c 'npm ci && npm run test:e2e:direct -- "$@"' bash "$@"
