#!/bin/zsh

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ENV_FILE="${BORG_ADVANCED_ENV_FILE:-$HOME/Documents/borg_xgboost_workspace/config/advanced_xgboost.env}"

"${REPO_ROOT}/scripts/setup_advanced_xgboost_workspace.sh" >/dev/null

if [[ ! -f "${ENV_FILE}" ]]; then
  cp "${REPO_ROOT}/config/advanced_xgboost.env.example" "${ENV_FILE}"
fi

set -a
source "${ENV_FILE}"
set +a

"${REPO_ROOT}/scripts/download_shards.sh"
