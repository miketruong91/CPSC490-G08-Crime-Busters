"""Tests for normalize.py (Task #11). Run: python3 -m unittest discover prototype

The first test checks the exact example record in docs/crime-data-format.md.
The other records are synthetic, built to trigger each validation rule.
"""
import copy
import unittest

import normalize as n


def feature(**attrs):
    """A Costa Mesa feature shaped like the layer's JSON, with overridable fields."""
    base = {"FID": 1, "ID": "2025068460", "CallDate": "07/26/2025",
            "CallTime": "12:12:51", "Type": 7, "Code": "459V",
            "Nature": "BURGLARY VEHICLE", "Location": "100 BLK E 18TH ST",
            "City": "COSTA MESA", "Agency": "CMPD", "Dispo": "   "}
    geometry = {"x": -117.91764968214937, "y": 33.639379802719652}
    if "geometry" in attrs:
        geometry = attrs.pop("geometry")
    base.update(attrs)
    return {"attributes": base, "geometry": geometry}


class SampleRecord(unittest.TestCase):
    def test_matches_documented_example(self):
        record = n.normalize_feature(feature())
        self.assertEqual(record, {
            "source": "costa_mesa_police_incidents",
            "source_record_id": "2025068460",
            "record_kind": "call_for_service",
            "crime_type": "burglary",
            "source_code": "459V",
            "description": "BURGLARY VEHICLE",
            "location": "100 BLK E 18TH ST",
            "city": "COSTA MESA",
            "agency": "CMPD",
            "incident_date": "2025-07-26",
            "incident_time": "12:12:51",
            "timezone": None,
            "latitude": 33.639379802719652,
            "longitude": -117.91764968214937,
            "location_precision": "block",
            "disposition": None,
            "quality_flags": ["timezone_unverified", "location_not_exact"],
        })


class ValidationRules(unittest.TestCase):
    def flags(self, **kw):
        return n.normalize_feature(feature(**kw))["quality_flags"]

    def test_invalid_calendar_date(self):
        record = n.normalize_feature(feature(CallDate="02/30/2025"))
        self.assertIsNone(record["incident_date"])
        self.assertIn("invalid_date", record["quality_flags"])

    def test_wrong_date_format(self):
        self.assertIn("invalid_date", self.flags(CallDate="2025-07-26"))

    def test_missing_date_and_time(self):
        flags = self.flags(CallDate=None, CallTime="  ")
        self.assertIn("missing_date", flags)
        self.assertIn("missing_time", flags)

    def test_invalid_time(self):
        record = n.normalize_feature(feature(CallTime="25:61:00"))
        self.assertIsNone(record["incident_time"])
        self.assertIn("invalid_time", record["quality_flags"])

    def test_missing_location(self):
        record = n.normalize_feature(feature(Location=" "))
        self.assertIsNone(record["location"])
        self.assertIn("missing_location", record["quality_flags"])

    def test_missing_coordinates_become_null_not_zero(self):
        record = n.normalize_feature(feature(geometry={"x": -117.9}))
        self.assertIsNone(record["latitude"])
        self.assertIsNone(record["longitude"])
        self.assertIn("missing_coordinates", record["quality_flags"])

    def test_no_geometry_at_all(self):
        record = n.normalize_feature({"attributes": feature()["attributes"]})
        self.assertEqual((record["latitude"], record["longitude"]), (None, None))
        self.assertIn("missing_coordinates", record["quality_flags"])

    def test_out_of_range_coordinates_null_both(self):
        for geom in ({"x": -117.9, "y": 91.0}, {"x": -181.0, "y": 33.6},
                     {"x": "abc", "y": 33.6}, {"x": float("nan"), "y": 33.6},
                     {"x": True, "y": 33.6}):
            record = n.normalize_feature(feature(geometry=geom))
            self.assertEqual((record["latitude"], record["longitude"]), (None, None), geom)
            self.assertIn("invalid_coordinates", record["quality_flags"], geom)

    def test_whitespace_disposition_is_null(self):
        self.assertIsNone(n.normalize_feature(feature(Dispo="  \t "))["disposition"])

    def test_disposition_text_kept_as_is(self):
        record = n.normalize_feature(feature(Dispo=" NO REPORT REQUIRED "))
        self.assertEqual(record["disposition"], "NO REPORT REQUIRED")

    def test_canceled_call_is_retained(self):
        record = n.normalize_feature(feature(Dispo="CANCELED"))
        self.assertIsNotNone(record)

    def test_id_stays_a_string_with_leading_zeros(self):
        self.assertEqual(n.normalize_feature(feature(ID="000123"))["source_record_id"], "000123")

    def test_numeric_type_field_is_not_used(self):
        a = n.normalize_feature(feature(Type=1))
        b = n.normalize_feature(feature(Type=99))
        self.assertEqual(a["crime_type"], b["crime_type"])

    def test_call_is_never_a_confirmed_crime(self):
        self.assertEqual(n.normalize_feature(feature())["record_kind"], "call_for_service")


class HeldAndDuplicates(unittest.TestCase):
    def test_missing_id_is_held_not_accepted(self):
        accepted, held = n.normalize({"features": [feature(ID=None), feature(ID="  ")]})
        self.assertEqual(accepted, [])
        self.assertEqual([h["reason"] for h in held], ["missing_source_record_id"] * 2)

    def test_identical_duplicate_is_dropped(self):
        accepted, held = n.normalize({"features": [feature(), feature()]})
        self.assertEqual((len(accepted), len(held)), (1, 0))

    def test_conflicting_duplicate_is_held_and_first_kept(self):
        accepted, held = n.normalize({"features": [feature(), feature(Nature="THEFT")]})
        self.assertEqual(len(accepted), 1)
        self.assertEqual(accepted[0]["description"], "BURGLARY VEHICLE")
        self.assertEqual(held[0]["reason"], "conflicting_duplicate")

    def test_same_date_and_coordinates_alone_are_not_duplicates(self):
        accepted, held = n.normalize({"features": [feature(ID="1"), feature(ID="2")]})
        self.assertEqual((len(accepted), len(held)), (2, 0))

    def test_input_is_not_modified(self):
        payload = {"features": [feature()]}
        before = copy.deepcopy(payload)
        n.normalize(payload)
        self.assertEqual(payload, before)

    def test_empty_response(self):
        self.assertEqual(n.normalize({}), ([], []))


if __name__ == "__main__":
    unittest.main()
