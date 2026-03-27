#!/bin/zsh

set -euo pipefail

ADVANCED_ROOT="${BORG_ADVANCED_ROOT:-$HOME/Documents/borg_xgboost_workspace}"

echo "Creating advanced workspace under ${ADVANCED_ROOT}..."

mkdir -p \
  "${ADVANCED_ROOT}/raw/events" \
  "${ADVANCED_ROOT}/raw/machines" \
  "${ADVANCED_ROOT}/raw/usage" \
  "${ADVANCED_ROOT}/processed/flat_shards" \
  "${ADVANCED_ROOT}/processed/datasets" \
  "${ADVANCED_ROOT}/processed/common_forecaster" \
  "${ADVANCED_ROOT}/processed/training_matrices" \
  "${ADVANCED_ROOT}/processed/feature_store" \
  "${ADVANCED_ROOT}/models/xgboost" \
  "${ADVANCED_ROOT}/models/ensembles" \
  "${ADVANCED_ROOT}/models/checkpoints" \
  "${ADVANCED_ROOT}/reports" \
  "${ADVANCED_ROOT}/runtime/logs" \
  "${ADVANCED_ROOT}/runtime/tmp" \
  "${ADVANCED_ROOT}/config"

cat > "${ADVANCED_ROOT}/README.md" <<EOF
# Advanced Borg XGBoost Workspace

This workspace is reserved for the second machine-learning track.

Directory intent:

- raw/: original downloaded Borg JSON shards for the advanced track only
- processed/: flattened parquet, feature sets, and training matrices for the advanced track
- models/: trained model artifacts, checkpoints, and ensemble outputs
- reports/: evaluation reports and experiment summaries
- runtime/: transient logs and temporary run files
- config/: copied or generated runtime configuration files for the advanced track

Recommended environment variables:

- BORG_RAW_DIR=${ADVANCED_ROOT}/raw
- BORG_PROCESSED_DIR=${ADVANCED_ROOT}/processed
- BORG_XGBOOST_MODEL_DIR=${ADVANCED_ROOT}/models/xgboost
- BORG_REPORT_DIR=${ADVANCED_ROOT}/reports
- TMPDIR=${ADVANCED_ROOT}/runtime/tmp

Keep this workspace separate from:

- ~/Documents/borg_data
- ~/Documents/borg_processed
EOF

echo "Advanced workspace ready."
echo "Root: ${ADVANCED_ROOT}"
