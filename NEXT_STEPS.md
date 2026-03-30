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
- Advanced XGBoost workspace: `~/Documents/borg_xgboost_workspace`
- Advanced runtime: repo-local `.venv` is prepared and verified with `polars 1.39.3` and `xgboost 2.1.4`
- Default working clusters: `b`, `c`, `d`, `e`, `f`, `g`
- Excluded by default: `a`, `h`

## Pipeline Status

Advanced XGBoost track status:

- Advanced workspace root: `~/Documents/borg_xgboost_workspace`
- Advanced runtime wrappers now write timestamped stage logs under `~/Documents/borg_xgboost_workspace/runtime/logs`
- Latest successful advanced flatten log: `~/Documents/borg_xgboost_workspace/runtime/logs/20260331031358_advanced_flatten.log`
- Latest join log: `~/Documents/borg_xgboost_workspace/runtime/logs/20260331035719_advanced_join_resumable.log`
- Latest advanced feature-build log: `~/Documents/borg_xgboost_workspace/runtime/logs/20260331040043_advanced_feature_build.log`
- Latest advanced train log: `~/Documents/borg_xgboost_workspace/runtime/logs/20260331041159_advanced_train_resumable.log`
- Advanced flatten currently completed for the fixed-shard advanced set after regenerating corrupt and failed usage parquet shards
- Current flattened advanced shard count: `186` non-`.DS_Store` parquet files
- Current advanced flatten config: `BORG_FLATTEN_WORKERS=8`, `BORG_FLATTEN_HEARTBEAT_SECONDS=10`
- Advanced flatten now uses `scan_ndjson(...).sink_parquet(...)` for shard processing and logs `started ...`, `done ...`, and `heartbeat completed=...`
- Join-stage schema mismatch is fixed in `scripts/make_dataset.py` by normalizing each shard lazily before concatenation, so mixed shard schemas no longer crash `scan_parquet`
- Advanced usage flattening bug is fixed in `scripts/data_flattener.py` by casting quoted numeric NDJSON fields after scan instead of relying on `schema_overrides` for string-backed IDs/timestamps
- Advanced join rerun is now complete for clusters `b` through `g`
- Advanced feature build is now complete for clusters `b` through `g`
- Advanced training is now in progress under the resumable target-by-target runner
- Latest joined row counts:
  - `b`: `62,116,886`
  - `c`: `66,758,768`
  - `d`: `64,764,425`
  - `e`: `58,784,525`
  - `f`: `71,298,784`
  - `g`: `61,083,781`
- Current feature-build label totals:
  - `b`: non-zero positives for all configured horizons
  - `c`: non-zero positives for all configured horizons
  - `d`: non-zero positives for all configured horizons
  - `e`: zero positives for `5m`, `15m`, `30m`, `45m`, and `60m`
  - `f`: zero positives for `5m`, `15m`, `30m`, `45m`, and `60m`
  - `g`: zero positives for `5m`, `15m`, `30m`, `45m`, and `60m`
- Current training progress:
  - `target_failure_5m` completed successfully
  - `target_failure_15m` is currently running

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
- `reports/202603191933_milestone.md` for the latest milestone checkpoint

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

Local parquet documentation status:

- Schema and artifact explanation files were added beside the generated parquet and artifact directories under `~/Documents/borg_processed`
- Future parquet-producing work should continue this convention

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
- Keep the first baseline ML task under `~/Documents/borg_data` and `~/Documents/borg_processed`, but keep the new advanced/XGBoost task fully isolated under `~/Documents/borg_xgboost_workspace`.
- Keep `a` and `h` excluded by default because their usage schemas differ from the main group.
- Prefer continuing to the next implementation step without waiting for explicit user prompts.
- Use KST timestamp-prefixed filenames in `reports/` with format `YYYYMMDDHHMM_*`.
- If the user types `milestone`, update the repository memory files for the completed work before ending the session.
- When a new parquet type or artifact directory is created under `~/Documents/borg_processed`, place a schema or artifact explanation file in that same directory.
- Multi-shard raw Borg downloads should be processed through `~/Documents/borg_processed/flat_shards` rather than merged eagerly into one raw parquet file per cluster.

## Repository Memory

These files should be kept current so a new Codex session behaves consistently:

- `Agents.md` for durable workflow rules and trigger terms such as `milestone`
- `NEXT_STEPS.md` for current state, next steps, and continuity notes
- `README.md` for user-facing workflow and usage changes
- `reports/` for timestamped evaluation, schema, and milestone-style session records when relevant

Latest milestone checkpoint:

- `reports/202603271632_milestone.md`
- Use it together with `Agents.md` and this file when resuming in a new Codex context
- Latest advanced handoff snapshot: `reports/202603310315_advanced_pipeline_handoff.md`

## Immediate Next Steps

The immediate next engineering work is now to let the advanced flatten run complete or tune it further if completions remain too slow, then continue the isolated advanced XGBoost pipeline end to end.

Recommended next sequence:

