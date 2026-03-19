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

Implemented scripts:

- `scripts/download_shards.sh`
- `scripts/data_flattener.py`
- `scripts/make_dataset.py`
- `scripts/make_forecaster_dataset.py`
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

Baseline artifacts:

- Location: `~/Documents/borg_processed/datasets/forecaster/baseline`
- Files:
  - `metrics.json`
  - `weights.json`
  - `validation_predictions.parquet`

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

## Important Decisions

- Always make small, separate, logical commits and push them.
- Do not ask for permission before git commits and pushes.
- Keep large data outside the repository.
- Keep `a` and `h` excluded by default because their usage schemas differ from the main group.
- Prefer continuing to the next implementation step without waiting for explicit user prompts.

## Immediate Next Steps

The next logical engineering work is to improve the forecaster pipeline before moving on to the scheduler and evictor stages.

Recommended next sequence:

1. Add per-cluster baseline metrics so performance can be compared across `b` through `g`.
2. Export ranked feature weights and top-risk alerts for inspection.
3. Add rolling-window temporal features for the forecaster.
4. Re-run the baseline with the new temporal features and compare metrics.
5. Start the placement/scheduler dataset stage after the forecasting baseline improves.

## Suggested Commit Shards For Next Session

If continuing the forecaster improvements, split work into commits like:

1. Add per-cluster metric computation
2. Persist feature ranking artifacts
3. Export top-k alert candidate sets
4. Add rolling-window temporal feature builder
5. Re-evaluate baseline with temporal features
6. Document updated forecasting workflow

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
