#!/bin/zsh

set -euo pipefail

source "$(cd "$(dirname "$0")" && pwd)/advanced_env.sh"

LOG_DIR="${HOME}/Documents/borg_xgboost_workspace/runtime/logs"
mkdir -p "${LOG_DIR}"
STAMP="$(TZ=Asia/Seoul date +%Y%m%d%H%M%S)"
LOG_FILE="${LOG_DIR}/${STAMP}_advanced_pipeline.log"
LATEST_LOG="${LOG_DIR}/latest_advanced_pipeline.log"
ln -sfn "${LOG_FILE}" "${LATEST_LOG}"
exec > >(tee -a "${LOG_FILE}") 2>&1

echo "[advanced_pipeline] started_at=${STAMP}"
echo "[advanced_pipeline] log=${LOG_FILE}"

"${REPO_ROOT}/scripts/run_advanced_flatten.sh"
"${REPO_ROOT}/scripts/run_advanced_join.sh"
"${REPO_ROOT}/scripts/run_advanced_feature_build.sh"
"${REPO_ROOT}/scripts/run_advanced_train.sh"
