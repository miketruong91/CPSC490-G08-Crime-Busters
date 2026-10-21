# Crime Pattern Analysis — selected-area filtering

**Goal:** #14 (Identify possible crime patterns)  
**Objective:** #15 (Analyze crime incidents within the selected area)  
**Task addressed:** #17 (Identify crime incidents within the selected area)  
**Related future task:** #18 (Analyze crime frequency by crime type, date, and time)

## Purpose and scope

Task #17 identifies crime incident records inside a user-selected circular
search area. It returns only those records for later frequency analysis under
Task #18. It does not draw a map, calculate statistics, or connect to a live
crime database. These are separate integration steps.

## Inputs and assumptions

- Search center: latitude in [-90, 90] and longitude in [-180, 180], decimal degrees.
- Search radius: a finite, nonnegative number in **miles**.
- Incident records: dictionaries containing numeric `latitude` and `longitude`;
  all other fields (e.g. incident ID, crime type, date, time) are preserved.
- Coordinates must be incident-level points. Actual public dataset, field names,
  coordinate quality, and data source **have not yet been confirmed** with Goal 1.
- A circular radius is supported in the current prototype. Polygon/neighborhood
  boundaries are **not** implemented.

## Filtering method

The standalone Python prototype in `prototype/area_filter.py` calculates
great-circle distance using the Haversine formula (Earth radius 3958.7613 miles).

1. Validate the user-selected center and radius.
2. For each incident, validate its latitude and longitude.
3. Compute distance from the search center to the incident.
4. **Include** the incident when distance is less than or equal to the radius.
5. **Exclude** incidents outside the radius. Skip records with missing or invalid
   coordinates; these records must not be interpreted as evidence of no crime.
6. Return the selected incident dictionaries unchanged and in input order.

The returned list can be passed to Task #18 to count incidents by crime type,
date, and time. Invalid search parameters raise `ValueError`.

## Expected output

A list of incident records meeting the area condition, including all original
available fields. An empty list means no valid-coordinate records matched
the search criteria, **not** necessarily that no crime occurred.

## Verification

Run the unit tests from the repository root:

```bash
python -m unittest discover -s prototype -p 'test_area_filter.py' -v
```

Tests cover:
- Incidents inside and outside a 2-mile search radius.
- A zero-radius search and an empty result.
- A point exactly on the computed boundary (included).
- Missing/invalid incident coordinates (skipped).
- Invalid radius or search-center inputs (rejected).
- Preservation of the original crime fields.

The tests use **synthetic example coordinates**, not official crime records.
Passing these tests verifies the isolated filtering logic, not integration with
the actual dataset, API, database, or interactive map.

## Dependencies and follow-up

- **Goal 1:** Confirm the crime dataset, location precision, schema, and rules
  for incidents with missing coordinates.
- **Goal 3:** Confirm how selected center/radius are supplied and whether the
  map already performs geographic filtering, to avoid duplicate logic.
- **Task #18:** Use the filtered incident list to compute crime frequency.
- Before marking #17 complete, the team should review this approach, run the
  tests in the repository, and agree whether prototype-only filtering satisfies
  the Issue's Definition of Done or whether dataset integration is required.
