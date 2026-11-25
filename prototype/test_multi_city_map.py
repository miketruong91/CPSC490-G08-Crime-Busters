import json
from pathlib import Path
import sqlite3
import tempfile
import unittest

from app import app
from build_map_db import build, DATA
from load_db import connect


class MultiCityMapTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / 'combined.db'
        self.report = build(self.path)
        self.previous = app.config['DATABASE']
        app.config['DATABASE'] = str(self.path)
        self.client = app.test_client()

    def tearDown(self):
        app.config['DATABASE'] = self.previous
        self.temp.cleanup()

    def test_combined_data_and_coverage(self):
        response = self.client.get('/api/map-incidents')
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertEqual(data['total_records'], 370)
        self.assertEqual(data['count'], 353)
        self.assertEqual(data['unmapped_count'], 17)
        self.assertEqual({r['city'] for r in data['incidents']}, {'Costa Mesa', 'Anaheim', 'Fullerton'})
        self.assertEqual(data['by_city']['Costa Mesa']['mapped'], 19)
        self.assertEqual(data['by_city']['Anaheim']['mapped'], 246)
        self.assertEqual(data['by_city']['Fullerton']['mapped'], 88)

    def test_derived_coordinates_have_provenance_and_original_locations(self):
        records = self.client.get('/api/map-incidents').json['incidents']
        for record in records:
            self.assertTrue(record['location_label'].startswith('Approximate'))
            if record['city'] != 'Costa Mesa':
                self.assertIn('US Census', record['geocoding']['provider'])
                self.assertTrue('BLOCK' in record['location'] or '/' in record['location'])
        with sqlite3.connect(self.path) as conn:
            self.assertEqual(conn.execute('SELECT COUNT(*) FROM incident_geocoding').fetchone()[0], 334)
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM incidents WHERE source != 'costa_mesa_police_incidents' AND city IS NOT NULL").fetchone()[0], 0)
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM incident_quality_flags f JOIN incidents i ON i.id=f.incident_id WHERE i.latitude IS NOT NULL AND f.flag='missing_coordinates'").fetchone()[0], 0)
            self.assertGreater(conn.execute("SELECT COUNT(*) FROM incidents WHERE location='500 BLOCK N HANOVER ST' AND latitude IS NOT NULL").fetchone()[0], 0)

    def test_reimport_of_combined_records_does_not_duplicate_or_change_them(self):
        from load_db import get_incident, load_records, verify
        conn = connect(self.path)
        try:
            records = [get_incident(conn, source, identifier) for source, identifier in
                       conn.execute('SELECT source, source_record_id FROM incidents').fetchall()]
            self.assertEqual(load_records(conn, records), {'inserted': 0, 'unchanged': 370, 'held': []})
            self.assertEqual(verify(conn, records), [])
            self.assertEqual(conn.execute('SELECT COUNT(*) FROM incident_geocoding').fetchone()[0], 334)
        finally:
            conn.close()

    def test_standalone_export_includes_combined_records(self):
        from export_map import export
        page = Path(self.temp.name) / 'map.html'
        export(page)
        content = page.read_text()
        self.assertIn('window.CRIME_BUSTERS_DATA=', content)
        self.assertIn('"total_records": 370', content)
        self.assertIn('"count": 353', content)
        self.assertIn('"city": "Fullerton"', content)
        self.assertIn('"city": "Anaheim"', content)

    def test_every_original_case_date_and_description_remains_attached(self):
        from normalize_city import normalize_records
        expected={}
        for city, filename in [('anaheim','anaheim-september-2026-raw.json'),('fullerton','fullerton-november-2026-raw.json')]:
            records,held=normalize_records(json.loads((DATA/filename).read_text()),city)
            self.assertEqual(held,[])
            for record in records:expected[(record['source'],record['source_record_id'])]=record
        with sqlite3.connect(self.path) as conn:
            conn.row_factory=sqlite3.Row
            for stored in conn.execute("SELECT * FROM incidents WHERE source!='costa_mesa_police_incidents'"):
                original=expected[(stored['source'],stored['source_record_id'])]
                for field in ['source_record_id','incident_date','incident_time','description','location','source_code','record_kind','city','agency']:
                    self.assertEqual(stored[field],original[field],(stored['source_record_id'],field))

    def test_out_of_city_follow_up_is_retained_for_review_and_not_plotted(self):
        visible=self.client.get('/api/map-incidents').json['incidents']
        self.assertFalse(any(r['source_record_id']=='26-57389' and r['source']=='fullerton_police_calls_for_service' for r in visible))
        with sqlite3.connect(self.path) as conn:
            record=conn.execute("SELECT location, description, latitude, longitude FROM incidents WHERE source='fullerton_police_calls_for_service' AND source_record_id='26-57389'").fetchone()
            self.assertEqual(record,('26300 BLOCK IRIS AVE MORENO VALLEY','FOLLOW UP CASE',None,None))
        manifest=json.loads((DATA/'geocoding'/'resolved-locations.json').read_text())
        review=next(r for r in manifest['review_candidates'] if r['original_location']=='26300 BLOCK IRIS AVE MORENO VALLEY')
        self.assertEqual(review['status'],'needs_location_review')
        self.assertEqual(review['matched_city'],'Moreno Valley')
        self.assertEqual(review['city_context'],'Fullerton')

    def test_existing_database_is_never_overwritten(self):
        before = self.path.read_bytes()
        with self.assertRaises(FileExistsError):
            build(self.path)
        self.assertEqual(self.path.read_bytes(), before)

    def test_old_database_without_geocoding_table_still_works(self):
        legacy = Path(self.temp.name) / 'legacy.db'
        conn = connect(legacy)
        conn.execute("DROP TABLE incident_geocoding")
        conn.commit()
        conn.close()
        app.config['DATABASE'] = str(legacy)
        response = self.client.get('/api/map-incidents')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['incidents'], [])

    def test_missing_database_returns_503(self):
        app.config['DATABASE'] = str(Path(self.temp.name) / 'missing.db')
        self.assertEqual(self.client.get('/api/map-incidents').status_code, 503)

    def test_page_includes_city_filter_and_multi_city_labels(self):
        page = self.client.get('/').get_data(as_text=True)
        self.assertIn('id="city-filter"', page)
        self.assertIn('Anaheim crime incidents', page)
        self.assertIn('Approximate location', page)


if __name__ == '__main__':
    unittest.main()
