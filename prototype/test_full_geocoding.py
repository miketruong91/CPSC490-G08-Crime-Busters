import unittest
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


if __name__=='__main__':unittest.main()
