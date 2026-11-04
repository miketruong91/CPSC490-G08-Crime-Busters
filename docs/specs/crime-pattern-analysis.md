# Specification — Crime Pattern Analysis

> Epic: #14 · Stories: #15, #16 · Tasks: #17, #18, #19, #20
> Owner: Alex Reyes · Status: draft for teammate review

## Scope

Goal 2: Identify possible crime patterns.

In scope: select records within a circular area, summarize their categories,
dates, and hours, and present totals and charts for the same selected records.
Results describe the available records; they do not establish causation,
confirmed crime counts, population-adjusted risk, or future crime predictions.

Out of scope: live feeds, predictive models, polygon boundaries, and implementing
map controls here. [Goal 3](crime-map.md) supplies the user-selected center,
radius, and filters; Goal 2 supplies descriptive analysis of that selection.

## Source documents and interfaces

- [Crime Pattern Analysis](../crime-pattern-analysis.md) defines the existing
  standalone filtering and frequency behavior and synthetic-data checks.
- [Standardized Crime Data Format v1](../crime-data-format.md) defines input
  fields and missing-value rules.
- [Goal 1 specification](crime-data-foundation.md) defines collection, storage,
  retrieval, and preservation of record meaning.

The analysis input is the selected standardized records, together with a valid
center and radius when area selection is needed. Center coordinates are decimal
degrees in EPSG:4326; radius is finite, nonnegative, and measured in miles.
The area filter includes the boundary and preserves matching records and order.

Frequency output contains total_incidents, by_crime_type, by_date, and by_hour.
Dates use YYYY-MM-DD; hour buckets use HH:00 and combine the same hour of day
across dates. These are hour-of-day counts, not combined date/hour intervals.

The current frequency module accepts date/time or datetime/timestamp, while
format v1 supplies incident_date/incident_time. A reviewed adapter or interface
change and integration tests are required; direct compatibility is not assumed.
No timezone conversion may be invented for records with an unknown timezone.

## Functional requirements

| ID | Requirement | Story |
|---|---|---|
| G2-FR-1 | When a valid center and radius are supplied, the system shall select valid-coordinate records whose Haversine distance is less than or equal to the radius, using the documented Earth radius of 3958.7613 miles. | #15 |
| G2-FR-2 | When the center or radius is invalid, the filtering module shall reject the request with ValueError; records with missing or invalid coordinates shall be skipped. | #15 |
| G2-FR-3 | When selected records are analyzed, the system shall return their total count and frequency tables by nonempty crime_type, valid date, and valid hour of day. | #15 |
| G2-FR-4 | When a grouping field is unavailable or invalid, the record shall remain in the selected total but be omitted from the affected grouping; missing information shall not be represented as zero activity. | #15 |
| G2-FR-5 | When standardized records are supplied, the integration shall explicitly map incident_date and incident_time to the analysis interface while preserving the original standardized record. | #15 |
| G2-FR-6 | When summaries are requested, the application shall present total selected-record count and counts by category matching the corresponding database selection. | #16 |
| G2-FR-7 | When charts are displayed, their labels and values shall reflect the same selection and frequency results as the accompanying totals. | #16 |
| G2-FR-8 | When no usable records match the selection, the application shall show zero matching records and empty summaries without asserting that no crime occurred. | #15, #16 |

## Non-functional requirements

| ID | Requirement | Reason |
|---|---|---|
| G2-NFR-1 | Filtering and analysis shall preserve source identifiers, record_kind, dispositions, and quality flags in the underlying records. | Keep results traceable. |
| G2-NFR-2 | Summaries and charts shall label calls for service appropriately and disclose missing-field and location-precision limitations. | Avoid presenting sampled calls as confirmed crimes or exact locations. |
| G2-NFR-3 | Identical input and selection shall produce identical counts and stable category/date/hour ordering. | Support reproducible verification. |
| G2-NFR-4 | Analysis and display shall use consistent distance units and the same selected-record set. | Keep map and summary results consistent. |

## Acceptance criteria

These checks elaborate the existing objectives; they do not replace issue criteria.

- [ ] Synthetic cases cover inside, outside, boundary, zero-radius, empty, and invalid-coordinate selections, with matching records preserved unchanged.
- [ ] For a manually counted test dataset, total, category, date, and hour results match the expected counts under #15.
- [ ] Missing or invalid grouping fields are excluded from the affected groups without disappearing from the selected total; incomplete coverage is explained.
- [ ] A standardized-format test exercises the explicit date/time integration and yields the expected date and hour counts.
- [ ] Application totals, category counts, and charts under #16 match the database query results for the same selection.
- [ ] An empty selection produces a clear no-matching-records message, zero total, and empty groups without an error.
- [ ] Before real-data integration is claimed, an approved source sample is manually checked against the displayed and computed results.

## Existing evidence and remaining verification

The standalone area_filter.py and crime_frequency.py modules and synthetic
tests exist under prototype/. The referenced analysis document records those
checks. They do not establish standardized-record integration, database-backed
application summaries, or charts. This specification adds no implementation
and does not close #15 or #16.

Run existing module tests from the repository root:

    python3 -m unittest discover -s prototype -p 'test_area_filter.py' -v
    python3 -m unittest discover -s prototype -p 'test_crime_frequency.py' -v
    python3 .github/scripts/check_repo.py

## Open questions

| Decision | Owner | Needed by |
|---|---|---|
| Adapter versus analysis interface change for standardized fields | Goal 1 and Goal 2 owners | Before standardized-data integration |
| Reporting timezone and behavior when date/time components are incomplete | Goal 1 and Goal 2 owners | Before cross-source temporal summaries |
| Whether canceled calls and other dispositions are excluded from particular analyses | Team | Before interpreting source counts |
| Chart forms, presentation of incomplete grouping coverage, and selection interface | Goal 2 and Goal 3 owners | Before chart implementation |
| Dataset size and measurable response-time target | Team | Before performance acceptance testing |
