from __future__ import annotations

import json
import os
from contextlib import contextmanager
from datetime import datetime

import polars as pl

from scripts.train_advanced_xgboost import load_feature_scan
from src.advanced_xgboost.features import target_column_name
from src.advanced_xgboost.settings import feature_store_dir, parse_clusters, report_dir
from src.advanced_xgboost.train import train_and_evaluate


DEFAULT_TUNE_HORIZONS = (5, 15)
DEFAULT_CANDIDATES = (
    {
        "name": "baseline_es",
        "params": {
            "BORG_XGB_N_ESTIMATORS": "1200",
            "BORG_XGB_MAX_DEPTH": "8",
            "BORG_XGB_LEARNING_RATE": "0.05",
            "BORG_XGB_SUBSAMPLE": "0.8",
            "BORG_XGB_COLSAMPLE_BYTREE": "0.8",
            "BORG_XGB_MIN_CHILD_WEIGHT": "5",
            "BORG_XGB_REG_ALPHA": "0.0",
            "BORG_XGB_REG_LAMBDA": "1.0",
            "BORG_XGB_EARLY_STOPPING_ROUNDS": "50",
        },
    },
    {
        "name": "regularized_balanced",
        "params": {
            "BORG_XGB_N_ESTIMATORS": "1600",
            "BORG_XGB_MAX_DEPTH": "6",
            "BORG_XGB_LEARNING_RATE": "0.03",
            "BORG_XGB_SUBSAMPLE": "0.9",
            "BORG_XGB_COLSAMPLE_BYTREE": "0.7",
            "BORG_XGB_MIN_CHILD_WEIGHT": "8",
            "BORG_XGB_REG_ALPHA": "0.2",
            "BORG_XGB_REG_LAMBDA": "2.0",
            "BORG_XGB_EARLY_STOPPING_ROUNDS": "80",
        },
    },
    {
        "name": "shallow_conservative",
        "params": {
            "BORG_XGB_N_ESTIMATORS": "1800",
            "BORG_XGB_MAX_DEPTH": "5",
            "BORG_XGB_LEARNING_RATE": "0.03",
            "BORG_XGB_SUBSAMPLE": "0.9",
            "BORG_XGB_COLSAMPLE_BYTREE": "0.85",
            "BORG_XGB_MIN_CHILD_WEIGHT": "12",
            "BORG_XGB_REG_ALPHA": "0.4",
            "BORG_XGB_REG_LAMBDA": "3.0",
            "BORG_XGB_EARLY_STOPPING_ROUNDS": "100",
        },
    },
    {
        "name": "wider_regularized",
        "params": {
            "BORG_XGB_N_ESTIMATORS": "1400",
            "BORG_XGB_MAX_DEPTH": "7",
            "BORG_XGB_LEARNING_RATE": "0.03",
            "BORG_XGB_SUBSAMPLE": "0.85",
            "BORG_XGB_COLSAMPLE_BYTREE": "0.75",
            "BORG_XGB_MIN_CHILD_WEIGHT": "6",
            "BORG_XGB_REG_ALPHA": "0.1",
            "BORG_XGB_REG_LAMBDA": "1.5",
            "BORG_XGB_EARLY_STOPPING_ROUNDS": "80",
        },
    },
)


def parse_tune_horizons() -> list[int]:
    raw = os.environ.get("BORG_XGB_TUNE_HORIZONS")
    if not raw:
        return list(DEFAULT_TUNE_HORIZONS)
    return [int(value.strip()) for value in raw.split(",") if value.strip()]


@contextmanager
def temporary_env(overrides: dict[str, str]):
    previous = {key: os.environ.get(key) for key in overrides}
    try:
        for key, value in overrides.items():
            os.environ[key] = value
        yield
    finally:
        for key, value in previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def candidate_score(metrics: list[dict[str, int | float | str]]) -> float:
    average_precision = sum(float(item["average_precision"]) for item in metrics) / len(metrics)
    recall_at_1 = sum(float(item["recall_at_1_percent"]) for item in metrics) / len(metrics)
    precision_at_1 = sum(float(item["precision_at_1_percent"]) for item in metrics) / len(metrics)
    return average_precision + (0.2 * recall_at_1) + (0.05 * precision_at_1)


def tuning_report_path() -> str:
    stamp = datetime.now().strftime("%Y%m%d%H%M")
    return str(report_dir() / f"{stamp}_advanced_xgboost_tuning.json")


def main() -> None:
    clusters = parse_clusters()
    horizons = parse_tune_horizons()
    feature_scan = load_feature_scan(clusters)
    report_dir().mkdir(parents=True, exist_ok=True)

    base_overrides = {
        "BORG_XGB_MAX_TRAIN_ROWS": os.environ.get("BORG_XGB_MAX_TRAIN_ROWS", "3000000"),
        "BORG_XGB_MAX_VALID_ROWS": os.environ.get("BORG_XGB_MAX_VALID_ROWS", "750000"),
        "BORG_XGB_N_JOBS": os.environ.get("BORG_XGB_N_JOBS", "10"),
    }

    results = []
    for candidate in DEFAULT_CANDIDATES:
        model_name = f"xgboost_tune_{candidate['name']}"
        overrides = {
            **base_overrides,
            **candidate["params"],
            "BORG_XGB_MODEL_NAME": model_name,
        }
        print(f"=== candidate={candidate['name']} horizons={horizons} ===")
        horizon_metrics = []
        with temporary_env(overrides):
            for minutes in horizons:
                target = target_column_name(minutes)
                metrics = train_and_evaluate(feature_scan, target)
                horizon_metrics.append(metrics)
                print(
                    f"candidate={candidate['name']} target={target} "
                    f"ap={metrics['average_precision']:.6f} "
                    f"p@1={metrics['precision_at_1_percent']:.6f} "
                    f"r@1={metrics['recall_at_1_percent']:.6f}"
                )

        results.append(
            {
                "candidate": candidate["name"],
                "params": {**base_overrides, **candidate["params"]},
                "model_name": model_name,
                "horizons": horizons,
                "metrics": horizon_metrics,
                "score": candidate_score(horizon_metrics),
            }
        )

    ranked = sorted(results, key=lambda item: item["score"], reverse=True)
    output_path = tuning_report_path()
    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(
            {
                "clusters": clusters,
                "feature_store_dir": str(feature_store_dir()),
                "horizons": horizons,
                "results": ranked,
                "winner": ranked[0] if ranked else None,
            },
            handle,
            indent=2,
        )
    print(f"Wrote tuning report to {output_path}")
    if ranked:
        print(f"Winner: {ranked[0]['candidate']} score={ranked[0]['score']:.6f}")


if __name__ == "__main__":
    main()
