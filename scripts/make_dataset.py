import os
from pathlib import Path

import polars as pl

DEFAULT_PROCESSED_DIR = Path.home() / "Documents" / "borg_processed"
DEFAULT_DATASET_DIR = DEFAULT_PROCESSED_DIR / "datasets"
DEFAULT_CLUSTERS = ("b", "c", "d", "e", "f", "g")

PROCESSED_DIR = Path(os.environ.get("BORG_PROCESSED_DIR", DEFAULT_PROCESSED_DIR)).expanduser()
DATASET_DIR = Path(os.environ.get("BORG_DATASET_DIR", DEFAULT_DATASET_DIR)).expanduser()
DATASET_DIR.mkdir(parents=True, exist_ok=True)
FLAT_SHARD_DIR = PROCESSED_DIR / "flat_shards"


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


def optional_int_col(schema_names: set[str], name: str) -> pl.Expr:
    if name in schema_names:
        return int_col(name).alias(name)
    return pl.lit(None, dtype=pl.Int64).alias(name)


def optional_float_col(schema_names: set[str], name: str) -> pl.Expr:
    if name in schema_names:
        return float_col(name).alias(name)
    return pl.lit(None, dtype=pl.Float64).alias(name)


def cluster_file(cluster_id: str, suffix: str) -> Path:
    return PROCESSED_DIR / f"{cluster_id}_{suffix}.parquet"


def sharded_cluster_glob(cluster_id: str, suffix: str) -> str:
    kind = {"events": "events", "machines": "machines", "usage": "usage"}[suffix]
    return str(FLAT_SHARD_DIR / kind / cluster_id / "*.parquet")


def cluster_source_exists(cluster_id: str, suffix: str) -> bool:
    shard_dir = FLAT_SHARD_DIR / suffix / cluster_id
    if shard_dir.exists() and any(shard_dir.glob("*.parquet")):
        return True
    return cluster_file(cluster_id, suffix).exists()


def cluster_source(cluster_id: str, suffix: str) -> str:
    shard_dir = FLAT_SHARD_DIR / suffix / cluster_id
    if shard_dir.exists() and any(shard_dir.glob("*.parquet")):
        return sharded_cluster_glob(cluster_id, suffix)
    return str(cluster_file(cluster_id, suffix))


def cluster_source_paths(cluster_id: str, suffix: str) -> list[Path]:
    shard_dir = FLAT_SHARD_DIR / suffix / cluster_id
    if shard_dir.exists():
        shard_paths = sorted(shard_dir.glob("*.parquet"))
        if shard_paths:
            return shard_paths
    return [cluster_file(cluster_id, suffix)]


def concat_normalized_sources(source_paths: list[Path], builder) -> pl.LazyFrame:
    normalized_frames = [builder(path) for path in source_paths]
    if len(normalized_frames) == 1:
        return normalized_frames[0]
    return pl.concat(normalized_frames, how="vertical_relaxed")


def dataset_file(cluster_id: str) -> Path:
    return DATASET_DIR / f"{cluster_id}_dataset.parquet"


def load_event_features(cluster_id: str) -> pl.LazyFrame:
    def build_normalized_event_frame(path: Path) -> pl.LazyFrame:
        return (
            pl.scan_parquet(str(path))
            .select(
                [
                    int_col("time").alias("event_time"),
                    int_col("collection_id").alias("collection_id"),
                    int_col("instance_index").alias("instance_index"),
                    int_col("machine_id").alias("event_machine_id"),
                    int_col("alloc_collection_id").alias("alloc_collection_id"),
                    int_col("alloc_instance_index").alias("alloc_instance_index"),
                    int_col("type").alias("event_type"),
                    int_col("scheduling_class").alias("scheduling_class"),
                    int_col("priority").alias("priority"),
                    str_col("missing_type").alias("missing_type"),
                    float_col("req_cpu").alias("req_cpu"),
                    float_col("req_mem").alias("req_mem"),
                ]
            )
        )

    return (
        concat_normalized_sources(cluster_source_paths(cluster_id, "events"), build_normalized_event_frame)
        .filter(pl.col("collection_id").is_not_null() & pl.col("instance_index").is_not_null())
        .sort(["collection_id", "instance_index", "event_time"])
        .group_by(["collection_id", "instance_index"])
        .agg(
            [
                pl.col("event_time").min().alias("first_event_time"),
                pl.col("event_time").max().alias("last_event_time"),
                pl.len().alias("event_count"),
                pl.col("event_type").last().alias("final_event_type"),
                pl.col("scheduling_class").drop_nulls().last().alias("scheduling_class"),
                pl.col("priority").drop_nulls().last().alias("priority"),
                pl.col("req_cpu").max().alias("req_cpu"),
                pl.col("req_mem").max().alias("req_mem"),
                pl.col("event_machine_id").drop_nulls().last().alias("last_event_machine_id"),
                pl.col("alloc_collection_id").drop_nulls().last().alias("alloc_collection_id"),
                pl.col("alloc_instance_index").drop_nulls().last().alias("alloc_instance_index"),
                pl.col("missing_type").drop_nulls().last().alias("missing_type"),
            ]
        )
    )


