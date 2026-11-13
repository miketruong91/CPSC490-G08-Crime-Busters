import os
import sqlite3
from contextlib import closing
from pathlib import Path

from flask import Flask, jsonify, render_template

app = Flask(__name__)

default_db = Path(__file__).with_name("crime.db")
app.config["DATABASE"] = os.environ.get("CRIME_DB_PATH", str(default_db))


@app.get("/")
def home():
    return render_template("index.html")


@app.get("/health")
def health():
    return jsonify(status="ok")


@app.get("/api/incidents")
def incidents():
    path = Path(app.config["DATABASE"]).expanduser().resolve()

    try:
        with closing(sqlite3.connect(
            path.as_uri() + "?mode=ro", uri=True
        )) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("""
                SELECT id, source, source_record_id, record_kind,
                       crime_type, description, location,
                       incident_date, incident_time, timezone,
                       latitude, longitude, location_precision
                FROM incidents
                WHERE latitude BETWEEN -90 AND 90
                  AND longitude BETWEEN -180 AND 180
                ORDER BY id
            """).fetchall()

        records = [dict(row) for row in rows]
        return jsonify(count=len(records), incidents=records)

    except sqlite3.Error:
        app.logger.exception("Could not read incident database")
        return jsonify(error="Incident database unavailable"), 503
