# Feature Dictionary Explained

## Purpose

This report explains what the advanced XGBoost feature columns mean in plain language.

The goal is to make the model inputs understandable to a reader who is not deep in machine learning. The descriptions here are especially useful for the final project milestone, where the model will later be adapted to a local cloud environment.

## How To Read These Features

A feature is just one measured or derived property of a task at a given time window.

The model does not see a whole task “story” directly. It sees many columns such as:

- how much CPU was used
- how much memory was used
- how old the task is
- how many events happened around it
- how crowded the machine is
- whether similar failures recently happened nearby

Then it combines those signals to estimate the risk of failure in the next `5m`, `15m`, `30m`, `45m`, or `60m`.

## Important Notes

- `priority` and `scheduling_class` are metadata from the workload scheduler, not the model’s own output.
- Ratios such as `avg_mem_to_request_ratio` are “how much was used relative to what was requested.”
- Features ending in `_lag_1`, `_delta_1`, or `_roll3_mean` are time-series features derived from the same task’s recent past.
- Features ending in `_is_missing` are binary indicators that mark whether the source value was missing.

## Feature Groups

### 1. Basic usage features

These describe direct resource usage inside the current observation window.

| Feature | Meaning |
| --- | --- |
| `usage_window` | Length or size of the usage observation window for the row |
| `avg_cpu` | Average CPU used during the window |
| `max_cpu` | Maximum CPU used during the window |
| `avg_mem` | Average memory used during the window |
| `max_mem` | Maximum memory used during the window |
| `avg_cpu_utilization` | Average CPU usage normalized as utilization |
| `max_cpu_utilization` | Peak CPU utilization in the window |
| `avg_mem_utilization` | Average memory utilization in the window |
| `max_mem_utilization` | Peak memory utilization in the window |

Operational meaning:

- These tell you whether the task is lightly loaded, steadily loaded, or showing peaks/spikes.

### 2. Requested resource and scheduler metadata

These describe what the task asked for and how it was classified by the scheduler.

| Feature | Meaning |
| --- | --- |
| `req_cpu` | CPU requested by the task |
| `req_mem` | Memory requested by the task |
| `priority` | Scheduler priority level of the task |
| `scheduling_class` | Scheduler class or policy bucket for the task |

Operational meaning:

- `priority` usually reflects how important or urgent the workload is to the scheduler.
- `scheduling_class` usually reflects what kind of placement/handling policy the scheduler uses.
- These can matter because urgent or special-class tasks may behave differently from background or batch tasks.

### 3. Lifecycle and event-history features

These describe where the task is in its life and how much event activity it has accumulated.

| Feature | Meaning |
| --- | --- |
| `event_count` | Number of joined event records linked to the task |
| `task_age_us` | Time elapsed from the task’s first observed event to the current window end |
| `observed_failure_by_window` | Whether a failure-like terminal pattern was already seen before the current window end |
| `machine_recent_failure_count_12` | Recent failure count on the same machine over the previous 12 observed windows |
| `collection_recent_failure_count_12` | Recent failure count in the same collection over the previous 12 windows |
| `machine_recent_terminal_count_12` | Recent terminal-event count on the same machine over the previous 12 windows |
| `collection_recent_terminal_count_12` | Recent terminal-event count in the same collection over the previous 12 windows |

Operational meaning:

- `task_age_us` answers: “How old is this task right now?”
- `event_count` answers: “How much scheduler/event activity has happened around this task?”
- The “recent failure” and “recent terminal” features answer: “Has this neighborhood already been unstable lately?”

### 4. Machine capacity features

These describe the machine’s available capacity.

| Feature | Meaning |
| --- | --- |
| `machine_cpu` | CPU capacity of the assigned machine |
| `machine_mem` | Memory capacity of the assigned machine |

Operational meaning:

- These let the model compare the task’s size to the machine’s size.

### 5. Resource-fit ratio features

These compare usage or requests against requested or available capacity.

| Feature | Meaning |
| --- | --- |
| `cpu_request_ratio` | Requested CPU divided by machine CPU |
| `mem_request_ratio` | Requested memory divided by machine memory |
| `avg_cpu_to_request_ratio` | Average CPU usage divided by requested CPU |
| `avg_mem_to_request_ratio` | Average memory usage divided by requested memory |
| `max_cpu_to_request_ratio` | Peak CPU usage divided by requested CPU |
| `max_mem_to_request_ratio` | Peak memory usage divided by requested memory |

Operational meaning:

- Values near or above `1` often mean the task is using close to or above its requested level.
- These are useful for detecting resource under-requesting or workload mismatch.

### 6. Headroom and spike features

These describe slack and burstiness.

| Feature | Meaning |
| --- | --- |
| `cpu_headroom` | Machine CPU minus average task CPU usage |
| `mem_headroom` | Machine memory minus average task memory usage |
| `cpu_spike_gap` | Peak CPU minus average CPU |
| `mem_spike_gap` | Peak memory minus average memory |

Operational meaning:

- `headroom` answers: “How much space is left?”
- `spike_gap` answers: “How bursty is this task compared with its normal level?”

### 7. Machine-level and collection-level crowding features

These describe how crowded the environment is during the same window.

| Feature | Meaning |
| --- | --- |
| `machine_task_count_window` | Number of tasks on the same machine in the current window |
| `collection_task_count_window` | Number of tasks in the same collection in the current window |
| `machine_window_avg_cpu_sum` | Sum of average CPU across tasks on the same machine in the same window |
| `machine_window_avg_mem_sum` | Sum of average memory across tasks on the same machine in the same window |
| `machine_window_avg_cpu_load_ratio` | Machine-level average CPU load normalized by machine capacity |
| `machine_window_avg_mem_load_ratio` | Machine-level average memory load normalized by machine capacity |
| `collection_window_avg_cpu_sum` | Sum of average CPU across tasks in the same collection and window |
| `collection_window_avg_mem_sum` | Sum of average memory across tasks in the same collection and window |

