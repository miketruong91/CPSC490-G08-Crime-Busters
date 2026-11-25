import unittest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch
import expand_saved_geocoding as expansion
import street_geometry
from geocode_all import make_jobs, address_csv, assess_row, collect
from street_geometry import crossing, road_matches, road_key
from expand_saved_geocoding import corroborate


def road(name, path):
    return {'attributes':{'NAME':name},'geometry':{'paths':[path]}}


class FullGeocodingTests(unittest.TestCase):
    def setUp(self):
        self.job={'city':'Anaheim','original':'500 BLOCK N HANOVER ST','number':500,'street':'N HANOVER ST'}
        self.row=['1','500 N HANOVER ST, Anaheim, CA,','Match','Exact',
                  '500 N HANOVER ST, ANAHEIM, CA, 92801','-117.9745,33.8375','123','R']

    def test_request_contains_only_address_context_and_synthetic_id(self):
        jobs=make_jobs([('Anaheim','500 BLOCK N HANOVER ST')])
        self.assertEqual(address_csv(jobs),'1,500 N HANOVER ST,Anaheim,CA,\r\n')
        self.assertNotIn('original',address_csv(jobs))
        self.assertNotIn('case_id',address_csv(jobs))

    def test_fallback_never_leaves_block(self):
        jobs=make_jobs([('Anaheim','500 BLOCK N HANOVER ST')],True)
        self.assertEqual([j['number'] for j in jobs.values()],list(range(501,600)))

    def test_out_of_order_results_select_lowest_matching_number(self):
        jobs=make_jobs([('Anaheim','500 BLOCK N HANOVER ST')],True)
        selected={}
        import csv,io
        rows=[]
        for key,job in reversed(list(jobs.items())):
            n=job['number'];rows.append([key,'input','Match','Exact',
                f'{n} N HANOVER ST, ANAHEIM, CA, 92801','-117.9745,33.8375','123','R'])
        buf=io.StringIO();csv.writer(buf).writerows(rows)
        collect(jobs,buf.getvalue(),selected)
        self.assertEqual(next(iter(selected.values()))['selected_query_number'],501)

    def test_wrong_city_opposite_direction_and_nan_rejected(self):
        for address in ['500 N HANOVER ST, FULLERTON, CA, 92801','500 S HANOVER ST, ANAHEIM, CA, 92801']:
            row=self.row[:];row[4]=address;self.assertIsNone(assess_row(row,self.job))
        row=self.row[:];row[5]='nan,33.8';self.assertIsNone(assess_row(row,self.job))

    def test_missing_direction_needs_local_road_evidence(self):
        row=self.row[:];row[3]='Non_Exact';row[4]='500 HANOVER ST, ANAHEIM, CA, 92801'
        self.assertIsNone(assess_row(row,self.job))
        good=road('N Hanover St',[[-117.9745,33.83],[-117.9745,33.85]])
        result=corroborate(self.job,row,[good],{})
        self.assertIsNotNone(result)
        far=road('N Hanover St',[[-117.99,33.83],[-117.99,33.85]])
        self.assertIsNone(corroborate(self.job,row,[far],{}))

    def test_parallel_streets_and_street_type_conflicts_are_not_crossings(self):
        self.assertIsNone(crossing([0,0],[1,0],[0,1],[1,1]))
        self.assertFalse(road_matches('N CITRON ST',road('N Citron Ln',[[0,0],[1,1]])))

    def test_east_st_is_not_an_empty_directional_name(self):
        self.assertEqual(road_key('East Street'),'EAST ST')
        self.assertTrue(road_matches('EAST ST',road('N East St',[[0,0],[1,1]])))
        self.assertFalse(road_matches('EAST ST',road('N Other St',[[0,0],[1,1]])))

    def test_shared_crossing(self):
        self.assertEqual(crossing([0,0],[1,1],[0,1],[1,0]),[0.5,0.5])


class RoadExtractSafetyTests(unittest.TestCase):
    def setUp(self):
        self.directory=tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root=Path(self.directory.name)
        self.roads=self.root/'data/geocoding/roads'
        self.roads.mkdir(parents=True)
        self.manifest=self.roads.parent/'resolved-locations.json'
        self.saved='{"results": ["previously reviewed coordinates"]}\n'
        self.manifest.write_text(self.saved)
        self.feature=road('N Hanover St',[[-117.9745,33.83],[-117.9745,33.85]])
        for layer in (2,6,8):
            (self.roads/f'tiger-layer-{layer}.json').write_text(json.dumps({'features':[self.feature]}))

    def assert_rebuild_preserves_manifest(self):
        with patch.object(street_geometry,'ROADS',self.roads), patch.object(expansion.g,'ROOT',self.root):
            with self.assertRaises(ValueError):
                expansion.run()
        self.assertEqual(self.manifest.read_text(),self.saved)

    def test_missing_each_required_layer_preserves_saved_coordinates(self):
        for layer in (2,6,8):
            with self.subTest(layer=layer):
                file=self.roads/f'tiger-layer-{layer}.json'
                saved=file.read_text()
                file.unlink()
                self.assert_rebuild_preserves_manifest()
                file.write_text(saved)

    def test_missing_directory_preserves_saved_coordinates(self):
        for file in self.roads.iterdir():file.unlink()
        self.roads.rmdir()
        self.assert_rebuild_preserves_manifest()

    def test_invalid_extract_preserves_saved_coordinates(self):
        invalid=[{'features':[]},{'features':{}},{},[],
                 {'features':[self.feature],'exceededTransferLimit':True},
                 {'features':[self.feature],'error':{'message':'Unavailable'}}]
        for document in invalid:
            with self.subTest(document=document):
                (self.roads/'tiger-layer-6.json').write_text(json.dumps(document))
                self.assert_rebuild_preserves_manifest()

    def test_malformed_json_preserves_saved_coordinates(self):
        (self.roads/'tiger-layer-6.json').write_text('{')
        self.assert_rebuild_preserves_manifest()

    def test_complete_extract_loads_all_required_layers(self):
        with patch.object(street_geometry,'ROADS',self.roads):
            self.assertEqual(street_geometry.read_roads(),[self.feature]*3)


if __name__=='__main__':unittest.main()
