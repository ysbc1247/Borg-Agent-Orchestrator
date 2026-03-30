#!/bin/zsh

set -euo pipefail

source "$(cd "$(dirname "$0")" && pwd)/advanced_env.sh"

LOG_DIR="${HOME}/Documents/borg_xgboost_workspace/runtime/logs"
mkdir -p "${LOG_DIR}"
STAMP="$(TZ=Asia/Seoul date +%Y%m%d%H%M%S)"
LOG_FILE="${LOG_DIR}/${STAMP}_advanced_join.log"
LATEST_LOG="${LOG_DIR}/latest_advanced_join.log"
ln -sfn "${LOG_FILE}" "${LATEST_LOG}"
exec > >(tee -a "${LOG_FILE}") 2>&1

echo "[advanced_join] started_at=${STAMP}"
echo "[advanced_join] log=${LOG_FILE}"

"${BORG_ADVANCED_PYTHON}" -u "${REPO_ROOT}/scripts/make_dataset.py"
