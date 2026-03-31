# Model Directory Registry And ML Evolution

## Purpose

This report explains the XGBoost model-artifact directories under:

- `~/Documents/borg_xgboost_workspace/models/xgboost`

It focuses on two questions:

1. What each directory represents
2. How the machine-learning process evolved over time

## Directory Families

### 1. Smoke-test family

- `xgboost_smoke_target_failure_5m`

Meaning:

- This was the early smoke run used to verify that the isolated advanced XGBoost pipeline worked.
- It validated plumbing, not final model quality.

Why it exists:

- Before full training, it is standard to run a much smaller or less strict experiment to confirm:
  - feature loading works
  - training works
  - artifact export works
  - metrics export works

### 2. Baseline full advanced family

- `xgboost_failure_risk_target_failure_5m`
- `xgboost_failure_risk_target_failure_15m`
- `xgboost_failure_risk_target_failure_30m`
- `xgboost_failure_risk_target_failure_45m`
- `xgboost_failure_risk_target_failure_60m`

Meaning:

- These are the first complete multi-horizon advanced XGBoost models.
- They form the baseline family for the advanced track.

What changed compared with the smoke run:

- more data
- multi-cluster feature store
- multi-horizon training
- full artifact export
- full feature-importance export

### 3. Pilot tuning family

- `xgboost_tune_baseline_es_target_failure_5m`
- `xgboost_tune_regularized_balanced_target_failure_5m`
- `xgboost_tune_shallow_conservative_target_failure_5m`
- `xgboost_tune_wider_regularized_target_failure_5m`

Meaning:

- These are controlled tuning candidates used only for the `5m` horizon.
- They were created to compare parameter families before spending time on a full tuned retrain across all windows.

Why this step is normal:

- It is expensive to tune every horizon immediately.
- A common practice is to pick one representative horizon, run several candidate configurations, and select a winning profile.

Result:

- `regularized_balanced` won the pilot sweep and became the basis for the later full tuned retrain attempt.

### 4. Full tuned retrain family

- `xgboost_failure_risk_tuned_v1_target_failure_5m`
- `xgboost_failure_risk_tuned_v2_repaired_labels_target_failure_5m`

Meaning:

- These directories represent the attempt to turn the tuning winner into a full tuned model lineage.

Difference between the two:

- `tuned_v1`
  - first full tuned attempt
  - started before the `e/f/g` repaired-label fix
  - obsolete
- `tuned_v2_repaired_labels`
  - correct successor run
  - includes repaired `e/f/g` labels
  - current tuned branch to watch

## ML Process Evolution

The learning process evolved in the following sequence.

### Step 1. Pipeline proving

Goal:

- prove the isolated advanced XGBoost pipeline worked end to end

Artifact:

- `xgboost_smoke_target_failure_5m`

What the team learned:

- the code path for feature loading, training, scoring, and saving artifacts was operational

### Step 2. First full baseline modeling

Goal:

- train a serious baseline model family for multiple failure horizons

Artifacts:

- `xgboost_failure_risk_target_failure_5m`
- `xgboost_failure_risk_target_failure_15m`
- `xgboost_failure_risk_target_failure_30m`
- `xgboost_failure_risk_target_failure_45m`
- `xgboost_failure_risk_target_failure_60m`

What changed:

- the project moved from “can we train?” to “what is the baseline signal across windows?”

What the team learned:

- feature importance was dominated by lifecycle and event-history features
- the advanced XGBoost pipeline could produce strong internal ranking metrics
- different windows shifted importance toward short-term metadata vs longer-horizon resource-fit signals

### Step 3. Parameter tuning

Goal:

- improve the baseline with better hyperparameters while controlling overfitting through regularization and early stopping

Artifacts:

- the `xgboost_tune_*` directories

What changed:

- the team moved from “default-ish baseline” to “compare parameter families”
- this is the classic model-selection phase

What the team learned:

- `regularized_balanced` looked like the strongest pilot candidate
- the tuning artifacts were still evaluated on sampled validation data, so they were useful for comparison but not final deployment proof

### Step 4. Label-quality correction

Goal:

- repair the hidden data issue in clusters `e/f/g`

What was wrong:

- event flat shards for `e/f/g` had broken join keys
- therefore the joined datasets had no event labels
- therefore feature sets had zero positives for `e/f/g`

What changed:

- event flat shards were regenerated
- `e/f/g` joins were rerun
- `e/f/g` feature sets were rerun
- positive labels appeared again across all windows

Why this matters:

- this is not just a tuning change
- it is a data-quality correction that changes what the model can actually learn

### Step 5. Repaired-label tuned retraining

Goal:

- rerun the tuned model family on corrected labels

Artifacts:

- `xgboost_failure_risk_tuned_v1_target_failure_5m`
- `xgboost_failure_risk_tuned_v2_repaired_labels_target_failure_5m`

Interpretation:

- `tuned_v1` is a historical failed branch
- `tuned_v2_repaired_labels` is the meaningful successor

## Important Process Caveat

The current advanced XGBoost workflow uses negative downsampling in both training and validation. That means:

- the saved artifacts are valid experiment artifacts
- the metrics are useful for model-vs-model comparison
- the metrics are not yet the final production-style local-cloud numbers

So the ML process so far has evolved in this pattern:

1. infrastructure validation
2. baseline modeling
3. tuning
4. data repair
5. corrected tuned retraining
6. upcoming production-style evaluation for local-cloud transfer

## What The Final Milestone Should Add

For the local cloud milestone, the next evolution should be:

1. score final candidate models on an unsampled holdout
2. add ROC-AUC beside PR-AUC / average precision
3. compare thresholds on realistic class imbalance
4. map Borg-style features into local-cloud equivalents
5. validate whether the same feature logic still drives the model after transfer

## Directory-Level Documentation

Short `README.md` files were added directly inside the model-artifact directories under:

- `~/Documents/borg_xgboost_workspace/models/xgboost`

Those local files explain each directory in place so the artifact tree is self-describing even outside the git repository.