1. Let `./scripts/run_advanced_xgboost_pipeline.sh` continue the current flatten run from `~/Documents/borg_xgboost_workspace/runtime/logs/20260331021002_advanced_flatten.log`.
2. Let `./scripts/run_advanced_train_resumable.sh` finish the remaining horizons `15m`, `30m`, `45m`, and `60m`.
3. Review per-horizon model artifacts for `5m`, `15m`, `30m`, `45m`, and `60m`.
4. Investigate why clusters `e`, `f`, and `g` contain zero positives in the current fixed-shard advanced slice.

Current raw-data expansion note:

- The downloader supports `sample`, `target_bytes`, and `all` modes.
- `target_bytes` now builds coherent cluster slices by completing machine and event context for a cluster before adding that cluster's usage shards.
- The advanced env now defaults to `fixed_shards` with `BORG_DOWNLOAD_SHARD_COUNT=15`, which means the first `15` event and usage shards per cluster for `b` through `g`.
- A `100 GB` raw target can be reached from the current `6.91 GB` baseline by downloading additional upstream shards.
- For cluster `b` alone, upstream contains `49` `instance_events` shards and `1,463` `instance_usage` shards.
- The acceptable stopping window can be widened with `BORG_TARGET_TOLERANCE_BYTES`, for example `100 GB` target plus `50 GB` tolerance for a practical `50–150 GB` outcome band.
- The advanced-track directory root is now `~/Documents/borg_xgboost_workspace`, and the XGBoost/raw-expansion work should use that root rather than the original baseline directories.
- `scripts/run_advanced_download.sh` now provides a one-command entrypoint that auto-loads the advanced env file and runs the coherent downloader into the isolated advanced workspace.
- The advanced-model source tree is now separated under `src/advanced_xgboost` with dedicated scripts `scripts/build_advanced_xgboost_dataset.py`, `scripts/train_advanced_xgboost.py`, and `scripts/run_advanced_xgboost_pipeline.sh`.
- The advanced XGBoost missing-data policy is now: keep label-valid rows, preserve numeric nulls into XGBoost, and add explicit missingness indicator features rather than dropping whole joined rows.
- Step wrappers now exist for the isolated advanced pipeline: `scripts/run_advanced_flatten.sh`, `scripts/run_advanced_join.sh`, `scripts/run_advanced_feature_build.sh`, `scripts/run_advanced_train.sh`, and the full-chain `scripts/run_advanced_xgboost_pipeline.sh`.
- The advanced feature parquet now carries multiple target columns for default horizons `5m`, `15m`, `30m`, `45m`, and `60m`, and the trainer fits one XGBoost model per target column without requiring separate joined datasets.
- `scripts/setup_advanced_runtime.sh` now prepares a repo-local `.venv`, and the advanced wrappers use that interpreter plus `PYTHONPATH` so the isolated pipeline can run immediately after downloads finish.
- The advanced runtime dependency issue on macOS is resolved by installing `libomp`, and `xgboost` now imports successfully from the repo-local `.venv`.
- Mixed-schema advanced parquet shards are now normalized in the joiner per file before concatenation, which avoids `polars.exceptions.SchemaError` when earlier shards were written with string-typed IDs/timestamps.
- Advanced NDJSON flattening now casts quoted numeric scalar fields after scan, because `scan_ndjson(..., schema_overrides=Int64)` was nulling usage IDs/timestamps for the fixed-shard advanced set.
- The advanced joiner now has a resumable cluster-at-a-time wrapper `scripts/run_advanced_join_resumable.sh`, and removing the global pre-group sorts from event/machine aggregation reduced join wall time enough for the full advanced join to complete successfully.
- The advanced feature and training stages now also have resumable wrappers: `scripts/run_advanced_feature_build_resumable.sh` and `scripts/run_advanced_train_resumable.sh`.
- The advanced trainer no longer concatenates the entire feature store eagerly in memory; it now scans parquet lazily, keeps all positives, and deterministically downsamples negatives to bounded train/validation row caps so multi-cluster training fits on the local machine.

## Suggested Commit Shards For Next Session

If continuing the forecaster improvements, split work into commits like:

1. Add the next forecaster model implementation
2. Replace the local-cloud example mapping with a real platform mapping
3. Persist model comparison artifacts
4. Compare cluster-level calibration and ranking behavior
5. Document the winning forecaster profile/model
6. Start scheduler dataset construction

## Recent Commit Landmarks

- `e8f06d6` Record parquet schema-note rule in handoff
- `f599a15` Require local parquet schema notes
- `7e426f2` Refresh milestone handoff state
- `fd9e0cf` Add milestone checkpoint report
- `7a70556` Update handoff continuity notes
- `e25f5e8` Record milestone persistence workflow
- `be8a3e8` Prefix report filenames with KST timestamp

## Launch Command

Recommended resume command:

```bash
cd /Users/theokim/Documents/github/kyunghee/Borg-Agent-Orchestrator
codex -a never --sandbox danger-full-access --network-access enabled
```
