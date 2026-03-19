# Borg-MAS-Optimizer

Project scaffold for a Borg-inspired multi-agent scheduling and cluster optimization system.

## Structure

```text
.
├── AGENTS.md
├── MAS_ARCHITECTURE.md
├── scripts/
│   ├── download_shards.sh
│   ├── data_flattener.py
│   ├── make_dataset.py
│   ├── make_forecaster_dataset.py
│   └── train_forecaster_baseline.py
├── src/
│   ├── agents/
│   └── environment/
├── .gitignore
└── README.md
```

Note: on this filesystem, `AGENTS.md` is stored via the existing tracked [`Agents.md`](/Users/theokim/Documents/github/kyunghee/Borg-Agent-Orchestrator/Agents.md) path because filenames are case-insensitive.

## Data Layout

Raw Borg data should stay outside the repository by default.

- Default raw data path: `~/Documents/borg_data`
- Default processed data path: `~/Documents/borg_processed`

Both scripts can be overridden with environment variables:

```bash
export BORG_RAW_DIR=~/Documents/borg_data
export BORG_PROCESSED_DIR=~/Documents/borg_processed
python scripts/data_flattener.py
```

By default, the project processes clusters `b` through `g`.
Clusters `a` and `h` are excluded because their flattened usage schemas differ from the main dataset group.

To download shards into the default external location:

```bash
./scripts/download_shards.sh
```

To build joined per-window datasets for clusters `b` through `g`:

```bash
python scripts/make_dataset.py
```

To build forecaster training datasets from the joined datasets:

```bash
python scripts/make_forecaster_dataset.py
```

The forecaster builder labels a row as positive when the task's final terminal event is in the default failure set `2,3,6` and occurs within the next 15 minutes after the usage window ends.
It also writes task-history temporal features such as one-step lags, one-step deltas, and 3-window rolling means for CPU and memory usage/utilization.

To export those datasets into a platform-agnostic canonical schema that a local-cloud adapter can also target:

```bash
python scripts/export_common_forecaster_dataset.py
```

That exporter writes cluster parquet files under `~/Documents/borg_processed/datasets/forecaster/common_forecaster` by default.
The canonical schema keeps stable fields such as workload ID, node ID, window timing, observed/requested CPU and memory, temporal features, and failure labels without depending on Borg-specific column names.

To build the same canonical schema from local-cloud telemetry, prepare a parquet or CSV file plus a column-mapping JSON file and run:

```bash
python scripts/build_local_common_forecaster_dataset.py \
  --input ~/Documents/local_cloud/telemetry.parquet \
  --output ~/Documents/local_cloud/common_forecaster.parquet \
  --mapping config/local_common_forecaster.example.json \
  --source-platform local_cloud
```

The example mapping file at [`config/local_common_forecaster.example.json`](/Users/theokim/Documents/github/kyunghee/Borg-Agent-Orchestrator/config/local_common_forecaster.example.json) shows the expected `canonical_name -> raw_column` structure.

To train and evaluate the first Polars-only forecasting baseline:

```bash
python scripts/train_forecaster_baseline.py
```

The trainer supports named feature profiles through `BORG_BASELINE_PROFILE`:

- `base` keeps the strongest average-precision baseline and is the default.
- `base_plus_roll` adds rolling-mean temporal features and improves the top-risk alert slice.
- `temporal_full` adds lag, delta, and rolling temporal features for broader experimentation.

Example:

```bash
BORG_BASELINE_PROFILE=base_plus_roll \
BORG_BASELINE_DIR=~/Documents/borg_processed/datasets/forecaster/baseline_base_plus_roll \
python scripts/train_forecaster_baseline.py
```

The baseline trainer writes:

- `metrics.json`
- `weights.json`
- `cluster_metrics.json`
- `feature_ranking.json`
- `validation_predictions.parquet`
- `top_risk_alerts.parquet`

under `~/Documents/borg_processed/datasets/forecaster/baseline` by default.

## Python Environment

Use a project-local virtual environment in PyCharm and install dependencies from the repo metadata:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
