import concurrent.futures
import os
from pathlib import Path

import polars as pl

DEFAULT_RAW_DIR = Path.home() / "Documents" / "borg_data"
DEFAULT_OUT_DIR = Path.home() / "Documents" / "borg_processed"
DEFAULT_CLUSTERS = ("b", "c", "d", "e", "f", "g")

RAW_DIR = Path(os.environ.get("BORG_RAW_DIR", DEFAULT_RAW_DIR)).expanduser()
OUT_DIR = Path(os.environ.get("BORG_PROCESSED_DIR", DEFAULT_OUT_DIR)).expanduser()
OUT_DIR.mkdir(parents=True, exist_ok=True)
FLAT_SHARD_DIR = OUT_DIR / "flat_shards"
FLAT_SHARD_DIR.mkdir(parents=True, exist_ok=True)
DEFAULT_FLATTEN_WORKERS = max(1, os.cpu_count() or 1)


def parse_clusters() -> list[str]:
    raw = os.environ.get("BORG_CLUSTERS")
    if not raw:
        return list(DEFAULT_CLUSTERS)
    return [cluster.strip() for cluster in raw.split(",") if cluster.strip()]


def flatten_workers() -> int:
    raw = os.environ.get("BORG_FLATTEN_WORKERS")
    if raw:
        return max(1, int(raw))
    return DEFAULT_FLATTEN_WORKERS


def raw_shard_paths(cluster_id: str, kind: str) -> list[Path]:
    kind_dir = RAW_DIR / kind
    legacy_name = {
        "machines": f"{cluster_id}_machines.json.gz",
        "events": f"{cluster_id}_events.json.gz",
        "usage": f"{cluster_id}_usage.json.gz",
    }[kind]
    shard_glob = {
        "machines": f"{cluster_id}_machines-*.json.gz",
        "events": f"{cluster_id}_events-*.json.gz",
        "usage": f"{cluster_id}_usage-*.json.gz",
    }[kind]

    paths = []
    legacy_path = kind_dir / legacy_name
    if legacy_path.exists():
        paths.append(legacy_path)
    paths.extend(sorted(kind_dir.glob(shard_glob)))
    return paths


def shard_output_path(cluster_id: str, kind: str, raw_path: Path) -> Path:
    cluster_dir = FLAT_SHARD_DIR / kind / cluster_id
    cluster_dir.mkdir(parents=True, exist_ok=True)
    raw_name = raw_path.name.removesuffix(".json.gz")
    return cluster_dir / f"{raw_name}.parquet"


def safe_extract_expr(schema: dict[str, pl.DataType], root_col: str, field_name: str, new_name: str) -> pl.Expr:
    if root_col not in schema:
        return pl.lit(None).cast(pl.Float64).alias(new_name)

    root_dtype = schema[root_col]

    if root_dtype == pl.Object:
        return (
            pl.col(root_col)
            .map_elements(
                lambda value: float(value[field_name]) if isinstance(value, dict) and value.get(field_name) is not None else None,
                return_dtype=pl.Float64,
            )
            .alias(new_name)
        )

    if isinstance(root_dtype, pl.Struct):
        field_names = {field.name for field in root_dtype.fields}
        if field_name in field_names:
            return pl.col(root_col).struct.field(field_name).cast(pl.Float64).alias(new_name)

    return pl.lit(None).cast(pl.Float64).alias(new_name)


def read_ndjson_permissive(path: Path, kind: str) -> pl.DataFrame:
    schema_overrides: dict[str, pl.DataType] = {}

    if kind == "usage":
        schema_overrides = {
            "assigned_memory": pl.Float64,
            "page_cache_memory": pl.Float64,
            "sample_rate": pl.Float64,
            "memory_accesses_per_instruction": pl.Float64,
            "start_time": pl.Int64,
            "end_time": pl.Int64,
            "collection_id": pl.Int64,
            "instance_index": pl.Int64,
            "machine_id": pl.Int64,
            "alloc_collection_id": pl.Int64,
            "alloc_instance_index": pl.Int64,
        }
    elif kind == "events":
        schema_overrides = {
            "time": pl.Int64,
            "collection_id": pl.Int64,
            "instance_index": pl.Int64,
            "machine_id": pl.Int64,
            "alloc_collection_id": pl.Int64,
            "alloc_instance_index": pl.Int64,
            "type": pl.Int64,
            "priority": pl.Int64,
            "scheduling_class": pl.Int64,
            "resource_request": pl.Object,
            "constraint": pl.Object,
        }
    elif kind == "machines":
        schema_overrides = {
            "time": pl.Int64,
            "machine_id": pl.Int64,
            "type": pl.Int64,
            "capacity": pl.Object,
        }

    return pl.read_ndjson(
        path,
        infer_schema_length=10000,
        schema_overrides=schema_overrides,
        ignore_errors=True,
        low_memory=True,
    )


