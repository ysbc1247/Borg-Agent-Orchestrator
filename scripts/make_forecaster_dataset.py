import os
from pathlib import Path

import polars as pl

DEFAULT_DATASET_DIR = Path.home() / "Documents" / "borg_processed" / "datasets"
DEFAULT_OUTPUT_DIR = DEFAULT_DATASET_DIR / "forecaster"
DEFAULT_CLUSTERS = ("b", "c", "d", "e", "f", "g")
DEFAULT_FAILURE_EVENT_TYPES = (2, 3, 6)
DEFAULT_PREDICTION_HORIZON = 15 * 60 * 1_000_000

DATASET_DIR = Path(os.environ.get("BORG_DATASET_DIR", DEFAULT_DATASET_DIR)).expanduser()
OUTPUT_DIR = Path(os.environ.get("BORG_FORECASTER_DIR", DEFAULT_OUTPUT_DIR)).expanduser()
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def parse_clusters() -> list[str]:
    raw = os.environ.get("BORG_CLUSTERS")
    if not raw:
        return list(DEFAULT_CLUSTERS)
    return [cluster.strip() for cluster in raw.split(",") if cluster.strip()]


def parse_failure_event_types() -> list[int]:
    raw = os.environ.get("BORG_FAILURE_EVENT_TYPES")
    if not raw:
        return list(DEFAULT_FAILURE_EVENT_TYPES)
    return [int(value.strip()) for value in raw.split(",") if value.strip()]


def prediction_horizon() -> int:
    raw = os.environ.get("BORG_PREDICTION_HORIZON_US")
    if not raw:
        return DEFAULT_PREDICTION_HORIZON
    return int(raw)


def dataset_file(cluster_id: str) -> Path:
    return DATASET_DIR / f"{cluster_id}_dataset.parquet"


def output_file(cluster_id: str) -> Path:
    return OUTPUT_DIR / f"{cluster_id}_forecaster.parquet"


def add_temporal_features(frame: pl.LazyFrame) -> pl.LazyFrame:
    task_keys = ["collection_id", "instance_index"]
    temporal_bases = [
        "avg_cpu",
        "max_cpu",
        "avg_mem",
        "max_mem",
        "avg_cpu_utilization",
        "max_cpu_utilization",
        "avg_mem_utilization",
        "max_mem_utilization",
    ]

    expressions: list[pl.Expr] = []
    for feature in temporal_bases:
        lag_expr = pl.col(feature).shift(1).over(task_keys)
        expressions.extend(
            [
                lag_expr.alias(f"{feature}_lag_1"),
                (pl.col(feature) - lag_expr).alias(f"{feature}_delta_1"),
                pl.col(feature).rolling_mean(window_size=3, min_samples=1).over(task_keys).alias(f"{feature}_roll3_mean"),
            ]
        )

    return frame.with_columns(expressions)


def build_forecaster_frame(cluster_id: str) -> pl.DataFrame:
    failure_event_types = parse_failure_event_types()
    horizon_us = prediction_horizon()

    dataset = pl.scan_parquet(dataset_file(cluster_id))

    return (
        dataset
        .sort(["collection_id", "instance_index", "end_time"])
        .with_columns(
            [
                (pl.col("last_event_time") - pl.col("end_time")).alias("time_to_terminal_event_us"),
                pl.col("final_event_type").is_in(failure_event_types).alias("is_failure_terminal_event"),
            ]
        )
        .pipe(add_temporal_features)
        .with_columns(
            [
                (
                    pl.col("is_failure_terminal_event") &
                    pl.col("time_to_terminal_event_us").is_not_null() &
                    (pl.col("time_to_terminal_event_us") >= 0) &
                    (pl.col("time_to_terminal_event_us") <= horizon_us)
                ).alias("failure_within_horizon"),
                (
                    pl.col("final_event_type").is_not_null() &
                    (pl.col("last_event_time") < pl.col("end_time"))
                ).alias("terminal_event_before_window_end"),
            ]
        )
        .select(
            [
                pl.col("cluster_id"),
                pl.col("collection_id"),
                pl.col("instance_index"),
                pl.col("machine_id"),
                pl.col("start_time"),
                pl.col("end_time"),
                pl.col("usage_window"),
                pl.col("avg_cpu"),
                pl.col("max_cpu"),
                pl.col("avg_mem"),
                pl.col("max_mem"),
                pl.col("avg_cpu_utilization"),
                pl.col("max_cpu_utilization"),
                pl.col("avg_mem_utilization"),
                pl.col("max_mem_utilization"),
                pl.col("avg_cpu_lag_1"),
                pl.col("avg_cpu_delta_1"),
                pl.col("avg_cpu_roll3_mean"),
                pl.col("max_cpu_lag_1"),
                pl.col("max_cpu_delta_1"),
                pl.col("max_cpu_roll3_mean"),
                pl.col("avg_mem_lag_1"),
                pl.col("avg_mem_delta_1"),
                pl.col("avg_mem_roll3_mean"),
                pl.col("max_mem_lag_1"),
                pl.col("max_mem_delta_1"),
                pl.col("max_mem_roll3_mean"),
                pl.col("avg_cpu_utilization_lag_1"),
                pl.col("avg_cpu_utilization_delta_1"),
                pl.col("avg_cpu_utilization_roll3_mean"),
                pl.col("max_cpu_utilization_lag_1"),
                pl.col("max_cpu_utilization_delta_1"),
                pl.col("max_cpu_utilization_roll3_mean"),
                pl.col("avg_mem_utilization_lag_1"),
                pl.col("avg_mem_utilization_delta_1"),
                pl.col("avg_mem_utilization_roll3_mean"),
                pl.col("max_mem_utilization_lag_1"),
                pl.col("max_mem_utilization_delta_1"),
                pl.col("max_mem_utilization_roll3_mean"),
                pl.col("req_cpu"),
                pl.col("req_mem"),
                pl.col("priority"),
                pl.col("scheduling_class"),
                pl.col("event_count"),
                pl.col("first_event_time"),
                pl.col("last_event_time"),
                pl.col("final_event_type"),
                pl.col("time_to_terminal_event_us"),
                pl.col("is_failure_terminal_event"),
                pl.col("failure_within_horizon").alias("target_failure_15m"),
                pl.col("terminal_event_before_window_end"),
            ]
        )
        .collect(engine="streaming")
    )


def write_forecaster_frame(cluster_id: str) -> Path:
    frame = build_forecaster_frame(cluster_id)
    path = output_file(cluster_id)
    frame.write_parquet(path)

    positive_rows = frame.filter(pl.col("target_failure_15m")).height
    positive_rate = positive_rows / frame.height if frame.height else 0.0

    print(
        f"✅ {cluster_id}: wrote {frame.height} rows to {path} "
        f"(positive labels: {positive_rows}, rate: {positive_rate:.4%})"
    )
    return path


def main() -> None:
    clusters = parse_clusters()

    print(f"Reading joined datasets from: {DATASET_DIR}")
    print(f"Writing forecaster datasets to: {OUTPUT_DIR}")
    print(f"Clusters: {clusters}")
    print(f"Failure event types: {parse_failure_event_types()}")
    print(f"Prediction horizon (us): {prediction_horizon()}")

    for cluster_id in clusters:
        path = dataset_file(cluster_id)
        if not path.exists():
            print(f"Skipping {cluster_id}: missing {path.name}")
            continue
        write_forecaster_frame(cluster_id)


if __name__ == "__main__":
    main()
