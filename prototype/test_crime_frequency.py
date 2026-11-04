"""Tests for selected-area crime frequency analysis (Issue #18)."""
import unittest

from area_filter import filter_incidents
from crime_frequency import analyze_frequency


class CrimeFrequencyTests(unittest.TestCase):
    def setUp(self):
        self.incidents = [
            {"id": 1, "crime_type": "Theft", "latitude": 33.84, "longitude": -117.91,
             "date": "2026-10-19", "time": "09:15:00"},
            {"id": 2, "crime_type": "Assault", "latitude": 33.85, "longitude": -117.91,
             "datetime": "2026-10-19T21:30:00"},
            {"id": 3, "crime_type": "Theft", "latitude": 33.84, "longitude": -117.91,
             "timestamp": "2026-10-20T09:05:00Z"},
            {"id": 4, "crime_type": "Burglary", "latitude": 34.05, "longitude": -118.25,
             "date": "2026-10-20", "time": "15:00:00"},
        ]

    def test_counts_by_type_date_and_hour(self):
        result = analyze_frequency(self.incidents[:3])
        self.assertEqual(result["total_incidents"], 3)
        self.assertEqual(result["by_crime_type"], {"Assault": 1, "Theft": 2})
        self.assertEqual(result["by_date"], {"2026-10-19": 2, "2026-10-20": 1})
        self.assertEqual(result["by_hour"], {"09:00": 2, "21:00": 1})

    def test_selected_area_excludes_outside_records(self):
        selected = filter_incidents(self.incidents, 33.84, -117.91, 2)
        result = analyze_frequency(selected)
        self.assertEqual(result["total_incidents"], 3)
        self.assertNotIn("Burglary", result["by_crime_type"])

    def test_empty_input(self):
        self.assertEqual(analyze_frequency([]), {
            "total_incidents": 0, "by_crime_type": {}, "by_date": {}, "by_hour": {}
        })

    def test_missing_fields_still_count_toward_total(self):
        result = analyze_frequency([{}, {"crime_type": "  "}, {"crime_type": "Theft"}])
        self.assertEqual(result["total_incidents"], 3)
        self.assertEqual(result["by_crime_type"], {"Theft": 1})
        self.assertEqual(result["by_date"], {})
        self.assertEqual(result["by_hour"], {})

    def test_invalid_dates_and_times_skipped(self):
        result = analyze_frequency([
            {"crime_type": "Theft", "date": "not-a-date", "time": "12:00"},
            {"crime_type": "Theft", "date": "2026-10-19", "time": "bad"},
        ])
        self.assertEqual(result["by_date"], {"2026-10-19": 1})
        self.assertEqual(result["by_hour"], {})

    def test_type_whitespace_normalized(self):
        result = analyze_frequency([{"crime_type": " Theft "}, {"crime_type": "Theft"}])
        self.assertEqual(result["by_crime_type"], {"Theft": 2})


if __name__ == "__main__":
    unittest.main()
