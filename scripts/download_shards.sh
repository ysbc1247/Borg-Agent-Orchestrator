#!/bin/zsh

set -euo pipefail

RAW_DIR="${BORG_RAW_DIR:-$HOME/Documents/borg_data}"
CLUSTERS_RAW="${BORG_CLUSTERS:-b,c,d,e,f,g}"
DOWNLOAD_MODE="${BORG_DOWNLOAD_MODE:-sample}"
TARGET_RAW_BYTES="${BORG_TARGET_RAW_BYTES:-100000000000}"
BORG_TARGET_TOLERANCE_BYTES="${BORG_TARGET_TOLERANCE_BYTES:-50000000000}"
BORG_DOWNLOAD_SHARD_COUNT="${BORG_DOWNLOAD_SHARD_COUNT:-15}"
GSUTIL_OPTS=(-o "GSUtil:parallel_process_count=1")

typeset -a CLUSTERS
IFS=',' read -rA CLUSTERS <<< "${CLUSTERS_RAW}"

echo "Creating directories under ${RAW_DIR}..."
mkdir -p "${RAW_DIR}/events" "${RAW_DIR}/usage" "${RAW_DIR}/machines"

current_raw_bytes() {
  BORG_RAW_DIR_FOR_SIZE="${RAW_DIR}" python3 - <<'PY'
import os
from pathlib import Path

root = Path(os.environ["BORG_RAW_DIR_FOR_SIZE"]).expanduser()
total = 0
for sub in ("events", "machines", "usage"):
    path = root / sub
    if not path.exists():
        continue
    total += sum(p.stat().st_size for p in path.iterdir() if p.is_file())
print(total)
PY
}

download_object() {
  local cluster="$1"
  local remote_name="$2"
  local local_dir="$3"
  local local_prefix="$4"

  local shard_id="${remote_name#*-}"
  shard_id="${shard_id%.json.gz}"
  local local_path="${RAW_DIR}/${local_dir}/${cluster}_${local_prefix}-${shard_id}.json.gz"
  local legacy_path=""

  if [[ "${shard_id}" == "000000000000" ]]; then
    legacy_path="${RAW_DIR}/${local_dir}/${cluster}_${local_prefix}.json.gz"
  fi

  if [[ -f "${local_path}" ]]; then
    echo "Skipping existing ${local_path:t}"
    return 0
  fi

  if [[ -n "${legacy_path}" && -f "${legacy_path}" ]]; then
    echo "Skipping existing legacy ${legacy_path:t}"
    return 0
  fi

  echo "Downloading ${remote_name} -> ${local_path}"
  gsutil "${GSUTIL_OPTS[@]}" cp "gs://clusterdata_2019_${cluster}/${remote_name}" "${local_path}"
}

download_first_shard() {
  local cluster="$1"
  download_object "${cluster}" "instance_events-000000000000.json.gz" "events" "events"
  download_object "${cluster}" "instance_usage-000000000000.json.gz" "usage" "usage"
  download_object "${cluster}" "machine_events-000000000000.json.gz" "machines" "machines"
}

download_matching_series() {
  local cluster="$1"
  local remote_glob="$2"
  local local_dir="$3"
  local local_prefix="$4"

  local remote_name
  while IFS= read -r remote_path; do
    [[ -z "${remote_path}" ]] && continue
    remote_name="${remote_path:t}"
    download_object "${cluster}" "${remote_name}" "${local_dir}" "${local_prefix}"
  done < <(gsutil ls "gs://clusterdata_2019_${cluster}/${remote_glob}" | sort)
}

