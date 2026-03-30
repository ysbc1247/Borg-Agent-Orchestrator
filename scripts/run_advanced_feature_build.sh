#!/bin/zsh

set -euo pipefail

source "$(cd "$(dirname "$0")" && pwd)/advanced_env.sh"

LOG_DIR="${HOME}/Documents/borg_xgboost_workspace/runtime/logs"
mkdir -p "${LOG_DIR}"
STAMP="$(TZ=Asia/Seoul date +%Y%m%d%H%M%S)"
LOG_FILE="${LOG_DIR}/${STAMP}_advanced_feature_build.log"
LATEST_LOG="${LOG_DIR}/latest_advanced_feature_build.log"
ln -sfn "${LOG_FILE}" "${LATEST_LOG}"
exec > >(tee -a "${LOG_FILE}") 2>&1

echo "[advanced_feature_build] started_at=${STAMP}"
echo "[advanced_feature_build] log=${LOG_FILE}"

"${BORG_ADVANCED_PYTHON}" -u "${REPO_ROOT}/scripts/build_advanced_xgboost_dataset.py"
