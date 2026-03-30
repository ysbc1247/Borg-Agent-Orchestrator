# Advanced Feature And Training Progress

Timestamp: `2026-03-31 04:15 KST`

## Feature Build Status

- Advanced feature parquet generation is complete for clusters `b`, `c`, `d`, `e`, `f`, and `g`
- Feature store directory:
  - `~/Documents/borg_xgboost_workspace/processed/feature_store`
- Latest feature-build log:
  - `~/Documents/borg_xgboost_workspace/runtime/logs/20260331040043_advanced_feature_build.log`

## Feature Label Summary

- `b`
  - non-zero positives for `5m`, `15m`, `30m`, `45m`, `60m`
- `c`
  - non-zero positives for `5m`, `15m`, `30m`, `45m`, `60m`
- `d`
  - non-zero positives for `5m`, `15m`, `30m`, `45m`, `60m`
- `e`
  - zero positives for `5m`, `15m`, `30m`, `45m`, `60m`
- `f`
  - zero positives for `5m`, `15m`, `30m`, `45m`, `60m`
- `g`
  - zero positives for `5m`, `15m`, `30m`, `45m`, `60m`

## Training Path Changes

- Added deterministic bounded negative sampling to the advanced trainer so all positives are preserved while total train/validation rows stay within a laptop-friendly cap
- Default caps are:
  - train: `8,000,000` rows
  - validation: `2,000,000` rows
- Added resumable wrappers:
  - `scripts/run_advanced_feature_build_resumable.sh`
  - `scripts/run_advanced_train_resumable.sh`

## Training Progress

- Latest resumable training log:
  - `~/Documents/borg_xgboost_workspace/runtime/logs/20260331041159_advanced_train_resumable.log`
- Completed target:
  - `target_failure_5m`
- Current running target:
  - `target_failure_15m`

## 5-Minute Horizon Metrics

- Model directory:
  - `~/Documents/borg_xgboost_workspace/models/xgboost/xgboost_failure_risk_target_failure_5m`
- Metrics summary:
  - source train rows: `307,815,199`
  - source validation rows: `76,991,970`
  - sampled train rows: `8,003,074`
  - sampled validation rows: `2,000,796`
  - validation positives: `50,843`
  - average precision: `0.9810528429`
  - precision@0.1%: `0.9955022489`
  - recall@0.1%: `0.0391794347`
  - precision@1%: `0.9940523790`
  - recall@1%: `0.3911846272`
