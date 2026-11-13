# Prototype

The Crime Busters prototype displays historical Costa Mesa burglary-related calls for service on a Leaflet map. Flask serves the map and reads the records from a local SQLite database. Locations are block-level, and the source timezone is unverified.

## How to run

From the root of a fresh clone, create a Python virtual environment and install the dependencies. The demo was tested with Python 3.11.9 and Flask 3.1.3.

```bash
cd prototype
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

### Create and populate the SQLite database

From `prototype/`, normalize the bundled Costa Mesa snapshot and load it into SQLite.

```bash
python normalize.py data/layer57.json standardized.json
python load_db.py standardized.json crime.db
```

On a fresh database, the loader should report `inserted 19, unchanged 0, held 0`, followed by `verification passed`. Running the same load again should report `unchanged 19`.

See [Crime Data Sources](../docs/crime-data-sources.md) for background on the Costa Mesa data.

### Launch the map

From `prototype/` with the virtual environment active, run:

```bash
python -m flask --app app run --port 5051
```

Open the [local map](http://127.0.0.1:5051/). It should show **19 records across 13 mapped locations**. Click a marker to view the calls associated with that location. The [incident API](http://127.0.0.1:5051/api/incidents) should return `"count": 19`.

Flask uses `crime.db` next to `app.py` by default. Press **Ctrl+C** in Terminal to stop the server.

## How to test

From `prototype/` with the virtual environment active, run:

```bash
python -m pip install pytest
python -m pytest -q
```

## What it proves

The prototype can normalize the Costa Mesa snapshot, store and verify its records in SQLite, and display them on a local map. Records that share coordinates appear under the same marker. The demo shows calls for service, which should be interpreted as reported activity.

## Status

| Sprint | Increment |
| --- | --- |
| Sprint 3 | Added a runnable Flask and Leaflet demo that displays 19 Costa Mesa calls for service across 13 mapped locations. |
