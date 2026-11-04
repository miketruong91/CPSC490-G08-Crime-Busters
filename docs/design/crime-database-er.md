> Epic: #3 · Story: #28 · Task: #32 (schema); related: #5, #10, #11, #35, #36

# Crime Database ER Diagram

This document describes the initial SQLite schema for standardized crime
incident records. It is a design for review, not evidence that records have
been loaded. The fields come from version 1 of the
[Standardized Crime Data Format](../crime-data-format.md); the executable
schema is [`prototype/schema.sql`](../../prototype/schema.sql).

## Entity-relationship diagram

```mermaid
erDiagram
    INCIDENTS ||--o{ INCIDENT_QUALITY_FLAGS : "has"

    INCIDENTS {
        integer id PK
        text source UK "stable source dataset id"
        text source_record_id UK "source-supplied id, kept as text"
        text record_kind "call_for_service, crime_incident, unknown"
        text crime_type "burglary, theft, vandalism, assault, other; nullable"
        text source_code "nullable"
        text description "nullable"
        text location "nullable"
        text city "nullable"
        text agency "nullable"
        text disposition "nullable"
        text incident_date "YYYY-MM-DD; nullable"
        text incident_time "HH:MM:SS; nullable"
        text timezone "nullable until verified"
        real latitude "EPSG:4326; nullable"
        real longitude "EPSG:4326; nullable"
        text location_precision "exact, block, approximate, unknown"
    }

    INCIDENT_QUALITY_FLAGS {
        integer incident_id PK, FK
        text flag PK "e.g. timezone_unverified"
    }
```

## Design notes

- **Identity.** `(source, source_record_id)` is unique, matching validation
  rule 7. A conflicting second version of a record is rejected by the
  database, so the loader must flag it for review instead of overwriting it.
- **Quality flags.** The format's `quality_flags` array becomes the child
  table `incident_quality_flags`, so records can be queried by flag. A record
  with no flags has no child rows.
- **Coordinates.** Latitude and longitude are both present and in range, or
  both NULL (validation rule 5). Missing coordinates are never stored as 0.
  Records without coordinates cannot appear in radius results.
- **Dates and times.** Stored as ISO text and checked with SQLite's
  `date()` and `time()` functions. Invalid values are stored as NULL with
  an `invalid_date` or `invalid_time` flag.
- **Source values.** Original codes, descriptions, locations and
  dispositions are stored as supplied. A call for service is not a confirmed
  crime; `record_kind` keeps that distinction visible.
- **Excluded records.** Records missing `source` or `source_record_id` are
  held for correction and never enter the database (validation rule 1).

## Open questions for the team

- Whether `quality_flags` should stay a child table or become a JSON text
  column.
- Whether the flag vocabulary should be enforced by the database or by the
  loader.
- Whether a `sources` table is needed once a second dataset is adopted.
- Reuse terms for the Costa Mesa data remain unresolved; see
  [Crime Data Sources](../crime-data-sources.md).
