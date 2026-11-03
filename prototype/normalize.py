"""Normalize Costa Mesa PoliceIncidents (layer 57) records to the project's
standardized incident format, version 1 (Task #11, Story #5).

Rules come from docs/crime-data-format.md. Standard library only.

    python3 prototype/normalize.py costa_mesa_query.json standardized.json

The input is the JSON returned by the layer's Query page (outSR=4326).
Records that cannot be accepted (no ID, or a conflicting duplicate) are not
written to the output; they are listed on stderr so they can be corrected.
"""
from __future__ import annotations

import json
import math
import re
import sys
from datetime import datetime

SOURCE = "costa_mesa_police_incidents"
TIME_RE = re.compile(r"^(\d{2}):(\d{2}):(\d{2})$")


def clean(value):
    """Trim text; absent, empty or whitespace-only values become None."""
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def convert_date(raw):
    """MM/DD/YYYY -> (YYYY-MM-DD, flag). Invalid dates become None + flag."""
    text = clean(raw)
    if text is None:
        return None, "missing_date"
    try:
        return datetime.strptime(text, "%m/%d/%Y").strftime("%Y-%m-%d"), None
    except ValueError:
        return None, "invalid_date"


def validate_time(raw):
    """HH:MM:SS on the 24-hour clock -> (time, flag)."""
    text = clean(raw)
    if text is None:
        return None, "missing_time"
    m = TIME_RE.match(text)
    if m and int(m[1]) < 24 and int(m[2]) < 60 and int(m[3]) < 60:
        return text, None
    return None, "invalid_time"


def _number(value):
    """A finite number, or None. Booleans and numeric strings are rejected."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return float(value) if math.isfinite(value) else None


def validate_coordinates(geometry):
    """-> (latitude, longitude, flag). Both null if either is bad (rule 5).

    Missing coordinates are never replaced with zero.
    """
    geometry = geometry or {}
    x, y = geometry.get("x"), geometry.get("y")      # x = longitude, y = latitude
    if x is None or y is None:
        return None, None, "missing_coordinates"
    lon, lat = _number(x), _number(y)
    if lat is None or lon is None or not -90 <= lat <= 90 or not -180 <= lon <= 180:
        return None, None, "invalid_coordinates"
    return lat, lon, None


def normalize_feature(feature):
    """One ArcGIS feature -> a standardized record, or None if it has no ID."""
    attrs = feature.get("attributes") or {}
    record_id = clean(attrs.get("ID"))
    if record_id is None:                              # rule 1: held for correction
        return None

    flags = []
    incident_date, flag = convert_date(attrs.get("CallDate"))
    flags += [flag] if flag else []
    incident_time, flag = validate_time(attrs.get("CallTime"))
    flags += [flag] if flag else []
    latitude, longitude, flag = validate_coordinates(feature.get("geometry"))
    flags += [flag] if flag else []

    location = clean(attrs.get("Location"))
    if location is None:
        flags.append("missing_location")

    # The layer is the Burglary layer, so crime_type is fixed. The numeric
    # Type field is not interpreted (format doc, Costa Mesa mapping).
    flags += ["timezone_unverified", "location_not_exact"]

    return {
        "source": SOURCE,
        "source_record_id": record_id,
        "record_kind": "call_for_service",
        "crime_type": "burglary",
        "source_code": clean(attrs.get("Code")),
        "description": clean(attrs.get("Nature")),
        "location": location,
        "city": clean(attrs.get("City")),
        "agency": clean(attrs.get("Agency")),
        "incident_date": incident_date,
        "incident_time": incident_time,
        "timezone": None,
        "latitude": latitude,
        "longitude": longitude,
        "location_precision": "block",
        "disposition": clean(attrs.get("Dispo")),
        "quality_flags": flags,
    }


def normalize(payload):
    """ArcGIS query response -> (accepted records, held records).

    A repeated (source, source_record_id) that is identical is dropped; a
    conflicting version is held for review rather than overwriting (rule 7).
    """
    accepted, held, seen = [], [], {}
    for index, feature in enumerate(payload.get("features", [])):
        record = normalize_feature(feature)
        if record is None:
            held.append({"index": index, "reason": "missing_source_record_id"})
            continue
        key = (record["source"], record["source_record_id"])
        if key in seen:
            if seen[key] != record:
                held.append({"index": index, "reason": "conflicting_duplicate",
                             "source_record_id": record["source_record_id"]})
            continue
        seen[key] = record
        accepted.append(record)
    return accepted, held


def main(argv):
    if len(argv) != 3:
        sys.exit("usage: normalize.py <costa_mesa_query.json> <standardized.json>")
    with open(argv[1], encoding="utf-8") as f:
        payload = json.load(f)
    accepted, held = normalize(payload)
    with open(argv[2], "w", encoding="utf-8") as f:
        json.dump(accepted, f, indent=2)
        f.write("\n")
    print(f"accepted {len(accepted)} record(s); held {len(held)}", file=sys.stderr)
    for h in held:
        print(f"  held: {h}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
