"""Summarize selected crime incidents by type, date, and hour (Issue #18).

Input is the iterable of records already selected by area_filter.filter_incidents.
Missing/invalid category and timestamp values are not included in their group
counts. The overall incident count still includes every selected record.

AI-assisted draft; verify behavior with the team's eventual real data schema.
"""
from collections import Counter
from datetime import date, datetime, time


def _date_and_hour(incident):
    """Return (ISO date, hour) or (None, None) for unavailable timestamps."""
    raw = incident.get("datetime")
    if raw is None:
        raw = incident.get("timestamp")
    if isinstance(raw, datetime):
        return raw.date().isoformat(), f"{raw.hour:02d}:00"
    if isinstance(raw, str):
        try:
            parsed = datetime.fromisoformat(raw.strip().replace("Z", "+00:00"))
            return parsed.date().isoformat(), f"{parsed.hour:02d}:00"
        except ValueError:
            pass

    day = incident.get("date")
    hour_value = incident.get("time")
    try:
        if isinstance(day, datetime):
            day = day.date()
        if isinstance(day, date):
            parsed_day = day.isoformat()
        elif isinstance(day, str):
            parsed_day = date.fromisoformat(day.strip()).isoformat()
        else:
            return None, None
    except ValueError:
        return None, None

    if isinstance(hour_value, time):
        return parsed_day, f"{hour_value.hour:02d}:00"
    if isinstance(hour_value, str):
        try:
            parsed_time = time.fromisoformat(hour_value.strip())
            return parsed_day, f"{parsed_time.hour:02d}:00"
        except ValueError:
            return parsed_day, None
    return parsed_day, None


def analyze_frequency(incidents):
    """Return incident totals and frequency dictionaries for selected records.

    Grouped values are ordered alphabetically/chronologically for stable output.
    Dates use YYYY-MM-DD; hours use 24-hour HH:00 labels.
    """
    by_type, by_date, by_hour = Counter(), Counter(), Counter()
    total = 0
    for incident in incidents:
        total += 1
        crime_type = incident.get("crime_type")
        if isinstance(crime_type, str) and crime_type.strip():
            by_type[crime_type.strip()] += 1

        incident_date, incident_hour = _date_and_hour(incident)
        if incident_date is not None:
            by_date[incident_date] += 1
        if incident_hour is not None:
            by_hour[incident_hour] += 1

    return {
        "total_incidents": total,
        "by_crime_type": dict(sorted(by_type.items())),
        "by_date": dict(sorted(by_date.items())),
        "by_hour": dict(sorted(by_hour.items())),
    }
