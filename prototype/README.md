# Prototype

Proof-of-concept code for Crime Busters, an interactive crime map and database. The current prototype normalizes Costa Mesa crime records, loads them into SQLite, and includes functions for filtering incidents by area and calculating crime frequencies.

## How to run

Use Python 3.12. From the repository root, create a virtual environment and install the prototype dependencies:

```bash
cd prototype
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

### Create and populate the SQLite database

Save a Costa Mesa ArcGIS query response as `costa_mesa_query.json` in the `prototype` directory. Use `outSR=4326` when exporting the query. See [Crime Data Sources](../docs/crime-data-sources.md) for source details.

From the `prototype` directory, run:

```bash
python normalize.py costa_mesa_query.json standardized.json
python load_db.py standardized.json crime.db
```

The first command creates `standardized.json`. The second creates `crime.db` if needed, loads the records, and reports how many were inserted, unchanged, or held for review. Check for `verification passed` in the output.

## How to test

From the `prototype` directory with the virtual environment active, run:

```bash
python -m pip install pytest
python -m pytest -q
```

## What it proves

The prototype can convert Costa Mesa records into a consistent format, store them in SQLite, and verify that retrieved records match the standardized input. The tests also cover area filtering and crime frequency calculations.

## Status

| Sprint | Increment |
| --- | --- |
| Sprint 3 | The Python prototype includes record normalization, SQLite loading and retrieval, area filtering, and crime frequency calculations. The Flask and Leaflet demo setup is pending. |
