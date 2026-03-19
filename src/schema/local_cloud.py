from __future__ import annotations

from typing import Any

import polars as pl

from src.schema.common import COMMON_FORECASTER_COLUMNS
from src.schema.common import COMMON_FORECASTER_SCHEMA_VERSION

REQUIRED_LOCAL_MAPPING_KEYS = (
    "source_workload_id",
    "source_workload_instance_id",
    "source_node_id",
    "window_start_us",
    "window_end_us",
    "observed_cpu_avg",
    "observed_cpu_peak",
    "observed_mem_avg",
    "observed_mem_peak",
)

OPTIONAL_LOCAL_COLUMNS = {
    "source_cluster_id": (pl.Utf8, None),
    "observed_cpu_avg_ratio": (pl.Float64, None),
    "observed_cpu_peak_ratio": (pl.Float64, None),
    "observed_mem_avg_ratio": (pl.Float64, None),
    "observed_mem_peak_ratio": (pl.Float64, None),
    "requested_cpu": (pl.Float64, None),
    "requested_mem": (pl.Float64, None),
    "workload_priority": (pl.Int64, None),
    "workload_class": (pl.Int64, None),
    "event_count": (pl.Int64, 0),
    "terminal_event_time_us": (pl.Int64, None),
    "terminal_event_type": (pl.Int64, None),
    "is_failure_terminal_event": (pl.Boolean, None),
    "target_failure_within_horizon": (pl.Boolean, None),
    "terminal_event_before_window_end": (pl.Boolean, None),
}

TEMPORAL_FEATURE_SPECS = (
    ("observed_cpu_avg", "cpu_avg"),
    ("observed_cpu_peak", "cpu_peak"),
    ("observed_mem_avg", "mem_avg"),
    ("observed_mem_peak", "mem_peak"),
    ("observed_cpu_avg_ratio", "cpu_avg_ratio"),
    ("observed_cpu_peak_ratio", "cpu_peak_ratio"),
    ("observed_mem_avg_ratio", "mem_avg_ratio"),
    ("observed_mem_peak_ratio", "mem_peak_ratio"),
)


def _missing_expr(name: str, dtype: pl.DataType, default: Any) -> pl.Expr:
    return pl.lit(default, dtype=dtype).alias(name)


def _rename_using_mapping(frame: pl.DataFrame, mapping: dict[str, str]) -> pl.DataFrame:
    missing = [key for key in REQUIRED_LOCAL_MAPPING_KEYS if key not in mapping]
    if missing:
        raise ValueError(f"Local mapping is missing required canonical keys: {missing}")

    missing_columns = [raw_name for raw_name in mapping.values() if raw_name not in frame.columns]
    if missing_columns:
        raise ValueError(f"Input data is missing mapped source columns: {missing_columns}")

    selected = [pl.col(raw_name).alias(canonical_name) for canonical_name, raw_name in mapping.items()]
    return frame.select(selected)


def _ensure_optional_columns(frame: pl.DataFrame, default_cluster_id: str | None) -> pl.DataFrame:
    expressions: list[pl.Expr] = []
    for name, (dtype, default) in OPTIONAL_LOCAL_COLUMNS.items():
        if name in frame.columns:
            continue
        if name == "source_cluster_id" and default_cluster_id is not None:
            expressions.append(pl.lit(default_cluster_id).alias(name))
            continue
        expressions.append(_missing_expr(name, dtype, default))
    return frame.with_columns(expressions)


def _compute_temporal_features(frame: pl.DataFrame) -> pl.DataFrame:
    keys = ["source_workload_id", "source_workload_instance_id"]
    temporal_exprs: list[pl.Expr] = []
    for source_name, prefix in TEMPORAL_FEATURE_SPECS:
        lag_expr = pl.col(source_name).cast(pl.Float64, strict=False).shift(1).over(keys)
        temporal_exprs.extend(
            [
                lag_expr.alias(f"{prefix}_prev_1"),
                (pl.col(source_name).cast(pl.Float64, strict=False) - lag_expr).alias(f"{prefix}_delta_1"),
                pl.col(source_name).cast(pl.Float64, strict=False).rolling_mean(window_size=3, min_samples=1).over(keys).alias(f"{prefix}_roll3_mean"),
            ]
        )
    return frame.with_columns(temporal_exprs)


