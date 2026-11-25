# Combined Crime Busters map

This integration is part of the Flask prototype, not just a standalone preview. Follow [prototype/README.md](prototype/README.md) to build the database and run the project. Full coverage and provenance are documented in [docs/multi-city-map.md](docs/multi-city-map.md).

The existing incidents API remains compatible. The combined map uses `/api/map-incidents`, with city colors, joint city/type filtering, original source locations, approximate-location labels and explicit counts of records awaiting coordinates.

To preview the optional HTML snapshot, run `python3 -m http.server 8000` from `prototype/` and open http://localhost:8000/multi-city-map.html. Avoid opening the file directly: OpenStreetMap requires an HTTP referrer for its tiles.

All 370 sample records are stored. Current map coverage is 353 records at 310 locations; 17 records still await coordinates. The default build uses saved Census responses and public-road checks. See the prototype README for address-only refreshes and offline rebuilds. Case IDs, dates and descriptions stay local and remain attached.

Assisted-by: ChatGPT
