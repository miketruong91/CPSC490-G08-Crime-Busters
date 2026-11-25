"""Normalize saved Anaheim or Fullerton samples (Task #97).

Offline only; accepts the raw JSON envelopes documented in city-data-import.md.
    python normalize_city.py anaheim raw.json standardized.json
    python normalize_city.py fullerton raw.json standardized.json
Held records are written to <output>.held.json and cause exit status 1.
"""
from __future__ import annotations

import argparse
from datetime import datetime, date
import json
from pathlib import Path
import re

ANAHEIM_CATEGORIES = {
    "Burglary": "burglary", "Theft / Larceny": "theft",
    "Motor Vehicle Theft": "theft", "Vandalism": "vandalism",
    "Assault": "assault", "Drugs / Alchohol Violations": "other",
    "Disturbing the Peace": "other", "Fraud": "other",
    "Sex Crimes": "other", "DUI": "other", "Robbery": "other",
    "Weapons": "other",
}
# Conservative mapping: the other call labels await category review.
FULLERTON_CATEGORIES = {"THEFT PETTY RPT": "theft", "BURGLARY RPT": "burglary"}


def text(value):
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError("text fields and identifiers must be strings")
    return value.strip() or None


def base_record(source, identifier, kind, category, description, location, mapping):
    identifier = text(identifier)
    if identifier is None:
        raise ValueError("missing source record identifier")
    category, description, location = map(text, (category, description, location))
    crime_type = mapping.get(category)
    precision = "block" if location and re.search(r"\bBLOCK\b", location) else "unknown"
    flags = ["missing_coordinates", "timezone_unverified"]
    if precision == "block":
        flags.append("location_not_exact")
    if location is None:
        flags.append("missing_location")
    if crime_type is None:
        flags.append("missing_crime_type" if category is None else "unmapped_category")
    return {
        "source": source, "source_record_id": identifier,
        "record_kind": kind, "crime_type": crime_type,
        "source_code": category, "description": description,
        "location": location, "city": None, "agency": None,
        "incident_date": None, "incident_time": None, "timezone": None,
        "latitude": None, "longitude": None,
        "location_precision": precision, "disposition": None,
        "quality_flags": flags,
    }


def normalize_anaheim(row):
    if row.get("source_id") != "anaheim-incidents" or row.get("area") != "Anaheim Police":
        raise ValueError("record is not from the evaluated Anaheim source/agency")
    # Case IDs are preserved; rolling export row numbers are not permanent IDs.
    record = base_record("anaheimcrime_anaheim_incidents", row.get("case_id"),
                         "crime_incident", row.get("category"), row.get("description"),
                         row.get("block"), ANAHEIM_CATEGORIES)
    record["agency"] = "Anaheim Police"
    raw_date = text(row.get("record_date"))
    if raw_date is None:
        record["quality_flags"].append("missing_date")
    else:
        try:
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", raw_date):
                raise ValueError("date must be YYYY-MM-DD")
            record["incident_date"] = date.fromisoformat(raw_date).isoformat()
        except ValueError:
            record["quality_flags"].append("invalid_date")
    record["quality_flags"].append("missing_time")
    return record


def normalize_fullerton(row):
    record = base_record("fullerton_police_calls_for_service", row.get("incident_number"),
                         "call_for_service", row.get("type"), row.get("type"),
                         row.get("address"), FULLERTON_CATEGORIES)
    if not re.fullmatch(r"\d{2}-\d+", record["source_record_id"]):
        raise ValueError("expected Fullerton year-number incident identifier")
    raw = text(row.get("date_time"))
    if raw is None:
        record["quality_flags"].extend(["missing_date", "missing_time"])
    else:
        try:
            parsed = datetime.strptime(raw, "%m/%d/%Y %I:%M %p")
            record["incident_date"] = parsed.date().isoformat()
            # :00 is format padding; the saved viewer supplies minute precision.
            record["incident_time"] = parsed.strftime("%H:%M:00")
        except ValueError:
            record["quality_flags"].extend(["invalid_date", "invalid_time"])
    return record


def normalize_records(document, city):
    if not isinstance(document, dict) or not isinstance(document.get("records"), list):
        raise ValueError("expected a raw JSON object with a records array")
    if city == "anaheim":
        if document.get("site") != "anaheimcrime.com":
            raise ValueError("unexpected Anaheim envelope")
        convert = normalize_anaheim
    elif city == "fullerton":
        if document.get("source_url") != "https://www2.cityoffullerton.com/webdata/apps/cfs/":
            raise ValueError("unexpected Fullerton envelope")
        convert = normalize_fullerton
    else:
        raise ValueError("city must be anaheim or fullerton")
    accepted, held, seen = [], [], {}
    for index, row in enumerate(document["records"]):
        try:
            if not isinstance(row, dict):
                raise ValueError("record must be an object")
            record = convert(row)
            record["quality_flags"] = sorted(set(record["quality_flags"]))
            key = (record["source"], record["source_record_id"])
            if key in seen:
                if seen[key] != record:
                    raise ValueError("conflicting duplicate identifier; first accepted record retained")
                continue
            seen[key] = record
            accepted.append(record)
        except ValueError as error:
            held.append({"index": index, "reason": str(error), "raw_record": row})
    return accepted, held


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("city", choices=["anaheim", "fullerton"])
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    held_path = args.output.with_suffix(args.output.suffix + ".held.json")
    paths = [args.input.resolve(), args.output.resolve(), held_path.resolve()]
    if len(set(paths)) != 3:
        parser.error("input, output, and held report must be different paths")
    try:
        accepted, held = normalize_records(json.loads(args.input.read_text(encoding="utf-8-sig")), args.city)
    except (ValueError, OSError) as error:
        parser.error(str(error))
    args.output.write_text(json.dumps(accepted, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    held_path.write_text(json.dumps(held, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"accepted {len(accepted)} record(s); held {len(held)}")
    return 1 if held else 0


if __name__ == "__main__":
    raise SystemExit(main())