download_until_target() {
  local current_bytes
  current_bytes="$(current_raw_bytes)"
  echo "Current raw bytes: ${current_bytes}"
  echo "Target raw bytes: ${TARGET_RAW_BYTES}"
  echo "Tolerance bytes: ${BORG_TARGET_TOLERANCE_BYTES}"

  if (( current_bytes >= TARGET_RAW_BYTES )); then
    echo "Target already satisfied. Nothing to download."
    return 0
  fi

  local cluster
  local remote_name
  local soft_cap=$(( TARGET_RAW_BYTES + BORG_TARGET_TOLERANCE_BYTES ))

  echo "Building coherent cluster slices:"
  echo "- download all machine shards for a cluster"
  echo "- download all event shards for that same cluster"
  echo "- then add usage shards for that cluster"
  echo "- stop only after finishing a usage shard once size is within the acceptable window"

  for cluster in "${CLUSTERS[@]}"; do
    echo "-----------------------------------------------"
    echo "Preparing cluster ${cluster}..."
    while IFS= read -r remote_path; do
      [[ -z "${remote_path}" ]] && continue
      remote_name="${remote_path:t}"
      download_object "${cluster}" "${remote_name}" "machines" "machines"
    done < <(gsutil ls "gs://clusterdata_2019_${cluster}/machine_events-*.json.gz" | sort)

    while IFS= read -r remote_path; do
      [[ -z "${remote_path}" ]] && continue
      remote_name="${remote_path:t}"
      download_object "${cluster}" "${remote_name}" "events" "events"
    done < <(gsutil ls "gs://clusterdata_2019_${cluster}/instance_events-*.json.gz" | sort)

    while IFS= read -r remote_path; do
      [[ -z "${remote_path}" ]] && continue
      remote_name="${remote_path:t}"
      download_object "${cluster}" "${remote_name}" "usage" "usage"
      current_bytes="$(current_raw_bytes)"
      if (( current_bytes >= TARGET_RAW_BYTES && current_bytes <= soft_cap )); then
        echo "Reached acceptable target window after usage download."
        echo "Current raw bytes: ${current_bytes}"
        return 0
      fi
      if (( current_bytes > soft_cap )); then
        echo "Exceeded soft cap after completing a coherent usage shard."
        echo "Current raw bytes: ${current_bytes}"
        return 0
      fi
    done < <(gsutil ls "gs://clusterdata_2019_${cluster}/instance_usage-*.json.gz" | sort)
  done

  echo "Remote data exhausted before reaching target."
}


download_fixed_shards() {
  local cluster="$1"
  local shard_count="$2"

  echo "-----------------------------------------------"
  echo "Processing cluster ${cluster} with fixed shard count ${shard_count}..."

  download_object "${cluster}" "machine_events-000000000000.json.gz" "machines" "machines"

  local remote_name
  local event_index=0
  while IFS= read -r remote_path; do
    [[ -z "${remote_path}" ]] && continue
    remote_name="${remote_path:t}"
    download_object "${cluster}" "${remote_name}" "events" "events"
    event_index=$(( event_index + 1 ))
    if (( event_index >= shard_count )); then
      break
    fi
  done < <(gsutil ls "gs://clusterdata_2019_${cluster}/instance_events-*.json.gz" | sort)

  local usage_index=0
  while IFS= read -r remote_path; do
    [[ -z "${remote_path}" ]] && continue
    remote_name="${remote_path:t}"
    download_object "${cluster}" "${remote_name}" "usage" "usage"
    usage_index=$(( usage_index + 1 ))
    if (( usage_index >= shard_count )); then
      break
    fi
  done < <(gsutil ls "gs://clusterdata_2019_${cluster}/instance_usage-*.json.gz" | sort)
}

echo "Clusters: ${CLUSTERS[*]}"
echo "Download mode: ${DOWNLOAD_MODE}"

case "${DOWNLOAD_MODE}" in
  sample)
    for cluster in "${CLUSTERS[@]}"; do
      echo "-----------------------------------------------"
      echo "Processing cluster ${cluster}..."
      download_first_shard "${cluster}"
    done
    ;;
  all)
    for cluster in "${CLUSTERS[@]}"; do
      echo "-----------------------------------------------"
      echo "Processing cluster ${cluster}..."
      download_matching_series "${cluster}" "instance_events-*.json.gz" "events" "events"
      download_matching_series "${cluster}" "instance_usage-*.json.gz" "usage" "usage"
      download_matching_series "${cluster}" "machine_events-*.json.gz" "machines" "machines"
    done
    ;;
  target_bytes)
    download_until_target
    ;;
  fixed_shards)
    echo "Fixed shard count per cluster: ${BORG_DOWNLOAD_SHARD_COUNT}"
    for cluster in "${CLUSTERS[@]}"; do
      download_fixed_shards "${cluster}" "${BORG_DOWNLOAD_SHARD_COUNT}"
    done
    ;;
  *)
    echo "Unsupported BORG_DOWNLOAD_MODE=${DOWNLOAD_MODE}" >&2
    echo "Use one of: sample, all, target_bytes, fixed_shards" >&2
    exit 1
    ;;
esac

echo "-----------------------------------------------"
echo "Download complete. Raw files saved to ${RAW_DIR}"
