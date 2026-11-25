"""Small Census geocoding pilot. Produces review candidates; never edits a database.

Run: python geocode_city_pilot.py
Responses are cached beside this file; remove a cached response only to refresh it.
Each number in a reported block is tried in ascending order until a consistent
address-range match is found. The selected number is not a known incident address.
Intersections are deliberately outside this structure-address pilot.
"""
import argparse
import json
from pathlib import Path
import re
import time
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent / "data" / "geocoding"
SAMPLES = [
    ("Fullerton", "3500 BLOCK W COMMONWEALTH AVE"),
    ("Fullerton", "2700 BLOCK W ORANGETHORPE AVE"),
    ("Fullerton", "1500 BLOCK DEERPARK DR"),
    ("Anaheim", "500 BLOCK N HANOVER ST"),
    ("Anaheim", "100 BLOCK S RIO VISTA ST"),
    ("Anaheim", "3100 BLOCK W LINCOLN AVE"),
]


def assess(city, original, response, query_number=None):
    """Return basic consistency checks; these do not constitute map review."""
    matches = response.get("result", {}).get("addressMatches", [])
    result = {"city_context": city, "original_location": original,
              "precision": "block", "method": "representative_block_number_query",
              "status": "unmatched", "candidates": [], "approved_for_import": False}
    number, street = re.fullmatch(r"(\d+) BLOCK (.+)", original).groups()
    if query_number is not None:
        number = str(query_number)
    for match in matches:
        parts = match.get("addressComponents", {})
        coords = match.get("coordinates", {})
        returned_street = " ".join(filter(None, [parts.get("preDirection"),
            parts.get("streetName"), parts.get("suffixType"), parts.get("suffixDirection")]))
        try:
            low, high = sorted([int(parts["fromAddress"]), int(parts["toAddress"])])
            in_range = (low <= int(number) <= high and
                        (low % 2 != high % 2 or int(number) % 2 == low % 2))
        except (ValueError, KeyError, TypeError):
            in_range = False
        x, y = coords.get("x"), coords.get("y")
        numeric = all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in (x, y))
        checks = {"city_label_matches": parts.get("city", "").upper() == city.upper(),
                  "state_matches": parts.get("state") == "CA",
                  "street_matches": returned_street == street,
                  "number_in_returned_range": in_range,
                  "valid_coordinates": numeric and -180 <= x <= 180 and -90 <= y <= 90}
        result["candidates"].append({"matched_address": match.get("matchedAddress"),
            "latitude": y, "longitude": x, "address_components": parts,
            "tiger_line": match.get("tigerLine"), "checks": checks})
    if matches:
        result["status"] = ("candidate_needs_map_review" if len(matches) == 1 and
            all(result["candidates"][0]["checks"].values()) else "needs_investigation")
    return result


class CacheMiss(Exception):
    """A lookup has not yet been performed in cached-only mode."""


def request_url(city, number, street):
    return "https://geocoding.geo.census.gov/geocoder/locations/address?" + urlencode({
        "street": f"{number} {street}", "city": city, "state": "CA",
        "benchmark": "Public_AR_Current", "format": "json"})


