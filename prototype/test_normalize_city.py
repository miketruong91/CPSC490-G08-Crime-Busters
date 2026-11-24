"""Offline mapping and database integration checks for Task #97."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from load_db import connect, get_incident, load_records, verify
from normalize_city import normalize_records


def anaheim(row=None):
    return {"site": "anaheimcrime.com", "records": [row or {
        "source_id": "anaheim-incidents", "source_record_id": "115",
        "case_id": "000123", "area": "Anaheim Police",
        "category": "Vandalism", "description": " Source description ",
        "block": "100 BLOCK TEST ST", "record_date": "2026-09-25",
        "latitude": None, "longitude": None,
    }]}


def fullerton():
    return {"source_url": "https://www2.cityoffullerton.com/webdata/apps/cfs/",
            "records": [{"incident_number": "26-000123", "type": "ALARM BURGLARY",
                         "date_time": "11/24/2026 12:05 AM", "address": "A ST / B ST"}]}


class CityNormalizationTests(unittest.TestCase):
    def test_bundled_snapshots_load_and_repeat(self):
        data = Path(__file__).with_name("data")
        all_records = []
        for city, filename, expected in [
            ("anaheim", "anaheim-september-2026-raw.json", 255),
            ("fullerton", "fullerton-november-2026-raw.json", 96),
        ]:
            document = json.loads((data / filename).read_text(encoding="utf-8"))
            records, held = normalize_records(document, city)
            self.assertEqual(held, [])
            self.assertEqual(len(records), expected)
            all_records.extend(records)
        with tempfile.TemporaryDirectory() as directory:
            conn = connect(str(Path(directory) / "test.db"))
            try:
                self.assertEqual(load_records(conn, all_records),
                                 {"inserted": 351, "unchanged": 0, "held": []})
                self.assertEqual(verify(conn, all_records), [])
                self.assertEqual(load_records(conn, all_records),
                                 {"inserted": 0, "unchanged": 351, "held": []})
                self.assertEqual(conn.execute("SELECT COUNT(*) FROM incidents").fetchone()[0], 351)
                self.assertEqual(conn.execute("SELECT COUNT(*) FROM incidents WHERE latitude IS NOT NULL OR longitude IS NOT NULL").fetchone()[0], 0)
            finally:
                conn.close()

    def test_anaheim_preserves_identity_and_missing_values(self):
        records, held = normalize_records(anaheim(), "anaheim")
        self.assertEqual(held, [])
        record = records[0]
        self.assertEqual(record["source_record_id"], "000123")
        self.assertEqual(record["description"], "Source description")
        self.assertEqual(record["crime_type"], "vandalism")
        self.assertEqual(record["incident_date"], "2026-09-25")
        self.assertEqual(record["record_kind"], "crime_incident")
        self.assertEqual(record["location_precision"], "block")
        for field in ["incident_time", "timezone", "latitude", "longitude", "city"]:
            self.assertIsNone(record[field])
        self.assertIn("missing_time", record["quality_flags"])

    def test_annual_statistics_are_not_incidents(self):
        document = anaheim()
        document["annual_statistics"] = [{"count": 6002}]
        self.assertEqual(len(normalize_records(document, "anaheim")[0]), 1)

    def test_fullerton_alarm_is_not_burglary(self):
        record = normalize_records(fullerton(), "fullerton")[0][0]
        self.assertEqual(record["record_kind"], "call_for_service")
        self.assertIsNone(record["crime_type"])
        self.assertIn("unmapped_category", record["quality_flags"])
        self.assertEqual(record["incident_time"], "00:05:00")
        self.assertEqual(record["location_precision"], "unknown")

    def test_fullerton_noon_and_theft_report(self):
        document = fullerton()
        document["records"][0].update(type="THEFT PETTY RPT", date_time="11/24/2026 12:05 PM")
        record = normalize_records(document, "fullerton")[0][0]
        self.assertEqual(record["incident_time"], "12:05:00")
        self.assertEqual(record["crime_type"], "theft")

    def test_bad_calendar_date_is_flagged(self):
        document = anaheim()
        document["records"][0]["record_date"] = "2026-02-30"
        record = normalize_records(document, "anaheim")[0][0]
        self.assertIsNone(record["incident_date"])
        self.assertIn("invalid_date", record["quality_flags"])

    def test_missing_id_and_wrong_agency_are_held(self):
        for field, value in [("case_id", " "), ("area", "Other Police")]:
            with self.subTest(field=field):
                document = anaheim()
                document["records"][0][field] = value
                records, held = normalize_records(document, "anaheim")
                self.assertEqual(records, [])
                self.assertEqual(len(held), 1)

    def test_duplicate_conflict_is_visible(self):
        document = anaheim()
        first = deepcopy(document["records"][0])
        document["records"].extend([first, {**first, "description": "Changed"}])
        records, held = normalize_records(document, "anaheim")
        self.assertEqual(len(records), 1)
        self.assertEqual(len(held), 1)
        self.assertIn("conflicting duplicate", held[0]["reason"])

    def test_database_repeat_and_conflict(self):
        records = normalize_records(anaheim(), "anaheim")[0]
        conn = connect(":memory:")
        self.addCleanup(conn.close)
        self.assertEqual(load_records(conn, records), {"inserted": 1, "unchanged": 0, "held": []})
        self.assertEqual(verify(conn, records), [])
        self.assertEqual(load_records(conn, records), {"inserted": 0, "unchanged": 1, "held": []})
        changed = [{**records[0], "description": "Changed"}]
        self.assertEqual(len(load_records(conn, changed)["held"]), 1)
        self.assertEqual(get_incident(conn, records[0]["source"], "000123")["description"], "Source description")


if __name__ == "__main__":
    unittest.main()
