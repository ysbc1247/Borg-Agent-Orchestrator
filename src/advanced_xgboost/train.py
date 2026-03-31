from __future__ import annotations

import json
import math
import os
from pathlib import Path

import numpy as np
import polars as pl
from xgboost import XGBClassifier

from src.advanced_xgboost.features import ADVANCED_FEATURE_COLUMNS, MISSINGNESS_FLAG_COLUMNS, target_column_name
from src.advanced_xgboost.settings import model_dir, report_dir


DEFAULT_VALID_FRACTION = 0.2
DEFAULT_MODEL_NAME = "xgboost_failure_risk"
DEFAULT_MAX_TRAIN_ROWS = 8_000_000
DEFAULT_MAX_VALID_ROWS = 2_000_000
SAMPLING_BUCKETS = 1_000_000
MODEL_FEATURE_COLUMNS = ADVANCED_FEATURE_COLUMNS + MISSINGNESS_FLAG_COLUMNS


def validation_fraction() -> float:
    raw = os.environ.get("BORG_VALID_FRACTION")
    if not raw:
        return DEFAULT_VALID_FRACTION
    return float(raw)


def model_name() -> str:
    return (
        os.environ.get("BORG_XGB_MODEL_NAME")
        or os.environ.get("BORG_XGBOOST_MODEL_NAME")
        or DEFAULT_MODEL_NAME
    ).strip()


def model_name_for_target(target_column: str) -> str:
    return f"{model_name()}_{target_column}"


def model_params() -> dict[str, float | int | str]:
    params: dict[str, float | int | str] = {
        "n_estimators": int(os.environ.get("BORG_XGB_N_ESTIMATORS", "400")),
        "max_depth": int(os.environ.get("BORG_XGB_MAX_DEPTH", "8")),
        "learning_rate": float(os.environ.get("BORG_XGB_LEARNING_RATE", "0.05")),
        "subsample": float(os.environ.get("BORG_XGB_SUBSAMPLE", "0.8")),
        "colsample_bytree": float(os.environ.get("BORG_XGB_COLSAMPLE_BYTREE", "0.8")),
        "min_child_weight": float(os.environ.get("BORG_XGB_MIN_CHILD_WEIGHT", "5")),
        "reg_alpha": float(os.environ.get("BORG_XGB_REG_ALPHA", "0.0")),
        "reg_lambda": float(os.environ.get("BORG_XGB_REG_LAMBDA", "1.0")),
        "objective": "binary:logistic",
        "eval_metric": "aucpr",
        "tree_method": os.environ.get("BORG_XGB_TREE_METHOD", "hist"),
        "random_state": int(os.environ.get("BORG_XGB_RANDOM_STATE", "42")),
        "n_jobs": int(os.environ.get("BORG_XGB_N_JOBS", "8")),
    }
    raw_early_stopping = os.environ.get("BORG_XGB_EARLY_STOPPING_ROUNDS")
    if raw_early_stopping:
        params["early_stopping_rounds"] = int(raw_early_stopping)
    return params


def model_output_dir(target_column: str) -> Path:
    path = model_dir() / model_name_for_target(target_column)
    path.mkdir(parents=True, exist_ok=True)
    return path


def metrics_path(target_column: str) -> Path:
    return model_output_dir(target_column) / "metrics.json"


def feature_importance_path(target_column: str) -> Path:
    return model_output_dir(target_column) / "feature_importance.json"


def prediction_path(target_column: str) -> Path:
    return model_output_dir(target_column) / "validation_predictions.parquet"


def config_path(target_column: str) -> Path:
    return model_output_dir(target_column) / "model_config.json"


def model_path(target_column: str) -> Path:
    return model_output_dir(target_column) / "model.json"


def summary_report_path(target_column: str) -> Path:
    report_dir().mkdir(parents=True, exist_ok=True)
    return report_dir() / f"advanced_xgboost_training_summary_{target_column}.json"


def max_train_rows() -> int:
    raw = os.environ.get("BORG_XGB_MAX_TRAIN_ROWS")
    if not raw:
        return DEFAULT_MAX_TRAIN_ROWS
    return max(1, int(raw))


def max_valid_rows() -> int:
    raw = os.environ.get("BORG_XGB_MAX_VALID_ROWS")
    if not raw:
        return DEFAULT_MAX_VALID_ROWS
    return max(1, int(raw))


def sampling_seed() -> int:
    raw = os.environ.get("BORG_XGB_SAMPLING_SEED")
    if not raw:
        return int(os.environ.get("BORG_XGB_RANDOM_STATE", "42"))
    return int(raw)


