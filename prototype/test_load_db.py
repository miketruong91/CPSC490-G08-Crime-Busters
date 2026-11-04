"""Tests for load_db.py (Tasks #35, #36). Run: python3 -m unittest discover prototype

Uses an in-memory database, so nothing is written to disk.
"""
import copy
import unittest

import load_db as db
import normalize as n
from test_normalize import feature


def records(*features):
    accepted, held = n.normalize({"features": list(features)})
    assert not held
    return accepted


class LoadAndRetrieve(unittest.TestCase):
    def setUp(self):
        self.conn = db.connect(":memory:")

    def test_sample_round_trips(self):
        recs = records(feature())
        self.assertEqual(db.load_records(self.conn, recs)["inserted"], 1)
        stored = db.get_incident(self.conn, "costa_mesa_police_incidents", "2025068460")
        expected = copy.deepcopy(recs[0])
        expected["quality_flags"] = sorted(expected["quality_flags"])
        self.assertEqual(stored, expected)
        self.assertEqual(db.verify(self.conn, recs), [])

    def test_stored_count_matches_loaded(self):
        recs = records(feature(ID="1"), feature(ID="2"), feature(ID="3"))
        db.load_records(self.conn, recs)
        count = self.conn.execute("SELECT COUNT(*) FROM incidents").fetchone()[0]
        self.assertEqual(count, 3)

    def test_null_coordinates_and_dates_are_stored_as_null(self):
        recs = records(feature(CallDate=None, geometry={}))
        db.load_records(self.conn, recs)
        stored = db.get_incident(self.conn, recs[0]["source"], "2025068460")
        self.assertIsNone(stored["latitude"])
        self.assertIsNone(stored["longitude"])
        self.assertIsNone(stored["incident_date"])
        self.assertIn("missing_coordinates", stored["quality_flags"])

    def test_leading_zero_id_survives(self):
        recs = records(feature(ID="000123"))
        db.load_records(self.conn, recs)
        self.assertIsNotNone(db.get_incident(self.conn, recs[0]["source"], "000123"))

    def test_unknown_record_returns_none(self):
        self.assertIsNone(db.get_incident(self.conn, "nope", "nope"))

    def test_reloading_is_idempotent(self):
        recs = records(feature())
        db.load_records(self.conn, recs)
        second = db.load_records(self.conn, recs)
        self.assertEqual((second["inserted"], second["unchanged"]), (0, 1))
        self.assertEqual(self.conn.execute("SELECT COUNT(*) FROM incidents").fetchone()[0], 1)

    def test_conflicting_version_is_held_and_not_overwritten(self):
        db.load_records(self.conn, records(feature()))
        changed = records(feature(Nature="THEFT"))
        summary = db.load_records(self.conn, changed)
        self.assertEqual(summary["inserted"], 0)
        self.assertEqual(summary["held"][0]["reason"], "conflicts with stored version")
        stored = db.get_incident(self.conn, changed[0]["source"], "2025068460")
        self.assertEqual(stored["description"], "BURGLARY VEHICLE")

    def test_unknown_flag_is_held(self):
        recs = records(feature())
        recs[0]["quality_flags"].append("made_up_flag")
        summary = db.load_records(self.conn, recs)
        self.assertEqual(summary["inserted"], 0)
        self.assertIn("unknown flag", summary["held"][0]["reason"])
        self.assertEqual(self.conn.execute("SELECT COUNT(*) FROM incidents").fetchone()[0], 0)

    def test_database_rejection_is_held_and_rest_still_load(self):
        good, bad = records(feature(ID="1"), feature(ID="2"))
        bad["record_kind"] = "crime"                  # not an allowed value
        summary = db.load_records(self.conn, [bad, good])
        self.assertEqual(summary["inserted"], 1)
        self.assertEqual(len(summary["held"]), 1)

    def test_records_can_be_found_by_flag(self):
        db.load_records(self.conn, records(feature(ID="1"), feature(ID="2", geometry={})))
        rows = self.conn.execute(
            "SELECT i.source_record_id FROM incidents i JOIN incident_quality_flags f "
            "ON f.incident_id = i.id WHERE f.flag = 'missing_coordinates'").fetchall()
        self.assertEqual(rows, [("2",)])

    def test_verify_detects_a_changed_value(self):
        recs = records(feature())
        db.load_records(self.conn, recs)
        self.conn.execute("UPDATE incidents SET description = 'TAMPERED'")
        self.assertTrue(any("differ" in p for p in db.verify(self.conn, recs)))

    def test_verify_detects_a_missing_record(self):
        recs = records(feature(ID="1"), feature(ID="2"))
        db.load_records(self.conn, recs[:1])
        problems = db.verify(self.conn, recs)
        self.assertTrue(any("not found" in p for p in problems))

    def test_deleting_an_incident_removes_its_flags(self):
        db.load_records(self.conn, records(feature()))
        self.conn.execute("DELETE FROM incidents")
        self.assertEqual(
            self.conn.execute("SELECT COUNT(*) FROM incident_quality_flags").fetchone()[0], 0)


if __name__ == "__main__":
    unittest.main()