def resolve_block(city, original, fetch):
    """Try each number in order, stopping at the first consistent unique match.

    fetch(city, number, street) supplies a provider response. A failed request
    stops this block so that an outage cannot masquerade as a missing address.
    Census address-range matches do not prove that a building exists.
    """
    parsed = re.fullmatch(r"(\d+) BLOCK (.+)", original)
    base = {"city_context": city, "original_location": original,
            "precision": "block", "location_label": "Approximate location",
            "method": "sequential_block_number_query", "approved_for_import": False,
            "attempts": [], "candidates": [], "status": "needs_review"}
    if parsed is None:
        base["reason"] = "Unsupported block address; manual review required."
        return base
    start, street = int(parsed[1]), parsed[2]
    end = (start // 100 + 1) * 100
    for number in range(start, end):
        url = request_url(city, number, street)
        attempt = {"query_number": number, "request_url": url}
        try:
            response = fetch(city, number, street)
            if not isinstance(response.get("result", {}).get("addressMatches"), list):
                raise ValueError("Geocoder response is missing addressMatches")
            checked = assess(city, original, response, query_number=number)
        except CacheMiss:
            attempt["status"] = "lookup_pending"
            base["attempts"].append(attempt)
            base.update(status="lookup_pending", reason="Run without --cached-only to continue live lookups.")
            return base
        except Exception as exc:
            attempt.update(status="request_failed", error=str(exc))
            base["attempts"].append(attempt)
            base.update(status="request_failed", reason="Retry this block after resolving the request failure.")
            return base
        attempt.update(status=checked["status"], candidates=checked["candidates"],
                       benchmark=response.get("result", {}).get("input", {}).get("benchmark"))
        base["attempts"].append(attempt)
        if checked["status"] == "candidate_needs_map_review":
            base.update(status=checked["status"], candidates=checked["candidates"],
                        selected_query_address=f"{number} {street}", request_url=url,
                        benchmark=attempt["benchmark"])
            return base
    base["reason"] = "No consistent unique match within the reported block; manual review required."
    return base


def cached_fetch(index, original, cached_only=False):
    """Keep original pilot caches and cache each fallback by sample and number."""
    start = int(original.split()[0])

    def fetch(city, number, street):
        cache = ROOT / (f"census-response-{index:02d}.json" if number == start
                        else f"census-response-{index:02d}-{number}.json")
        url = request_url(city, number, street)
        if cache.exists():
            response = json.loads(cache.read_text())
            address = response.get("result", {}).get("input", {}).get("address", {})
            if (address.get("street", "").upper() != f"{number} {street}".upper()
                    or address.get("city", "").upper() != city.upper()
                    or address.get("state") != "CA"):
                raise ValueError("Cached response does not match the requested address")
            return response
        if cached_only:
            raise CacheMiss()
        req = Request(url, headers={"User-Agent": "CrimeBusters-StudentGeocodingPilot/1.0"})
        try:
            with urlopen(req, timeout=15) as stream:
                response = json.load(stream)
            if "error" in response or "errors" in response or "result" not in response:
                raise ValueError("Geocoder returned an error or invalid response")
            cache.write_text(json.dumps(response, indent=2) + "\n")
            return response
        finally:
            time.sleep(1)
    return fetch


def write_map(results):
    """Regenerate the preview from this run, including only consistent matches."""
    points = []
    for result in results:
        if result["status"] == "candidate_needs_map_review":
            candidate = result["candidates"][0]
            points.append(dict(city=result["city_context"], address=result["original_location"],
                               selected=result["selected_query_address"],
                               lat=candidate["latitude"], lon=candidate["longitude"]))
    template = (ROOT / "pilot-map.html").read_text()
    template = re.sub(r"const points=.*?;const map=", lambda _: "const points=" + json.dumps(points) + ";const map=", template)
    template = re.sub(r"<h1>.*?</div><ul", '<h1>Fullerton and Anaheim geocoding pilot</h1>'
        f'<p>{len(points)} approximate candidates for review. Blue: Fullerton. Orange: Anaheim.</p>'
        '<p>Approximate location within the reported block. Address-range matches do not verify individual buildings or incident locations.</p>'
        '<div id="map"></div><ul', template)
    template = template.replace("Approximate representative point; awaiting review.", "Approximate location; awaiting review.")
    template = template.replace("map.fitBounds(bounds,{padding:[35,35]});", "if(bounds.length){map.fitBounds(bounds,{padding:[35,35]})}else{map.setView([33.85,-117.93],12)};")
    (ROOT / "pilot-map.html").write_text(template)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cached-only", action="store_true", help="Use saved responses only; mark remaining lookups pending")
    args = parser.parse_args()
    results = []
    for index, (city, original) in enumerate(SAMPLES, 1):
        result = resolve_block(city, original, cached_fetch(index, original, args.cached_only))
        results.append(result)
        print(city, original, "->", result["status"], f"({len(result['attempts'])} attempts)", flush=True)
    (ROOT / "pilot-results.json").write_text(json.dumps({
        "provider": "US Census Geocoder", "database_modified": False,
        "note": "Derived approximate candidates. No actual event house numbers are known.",
        "results": results}, indent=2) + "\n")
    write_map(results)


if __name__ == "__main__":
    main()