def _compute_labels(
    frame: pl.DataFrame,
    failure_event_types: list[int],
    horizon_us: int,
) -> pl.DataFrame:
    return (
        frame
        .with_columns(
            [
                (pl.col("window_end_us") - pl.col("window_start_us")).cast(pl.Int64, strict=False).alias("window_duration_us"),
                (pl.col("terminal_event_time_us") - pl.col("window_end_us")).cast(pl.Int64, strict=False).alias("time_to_terminal_event_us"),
            ]
        )
        .with_columns(
            [
                pl.when(pl.col("is_failure_terminal_event").is_not_null())
                .then(pl.col("is_failure_terminal_event"))
                .otherwise(pl.col("terminal_event_type").is_in(failure_event_types))
                .alias("is_failure_terminal_event"),
                pl.when(pl.col("terminal_event_before_window_end").is_not_null())
                .then(pl.col("terminal_event_before_window_end"))
                .otherwise(
                    pl.col("terminal_event_time_us").is_not_null() &
                    (pl.col("terminal_event_time_us") < pl.col("window_end_us"))
                )
                .alias("terminal_event_before_window_end"),
            ]
        )
        .with_columns(
            [
                pl.when(pl.col("target_failure_within_horizon").is_not_null())
                .then(pl.col("target_failure_within_horizon"))
                .otherwise(
                    pl.col("is_failure_terminal_event").fill_null(False) &
                    pl.col("time_to_terminal_event_us").is_not_null() &
                    (pl.col("time_to_terminal_event_us") >= 0) &
                    (pl.col("time_to_terminal_event_us") <= horizon_us)
                )
                .alias("target_failure_within_horizon"),
            ]
        )
    )


def build_local_common_forecaster_frame(
    frame: pl.DataFrame,
    mapping: dict[str, str],
    source_platform: str,
    default_cluster_id: str | None,
    failure_event_types: list[int],
    horizon_us: int,
) -> pl.DataFrame:
    renamed = _rename_using_mapping(frame, mapping)
    enriched = _ensure_optional_columns(renamed, default_cluster_id)
    base = (
        enriched
        .with_columns(
            [
                pl.lit(source_platform).alias("source_platform"),
                pl.lit(COMMON_FORECASTER_SCHEMA_VERSION).alias("source_schema_version"),
                pl.col("source_workload_id").cast(pl.Utf8, strict=False).alias("source_workload_id"),
                pl.col("source_workload_instance_id").cast(pl.Utf8, strict=False).alias("source_workload_instance_id"),
                pl.col("source_node_id").cast(pl.Utf8, strict=False).alias("source_node_id"),
                pl.col("source_cluster_id").cast(pl.Utf8, strict=False).alias("source_cluster_id"),
                pl.col("window_start_us").cast(pl.Int64, strict=False).alias("window_start_us"),
                pl.col("window_end_us").cast(pl.Int64, strict=False).alias("window_end_us"),
                pl.col("event_count").cast(pl.UInt32, strict=False).alias("event_count"),
                pl.col("workload_priority").cast(pl.Int64, strict=False).alias("workload_priority"),
                pl.col("workload_class").cast(pl.Int64, strict=False).alias("workload_class"),
                pl.col("terminal_event_time_us").cast(pl.Int64, strict=False).alias("terminal_event_time_us"),
                pl.col("terminal_event_type").cast(pl.Int64, strict=False).alias("terminal_event_type"),
            ]
        )
        .sort(["source_workload_id", "source_workload_instance_id", "window_end_us"])
    )
    with_temporal = _compute_temporal_features(base)
    labeled = _compute_labels(with_temporal, failure_event_types=failure_event_types, horizon_us=horizon_us)

    missing = [name for name in COMMON_FORECASTER_COLUMNS if name not in labeled.columns]
    if missing:
        raise ValueError(f"Local canonical frame is missing required columns: {missing}")

    return labeled.select(list(COMMON_FORECASTER_COLUMNS))
