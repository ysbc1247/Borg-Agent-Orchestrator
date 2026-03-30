# Advanced Pipeline Handoff

Timestamp: `2026-03-31 03:15 KST`

## Current Stage

- Advanced flattening is complete for the fixed-shard advanced set under `~/Documents/borg_xgboost_workspace/processed/flat_shards`
- Current non-`.DS_Store` flat-shard parquet count: `186`
- Latest successful advanced flatten log: `~/Documents/borg_xgboost_workspace/runtime/logs/20260331031358_advanced_flatten.log`

## Flatten Fixes Applied

- Replaced the earlier eager shard path with a lazy streaming path using `scan_ndjson(...).sink_parquet(...)`
- Replaced object-backed nested parsing with native struct schemas for:
  - `events.resource_request`
  - `usage.average_usage`
  - `usage.maximum_usage`
  - `machines.capacity`
- Reduced `BORG_FLATTEN_WORKERS` back to `8` after the `20`-worker run proved inefficient
- Removed unstable optional usage metric `memory_accesses_per_instruction` from flattening so failed usage shards could be regenerated

## Parquet Repair Work

- The earlier join attempt exposed six corrupt `b` usage parquet files from interrupted historical writes:
  - `b_usage-000000000005.parquet`
  - `b_usage-000000000008.parquet`
  - `b_usage-000000000009.parquet`
  - `b_usage-000000000010.parquet`
  - `b_usage-000000000012.parquet`
  - `b_usage-000000000013.parquet`
- Those files were removed and regenerated successfully
- Additional previously failed usage shards for `e`, `f`, and `g` were also regenerated successfully after the unstable field was removed

## Current Blocker

- The downstream join stage is still blocked
- Latest join log: `~/Documents/borg_xgboost_workspace/runtime/logs/20260331031434_advanced_join.log`
- Current error:

```text
polars.exceptions.SchemaError: data type mismatch for column time: incoming: Int64 != target: String
```

- No joined advanced dataset parquet has been written yet under `~/Documents/borg_xgboost_workspace/processed/datasets`

## Next Action

1. Inspect flat-shard parquet schemas for the event-related `time` column and any other mixed-type columns
2. Normalize those columns in `scripts/make_dataset.py` or at flatten time so `scan_parquet` sees a stable schema
3. Rerun join
4. Continue with advanced feature build and XGBoost training