def split_time_for_scan(frame: pl.LazyFrame, valid_fraction: float) -> int:
    split_time = (
        frame
        .select(pl.col("end_time").quantile(1.0 - valid_fraction).alias("split_time"))
        .collect()
        .item()
    )
    return int(split_time)


def prepare_matrix(frame: pl.DataFrame, target_column: str) -> tuple[list[list[float]], list[int]]:
    matrix_frame = frame.with_columns(
        [
            (
                pl.col(column)
                .cast(pl.Float64, strict=False)
                .fill_null(float("nan"))
                .alias(column)
            )
            for column in MODEL_FEATURE_COLUMNS
        ]
    )
    x = matrix_frame.select(list(MODEL_FEATURE_COLUMNS)).to_numpy()
    x = np.asarray(x, dtype=np.float32)
    y = matrix_frame.get_column(target_column).cast(pl.Int64).to_list()
    return x, y


def average_precision(prediction_frame: pl.DataFrame, target_column: str) -> float:
    ranked = (
        prediction_frame
        .sort("risk_score", descending=True)
        .with_row_index("rank", offset=1)
        .with_columns(
            [
                pl.col(target_column).cast(pl.Int64).cum_sum().alias("true_positives"),
                (pl.col(target_column).cast(pl.Int64).cum_sum() / pl.col("rank")).alias("precision_at_rank"),
            ]
        )
    )
    positives_total = ranked.filter(pl.col(target_column)).height
    if positives_total == 0:
        return 0.0
    ap_sum = ranked.filter(pl.col(target_column)).select(pl.col("precision_at_rank").sum()).item()
    return float(ap_sum) / positives_total if ap_sum is not None else 0.0


def precision_at_k(frame: pl.DataFrame, k: int, target_column: str) -> float:
    top_k = frame.sort("risk_score", descending=True).head(max(1, k))
    positives = top_k.filter(pl.col(target_column)).height
    return positives / top_k.height if top_k.height else 0.0


def recall_at_k(frame: pl.DataFrame, k: int, target_column: str) -> float:
    positives_total = frame.filter(pl.col(target_column)).height
    if positives_total == 0:
        return 0.0
    top_k = frame.sort("risk_score", descending=True).head(max(1, k))
    positives = top_k.filter(pl.col(target_column)).height
    return positives / positives_total


def compute_scale_pos_weight(y: list[int]) -> float:
    positives = sum(y)
    negatives = len(y) - positives
    if positives <= 0:
        return 1.0
    return max(1.0, negatives / positives)


def row_id_expr() -> pl.Expr:
    return pl.struct(["cluster_id", "collection_id", "instance_index", "start_time", "end_time"]).hash(
        seed=sampling_seed()
    )


def sampled_negative_filter(keep_fraction: float) -> pl.Expr:
    if keep_fraction <= 0.0:
        return pl.lit(False)
    if keep_fraction >= 1.0:
        return pl.lit(True)
    keep_threshold = max(1, int(keep_fraction * SAMPLING_BUCKETS))
    return row_id_expr().mod(SAMPLING_BUCKETS) < keep_threshold


def split_stats(frame: pl.LazyFrame, target_column: str) -> dict[str, int]:
    stats = frame.select(
        [
            pl.len().alias("rows"),
            pl.col(target_column).cast(pl.Int64).sum().fill_null(0).alias("positives"),
        ]
    ).collect().to_dicts()[0]
    rows = int(stats["rows"])
    positives = int(stats["positives"])
    return {
        "rows": rows,
        "positives": positives,
        "negatives": rows - positives,
    }


def negative_keep_fraction(rows: int, positives: int, max_rows: int) -> float:
    negatives = rows - positives
    if negatives <= 0:
        return 1.0
    remaining_budget = max_rows - positives
    if remaining_budget <= 0:
        return 0.0
    return min(1.0, remaining_budget / negatives)


def sample_split(
    frame: pl.LazyFrame,
    target_column: str,
    max_rows: int,
) -> tuple[pl.DataFrame, dict[str, int | float]]:
    stats = split_stats(frame, target_column)
    keep_fraction = negative_keep_fraction(stats["rows"], stats["positives"], max_rows)
    sampled = (
        frame
        .filter(pl.col(target_column) | sampled_negative_filter(keep_fraction))
        .collect(engine="streaming")
    )
    sampled_stats = {
        "rows": sampled.height,
        "positives": sampled.filter(pl.col(target_column)).height,
        "negatives": sampled.filter(~pl.col(target_column)).height,
        "negative_keep_fraction": keep_fraction,
    }
    sampled_stats.update(
        {
            "source_rows": stats["rows"],
            "source_positives": stats["positives"],
            "source_negatives": stats["negatives"],
        }
    )
    return sampled, sampled_stats


