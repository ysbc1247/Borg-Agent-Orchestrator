# Feature Importance Evaluation Across Windows

## Scope

This report summarizes the saved `feature_importance.json` artifacts for the finished baseline advanced XGBoost models:

- `xgboost_failure_risk_target_failure_5m`
- `xgboost_failure_risk_target_failure_15m`
- `xgboost_failure_risk_target_failure_30m`
- `xgboost_failure_risk_target_failure_45m`
- `xgboost_failure_risk_target_failure_60m`

The reported importance values are the model-exported XGBoost feature importances for each prediction horizon. They are useful for ranking which inputs the model relied on most, but they are not causal explanations.

## Main Findings

### 1. Two features dominate every window

Across all five windows, the models are dominated by:

- `task_age_us`
- `event_count`

Average importance across windows:

| Feature | Mean importance |
| --- | ---: |
| `task_age_us` | `0.688633` |
| `event_count` | `0.130892` |

Interpretation:

- `task_age_us` is the strongest signal by a very large margin in every model.
- `event_count` is the second strongest signal in every model.
- Together, they account for most of the model’s total importance mass.

This means the baseline advanced models are relying heavily on task maturity and event-history density to estimate near-term failure risk.

## Stable Core Features

These features remain important across most or all windows:

| Feature | Mean importance | Pattern |
| --- | ---: | --- |
| `task_age_us` | `0.688633` | Dominant at every horizon, slightly decreases as horizon length grows |
| `event_count` | `0.130892` | Strong and stable second feature across all horizons |
| `observed_failure_by_window` | `0.015891` | Stable prior-failure signal |
| `scheduling_class` | `0.015795` | Stable scheduling-policy signal |
| `priority` | `0.015499` | Strong at short windows, weaker later |
| `collection_recent_failure_count_12` | `0.008749` | Important across all windows, stronger at longer windows |
| `collection_recent_terminal_count_12` | `0.006563` | Stable historical terminal-event signal |
| `usage_window` | `0.006031` | Consistently useful, but secondary |
| `collection_window_avg_mem_sum` | `0.005524` | Stable workload-level load signal |
| `machine_recent_terminal_count_12` | `0.005028` | Stable machine-history signal |

## Top 10 Features By Window

### 5-minute model

1. `task_age_us` `0.717560`
2. `event_count` `0.134272`
3. `priority` `0.024799`
4. `observed_failure_by_window` `0.014286`
5. `scheduling_class` `0.012484`
6. `collection_recent_failure_count_12` `0.006880`
7. `avg_mem_to_request_ratio` `0.006291`
8. `usage_window` `0.006038`
9. `collection_window_avg_cpu_sum` `0.005629`
10. `collection_recent_terminal_count_12` `0.005353`

### 15-minute model

1. `task_age_us` `0.705644`
2. `event_count` `0.127874`
3. `priority` `0.025674`
4. `observed_failure_by_window` `0.015609`
5. `scheduling_class` `0.015569`
6. `collection_recent_failure_count_12` `0.008486`
7. `collection_recent_terminal_count_12` `0.006029`
8. `usage_window` `0.005710`
9. `collection_window_avg_mem_sum` `0.005257`
10. `req_cpu` `0.004991`

### 30-minute model

1. `task_age_us` `0.688073`
2. `event_count` `0.130745`
3. `scheduling_class` `0.016288`
4. `observed_failure_by_window` `0.015926`
5. `priority` `0.014835`
6. `req_cpu` `0.012222`
7. `collection_recent_failure_count_12` `0.007948`
8. `usage_window` `0.006907`
9. `collection_recent_terminal_count_12` `0.006522`
10. `max_mem_to_request_ratio` `0.006485`

### 45-minute model

1. `task_age_us` `0.675809`
2. `event_count` `0.128991`
3. `req_cpu` `0.019481`
4. `scheduling_class` `0.017011`
5. `observed_failure_by_window` `0.016949`
6. `collection_recent_failure_count_12` `0.008659`
7. `avg_mem_to_request_ratio` `0.007975`
8. `collection_recent_terminal_count_12` `0.007345`
9. `max_mem_to_request_ratio` `0.006408`
10. `usage_window` `0.006111`

### 60-minute model

1. `task_age_us` `0.656080`
2. `event_count` `0.132580`
3. `avg_mem_to_request_ratio` `0.018261`
4. `scheduling_class` `0.017623`
5. `req_cpu` `0.017073`
6. `observed_failure_by_window` `0.016685`
7. `collection_recent_failure_count_12` `0.011769`
8. `collection_recent_terminal_count_12` `0.007565`
9. `cpu_request_ratio` `0.007500`
10. `priority` `0.006286`

## Cross-Window Trends

### Short-window models rely more on workflow metadata

The `5m` and `15m` models place relatively more weight on:

- `priority`
- `scheduling_class`
- immediate historical failure indicators

Interpretation:

- For very short-horizon prediction, the model is leaning more on task urgency, scheduling context, and whether the task already shows signs of trouble.

### Longer-window models rely more on resource shape

The `30m` to `60m` models place relatively more weight on:

- `req_cpu`
- `avg_mem_to_request_ratio`
- `cpu_request_ratio`
- `max_mem_to_request_ratio`
- `req_mem`

Interpretation:

- Longer-horizon predictions rely more on whether the task looks structurally mismatched to its requested resources and machine capacity.
- This is a reasonable pattern: future risk further out is often tied to persistent resource pressure rather than only immediate near-failure symptoms.

### History features become more important as horizon grows

Features like:

- `collection_recent_failure_count_12`
- `collection_recent_terminal_count_12`
- `machine_recent_terminal_count_12`

become more important in the longer windows.

Interpretation:

- The further ahead the prediction horizon, the more the model uses accumulated instability history from the task’s broader context.

## Features With Near-Zero Importance

Many missingness flags have zero importance in the saved baseline models, especially in the `5m` model.

Interpretation:

- Either the corresponding source columns are rarely missing in this training slice, or
- the raw feature values already capture the useful signal, so the missingness indicator adds little.

This does not mean the missingness flags were a mistake. It means they were a low-usage safety feature in the current training data.

## Operational Reading

At a high level, the baseline advanced XGBoost models are mainly using four groups of evidence:

1. Lifecycle state
   - `task_age_us`
   - `usage_window`

2. Event-history density and prior instability
   - `event_count`
   - `observed_failure_by_window`
   - recent failure / terminal counters

3. Scheduling and task policy
   - `priority`
   - `scheduling_class`

4. Resource fit and pressure
   - `req_cpu`, `req_mem`
   - request ratios
   - memory-to-request ratios
   - collection and machine window load sums

This is directionally sensible for failure prediction: the models appear to combine “how old is the task,” “has it already shown signs of trouble,” “what scheduling regime is it in,” and “does its resource behavior look mismatched to its environment.”

## Risks And Limits

- These importances come from the saved baseline models, not the still-running repaired-label tuned retrain.
- Importance does not mean causation.
- If two features are highly correlated, importance can be split unevenly between them.
- The models were evaluated on a sampled validation set, so strong importance rankings do not by themselves prove strong production generalization.
- The very large dominance of `task_age_us` means the model may be relying heavily on lifecycle effects; this should be checked carefully when moving to a local cloud environment.

## Recommendation For The Final Milestone

Before deploying to the local cloud environment, compare whether these same top features remain dominant after:

- training on repaired-label tuned models
- evaluating on an unsampled holdout
- validating on local-cloud-shaped data

If the same features remain stable, that is a good sign for transferability. If they change sharply, the Borg-based model may be depending on dataset-specific shortcuts rather than durable operational signals.
