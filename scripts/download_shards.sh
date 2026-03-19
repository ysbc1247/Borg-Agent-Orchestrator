#!/bin/zsh

# 1. Create the local directory structure
echo "Creating directories..."
mkdir -p ./borg_data/events ./borg_data/usage ./borg_data/machines

# 2. Loop through all 8 clusters (a to h)
# Using the -o flag to prevent macOS multiprocessing hangs
for c in a b c d e f g h; do
  echo "-----------------------------------------------"
  echo "Processing Cluster ${c}..."

  # Download Instance Events
  echo "Downloading Events for ${c}..."
  gsutil -o "GSUtil:parallel_process_count=1" cp gs://clusterdata_2019_${c}/instance_events-000000000000.json.gz ./borg_data/events/${c}_events.json.gz

  # Download Instance Usage
  echo "Downloading Usage for ${c}..."
  gsutil -o "GSUtil:parallel_process_count=1" cp gs://clusterdata_2019_${c}/instance_usage-000000000000.json.gz ./borg_data/usage/${c}_usage.json.gz

  # Download Machine Events
  echo "Downloading Machine Specs for ${c}..."
  gsutil -o "GSUtil:parallel_process_count=1" cp gs://clusterdata_2019_${c}/machine_events-000000000000.json.gz ./borg_data/machines/${c}_machines.json.gz

done

echo "-----------------------------------------------"
echo "Download Complete. All shards saved to ./borg_data"