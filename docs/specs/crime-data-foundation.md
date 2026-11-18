# Specification — Crime Data Foundation

> Epic: #3 · Stories: #4, #5, #28 · Tasks: #8, #9, #10, #11, #32, #35, #36
> Owner: Alex Reyes · Status: draft for teammate review

## Scope

Goal 1: Establish a reliable and structured crime data foundation for the application.

In scope: document a public source, collect a local snapshot, normalize records,
store them in SQLite, and retrieve them without losing their source meaning.
The evaluated Costa Mesa layer 57 sample is historical calls for service;
its 19 records are verification evidence, not a minimum production dataset size.

Out of scope: live police feeds, public redistribution without confirmed reuse
terms, crime confirmation, predictive policing, and map rendering. Application
retrieval remains an integration requirement even when command-line checks pass.

## Source documents and interfaces

- [Crime Data Sources](../crime-data-sources.md) defines evaluated sources,
  access instructions, and unresolved source limitations.
- [Standardized Crime Data Format v1](../crime-data-format.md) is authoritative
  for all 17 exchange fields, types, nullability, mappings, and quality flags.
  This specification reuses those rules rather than redefining them.
- [Database ER design](../design/crime-database-er.md) describes SQLite storage.
- [Goal 2 specification](crime-pattern-analysis.md) consumes retrieved records;
  [Goal 3 specification](crime-map.md) covers their map presentation.

Input is a saved source response. Accepted normalized output is a UTF-8 JSON
array conforming to format v1. SQLite stores scalar values in incidents and
quality flags in incident_quality_flags. Record identity is the combined pair
(source, source_record_id), not either field individually.

## Functional requirements

| ID | Requirement | Story |
|---|---|---|
| G1-FR-1 | When a source is evaluated, the team shall document its publisher, access method, available required fields, and known limitations. | #4 |
| G1-FR-2 | When a source response is collected for prototype evaluation, the system shall allow it to be saved as a local snapshot, with collection evidence identifying the source and inspected record count. | #4 |
| G1-FR-3 | When the normalizer receives source records, it shall apply the field mapping and validation rules in format v1 and produce all 17 exchange fields for each accepted record. | #5 |
| G1-FR-4 | When values are absent or invalid, the normalizer shall apply v1 null and quality-flag rules without inventing replacement data; records without required identifiers shall be held outside accepted output. | #5 |
| G1-FR-5 | When repeated source identities occur, processing shall avoid duplicate accepted records and hold conflicting versions for review without silently overwriting stored records. | #5, #28 |
| G1-FR-6 | When accepted standardized records are loaded, SQLite shall preserve their scalar fields and associated quality flags and report inserted, unchanged, and held counts. | #28 |
| G1-FR-7 | When a stored record is requested by source and source_record_id, retrieval shall return its standardized values and quality flags; verification shall detect missing records or changed values. | #28 |
| G1-FR-8 | When the application accesses stored records, it shall retrieve the standardized fields and preserve record_kind and data-quality limitations for downstream filtering and analysis. | #28 |

## Non-functional requirements

| ID | Requirement | Reason |
|---|---|---|
| G1-NFR-1 | Identifiers shall remain strings, including leading zeros; unknown timezone values shall remain null. | Preserve source meaning. |
| G1-NFR-2 | Source evidence shall remain traceable; raw or generated data shall remain local while the documented reuse terms are unresolved. | Respect the current data-handling decision. |
| G1-NFR-3 | Calls for service shall retain that classification and shall not be labeled confirmed crimes solely from their category. | Prevent misleading interpretation. |
| G1-NFR-4 | Repeating a load of identical records shall leave the stored record count and values unchanged. | Support repeatable imports. |
| G1-NFR-5 | Missing or invalid coordinates shall not become zero coordinates; downstream spatial results shall exclude records without usable coordinates. | Avoid false locations. |

## Acceptance criteria

These checks elaborate the existing objectives; they do not replace issue criteria.
Unchecked boxes describe review targets, not claims that no implementation exists.

- [ ] For #4, a reviewer can follow the documented query method and inspect saved-snapshot evidence and required-field findings.
- [ ] For #5, valid and invalid synthetic inputs demonstrate the format v1 mapping, null handling, quality flags, identifier preservation, and conflicting-duplicate handling.
- [ ] For #28, a fresh SQLite database accepts an approved test input; its stored count equals the expected unique accepted records, and retrieved values match the input including quality flags.
- [ ] Reloading identical input inserts no duplicates; a conflicting version is held and the original stored values remain unchanged.
- [ ] Through the application, stored records can be retrieved with their standardized values; this satisfies the epic's existing application-retrieval success measure.

## Existing evidence and remaining verification

PR #56 added source documentation; PR #64 added format v1; PR #73 added the
schema, normalizer, loader, and tests. The November 3, 2026 verification recorded
19 accepted records, zero held, 19 database inserts, successful retrieval
comparison, and 34 passing normalization/database tests. Those results cover
one local sample and do not establish full application integration.

Relevant checks from the repository root:

    python3 -m unittest discover -s prototype -p 'test_normalize.py' -v
    python3 -m unittest discover -s prototype -p 'test_load_db.py' -v
    python3 .github/scripts/check_repo.py

## Open questions

| Decision | Owner | Needed by |
|---|---|---|
| Final source adoption, collection scope, and minimum dataset size | Alex and team | Before expanding beyond prototype sample evaluation |
| Reuse terms and access restrictions | Alex and team | Before public data redistribution |
| Timezone, refresh frequency, and location accuracy | Alex and team | Before claims about current activity or precise positions |
| Application retrieval interface and integration evidence | Backend and map owners | Before Epic #3 closure |
