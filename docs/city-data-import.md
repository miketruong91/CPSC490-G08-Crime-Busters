# Anaheim and Fullerton offline import

Goal 1, Epic #3; follow-up [Task #97](https://github.com/miketruong91/CPSC490-G08-Crime-Busters/issues/97). Related storage story #28. This is a prototype mapping for the saved samples, not a live feed or final source-adoption decision.

## Inputs and scope

- `prototype/data/anaheim-september-2026-raw.json`: 255 unique records from six user-downloaded pages of anaheimcrime.com, September 18–25, 2026. All records have `area == "Anaheim Police"`. Original export record IDs and case IDs remain in the raw snapshot. Annual totals were excluded. This independent site is the immediate source; its metadata links the city portal as its upstream source, which has not been independently matched to this historical snapshot.
- `prototype/data/fullerton-november-2026-raw.json`: 96 unique calls extracted from five user-saved HTML pages of the official Fullerton viewer. Dates span November 23–24, 2026. The five desktop tables contained 100 rows; four identical calls appeared on two pages and were removed. Mobile layout copies were excluded. This is a partial sample of a changing feed, not all Fullerton records.

Both raw envelopes include the original input filenames and SHA-256 hashes. Neither dataset includes coordinates. The samples have different dates, classifications, and coverage and must not be treated as directly comparable city crime rates. Source-specific reuse conditions remain unresolved; see [source evaluation](source-evaluation.md). The offline normalizer and default combined build perform no network requests and makes no claim of permission for redistribution.

## Field mappings

| Standard field | Anaheim mapping | Fullerton mapping |
|---|---|---|
| source | `anaheimcrime_anaheim_incidents` | `fullerton_police_calls_for_service` |
| source_record_id | `case_id` as text | `incident_number` as text, including year prefix |
| record_kind | `crime_incident`: portal labels these incident records, not calls | `call_for_service` |
| source_code | Original `category` label | Original `type` label; numeric call codes are absent from the saved table |
| description | Original `description`, outer whitespace trimmed | Original `type`, outer whitespace trimmed |
| location | `block` | `address` |
| agency | `area`, accepted only when exactly `Anaheim Police` | Null: agency is not an explicit field of the saved table |
| city, disposition | Null: not provided as explicit record fields | Null: not provided as explicit record fields |
| incident_date | Validated `record_date` calendar date | Date portion of `date_time` |
| incident_time | Null: absent from export | Parse 12-hour display; pad seconds with `00` to fit existing format |
| timezone | Null; no conversion inferred | Null; no conversion inferred |
| latitude, longitude | Null | Null |
| location_precision | `block` when location contains `BLOCK`; otherwise `unknown` | Same rule; intersections are not labeled exact |

Fullerton's `:00` seconds are formatting padding, not evidence that the call occurred exactly on the minute. Keep the raw display for its original precision. The current exchange format has no time-precision field.

Anaheim categories map Burglary to burglary, Theft / Larceny and Motor Vehicle Theft to theft, Vandalism to vandalism, and Assault to assault. The inspected Drugs / Alchohol Violations, Disturbing the Peace, Fraud, Sex Crimes, DUI, Robbery, and Weapons labels map to `other`, because the existing schema has no separate categories for them. Their original labels remain in source_code; `other` must not be described as a specific offense. An unrecognized category becomes null with unmapped_category.

Fullerton maps only THEFT PETTY RPT to theft and BURGLARY RPT to burglary. Other observed call labels remain null with unmapped_category pending review. In particular ALARM BURGLARY does not map to burglary. These records remain calls for service after normalization.

Anaheim case IDs are unique in this sample. They are used instead of rolling export row numbers. If a later source supplies multiple different records under one case ID, the later conflicting record is held for review; this prototype does not resolve multi-offense case identity. Different source identifiers keep Fullerton and Anaheim identities separate.

## Validation and duplicates

The script requires the expected envelope and record identities. It rejects other Anaheim agencies and missing/non-text identifiers into a held-record report. Invalid dates/times become null with the corresponding flags. Missing coordinates and unknown timezone are flagged. Missing Anaheim times receive missing_time. Block addresses receive location_not_exact; an unknown precision remains unknown.

Identical normalized duplicates are skipped. Conflicting normalized records sharing the same source and identifier are held; the first accepted version remains. Original input values are included in the held report. The command writes the standardized JSON array and `<output>.held.json`; it exits nonzero when records are held. Review that report before loading.

## Run from the prototype directory

```bash
python normalize_city.py anaheim data/anaheim-september-2026-raw.json anaheim-standardized.json
python normalize_city.py fullerton data/fullerton-november-2026-raw.json fullerton-standardized.json
python -m unittest -v test_normalize_city
```

Use a new test database filename, not an existing demo database:

```bash
python load_db.py anaheim-standardized.json city-import-check.db
python load_db.py fullerton-standardized.json city-import-check.db
python load_db.py anaheim-standardized.json city-import-check.db
python load_db.py fullerton-standardized.json city-import-check.db
```

Expected first loads: 255 and 96 inserted. Expected repeated loads: 0 inserted, 255 and 96 unchanged respectively, 0 held. The isolated integration test automatically creates and removes its own temporary database.

## Verification and limits

Assistant-side verification on November 24, 2026: nine unittest tests passed, including actual snapshot loading into temporary SQLite, exact count 351, all standardized values/flags read back, and repeat loading with 0 inserted and 351 unchanged. A separate raw-to-stored comparison checked identifiers, descriptions, locations, and Anaheim calendar dates. Conflicting stored versions were tested and remained unchanged. Annual totals were tested as excluded; missing identifiers, wrong agency, invalid dates, midnight/noon conversion, and alarm classification were also tested.

The existing loader and schema were retrieved from develop for these checks; neither was changed. The full integrated prototype suite now passes, including the existing Flask endpoint tests. The combined database builder also preserves the Costa Mesa sample, imports all 351 city records, and enriches 334 city records using saved address-range and local intersection matches. Map coverage and provenance are documented in [multi-city-map.md](multi-city-map.md). Other records retain null coordinates. Human source/mapping review and source-specific reuse resolution remain pending.

## AI use

ChatGPT drafted the normalizer, tests, extraction/combination steps, and this document. Initial drafts of these new code and documentation artifacts were entirely AI-assisted. The user supplied downloads and selected the source samples. A human must review the mappings, code, source terms, and test evidence before merge. Proposal prose is a separate course deliverable and must follow its own authorship rules.
