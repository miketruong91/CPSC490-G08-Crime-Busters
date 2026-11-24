# Anaheim and Fullerton source evaluation

Working evaluation for [task #97](https://github.com/miketruong91/CPSC490-G08-Crime-Busters/issues/97), checked November 24, 2026. This records source inspection, not completed integration. No new city records have been loaded into the project database.

## Decision so far

| Candidate | Observed data | Suitability decision |
|---|---|---|
| Fullerton official Calls for Service | Public query returned 20 calls on page 1, with identifiers, category codes/descriptions, block or intersection locations, and formatted dates/times. No numeric coordinates were present in this response. | Candidate for database storage after field mapping and reuse review. Map integration is unresolved. |
| Anaheim official Community Crime Map | Police documentation identifies LexisNexis as its public map provider, describes block-level locations, and warns that initial report classifications can change. | Viewing source confirmed. Reusable export/API, terms, and actual coordinate output remain unverified. |
| Anaheim ArcGIS item `9a32b866a3204bb5b9070b5a27248301` | A table without geometry. Three queried rows identified San Diego Police; a distinct-agency query returned eight San Diego-area agencies and no Anaheim agency. | Exclude from the Anaheim import. Publisher/title alone are insufficient evidence of geographic coverage. |

## Fullerton evidence and provisional mapping

Public viewer: https://www2.cityoffullerton.com/webdata/apps/cfs/

The viewer's public JavaScript calls `POST /WebData/Apps/CFS/FpdApi/Query` with `q`, `pg`, and `r`, plus a request-verification token from the public landing page. Inspection used the same anonymous cookie/token flow; no account credentials were used. This is an implementation endpoint, not a verified supported public API contract.

The response has a `success` property and a JSON-encoded `result`. Within the decoded result, records are in `hits.hits`, with original values in `_source` and additional display fields in `fields`. The inspected response reported 924 matching records; that is a query result count, not a verified historical total or a count imported into this project. The first returned call displayed November 24, 2026, 12:50 PM. The complete available date range and retention window remain unverified.

| Standard field | Candidate mapping or unresolved decision |
|---|---|
| `source` | Proposed dataset identifier `fullerton_police_calls_for_service`; document before adoption. |
| `source_record_id` | Evaluate `PK` (also returned as `_id`) for stability; preserve its value as text. Retain report year and number in raw evidence. Do not use report number alone across years. |
| `record_kind` | `call_for_service`, based on the official viewer's stated scope. |
| `source_code` | `_source.INCIDENT_TYPE`, preserving the original code. |
| `description` | `_source.INCIDENT_DESC`, preserving the original wording. |
| `location` | `_source.STREET_NAME_100BLK`; both block addresses and intersections appeared. |
| `incident_date`, `incident_time` | Parse `fields.incident_datetime[0]` after confirming display semantics. The display supplies minute precision; do not claim source-provided seconds. |
| `timezone` | Null until source documentation verifies it. Do not infer it from the city name or an epoch-like sort key. |
| `latitude`, `longitude` | Null for the inspected query output. `incident_haslatlon: true` is a Boolean, not a coordinate pair. |
| `location_precision` | Determine from source documentation and location form. Do not label intersections or unknown geometry as exact. |
| `crime_type` | Define and review a source-specific mapping. Patrol checks, traffic stops, and alarms must retain their call meaning; a burglary alarm is not automatically a burglary. |
| `city`, `agency`, `disposition` | Not explicit fields in the inspected `_source`; do not invent source-provided values. Document any later enrichment separately. |
| `quality_flags` | Apply existing missing/uncertain-value rules after finalizing the mapping. |

The current schema allows null coordinate pairs and multiple source identifiers. Its incident API excludes records without usable coordinates. Consequently, storing these Fullerton calls alone would not add Fullerton markers to the current map.

## Anaheim evidence

Official police description: https://pd.anaheim.net/280/Community-Crime-Map

The police department states that locations are rounded to block addresses and reports are preliminary. A separate evaluation is still needed for the public map's retrieval method, agency filtering, accessible history, category coverage, coordinate precision, and reuse conditions.

Rejected ArcGIS candidate metadata:
https://www.arcgis.com/sharing/rest/content/items/9a32b866a3204bb5b9070b5a27248301?f=json

Candidate table:
https://services3.arcgis.com/hPs600I3X0RTaaaq/arcgis/rest/services/Crime_Mapping_/FeatureServer/0

Its metadata describes a table and contains no geometry field. Query checks used `outFields=*`, `resultRecordCount=3`, and a separate distinct `Agency` query. Distinct agencies were Coronado Police, Escondido Police, La Mesa Police, Lemon Grove Sheriff, National City Police, San Diego County Sheriff, San Diego Harbor Police, and San Diego Police. The item metadata's `licenseInfo` was null; a blank license is not evidence of permission to redistribute.

## Remaining work

- Verify source-specific retrieval and redistribution terms for both cities. No conclusion that scraping is prohibited or permitted has been established here.
- Establish actual coverage and date retention from source evidence, rather than from a city name in a search URL.
- Find verified coordinates or an explicitly documented enrichment approach before promising additional map markers. Keep missing coordinates null.
- Finalize identifier, date/time, category, and precision mappings before writing an importer.
- For each adopted source, save a bounded input snapshot and retrieval metadata, normalize it, load a fresh database, verify every selected sample value and record count, and repeat the import to prove duplicate prevention.
- Run appropriate tests and repository checks, and obtain teammate review of the implementation PR.

## AI assistance

ChatGPT performed the initial public-source inspection and drafted this working evaluation. Human review of the evidence and mapping decisions is pending. The listed import and test steps have not yet been performed for Anaheim or Fullerton.
