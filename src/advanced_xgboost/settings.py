import os
from pathlib import Path


DEFAULT_ADVANCED_ROOT = Path.home() / "Documents" / "borg_xgboost_workspace"
DEFAULT_PROCESSED_DIR = DEFAULT_ADVANCED_ROOT / "processed"
DEFAULT_DATASET_DIR = DEFAULT_PROCESSED_DIR / "datasets"
DEFAULT_FEATURE_DIR = DEFAULT_PROCESSED_DIR / "feature_store"
DEFAULT_MODEL_DIR = DEFAULT_ADVANCED_ROOT / "models" / "xgboost"
DEFAULT_REPORT_DIR = DEFAULT_ADVANCED_ROOT / "reports"
DEFAULT_CLUSTERS = ("b", "c", "d", "e", "f", "g")
DEFAULT_FAILURE_EVENT_TYPES = (2, 3, 6)
DEFAULT_PREDICTION_HORIZON_US = 15 * 60 * 1_000_000
DEFAULT_PREDICTION_HORIZON_MINUTES = (5, 15, 30, 45, 60)


def env_path(name: str, default: Path) -> Path:
    return Path(os.environ.get(name, default)).expanduser()


def advanced_root() -> Path:
    return env_path("BORG_ADVANCED_ROOT", DEFAULT_ADVANCED_ROOT)


def processed_dir() -> Path:
    return env_path("BORG_PROCESSED_DIR", DEFAULT_PROCESSED_DIR)


def joined_dataset_dir() -> Path:
    return env_path("BORG_ADVANCED_JOINED_DIR", DEFAULT_DATASET_DIR)


def feature_store_dir() -> Path:
    return env_path("BORG_XGBOOST_FEATURE_DIR", DEFAULT_FEATURE_DIR)


def model_dir() -> Path:
    return env_path("BORG_XGBOOST_MODEL_DIR", DEFAULT_MODEL_DIR)


def report_dir() -> Path:
    return env_path("BORG_REPORT_DIR", DEFAULT_REPORT_DIR)


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


def prediction_horizon_us() -> int:
    raw = os.environ.get("BORG_PREDICTION_HORIZON_US")
    if not raw:
        return DEFAULT_PREDICTION_HORIZON_US
    return int(raw)


def parse_prediction_horizon_minutes() -> list[int]:
    raw = os.environ.get("BORG_PREDICTION_HORIZON_MINUTES")
    if not raw:
        return list(DEFAULT_PREDICTION_HORIZON_MINUTES)
    return [int(value.strip()) for value in raw.split(",") if value.strip()]
