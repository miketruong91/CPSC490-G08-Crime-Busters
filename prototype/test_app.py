import sqlite3
from pathlib import Path

import pytest

from app import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    database = tmp_path / "test-crime.db"
    schema = Path(__file__).with_name("schema.sql").read_text(
        encoding="utf-8"
    )

    with sqlite3.connect(database) as connection:
        connection.executescript(schema)
        connection.executemany(
            """
            INSERT INTO incidents (
                id, source, source_record_id, record_kind,
                crime_type, description, location,
                incident_date, incident_time, timezone,
                latitude, longitude, location_precision
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    2, "test_source", "002", "call_for_service",
                    "theft", "Test theft report", "200 BLK TEST ST",
                    "2026-11-02", "14:30:00", None,
                    33.65, -117.92, "block",
                ),
                (
                    1, "test_source", "001", "call_for_service",
                    "burglary", "Test burglary report", "100 BLK TEST ST",
                    "2026-11-01", "09:00:00", None,
                    33.64, -117.91, "block",
                ),
                (
                    3, "test_source", "003", "call_for_service",
                    "other", "Report without coordinates", None,
                    None, None, None,
                    None, None, "unknown",
                ),
            ],
        )

    monkeypatch.setitem(app.config, "TESTING", True)
    monkeypatch.setitem(app.config, "DATABASE", str(database))

    with app.test_client() as test_client:
        yield test_client


def test_map_route_serves_expected_page(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.mimetype == "text/html"

    html = response.get_data(as_text=True)
    assert "<title>Crime Busters</title>" in html
    assert 'id="map"' in html
    assert 'id="crime-type-filter"' in html
    assert "leaflet.js" in html


def test_incidents_route_returns_expected_records(client):
    response = client.get("/api/incidents")

    assert response.status_code == 200
    assert response.is_json
    assert response.get_json() == {
        "count": 2,
        "incidents": [
            {
                "id": 1,
                "source": "test_source",
                "source_record_id": "001",
                "record_kind": "call_for_service",
                "crime_type": "burglary",
                "description": "Test burglary report",
                "location": "100 BLK TEST ST",
                "incident_date": "2026-11-01",
                "incident_time": "09:00:00",
                "timezone": None,
                "latitude": 33.64,
                "longitude": -117.91,
                "location_precision": "block",
            },
            {
                "id": 2,
                "source": "test_source",
                "source_record_id": "002",
                "record_kind": "call_for_service",
                "crime_type": "theft",
                "description": "Test theft report",
                "location": "200 BLK TEST ST",
                "incident_date": "2026-11-02",
                "incident_time": "14:30:00",
                "timezone": None,
                "latitude": 33.65,
                "longitude": -117.92,
                "location_precision": "block",
            },
        ],
    }


def test_incidents_route_returns_empty_list_for_empty_database(client):
    with sqlite3.connect(app.config["DATABASE"]) as connection:
        connection.execute("DELETE FROM incidents")

    response = client.get("/api/incidents")

    assert response.status_code == 200
    assert response.get_json() == {"count": 0, "incidents": []}


def test_incidents_route_handles_missing_database(
    client, tmp_path, monkeypatch
):
    missing_database = tmp_path / "missing.db"
    monkeypatch.setitem(app.config, "DATABASE", str(missing_database))

    response = client.get("/api/incidents")

    assert response.status_code == 503
    assert response.get_json() == {
        "error": "Incident database unavailable"
    }
    assert not missing_database.exists()