def process_shard(cluster_id: str, kind: str, raw_path_str: str) -> str:
    raw_path = Path(raw_path_str)
    out_path = shard_output_path(cluster_id, kind, raw_path)

    if out_path.exists():
        return f"skip {kind} {cluster_id} {raw_path.name}"

    df = read_ndjson_permissive(raw_path, kind)
    schema = df.schema

    if kind == "machines":
        if "capacity" not in schema:
            return f"skip-empty {kind} {cluster_id} {raw_path.name}"
        df = df.with_columns([
            safe_extract_expr(schema, "capacity", "cpus", "machine_cpu"),
            safe_extract_expr(schema, "capacity", "memory", "machine_mem"),
        ]).drop("capacity")
        df = df.filter(pl.col("machine_cpu").is_not_null())
    elif kind == "events":
        df = df.with_columns([
            safe_extract_expr(schema, "resource_request", "cpus", "req_cpu"),
            safe_extract_expr(schema, "resource_request", "memory", "req_mem"),
        ])
        cols_to_drop = [c for c in ["resource_request", "constraint"] if c in df.columns]
        df = df.drop(cols_to_drop)
    elif kind == "usage":
        df = df.with_columns([
            safe_extract_expr(schema, "average_usage", "cpus", "avg_cpu"),
            safe_extract_expr(schema, "average_usage", "memory", "avg_mem"),
            safe_extract_expr(schema, "maximum_usage", "cpus", "max_cpu"),
            safe_extract_expr(schema, "maximum_usage", "memory", "max_mem"),
        ])
        to_drop = [
            "average_usage",
            "maximum_usage",
            "cpu_histogram",
            "cycles_per_instruction",
            "memory_accesses_per_1000_instructions",
        ]
        existing_drop = [c for c in to_drop if c in df.columns]
        df = df.drop(existing_drop).with_columns(pl.lit(cluster_id).alias("cluster_id"))

    df.write_parquet(out_path)
    return f"done {kind} {cluster_id} {raw_path.name} -> {out_path.name}"


def build_tasks(clusters: list[str]) -> list[tuple[str, str, str]]:
    tasks: list[tuple[str, str, str]] = []
    for cluster_id in clusters:
        print(f"\n⚡️ Queueing Cluster: {cluster_id}")
        for kind in ("machines", "events", "usage"):
            paths = raw_shard_paths(cluster_id, kind)
            for raw_path in paths:
                out_path = shard_output_path(cluster_id, kind, raw_path)
                if out_path.exists():
                    print(f"Skipping existing {kind} shard output {out_path.name}")
                    continue
                print(f"Queued {kind} shard {raw_path.name}")
                tasks.append((cluster_id, kind, str(raw_path)))
    return tasks


if __name__ == "__main__":
    print(f"Reading raw Borg data from: {RAW_DIR}")
    print(f"Writing flattened data to: {OUT_DIR}")
    print(f"Writing flattened shard parquet to: {FLAT_SHARD_DIR}")

    clusters = parse_clusters()
    workers = flatten_workers()
    tasks = build_tasks(clusters)

    print(f"\nUsing {workers} flatten workers for {len(tasks)} pending shard(s).")

    if not tasks:
        print("\n🚀 All done! No pending shard work.")
    else:
        with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as executor:
            future_to_task = {
                executor.submit(process_shard, cluster_id, kind, raw_path): (cluster_id, kind, raw_path)
                for cluster_id, kind, raw_path in tasks
            }
            for future in concurrent.futures.as_completed(future_to_task):
                cluster_id, kind, raw_path = future_to_task[future]
                try:
                    print(future.result(), flush=True)
                except Exception as e:
                    print(f"❌ Error in {kind} shard {Path(raw_path).name} for cluster {cluster_id}: {e}", flush=True)

    print("\n🚀 All done! Raw data can stay outside the repository.")
