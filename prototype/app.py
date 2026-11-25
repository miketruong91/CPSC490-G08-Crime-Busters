import os
import sqlite3
from contextlib import closing
from pathlib import Path

from flask import Flask, jsonify, render_template

app = Flask(__name__)

combined_db = Path(__file__).with_name("crime-multicity.db")
default_db = combined_db if combined_db.exists() else Path(__file__).with_name("crime.db")
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


@app.get("/api/map-incidents")
def map_incidents():
    path = Path(app.config["DATABASE"]).expanduser().resolve()

    try:
        with closing(sqlite3.connect(
            path.as_uri() + "?mode=ro", uri=True
        )) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("""
                SELECT id, source, source_record_id, record_kind,
                       crime_type, description, location, city,
                       incident_date, incident_time, timezone,
                       latitude, longitude, location_precision
                FROM incidents
                ORDER BY id
            """).fetchall()
            has_geocoding = conn.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='incident_geocoding'").fetchone()
            provenance = {}
            if has_geocoding:
                provenance = {row['incident_id']: dict(row) for row in conn.execute(
                    'SELECT incident_id, provider, method, selected_query_address, matched_address FROM incident_geocoding')}


        from build_map_db import CITY_BY_SOURCE
        records, by_city = [], {}
        for row in rows:
            record = dict(row)
            # Source context supplies a display city without rewriting the
            # publisher's original city field (which may be absent).
            record['source_city'] = record['city']
            record['city'] = CITY_BY_SOURCE.get(record['source'], record['city'] or 'Unknown')
            coverage = by_city.setdefault(record['city'], dict(total=0, mapped=0, unmapped=0))
            coverage['total'] += 1
            if record['latitude'] is None or record['longitude'] is None:
                coverage['unmapped'] += 1
                continue
            coverage['mapped'] += 1
            record['geocoding'] = provenance.get(record['id'])
            record['location_label'] = ('Approximate location' if record['location_precision'] != 'exact'
                                        else 'Publisher-supplied location')
            if record['geocoding'] and 'direction_unverified' in record['geocoding']['method']:
                record['location_label']='Approximate location — street direction unverified'
            elif record['geocoding'] and 'geometry_crossing' in record['geocoding']['method']:
                record['location_label']='Approximate intersection'
            records.append(record)
        return jsonify(count=len(records), total_records=len(rows),
                       unmapped_count=len(rows)-len(records), by_city=by_city, incidents=records)

    except sqlite3.Error:
        app.logger.exception("Could not read incident database")
        return jsonify(error="Incident database unavailable"), 503
