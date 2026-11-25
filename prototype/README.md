# Crime Busters map — Costa Mesa, Fullerton and Anaheim

The Flask map displays the original Costa Mesa data alongside approximate block points for Fullerton calls for service and Anaheim crime incidents. City colors, city and crime-type filters, grouped markers, popup details and automatic map framing apply to the combined dataset. Calls for service are not confirmed crime counts, and the cities cover different time periods.

## Open the standalone map

The repository includes `multi-city-map.html`. Serve it with `python3 -m http.server 8000` from this folder and open http://localhost:8000/multi-city-map.html to see the same markers, filters and popups without starting Flask. Opening it as a `file://` URL can cause OpenStreetMap tile access errors because a valid HTTP referrer is required. Internet access is needed for map tiles and Leaflet. It is a snapshot of the current 353 mapped records. Regenerate it after building a new database with `python export_map.py`.

## Run on macOS / Linux

From this folder:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python build_map_db.py
python -m flask --app app run --port 5051
```

Open http://127.0.0.1:5051. The database is generated from saved inputs and is excluded from git. Run the build command once after cloning. Flask automatically uses `crime-multicity.db` when it exists, and otherwise falls back to the original `crime.db`. Existing databases are never overwritten. To use another database, set `CRIME_DB_PATH` to its absolute path before running Flask.

## Current coverage

| Source city | Saved records | Mapped records | Mapped locations | Awaiting coordinates |
|---|---:|---:|---:|---:|
| Costa Mesa | 19 | 19 | 13 | 0 |
| Fullerton | 96 | 88 | 82 | 8 |
| Anaheim | 255 | 246 | 215 | 9 |
| Total | 370 | 353 | 310 | 17 |

All case/source IDs, dates, descriptions, original locations and other source fields remain attached. Coordinates are joined locally by source context and original location, so separate cases sharing a block remain distinct. Only synthetic job IDs, representative addresses and city/state labels were sent to Census, with the user's authorization. No case IDs, dates, descriptions or crime types were sent.

Saved results cover 254 of 265 block labels and all 44 intersection labels. The 17 unresolved records (16 unmatched locations plus this out-of-city review case) are listed in `data/unresolved-records.csv`; their coordinates remain null. Intersection estimates use public Census road crossings, including endpoint gaps up to 12 meters; grade-separated crossings are approximate. Matches where direction remains unverified have an explicit popup label. Source streets and addresses are never silently rewritten.

One Fullerton-source call explicitly reports Moreno Valley. The Census candidate in Moreno Valley is retained in `review_candidates`, but the record is withheld from the default map pending review. Its original source identity and reported address are unchanged. City colors and filters identify source datasets, not verified municipal boundaries. The other records also remain samples with different date ranges, not comparable city crime rates. Missing times, timezones and unclassified categories remain unknown.

## Reproduce or continue geocoding

Default builds use `data/geocoding/resolved-locations.json` without network requests. To rebuild that manifest from the included responses and public road extract:

```bash
python expand_saved_geocoding.py
python build_map_db.py --output crime-multicity-expanded.db
CRIME_DB_PATH="$PWD/crime-multicity-expanded.db" python -m flask --app app run --port 5051
```

`python geocode_all.py --live` refreshes address-only Census queries. Each block tries its starting number and then the remaining numbers through the end of that block, selecting the lowest consistent match even if batch rows arrive out of order. Batches stay within the 10,000-row limit. Run `expand_saved_geocoding.py` afterward for local road checks and intersection matching. `download_public_roads.py` refreshes the bounded public Census road extract without sending incident locations. The original isolated pilot remains available as `geocode_city_pilot.py`.

Each build requires a new database filename and refuses to overwrite an existing file. To view a new database, set `CRIME_DB_PATH` when starting Flask. Existing `crime.db` files remain untouched. Provenance records the provider, method, original location, representative query, returned address, benchmark and validation checks in the separate `incident_geocoding` table. Case/source IDs, dates and descriptions are verified against the normalized originals after enrichment.

## Verify

```bash
python -m pip install pytest
python -m pytest -q
```

Tests cover normalization, database loading, block fallback, preservation of source locations, coordinate provenance, combined API coverage, existing-database compatibility and missing-database errors.

Data inputs: Costa Mesa layer 57 saved prototype sample, Anaheim September 2026 saved export, Fullerton November 24, 2026 saved calls-for-service sample. No live fetching occurs during ordinary builds or map requests. Leaflet and OpenStreetMap tiles require internet access.

Assisted-by: ChatGPT

## API compatibility

`GET /api/incidents` retains its original response shape and coordinate filtering. `GET /api/map-incidents` supplies the combined map with display cities, geocoding details, `total_records`, `unmapped_count` and `by_city` coverage. `GET /` uses the combined endpoint. `/health` is unchanged. The existing crime filter still clears the marker layer before drawing a new selection; the city filter is applied together with it.

For source mappings and provenance, see [city-data-import.md](../docs/city-data-import.md) and [multi-city-map.md](../docs/multi-city-map.md). Stored `city` values remain as supplied by each publisher; the map's city labels use documented source context.
