# Multi-city map integration — Task #97

The normal map at `/` now shows Costa Mesa calls for service, Fullerton calls for service and Anaheim crime incidents from the saved samples. City colors, city and crime-type filters, grouped markers, original source IDs and approximate-location popups are included. Changing either filter clears the old marker layer so markers are not duplicated. New data is loaded through the existing loader and schema, with a separate provenance table for derived coordinates.

## Reproduce from a fresh clone

Follow [prototype/README.md](../prototype/README.md): install requirements, run `python build_map_db.py` inside `prototype`, and start `python -m flask --app app run --port 5051`. Visit http://127.0.0.1:5051. No source fetch or geocoder call is needed for this build. Existing databases are never overwritten. If `crime-multicity.db` exists already, use `--output` with a new filename and set `CRIME_DB_PATH` when starting Flask.

The standalone HTML snapshot is optional. Run `python export_map.py` to refresh it, then `python3 -m http.server 8000` and visit http://localhost:8000/multi-city-map.html. Opening the HTML directly as `file://` can omit the HTTP referrer required by OpenStreetMap and result in blocked tiles. This is a local prototype; map tiles and Leaflet require internet access.

## Current saved-data coverage

| City | Records stored | Records plotted | Distinct locations | Awaiting coordinates |
|---|---:|---:|---:|---:|
| Costa Mesa | 19 | 19 | 13 | 0 |
| Fullerton | 96 | 88 | 82 | 8 |
| Anaheim | 255 | 246 | 215 | 9 |
| Total | 370 | 353 | 310 | 17 |

These are bounded samples with different dates, classification schemes and coverage. They cannot establish comparative city crime rates. Missing timezones and times remain unknown. Fullerton alarms, disturbances and patrol activity are not classified as confirmed crimes. The independent Anaheim export and official Fullerton viewer are distinguished in [city-data-import.md](city-data-import.md).

## Block fallback and provenance

For a block such as `500 BLOCK N HANOVER ST`, the fallback tries 500, then 501, up to 599, stopping at the first consistent unique match. It requires matching street name, direction, city and state, a valid returned address range and odd/even side where applicable, and valid coordinates. A Census address-range match is an interpolated representative point; it does not prove a building exists or identify the incident address. The map labels it **Approximate location** and retains the original reported location.

Matching blocks share coordinates while retaining separate case identities. The expanded pass resolves 254 block labels and all 44 intersection labels. Lowest valid address numbers are selected explicitly, independent of response order. Case IDs, dates and descriptions remained local and were reattached after geocoding; only synthetic job IDs, representative addresses and city/state labels were submitted to Census with user authorization.

Missing street directions are checked against road geometry within 60 meters. Explicit opposite directions and conflicting street types are rejected. If both provider and nearby road linework omit direction, the method and popup retain that uncertainty. Intersection estimates allow endpoint gaps up to 12 meters and a single crossing cluster spanning at most 150 meters. They may represent grade-separated crossings. Bounds checks do not independently verify municipal boundaries.

One Fullerton-source record explicitly names Moreno Valley; its Iris Avenue candidate is retained for review and omitted from the default map. The Fullerton source identity and reported address are unchanged. City filters identify source datasets. Seventeen records remain without coordinates and are listed in `prototype/data/unresolved-records.csv`; arbitrary city-center points are not substituted.

The prototype README documents address-only refreshes and offline rebuilds from saved Census responses and public road geometry. Ordinary database builds do not query external services.

`incident_geocoding` records provider, method, original location, selected query address, source-context city, request URL, returned address, benchmark and validation checks, keyed to `incidents.id`. Source IDs, descriptions, dates, times and original city fields are preserved. The raw snapshots also remain unchanged. Derived coordinates replace nulls only in the fresh combined database; original data and existing databases are not rewritten.

## API compatibility and verification

`/api/incidents` retains its original response contract. The new `/api/map-incidents` endpoint returns mappable records with display cities and geocoding details, plus coverage counts that include unmapped records. The map and HTML export use this endpoint. Existing callers can keep using `/api/incidents`.

Tests cover both API contracts, all three cities, coverage totals, legacy databases, missing-database errors, source preservation, provenance, sequential fallback and block limits. Repeating an import of the 351 raw city records produces 0 inserted and 351 unchanged; repeating the 370-record combined import produces 0 inserted and 370 unchanged. The builder refuses to overwrite existing files. User review confirmed that the standalone map renders when served through localhost. Automated JavaScript logic checks cover filtering, empty results, grouping and approximate-location popups; automated visual rendering was not completed in the isolated execution environment.

Source-specific reuse terms and final team adoption remain unresolved; this implementation is a technical prototype and does not establish those decisions. It does not add a live feed or geocode all records.

Assisted-by: ChatGPT
