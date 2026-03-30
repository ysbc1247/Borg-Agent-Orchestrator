import concurrent.futures
import os
from pathlib import Path
import time

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
DEFAULT_HEARTBEAT_SECONDS = 30
CPU_MEM_STRUCT = pl.Struct({"cpus": pl.Float64, "memory": pl.Float64})


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


def heartbeat_seconds() -> int:
    raw = os.environ.get("BORG_FLATTEN_HEARTBEAT_SECONDS")
    if raw:
        return max(1, int(raw))
    return DEFAULT_HEARTBEAT_SECONDS


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

    if isinstance(root_dtype, pl.Struct):
        field_names = {field.name for field in root_dtype.fields}
        if field_name in field_names:
            return pl.col(root_col).struct.field(field_name).cast(pl.Float64).alias(new_name)

    return pl.lit(None).cast(pl.Float64).alias(new_name)


def scan_ndjson_permissive(path: Path, kind: str) -> pl.LazyFrame:
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
            "average_usage": CPU_MEM_STRUCT,
            "maximum_usage": CPU_MEM_STRUCT,
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
            "resource_request": CPU_MEM_STRUCT,
            "constraint": pl.Object,
        }
    elif kind == "machines":
        schema_overrides = {
            "time": pl.Int64,
            "machine_id": pl.Int64,
            "type": pl.Int64,
            "capacity": CPU_MEM_STRUCT,
        }
    return pl.scan_ndjson(
        path,
        infer_schema_length=10000,
        schema_overrides=schema_overrides,
        ignore_errors=True,
    )


def process_shard(cluster_id: str, kind: str, raw_path_str: str) -> str:
    raw_path = Path(raw_path_str)
    out_path = shard_output_path(cluster_id, kind, raw_path)

    if out_path.exists():
        return f"skip {kind} {cluster_id} {raw_path.name}"

    lf = scan_ndjson_permissive(raw_path, kind)
    schema_names = set(lf.collect_schema().names())

    if kind == "machines":
        if "capacity" not in schema_names:
            return f"skip-empty {kind} {cluster_id} {raw_path.name}"
        lf = (
            lf.with_columns([
                pl.col("capacity").struct.field("cpus").cast(pl.Float64, strict=False).alias("machine_cpu"),
                pl.col("capacity").struct.field("memory").cast(pl.Float64, strict=False).alias("machine_mem"),
            ])
            .drop("capacity")
            .filter(pl.col("machine_cpu").is_not_null())
        )
    elif kind == "events":
        lf = lf.with_columns([
            pl.col("resource_request").struct.field("cpus").cast(pl.Float64, strict=False).alias("req_cpu"),
            pl.col("resource_request").struct.field("memory").cast(pl.Float64, strict=False).alias("req_mem"),
        ])
        cols_to_drop = [c for c in ["resource_request", "constraint"] if c in schema_names]
        lf = lf.drop(cols_to_drop)
    elif kind == "usage":
        lf = lf.with_columns([
            pl.col("average_usage").struct.field("cpus").cast(pl.Float64, strict=False).alias("avg_cpu"),
            pl.col("average_usage").struct.field("memory").cast(pl.Float64, strict=False).alias("avg_mem"),
            pl.col("maximum_usage").struct.field("cpus").cast(pl.Float64, strict=False).alias("max_cpu"),
            pl.col("maximum_usage").struct.field("memory").cast(pl.Float64, strict=False).alias("max_mem"),
        ])
        to_drop = [
            "average_usage",
            "maximum_usage",
            "cpu_histogram",
            "cycles_per_instruction",
            "memory_accesses_per_1000_instructions",
        ]
        existing_drop = [c for c in to_drop if c in schema_names]
        lf = lf.drop(existing_drop).with_columns(pl.lit(cluster_id).alias("cluster_id"))

    lf.sink_parquet(out_path)
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
        heartbeat = heartbeat_seconds()
        total = len(tasks)
        completed = 0
        next_heartbeat = time.monotonic() + heartbeat

        with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as executor:
            task_iter = iter(tasks)
            future_to_task: dict[concurrent.futures.Future[str], tuple[str, str, str]] = {}

            def submit_next() -> bool:
                try:
                    cluster_id, kind, raw_path = next(task_iter)
                except StopIteration:
                    return False

                raw_name = Path(raw_path).name
                print(f"started {kind} {cluster_id} {raw_name}", flush=True)
                future = executor.submit(process_shard, cluster_id, kind, raw_path)
                future_to_task[future] = (cluster_id, kind, raw_path)
                return True

            for _ in range(min(workers, total)):
                submit_next()

            while future_to_task:
                done, _ = concurrent.futures.wait(
                    future_to_task,
                    timeout=1,
                    return_when=concurrent.futures.FIRST_COMPLETED,
                )

                if not done:
                    now = time.monotonic()
                    if now >= next_heartbeat:
                        running = len(future_to_task)
                        pending = total - completed - running
                        print(
                            f"heartbeat completed={completed}/{total} running={running} pending={pending}",
                            flush=True,
                        )
                        next_heartbeat = now + heartbeat
                    continue

                for future in done:
                    cluster_id, kind, raw_path = future_to_task.pop(future)
                    completed += 1
                    try:
                        print(future.result(), flush=True)
                    except Exception as e:
                        print(f"❌ Error in {kind} shard {Path(raw_path).name} for cluster {cluster_id}: {e}", flush=True)
                    submit_next()

    print("\n🚀 All done! Raw data can stay outside the repository.")
