import argparse
import json
import sys
from pathlib import Path

import polars as pl

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.schema.local_cloud import build_local_common_forecaster_frame

DEFAULT_FAILURE_EVENT_TYPES = (2, 3, 6)
DEFAULT_HORIZON_US = 15 * 60 * 1_000_000
DEFAULT_SOURCE_PLATFORM = "local_cloud"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a canonical forecaster dataset from local-cloud telemetry.")
    parser.add_argument("--input", required=True, help="Input telemetry file (.parquet or .csv).")
    parser.add_argument("--output", required=True, help="Output canonical parquet path.")
    parser.add_argument("--mapping", required=True, help="JSON file mapping canonical column names to raw input columns.")
    parser.add_argument("--source-platform", default=DEFAULT_SOURCE_PLATFORM, help="Label written into source_platform.")
    parser.add_argument("--default-cluster-id", default=None, help="Fallback cluster ID when the input has no cluster column.")
    parser.add_argument("--failure-event-types", default="2,3,6", help="Comma-separated terminal event types treated as failures.")
    parser.add_argument("--horizon-us", type=int, default=DEFAULT_HORIZON_US, help="Prediction horizon in microseconds.")
    return parser.parse_args()


def read_frame(path: Path) -> pl.DataFrame:
    if path.suffix == ".parquet":
        return pl.read_parquet(path)
    if path.suffix == ".csv":
        return pl.read_csv(path)
    raise ValueError(f"Unsupported input format for {path}. Expected .parquet or .csv")


def load_mapping(path: Path) -> dict[str, str]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("Mapping file must contain a flat JSON object of canonical_name -> raw_column.")
    return {str(key): str(value) for key, value in payload.items()}


def parse_failure_event_types(raw: str) -> list[int]:
    if not raw.strip():
        return list(DEFAULT_FAILURE_EVENT_TYPES)
    return [int(value.strip()) for value in raw.split(",") if value.strip()]


def main() -> None:
    args = parse_args()
    input_path = Path(args.input).expanduser()
    output_path = Path(args.output).expanduser()
    mapping_path = Path(args.mapping).expanduser()

    print(f"Reading local telemetry from: {input_path}")
    print(f"Mapping file: {mapping_path}")
    print(f"Writing canonical dataset to: {output_path}")
    print(f"Source platform label: {args.source_platform}")

    frame = read_frame(input_path)
    mapping = load_mapping(mapping_path)
    canonical = build_local_common_forecaster_frame(
        frame,
        mapping=mapping,
        source_platform=args.source_platform,
        default_cluster_id=args.default_cluster_id,
        failure_event_types=parse_failure_event_types(args.failure_event_types),
        horizon_us=args.horizon_us,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    canonical.write_parquet(output_path)

    positives = canonical.filter(pl.col("target_failure_within_horizon")).height
    print(f"Wrote {canonical.height} rows with {positives} positives.")


if __name__ == "__main__":
    main()
