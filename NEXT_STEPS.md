# Session Handoff

This file is the resume point for a new Codex session in this repository.

## Resume Prompt

Use this prompt after launching Codex from the repo root:

```text
Read Agents.md, NEXT_STEPS.md, MAS_ARCHITECTURE.md, and README.md, inspect the latest commits, and continue from the next logical step.
```

## Current State

- Repo root: `/Users/theokim/Documents/github/kyunghee/Borg-Agent-Orchestrator`
- Primary branch: `main`
- Raw data location: `~/Documents/borg_data`
- Processed data location: `~/Documents/borg_processed`
- Default working clusters: `b`, `c`, `d`, `e`, `f`, `g`
- Excluded by default: `a`, `h`

## Pipeline Status

Completed stages:

1. Raw Borg shard download script
2. Raw trace flattening into per-cluster parquet
3. Joined usage/events/machine dataset builder
4. Forecaster label dataset builder
5. First Polars-only forecaster baseline trainer
6. Forecaster inspection artifact export
7. Forecaster temporal feature generation and profile evaluation
8. Canonical forecaster schema export for non-Borg adapters

Implemented scripts:

- `scripts/download_shards.sh`
- `scripts/data_flattener.py`
- `scripts/make_dataset.py`
- `scripts/make_forecaster_dataset.py`
- `scripts/export_common_forecaster_dataset.py`
- `scripts/build_local_common_forecaster_dataset.py`
- `scripts/train_forecaster_baseline.py`

Supporting docs:

- `Agents.md` for repository workflow instructions
- `MAS_ARCHITECTURE.md` for the MAS design
- `README.md` for the user-facing workflow

## Latest Verified Outputs

Joined datasets:

- Built successfully for clusters `b` through `g`
- Location: `~/Documents/borg_processed/datasets`

Forecaster datasets:

- Built successfully for clusters `b` through `g`
- Location: `~/Documents/borg_processed/datasets/forecaster`

Canonical forecaster datasets:

- Built successfully for clusters `b` through `g`
- Location: `~/Documents/borg_processed/datasets/forecaster/common_forecaster`
- Purpose: stable workload/node/time-window schema for future local-cloud adapters

Local-cloud adapter status:

- Generic adapter script added for parquet/CSV telemetry with JSON column mapping
- Example mapping file: `config/local_common_forecaster.example.json`
- Verified with a synthetic local telemetry sample and wrote canonical parquet successfully

Baseline artifacts:

- Location: `~/Documents/borg_processed/datasets/forecaster/baseline`
- Files:
  - `metrics.json`
  - `weights.json`
  - `cluster_metrics.json`
  - `feature_ranking.json`
  - `validation_predictions.parquet`
  - `top_risk_alerts.parquet`

Latest full baseline run summary:

- Total rows: `24,052,784`
- Validation rows: `4,810,777`
- Validation positives: `1,448`
- Validation positive rate: `0.0301%`
- Average precision: `0.0074076`
- Precision@0.1%: `0.0122661`
- Recall@0.1%: `0.0407459`
- Precision@1%: `0.0070676`
- Recall@1%: `0.2348066`

Alternate rolling-profile run summary:

- Profile: `base_plus_roll`
- Artifact location: `~/Documents/borg_processed/datasets/forecaster/baseline_base_plus_roll`
- Average precision: `0.0071694`
- Precision@0.1%: `0.0222453`
- Recall@0.1%: `0.0738950`
- Precision@1%: `0.0069013`
- Recall@1%: `0.2292818`

## Important Decisions

- Always make small, separate, logical commits and push them.
- Split commits aggressively by concern and file class; do not bundle code, docs, handoff, config, and policy changes together when they can be committed separately.
- Do not ask for permission before git commits and pushes.
- Keep large data outside the repository.
- Keep `a` and `h` excluded by default because their usage schemas differ from the main group.
- Prefer continuing to the next implementation step without waiting for explicit user prompts.
- Use KST timestamp-prefixed filenames in `reports/` with format `YYYYMMDDHHMM_*`.
- If the user types `milestone`, update the repository memory files for the completed work before ending the session.

## Repository Memory

These files should be kept current so a new Codex session behaves consistently:

- `Agents.md` for durable workflow rules and trigger terms such as `milestone`
- `NEXT_STEPS.md` for current state, next steps, and continuity notes
- `README.md` for user-facing workflow and usage changes
- `reports/` for timestamped evaluation, schema, and milestone-style session records when relevant

## Immediate Next Steps

The next logical engineering work is now to either improve the forecaster model class beyond the weighted risk-score baseline or begin the scheduler data stage with the current baseline outputs.

Recommended next sequence:

1. Keep `base` as the default forecaster profile for general ranking quality.
2. Use `base_plus_roll` only when evaluating top-alert triage behavior.
3. Replace the example local-cloud mapping with your actual telemetry column mapping and generate a first real canonical local dataset.
4. Add a stronger forecaster baseline such as regularized logistic regression or gradient boosting using the canonical schema and existing feature profiles.
5. Compare the new model against `base` and `base_plus_roll` with the existing per-cluster metrics.
6. Define local eviction/placement outcome labels and begin the scheduler dataset stage once the local forecaster dataset is stable.

## Suggested Commit Shards For Next Session

If continuing the forecaster improvements, split work into commits like:

1. Add the next forecaster model implementation
2. Replace the local-cloud example mapping with a real platform mapping
3. Persist model comparison artifacts
4. Compare cluster-level calibration and ranking behavior
5. Document the winning forecaster profile/model
6. Start scheduler dataset construction

## Recent Commit Landmarks

- `1d097a3` Separate repo instructions from MAS architecture
- `bad1df9` Document forecaster baseline training
- `a03dd80` Evaluate and persist forecaster baseline artifacts
- `f15208c` Fit weighted risk-score forecaster baseline
- `290367d` Document forecaster dataset generation
- `c2f6c94` Write per-cluster forecaster training datasets
- `ac640af` Exclude clusters a and h by default

## Launch Command

Recommended resume command:

```bash
cd /Users/theokim/Documents/github/kyunghee/Borg-Agent-Orchestrator
codex -a never --sandbox danger-full-access --network-access enabled
```