Operational meaning:

- These answer questions like:
  - “Is the host crowded?”
  - “Is this whole collection busy right now?”
  - “Is failure risk coming from local task behavior, or from a crowded environment?”

### 8. Variability features

These describe recent instability or volatility within the task’s own time series.

| Feature | Meaning |
| --- | --- |
| `avg_cpu_roll6_std` | Standard deviation of average CPU over the last 6 observations |
| `avg_mem_roll6_std` | Standard deviation of average memory over the last 6 observations |
| `avg_cpu_utilization_roll6_std` | Standard deviation of average CPU utilization over the last 6 observations |
| `avg_mem_utilization_roll6_std` | Standard deviation of average memory utilization over the last 6 observations |

Operational meaning:

- High values mean the task is unstable or fluctuating over time.

### 9. Short-history temporal features

These compare the current observation to the task’s own recent past.

#### Lag features

| Feature | Meaning |
| --- | --- |
| `avg_cpu_lag_1` | Previous window’s average CPU |
| `max_cpu_lag_1` | Previous window’s max CPU |
| `avg_mem_lag_1` | Previous window’s average memory |
| `max_mem_lag_1` | Previous window’s max memory |
| `avg_cpu_utilization_lag_1` | Previous window’s average CPU utilization |
| `max_cpu_utilization_lag_1` | Previous window’s max CPU utilization |
| `avg_mem_utilization_lag_1` | Previous window’s average memory utilization |
| `max_mem_utilization_lag_1` | Previous window’s max memory utilization |

#### Delta features

| Feature | Meaning |
| --- | --- |
| `avg_cpu_delta_1` | Current average CPU minus previous average CPU |
| `max_cpu_delta_1` | Current max CPU minus previous max CPU |
| `avg_mem_delta_1` | Current average memory minus previous average memory |
| `max_mem_delta_1` | Current max memory minus previous max memory |
| `avg_cpu_utilization_delta_1` | Current average CPU utilization minus previous average CPU utilization |
| `max_cpu_utilization_delta_1` | Current max CPU utilization minus previous max CPU utilization |
| `avg_mem_utilization_delta_1` | Current average memory utilization minus previous average memory utilization |
| `max_mem_utilization_delta_1` | Current max memory utilization minus previous max memory utilization |

#### Short rolling means

| Feature | Meaning |
| --- | --- |
| `avg_cpu_roll3_mean` | Mean of average CPU over the last 3 observations |
| `max_cpu_roll3_mean` | Mean of max CPU over the last 3 observations |
| `avg_mem_roll3_mean` | Mean of average memory over the last 3 observations |
| `max_mem_roll3_mean` | Mean of max memory over the last 3 observations |
| `avg_cpu_utilization_roll3_mean` | Mean of average CPU utilization over the last 3 observations |
| `max_cpu_utilization_roll3_mean` | Mean of max CPU utilization over the last 3 observations |
| `avg_mem_utilization_roll3_mean` | Mean of average memory utilization over the last 3 observations |
| `max_mem_utilization_roll3_mean` | Mean of max memory utilization over the last 3 observations |

Operational meaning:

- Lag features tell the model what happened just before now.
- Delta features tell it whether the task is rising, falling, or changing sharply.
- Rolling means smooth out noise and show short-term trend.

### 10. Missingness flags

These are binary indicators like:

- `avg_cpu_is_missing`
- `req_mem_is_missing`
- `cpu_request_ratio_is_missing`
- `collection_recent_failure_count_12_is_missing`

Meaning:

- `1` means the source feature was missing for that row.
- `0` means the source feature was present.

Operational meaning:

- Sometimes “missing” is itself informative.
- In the saved baseline models, most of these flags had near-zero importance, which suggests the current data slice was fairly complete or the raw value columns already carried most of the usable information.

## Features Most Important In Practice

From the saved baseline models, the most operationally important features were mostly:

- `task_age_us`
- `event_count`
- `observed_failure_by_window`
- `scheduling_class`
- `priority`
- `collection_recent_failure_count_12`
- `req_cpu`
- `avg_mem_to_request_ratio`

This means the model is mostly asking:

1. How old is the task?
2. How much event activity has already happened around it?
3. Has it or its neighborhood already shown signs of failure?
4. What scheduler regime is it running under?
5. Does its resource usage look mismatched to what it requested?

## Mapping Guidance For The Future Local Cloud Milestone

When adapting to a local cloud environment, the safest feature priorities are:

### Highest priority to preserve

- Task/window timestamps
- CPU and memory usage
- CPU and memory requests or limits
- priority / scheduling metadata if available
- machine capacity
- terminal-event / failure history

### Good to preserve if possible

- machine-level concurrent task counts
- collection or service-level aggregated load
- recent temporal history per task

### Acceptable to approximate if exact equivalents do not exist

- Borg-specific scheduling class buckets
- Borg collection grouping if your local cloud uses service/job/application grouping instead
- event-count semantics if the local platform emits different lifecycle events

## Final Caution

These feature names are meaningful because they were built from Borg-style data joins. When moving to a local cloud:

- keep the operational meaning the same, not necessarily the original field name
- preserve directionality and units where possible
- document any feature substitutions carefully

For example:

- Borg `collection_id` may map to a local cloud service, deployment, job, or tenant identifier
- Borg `priority` may map to queue priority, QoS tier, or scheduling policy
- Borg `event_count` may map to restart count, lifecycle-transition count, or orchestration-event count

The strongest transfer strategy is to preserve semantics, not exact schema wording.
