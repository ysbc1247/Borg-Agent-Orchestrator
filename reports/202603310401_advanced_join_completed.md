# Advanced Join Completed

Timestamp: `2026-03-31 04:01 KST`

## Outcome

- The advanced joined dataset stage is now complete for clusters `b`, `c`, `d`, `e`, `f`, and `g`
- Final resumable join log:
  - `~/Documents/borg_xgboost_workspace/runtime/logs/20260331035719_advanced_join_resumable.log`

## Final Joined Row Counts

- `b`: `62,116,886`
- `c`: `66,758,768`
- `d`: `64,764,425`
- `e`: `58,784,525`
- `f`: `71,298,784`
- `g`: `61,083,781`

## Important Fixes That Enabled Completion

- `scripts/data_flattener.py`
  - Stopped relying on `scan_ndjson(..., schema_overrides=Int64)` for quoted numeric usage fields
  - Casts numeric scalar fields after scan with `strict=False`
- `scripts/make_dataset.py`
  - Normalizes each mixed-schema parquet shard before concatenation
  - Removed the final dataset-wide sort before collect
  - Replaced global event/machine pre-group sorts with grouped `sort_by(...).last()` aggregations
- `scripts/run_advanced_join_resumable.sh`
  - Runs one cluster at a time and skips completed datasets so failures can be retried from the failed cluster instead of restarting the full stage

## Next Step

- Run `./scripts/run_advanced_feature_build.sh`
- Then run `./scripts/run_advanced_train.sh`
