"""Filter crime incidents by a user-selected center and radius (Issue #17).

Pure Python prototype; integration with the team's data source/map is pending.
Coordinates use decimal degrees and distances use miles.
"""
from math import asin, cos, isfinite, radians, sin, sqrt

EARTH_RADIUS_MILES = 3958.7613


def _coordinate(value, name, lower, upper):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a number")
    if not isfinite(value) or not lower <= value <= upper:
        raise ValueError(f"{name} must be between {lower} and {upper}")
    return float(value)


def distance_miles(lat1, lon1, lat2, lon2):
    """Great-circle distance between two latitude/longitude pairs."""
    lat1 = _coordinate(lat1, "latitude", -90, 90)
    lat2 = _coordinate(lat2, "latitude", -90, 90)
    lon1 = _coordinate(lon1, "longitude", -180, 180)
    lon2 = _coordinate(lon2, "longitude", -180, 180)
    delta_lat = radians(lat2 - lat1)
    delta_lon = radians(lon2 - lon1)
    a = sin(delta_lat / 2) ** 2 + (
        cos(radians(lat1)) * cos(radians(lat2)) * sin(delta_lon / 2) ** 2
    )
    return 2 * EARTH_RADIUS_MILES * asin(min(1.0, sqrt(a)))


def filter_incidents(incidents, center_lat, center_lon, radius_miles):
    """Return valid-coordinate incidents within or on the chosen radius.

    Incidents without usable coordinates are skipped. Other incident fields
    are preserved. Invalid center/radius inputs raise ValueError.
    """
    center_lat = _coordinate(center_lat, "center_lat", -90, 90)
    center_lon = _coordinate(center_lon, "center_lon", -180, 180)
    if isinstance(radius_miles, bool) or not isinstance(radius_miles, (int, float)):
        raise ValueError("radius_miles must be a number")
    if not isfinite(radius_miles) or radius_miles < 0:
        raise ValueError("radius_miles must be finite and nonnegative")

    selected = []
    for incident in incidents:
        try:
            distance = distance_miles(
                center_lat, center_lon,
                incident["latitude"], incident["longitude"]
            )
        except (KeyError, TypeError, ValueError):
            continue
        if distance <= radius_miles:
            selected.append(incident)
    return selected
