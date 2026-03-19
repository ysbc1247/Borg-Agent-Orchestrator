# Schema Reference

This file records schema and type information observed from the processed Borg parquet outputs and related notes needed during analysis.

## Processed Event Parquet Schema

Source checked: `~/Documents/borg_processed/b_events.parquet`

Columns and types:

- `time`: `String`
- `type`: `String`
- `collection_id`: `String`
- `scheduling_class`: `String`
- `missing_type`: `String`
- `collection_type`: `String`
- `priority`: `String`
- `alloc_collection_id`: `String`
- `instance_index`: `String`
- `machine_id`: `String`
- `alloc_instance_index`: `String`
- `req_cpu`: `Float64`
- `req_mem`: `Float64`

Note:

- Although many event fields are stored as `String` in the processed parquet, the downstream dataset builder casts several of them to integer types before modeling.

## Event `type` Meaning

The `type` field is the Borg scheduler event enum used in `CollectionEvent` and `InstanceEvent`.

- `0`: `SUBMIT`
- `1`: `QUEUE`
- `2`: `ENABLE`
- `3`: `SCHEDULE`
- `4`: `EVICT`
- `5`: `FAIL`
- `6`: `FINISH`
- `7`: `KILL`
- `8`: `LOST`
- `9`: `UPDATE_PENDING`
- `10`: `UPDATE_RUNNING`

## Why Some Event `time` Values Are `0`

The Borg trace defines `time` as microseconds since the start of the trace.

Interpretation of `time = 0`:

- It often marks the beginning of the observation window rather than the true creation time of the workload.
- It can indicate that the workload or instance already existed when the trace began.
- It can also appear when the trace contains an initial observed state but not the prior transition that created that state.

Practical implication:

- `time = 0` should not automatically be interpreted as the true submission or creation moment.
- These rows are often better treated as initial observed state records.

## Processed Usage Parquet Schema

Source checked: `~/Documents/borg_processed/b_usage.parquet`

Columns and types:

- `start_time`: `String`
- `end_time`: `String`
- `collection_id`: `String`
- `instance_index`: `String`
- `machine_id`: `String`
- `alloc_collection_id`: `String`
- `alloc_instance_index`: `String`
- `collection_type`: `String`
- `random_sample_usage`: `Struct({'cpus': Float64})`
- `assigned_memory`: `Float64`
- `page_cache_memory`: `Float64`
- `memory_accesses_per_instruction`: `Float64`
- `sample_rate`: `Float64`
- `cpu_usage_distribution`: `List(Float64)`
- `tail_cpu_usage_distribution`: `List(Float64)`
- `avg_cpu`: `Float64`
- `avg_mem`: `Float64`
- `max_cpu`: `Float64`
- `max_mem`: `Float64`
- `cluster_id`: `String`

## Processed Machine Parquet Schema

Source checked: `~/Documents/borg_processed/b_machines.parquet`

Columns and types:

- `time`: `String`
- `machine_id`: `String`
- `type`: `String`
- `switch_id`: `String`
- `platform_id`: `String`
- `machine_cpu`: `Float64`
- `machine_mem`: `Float64`

## Modeling Note

The raw processed parquet schemas are not the same as the modeling schema.
The training pipeline casts and reshapes these columns into numeric features before building joined datasets and forecaster datasets.
