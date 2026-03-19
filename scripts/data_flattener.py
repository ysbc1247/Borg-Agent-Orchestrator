import os

import polars as pl

# Configuration
RAW_DIR = "./borg_data"
OUT_DIR = "./borg_processed"
os.makedirs(OUT_DIR, exist_ok=True)


def flatten_cluster(cluster_id):
    """Parses nested JSON files into flat Parquet for a specific cluster."""
    print(f"\n⚡️ Flattening Cluster: {cluster_id}")

    # --- 1. PROCESS MACHINES (The Hardware Grid) ---
    m_path = f"{RAW_DIR}/machines/{cluster_id}_machines.json.gz"
    if os.path.exists(m_path):
        # We read as NDJSON because Google's 2019 trace is newline-delimited JSON
        df_m = pl.read_ndjson(m_path)
        # Extract nested 'capacity' fields
        df_m = df_m.with_columns([
            pl.col("capacity").struct.field("cpus").alias("machine_cpu"),
            pl.col("capacity").struct.field("memory").alias("machine_mem")
        ]).drop("capacity")

        df_m.write_parquet(f"{OUT_DIR}/{cluster_id}_machines.parquet")
        print(f"✅ Machines: {df_m.shape[0]} nodes processed.")

    # --- 2. PROCESS EVENTS (Lifecycle & Failure Labels) ---
    e_path = f"{RAW_DIR}/events/{cluster_id}_events.json.gz"
    if os.path.exists(e_path):
        df_e = pl.read_ndjson(e_path)
        # Extract nested 'resource_request'
        df_e = df_e.with_columns([
            pl.col("resource_request").struct.field("cpus").alias("req_cpu"),
            pl.col("resource_request").struct.field("memory").alias("req_mem")
        ]).drop("resource_request")

        df_e.write_parquet(f"{OUT_DIR}/{cluster_id}_events.parquet")
        print(f"✅ Events: {df_e.shape[0]} events processed.")

    # --- 3. PROCESS USAGE (The Time-Series) ---
    u_path = f"{RAW_DIR}/usage/{cluster_id}_usage.json.gz"
    if os.path.exists(u_path):
        # Usage files are huge. Polars read_ndjson is memory-efficient.
        df_u = pl.read_ndjson(u_path)

        # Flatten average and maximum usage dictionaries
        # We drop 'cpu_histogram' to keep your 24GB RAM happy
        df_u = df_u.with_columns([
            pl.col("average_usage").struct.field("cpus").alias("avg_cpu"),
            pl.col("average_usage").struct.field("memory").alias("avg_mem"),
            pl.col("maximum_usage").struct.field("cpus").alias("max_cpu"),
            pl.col("maximum_usage").struct.field("memory").alias("max_mem")
        ]).drop(["average_usage", "maximum_usage", "cpu_histogram"])

        # Add cluster label for multi-cluster training later
        df_u = df_u.with_columns(pl.lit(cluster_id).alias("cluster_id"))

        df_u.write_parquet(f"{OUT_DIR}/{cluster_id}_usage.parquet")
        print(f"✅ Usage: {df_u.shape[0]} usage samples processed.")


if __name__ == "__main__":
    clusters = ["a", "b", "c", "d", "e", "f", "g", "h"]

    for c in clusters:
        try:
            flatten_cluster(c)
        except Exception as e:
            print(f"❌ Error in cluster {c}: {e}")

    print("\n🚀 All done! You can now delete the ./borg_data folder to save space.")
