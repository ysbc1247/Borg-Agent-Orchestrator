# Tuning And Tuned Retrain Status

Timestamp: `2026-03-31 11:20 KST`

## Tuning Result

- Pilot tuning sweep report:
  - `~/Documents/borg_xgboost_workspace/reports/202603311104_advanced_xgboost_tuning.json`
- Selected winner:
  - `regularized_balanced`
- Winning parameter set:
  - `n_estimators=1600`
  - `max_depth=6`
  - `learning_rate=0.03`
  - `subsample=0.9`
  - `colsample_bytree=0.7`
  - `min_child_weight=8`
  - `reg_alpha=0.2`
  - `reg_lambda=2.0`
  - `early_stopping_rounds=80`

## Why This Candidate Won

- On the pilot `5m` tuning sweep, `regularized_balanced` slightly outperformed the early-stopped baseline on the combined selection score
- The main gain came from slightly stronger precision at the fixed operating budget while keeping recall effectively unchanged on the pilot sample
- The candidate is also more conservative than the original production setting, which is desirable for reducing overfitting risk

## Current Active Work

- A full tuned retrain is running under:
  - model name: `xgboost_failure_risk_tuned_v1`
  - log: `~/Documents/borg_xgboost_workspace/runtime/logs/20260331111307_advanced_train_resumable.log`
- The tuned retrain uses the same full production sampling caps as the baseline for an apples-to-apples comparison:
  - train cap: `8,000,000`
  - validation cap: `2,000,000`

## Next Decision

- When the tuned retrain finishes, compare the tuned metrics against the current baseline for all horizons
- If the tuned model is better or more stable, regenerate the English/Korean evaluation reports using the tuned artifacts and promote the tuned configuration
