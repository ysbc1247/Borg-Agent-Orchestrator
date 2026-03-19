# Borg-MAS-Optimizer

Project scaffold for a Borg-inspired multi-agent scheduling and cluster optimization system.

## Structure

```text
.
├── Agents.md
├── scripts/
│   ├── download_shards.sh
│   ├── data_flattener.py
│   └── make_dataset.py
├── src/
│   ├── agents/
│   └── environment/
├── .gitignore
└── README.md
```

## Data Layout

Raw Borg data should stay outside the repository by default.

- Default raw data path: `~/Documents/borg_data`
- Default processed data path: `~/Documents/borg_processed`

Both scripts can be overridden with environment variables:

```bash
export BORG_RAW_DIR=~/Documents/borg_data
export BORG_PROCESSED_DIR=~/Documents/borg_processed
python scripts/data_flattener.py
```

By default, the project processes clusters `b` through `g`.
Clusters `a` and `h` are excluded because their flattened usage schemas differ from the main dataset group.

To download shards into the default external location:

```bash
./scripts/download_shards.sh
```

## Python Environment

Use a project-local virtual environment in PyCharm and install dependencies from the repo metadata:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
