# XGBoost Learning Process And Techniques

Timestamp: `2026-03-31 20:00 KST`

## Purpose

This report explains the actual XGBoost learning process used in the project after the initial test model. It is written to help a non-ML developer understand what kinds of ML techniques were used, why they were used, and what practical tradeoffs they created.

## What Came After The Test Model

After the smoke-test model proved that the isolated Advanced XGBoost pipeline could run end to end, the project moved into the real ML workflow:

1. build the joined dataset
2. engineer the feature store
3. generate multi-horizon failure labels
4. train baseline XGBoost models
5. tune candidate hyperparameter profiles
6. repair broken labels in `e/f/g`
7. restart tuned retraining on the repaired data

## Core ML Techniques Used

### 1. Multi-horizon learning

The project did not train one single model for all future failures.

Instead, it trained separate models for separate prediction windows:

- `5m`
- `15m`
- `30m`
- `45m`
- `60m`

Each model answers a slightly different question, such as:

- "Will this task fail within the next 5 minutes?"
- "Will this task fail within the next 60 minutes?"

This is useful because short-horizon and long-horizon prediction often depend on different signals.

### 2. Feature engineering

The model was not trained directly on raw Borg fields.

It used engineered features such as:

- CPU and memory usage summaries
- request-to-usage ratios
- machine-level and collection-level load
- task age
- recent failure history
- lag / delta / rolling statistics
- missingness flags

This lets XGBoost learn from operational patterns rather than only raw logs.

### 3. Time-based split

The training and validation sets were split by time rather than random row sampling.

That means:

- older windows were used for training
- newer windows were used for validation

This is closer to real production use, because the model is always asked to predict the future from the past.

### 4. Negative downsampling

Failures are rare, so negative rows massively outnumber positive rows.

To keep the training feasible on a local machine:

- all positive rows were kept
- only a fraction of negative rows were kept

This was done for both training and validation inside the current advanced trainer.

Benefits:

- much lower memory and runtime cost
- easier tuning and iteration
- more practical local training

Risk:

- PR-AUC and precision on sampled validation can look better than production reality

### 5. Lazy parquet scanning

The feature store was not loaded eagerly as one huge in-memory table.

Instead, the trainer used lazy parquet scanning and bounded sampling. This is more of a systems technique than an ML algorithm, but it is critical to making the ML workflow actually runnable on this machine.

### 6. `scale_pos_weight`

Because positives are rare, the trainer computes a class-balance weight for XGBoost:

- positives get effectively more attention
- negatives get relatively less influence

This helps the model avoid collapsing into "mostly predict normal" behavior.

### 7. Early stopping

The tuned runs use `early_stopping_rounds`.

Meaning:

- the model keeps adding trees while validation `aucpr` improves
- if validation `aucpr` stops improving for a configured number of rounds, training stops

This helps control overfitting and prevents wasting time on trees that no longer improve validation quality.

### 8. Regularization

The tuned candidates use regularization-related controls such as:

- lower `max_depth`
- higher `min_child_weight`
- `reg_alpha`
- `reg_lambda`
- `subsample`
- `colsample_bytree`

These reduce the chance that the model memorizes noisy or overly specific patterns from the training set.

### 9. Hyperparameter tuning

Before launching a full tuned retrain, the project ran a pilot tuning sweep on representative horizons.

Candidate families included:

- `baseline_es`
- `regularized_balanced`
- `shallow_conservative`
- `wider_regularized`

This is standard ML practice:

- compare a few coherent model families
- pick the most promising profile
- only then spend time on a full retrain

### 10. Feature importance export

After training, the project exported feature-importance files.

This does not prove causality, but it helps answer:

- what the model is relying on
- which signals dominate across windows
- whether the model is using sensible operational features

### 11. Validation prediction export

The pipeline also saves scored validation predictions.

This makes it possible to inspect:

- ranking behavior
- top-risk rows
- threshold effects
- later reporting and debugging

### 12. Resumable wrappers

Long-running steps such as join, feature build, and train were wrapped in resumable scripts.

This is not an ML algorithm by itself, but it is an important production engineering technique for long-running ML work on a local workstation.

## What `regularized_balanced` Means

`regularized_balanced` was the tuning profile that won the pilot sweep.

Its parameters were:

- `n_estimators=1600`
- `max_depth=6`
- `learning_rate=0.03`
- `subsample=0.9`
- `colsample_bytree=0.7`
- `min_child_weight=8`
- `reg_alpha=0.2`
- `reg_lambda=2.0`
- `early_stopping_rounds=80`

Why this profile was attractive:

- it learns slowly enough to be stable
- it uses enough trees to build a strong ensemble
- it is regularized enough to reduce aggressive overfitting
- it is not as shallow and conservative as to lose too much signal

In plain language, it was the "strong but careful" candidate.

## Data Repair As Part Of The ML Process

One of the most important discoveries in the project was that `e/f/g` initially had zero positives, not because the model was bad, but because the event-join keys were broken upstream.

That means one of the biggest ML lessons in the project was:

- good metrics are meaningless if the labeling pipeline is wrong

So the ML process in this project was not just:

- train
- tune
- compare

It also included:

- audit label quality
- repair upstream data
- rebuild features
- rerun training on corrected labels

## Practical Lessons

For a non-ML developer, the most important lessons are:

- the model only becomes trustworthy after the data pipeline is trustworthy
- high validation metrics do not automatically mean good production performance
- regularization and early stopping are guardrails against overfitting, not proof against it
- tuning is about finding a stable generalizing profile, not just making the score bigger
- exporting feature importance and validation predictions makes the ML process explainable and debuggable

## Next ML Step

The next high-value step is production-style evaluation:

- evaluate on an unsampled holdout if possible
- add explicit ROC-AUC beside PR-AUC / average precision
- compare threshold behavior under realistic class imbalance
- validate whether the same features transfer into the target local cloud environment