def train_and_evaluate(feature_scan: pl.LazyFrame, target_column: str) -> dict[str, int | float | str]:
    split_time = split_time_for_scan(feature_scan, validation_fraction())
    selected_columns = [
        "cluster_id",
        "collection_id",
        "instance_index",
        "machine_id",
        "start_time",
        "end_time",
        *MODEL_FEATURE_COLUMNS,
        target_column,
    ]
    base_scan = feature_scan.select(selected_columns).with_columns(pl.col(target_column).cast(pl.Boolean))
    train_scan = base_scan.filter(pl.col("end_time") < split_time)
    valid_scan = base_scan.filter(pl.col("end_time") >= split_time)
    train_df, train_stats = sample_split(train_scan, target_column, max_train_rows())
    valid_df, valid_stats = sample_split(valid_scan, target_column, max_valid_rows())
    train_x, train_y = prepare_matrix(train_df, target_column)
    valid_x, valid_y = prepare_matrix(valid_df, target_column)

    params = model_params()
    params["scale_pos_weight"] = compute_scale_pos_weight(train_y)

    model = XGBClassifier(**params)
    fit_kwargs: dict[str, object] = {}
    if "early_stopping_rounds" in params:
        fit_kwargs["eval_set"] = [(valid_x, valid_y)]
        fit_kwargs["verbose"] = False
    model.fit(train_x, train_y, **fit_kwargs)
    model.get_booster().save_model(model_path(target_column))
    valid_scores = model.predict_proba(valid_x)[:, 1].tolist()

    prediction_frame = valid_df.select(
        [
            pl.col("cluster_id"),
            pl.col("collection_id"),
            pl.col("instance_index"),
            pl.col("machine_id"),
            pl.col("start_time"),
            pl.col("end_time"),
            pl.col(target_column),
        ]
    ).with_columns(pl.Series("risk_score", valid_scores))

    prediction_frame.write_parquet(prediction_path(target_column))

    importances = [
        {
            "feature": feature,
            "importance": float(importance),
        }
        for feature, importance in sorted(
            zip(MODEL_FEATURE_COLUMNS, model.feature_importances_, strict=False),
            key=lambda item: item[1],
            reverse=True,
        )
    ]
    feature_importance_path(target_column).write_text(json.dumps(importances, indent=2))
    config_path(target_column).write_text(json.dumps(params, indent=2))

    one_percent = max(1, math.ceil(prediction_frame.height * 0.01))
    point_one_percent = max(1, math.ceil(prediction_frame.height * 0.001))
    metrics = {
        "model_name": model_name(),
        "target_column": target_column,
        "source_train_rows": train_stats["source_rows"],
        "source_validation_rows": valid_stats["source_rows"],
        "sampled_train_rows": train_df.height,
        "sampled_validation_rows": valid_df.height,
        "train_rows": train_df.height,
        "validation_rows": valid_df.height,
        "validation_positive_rows": prediction_frame.filter(pl.col(target_column)).height,
        "validation_positive_rate": (
            prediction_frame.filter(pl.col(target_column)).height / prediction_frame.height
            if prediction_frame.height else 0.0
        ),
        "train_positive_rows": sum(train_y),
        "sampled_train_positive_rows": train_stats["positives"],
        "sampled_validation_positive_rows": valid_stats["positives"],
        "train_negative_keep_fraction": train_stats["negative_keep_fraction"],
        "validation_negative_keep_fraction": valid_stats["negative_keep_fraction"],
        "best_iteration": getattr(model, "best_iteration", None),
        "best_score": (
            float(model.best_score)
            if getattr(model, "best_score", None) is not None
            else None
        ),
        "split_time": split_time,
        "average_precision": average_precision(prediction_frame, target_column),
        "precision_at_0_1_percent": precision_at_k(prediction_frame, point_one_percent, target_column),
        "recall_at_0_1_percent": recall_at_k(prediction_frame, point_one_percent, target_column),
        "precision_at_1_percent": precision_at_k(prediction_frame, one_percent, target_column),
        "recall_at_1_percent": recall_at_k(prediction_frame, one_percent, target_column),
    }
    metrics_path(target_column).write_text(json.dumps(metrics, indent=2))
    summary_report_path(target_column).write_text(json.dumps(metrics, indent=2))
    return metrics
