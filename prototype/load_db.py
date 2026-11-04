"""Load standardized crime records into SQLite and verify they can be read
back (Tasks #35 and #36, Story #28). Schema: prototype/schema.sql.

    python3 prototype/load_db.py standardized.json crime.db

Standard library only. Conflicting duplicates are reported, never overwritten.
"""
from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

SCHEMA = Path(__file__).with_name("schema.sql")

FIELDS = ["source", "source_record_id", "record_kind", "crime_type", "source_code",
          "description", "location", "city", "agency", "incident_date",
          "incident_time", "timezone", "latitude", "longitude",
          "location_precision", "disposition"]

# The loader enforces the flag vocabulary (see docs/design/crime-database-er.md).
# Keep this list in step with the validation rules in docs/crime-data-format.md.
ALLOWED_FLAGS = {
    "missing_crime_type", "missing_location", "missing_date", "missing_time",
    "invalid_date", "invalid_time", "unmapped_category", "missing_coordinates",
    "invalid_coordinates", "timezone_unverified", "location_not_exact",
}


def connect(path):
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA.read_text(encoding="utf-8"))
    return conn


def get_incident(conn, source, source_record_id):
    """Read one record back in the standardized format (Task #36)."""
    row = conn.execute(
        f"SELECT id, {', '.join(FIELDS)} FROM incidents "
        "WHERE source = ? AND source_record_id = ?", (source, source_record_id)).fetchone()
    if row is None:
        return None
    record = dict(zip(FIELDS, row[1:]))
    record["quality_flags"] = sorted(r[0] for r in conn.execute(
        "SELECT flag FROM incident_quality_flags WHERE incident_id = ?", (row[0],)))
    return record


def _same(stored, record):
    """Flags are a set; their order is not stored."""
    a = {**stored, "quality_flags": sorted(stored["quality_flags"])}
    b = {**record, "quality_flags": sorted(record["quality_flags"])}
    return a == b


def load_records(conn, records):
    """Insert records in one transaction. Returns a summary dict (Task #35).

    inserted   new records stored
    unchanged  already stored and identical, so skipped
    held       not stored: unknown flag, or a conflicting stored version
    """
    summary = {"inserted": 0, "unchanged": 0, "held": []}
    with conn:
        for record in records:
            unknown = set(record["quality_flags"]) - ALLOWED_FLAGS
            if unknown:
                summary["held"].append({"source_record_id": record["source_record_id"],
                                        "reason": f"unknown flag(s): {sorted(unknown)}"})
                continue
            stored = get_incident(conn, record["source"], record["source_record_id"])
            if stored is not None:
                if _same(stored, record):
                    summary["unchanged"] += 1
                else:
                    summary["held"].append({"source_record_id": record["source_record_id"],
                                            "reason": "conflicts with stored version"})
                continue
            try:
                cur = conn.execute(
                    f"INSERT INTO incidents ({', '.join(FIELDS)}) "
                    f"VALUES ({', '.join('?' * len(FIELDS))})",
                    [record[f] for f in FIELDS])
            except sqlite3.IntegrityError as e:
                summary["held"].append({"source_record_id": record["source_record_id"],
                                        "reason": f"database rejected record: {e}"})
                continue
            conn.executemany("INSERT INTO incident_quality_flags VALUES (?, ?)",
                             [(cur.lastrowid, f) for f in set(record["quality_flags"])])
            summary["inserted"] += 1
    return summary


def verify(conn, records):
    """Check the stored count and every stored record against the input
    (Story #28: stored count and retrieved information match the records
    loaded). Returns a list of problems; empty means they match."""
    problems = []
    for record in records:
        stored = get_incident(conn, record["source"], record["source_record_id"])
        if stored is None:
            problems.append(f"{record['source_record_id']}: not found")
        elif not _same(stored, record):
            problems.append(f"{record['source_record_id']}: stored values differ")
    expected = len({(r["source"], r["source_record_id"]) for r in records})
    count = conn.execute("SELECT COUNT(*) FROM incidents").fetchone()[0]
    if count < expected:
        problems.append(f"stored count {count} is below the {expected} records loaded")
    return problems


def main(argv):
    if len(argv) != 3:
        sys.exit("usage: load_db.py <standardized.json> <database.db>")
    with open(argv[1], encoding="utf-8") as f:
        records = json.load(f)
    conn = connect(argv[2])
    summary = load_records(conn, records)
    print(f"inserted {summary['inserted']}, unchanged {summary['unchanged']}, "
          f"held {len(summary['held'])}")
    for h in summary["held"]:
        print(f"  held: {h}")
    problems = verify(conn, [r for r in records
                             if r["source_record_id"] not in
                             {h["source_record_id"] for h in summary["held"]}])
    for p in problems:
        print(f"  PROBLEM: {p}")
    print("verification passed" if not problems else "verification FAILED")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
