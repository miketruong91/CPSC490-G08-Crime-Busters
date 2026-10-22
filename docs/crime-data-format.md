# Standardized Crime Data Format

Related issues: Task #10; Story #5; normalization Task #11.

## Purpose and scope

This document defines version 1 of the project's standardized incident
record format. It includes crime or call category, location, date, and
time when available, while preserving the source and meaning of each
record.

This is a format specification. It does not claim that records have
already been normalized, loaded into a database, or integrated with
the map.

Source findings and limitations are documented in
[Crime Data Sources](crime-data-sources.md).

## Record structure

The initial exchange format is a UTF-8 JSON array containing one object
per source record. Every object includes the fields below. Fields marked
nullable use JSON null when their values are unavailable.

| Field | Type | Nullable | Definition |
|---|---|---|---|
| source | string | No | Stable identifier for the source dataset |
| source_record_id | string | No | Identifier supplied by the source; preserve leading zeros |
| record_kind | string | No | `call_for_service`, `crime_incident`, or `unknown`, based on source documentation |
| crime_type | string | Yes | Standard category: `burglary`, `theft`, `vandalism`, `assault`, or `other`; does not establish a confirmed crime |
| source_code | string | Yes | Original source category or call code |
| description | string | Yes | Original incident or call description |
| location | string | Yes | Source-provided address, block, or location description |
| city | string | Yes | Source-provided city name |
| agency | string | Yes | Source-provided agency identifier |
| incident_date | string | Yes | Calendar date in `YYYY-MM-DD` format |
| incident_time | string | Yes | Time in 24-hour `HH:MM:SS` format |
| timezone | string | Yes | Verified timezone name or null if unknown |
| latitude | number | Yes | Latitude in decimal degrees, EPSG:4326 |
| longitude | number | Yes | Longitude in decimal degrees, EPSG:4326 |
| location_precision | string | No | `exact`, `block`, `approximate`, or `unknown`, based on source documentation |
| disposition | string | Yes | Source-provided outcome or disposition text |
| quality_flags | array of strings | No | Missing, invalid, or uncertain data; use an empty array when none apply |

## General formatting rules

- Trim leading and trailing whitespace from text.
- Convert absent, empty, or whitespace-only nullable values to null.
- Preserve identifiers as strings.
- Preserve the wording and capitalization of source descriptions,
  codes, locations, city names, agency identifiers, and dispositions.
- Use lowercase values for standardized categories and record kinds.
- Never invent a missing date, time, address, category, or coordinate.
- Do not replace missing coordinates with zero.
- Do not assume a timezone or convert times to UTC until the source
  timezone is verified.
- Preserve original source values in the import evidence when a value
  cannot be converted.

## Costa Mesa field mapping

The initial mapping uses the PoliceIncidents Burglary layer 57 and
the sample documented in crime-data-sources.md.

| Standard field | Costa Mesa input or mapping rule |
|---|---|
| source | `costa_mesa_police_incidents` |
| source_record_id | ID |
| record_kind | `call_for_service` |
| crime_type | `burglary`, based on the evaluated Burglary layer 57 |
| source_code | Code |
| description | Nature |
| location | Location |
| city | City |
| agency | Agency |
| incident_date | Convert CallDate from `MM/DD/YYYY` to `YYYY-MM-DD` |
| incident_time | CallTime, validated as `HH:MM:SS` |
| timezone | null until verified |
| latitude | geometry.y from query output requested in EPSG:4326 |
| longitude | geometry.x from query output requested in EPSG:4326 |
| location_precision | `block` for the inspected block-level locations |
| disposition | Dispo; whitespace-only values become null |
| quality_flags | Generated from the validation rules below |

The numeric Type field has not been interpreted and must not be used
to infer a category. FID is not used as the permanent record identifier.

Mappings for Fullerton and Community Crime Map have not been defined.
Each additional source requires its own documented mapping.

## Validation and missing-value rules

1. Require nonempty source and source_record_id values. Records missing
   either value are held for correction and excluded from accepted output.
2. Validate dates against the calendar and times against the 24-hour
   clock. Invalid values become null and receive `invalid_date` or
   `invalid_time` flags.
3. Missing category, location, date, or time receives the corresponding
   `missing_crime_type`, `missing_location`, `missing_date`, or
   `missing_time` flag.
4. Unknown categories become null with `unmapped_category` until reviewed.
   Use `other` only for a known category outside the listed categories.
5. Require finite numeric latitude between -90 and 90 and longitude
   between -180 and 180. If either coordinate is missing or invalid,
   set both to null and add `missing_coordinates` or
   `invalid_coordinates`. These records cannot appear in radius results.
6. Unknown timezone receives `timezone_unverified`. Block-level or
   approximate locations receive `location_not_exact`.
7. Use the pair (source, source_record_id) to identify repeated source
   records. Do not silently overwrite conflicting versions; flag them
   for review. Matching dates or coordinates alone do not prove duplication.
8. Retain canceled calls and other dispositions in the standardized
   records. Their inclusion in analytical results requires a separate
   documented filtering rule.
9. Flagged records remain traceable. A record with a missing field
   cannot participate in a filter or calculation requiring that field.
10. A call-for-service record must never be presented as a confirmed crime
    solely because its category is burglary or another crime-related label.

## Example standardized record

This example illustrates the proposed conversion of one record from
the inspected Costa Mesa sample. It is not evidence that the full
dataset has been normalized.

```json
[
  {
    "source": "costa_mesa_police_incidents",
    "source_record_id": "2025068460",
    "record_kind": "call_for_service",
    "crime_type": "burglary",
    "source_code": "459V",
    "description": "BURGLARY VEHICLE",
    "location": "100 BLK E 18TH ST",
    "city": "COSTA MESA",
    "agency": "CMPD",
    "incident_date": "2025-07-26",
    "incident_time": "12:12:51",
    "timezone": null,
    "latitude": 33.639379802719652,
    "longitude": -117.91764968214937,
    "location_precision": "block",
    "disposition": null,
    "quality_flags": [
      "timezone_unverified",
      "location_not_exact"
    ]
  }
]
```

## Review and future changes

Task #10 defines the fields and conversion rules. Task #11 will apply
them and provide normalization evidence. Database schema and loading
work are tracked separately.

The team may revise this format through a reviewed pull request.
Changes affecting existing records or code must describe any required
conversion and compatibility updates.
