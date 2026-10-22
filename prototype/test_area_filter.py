"""Unit tests for Issue #17; run: python -m unittest discover -s prototype -p 'test_area_filter.py'."""
import unittest

from area_filter import distance_miles, filter_incidents


class AreaFilterTests(unittest.TestCase):
    def setUp(self):
        self.center = (33.84, -117.91)
        self.incidents = [
            {"id": 1, "crime_type": "Theft", "latitude": 33.84, "longitude": -117.91},
            {"id": 2, "crime_type": "Assault", "latitude": 33.85, "longitude": -117.91},
            {"id": 3, "crime_type": "Burglary", "latitude": 34.05, "longitude": -118.25},
        ]

    def test_inside_and_outside(self):
        result = filter_incidents(self.incidents, *self.center, 2)
        self.assertEqual([item["id"] for item in result], [1, 2])

    def test_empty_result(self):
        result = filter_incidents(self.incidents[1:], *self.center, 0)
        self.assertEqual(result, [])

    def test_zero_radius_includes_center(self):
        result = filter_incidents(self.incidents, *self.center, 0)
        self.assertEqual([item["id"] for item in result], [1])

    def test_boundary_included(self):
        radius = distance_miles(*self.center, 33.85, -117.91)
        result = filter_incidents(self.incidents, *self.center, radius)
        self.assertEqual([item["id"] for item in result], [1, 2])

    def test_missing_or_invalid_coordinates_skipped(self):
        data = self.incidents[:1] + [
            {"id": 4, "latitude": None, "longitude": -117.91},
            {"id": 5, "latitude": 100, "longitude": -117.91},
            {"id": 6, "crime_type": "Unknown"},
        ]
        self.assertEqual([x["id"] for x in filter_incidents(data, *self.center, 2)], [1])

    def test_invalid_search_inputs(self):
        for radius in (-1, float("nan"), float("inf"), "2"):
            with self.assertRaises(ValueError):
                filter_incidents(self.incidents, *self.center, radius)
        with self.assertRaises(ValueError):
            filter_incidents(self.incidents, 91, -117.91, 2)

    def test_preserves_incident_fields(self):
        result = filter_incidents(self.incidents, *self.center, 2)
        self.assertEqual(result[0]["crime_type"], "Theft")


if __name__ == "__main__":
    unittest.main()