def load_machine_features(cluster_id: str) -> pl.LazyFrame:
    def build_normalized_machine_frame(path: Path) -> pl.LazyFrame:
        return (
            pl.scan_parquet(str(path))
            .select(
                [
                    int_col("time").alias("machine_event_time"),
                    int_col("machine_id").alias("machine_id"),
                    float_col("machine_cpu").alias("machine_cpu"),
                    float_col("machine_mem").alias("machine_mem"),
                    int_col("type").alias("machine_event_type"),
                    str_col("switch_id").alias("switch_id"),
                    str_col("platform_id").alias("platform_id"),
                ]
            )
        )

    return (
        concat_normalized_sources(cluster_source_paths(cluster_id, "machines"), build_normalized_machine_frame)
        .filter(pl.col("machine_id").is_not_null())
        .sort(["machine_id", "machine_event_time"])
        .group_by("machine_id")
        .agg(
            [
                pl.col("machine_event_time").max().alias("last_machine_event_time"),
                pl.col("machine_cpu").drop_nulls().last().alias("machine_cpu"),
                pl.col("machine_mem").drop_nulls().last().alias("machine_mem"),
                pl.col("machine_event_type").drop_nulls().last().alias("machine_event_type"),
                pl.col("switch_id").drop_nulls().last().alias("switch_id"),
                pl.col("platform_id").drop_nulls().last().alias("platform_id"),
            ]
        )
    )


def load_usage_features(cluster_id: str) -> pl.LazyFrame:
    def build_normalized_usage_frame(path: Path) -> pl.LazyFrame:
        usage = pl.scan_parquet(str(path))
        schema_names = set(usage.collect_schema().names())
        return usage.select(
            [
                str_col("cluster_id").alias("cluster_id"),
                int_col("start_time").alias("start_time"),
                int_col("end_time").alias("end_time"),
                int_col("collection_id").alias("collection_id"),
                int_col("instance_index").alias("instance_index"),
                int_col("machine_id").alias("machine_id"),
                optional_int_col(schema_names, "alloc_collection_id"),
                optional_int_col(schema_names, "alloc_instance_index"),
                float_col("avg_cpu").alias("avg_cpu"),
                float_col("avg_mem").alias("avg_mem"),
                float_col("max_cpu").alias("max_cpu"),
                float_col("max_mem").alias("max_mem"),
                optional_float_col(schema_names, "assigned_memory"),
                optional_float_col(schema_names, "page_cache_memory"),
                optional_float_col(schema_names, "sample_rate"),
                optional_float_col(schema_names, "memory_accesses_per_instruction"),
            ]
        )

    return (
        concat_normalized_sources(cluster_source_paths(cluster_id, "usage"), build_normalized_usage_frame)
        .filter(pl.col("collection_id").is_not_null() & pl.col("instance_index").is_not_null())
    )


def build_cluster_dataset(cluster_id: str) -> pl.DataFrame:
    usage = load_usage_features(cluster_id)
    events = load_event_features(cluster_id)
    machines = load_machine_features(cluster_id)

    dataset = (
        usage
        .join(events, on=["collection_id", "instance_index"], how="left", suffix="_event")
        .join(machines, on="machine_id", how="left", suffix="_machine")
        .with_columns(
            [
                (pl.col("end_time") - pl.col("start_time")).alias("usage_window"),
                (pl.col("avg_cpu") / pl.col("machine_cpu")).alias("avg_cpu_utilization"),
                (pl.col("max_cpu") / pl.col("machine_cpu")).alias("max_cpu_utilization"),
                (pl.col("avg_mem") / pl.col("machine_mem")).alias("avg_mem_utilization"),
                (pl.col("max_mem") / pl.col("machine_mem")).alias("max_mem_utilization"),
                (
                    (pl.col("first_event_time").is_not_null()) &
                    (pl.col("first_event_time") <= pl.col("start_time"))
                ).alias("has_started"),
                (
                    (pl.col("last_event_time").is_not_null()) &
                    (pl.col("last_event_time") >= pl.col("end_time"))
                ).alias("active_during_window"),
            ]
        )
        .with_columns(pl.lit(cluster_id).alias("source_cluster"))
        .collect(engine="streaming")
    )

    return dataset


def write_cluster_dataset(cluster_id: str) -> Path:
    output_path = dataset_file(cluster_id)
    dataset = build_cluster_dataset(cluster_id)
    dataset.write_parquet(output_path)
    print(f"✅ {cluster_id}: wrote {dataset.height} rows to {output_path}")
    return output_path


def main() -> None:
    clusters = parse_clusters()

    print(f"Reading flattened parquet files from: {PROCESSED_DIR}")
    print(f"Writing joined datasets to: {DATASET_DIR}")
    print(f"Clusters: {clusters}")

    for cluster_id in clusters:
        if not cluster_source_exists(cluster_id, "usage"):
            print(f"Skipping {cluster_id}: missing usage parquet")
            continue

        if not cluster_source_exists(cluster_id, "events"):
            print(f"Skipping {cluster_id}: missing events parquet")
            continue

        if not cluster_source_exists(cluster_id, "machines"):
            print(f"Skipping {cluster_id}: missing machines parquet")
            continue

        write_cluster_dataset(cluster_id)


if __name__ == "__main__":
    main()
