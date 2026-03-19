import os
from pathlib import Path

import polars as pl

DEFAULT_PROCESSED_DIR = Path.home() / "Documents" / "borg_processed"
DEFAULT_DATASET_DIR = DEFAULT_PROCESSED_DIR / "datasets"
DEFAULT_CLUSTERS = ("a", "b", "c", "d", "e", "f", "g", "h")

PROCESSED_DIR = Path(os.environ.get("BORG_PROCESSED_DIR", DEFAULT_PROCESSED_DIR)).expanduser()
DATASET_DIR = Path(os.environ.get("BORG_DATASET_DIR", DEFAULT_DATASET_DIR)).expanduser()
DATASET_DIR.mkdir(parents=True, exist_ok=True)


def parse_clusters() -> list[str]:
    raw = os.environ.get("BORG_CLUSTERS")
    if not raw:
        return list(DEFAULT_CLUSTERS)
    return [cluster.strip() for cluster in raw.split(",") if cluster.strip()]


def int_col(name: str) -> pl.Expr:
    return pl.col(name).cast(pl.Int64, strict=False)


def float_col(name: str) -> pl.Expr:
    return pl.col(name).cast(pl.Float64, strict=False)


def str_col(name: str) -> pl.Expr:
    return pl.col(name).cast(pl.Utf8, strict=False)


def cluster_file(cluster_id: str, suffix: str) -> Path:
    return PROCESSED_DIR / f"{cluster_id}_{suffix}.parquet"


def dataset_file(cluster_id: str) -> Path:
    return DATASET_DIR / f"{cluster_id}_dataset.parquet"


def main() -> None:
    print(f"Reading flattened parquet files from: {PROCESSED_DIR}")
    print(f"Writing joined datasets to: {DATASET_DIR}")
    print(f"Clusters: {parse_clusters()}")


if __name__ == "__main__":
    main()
