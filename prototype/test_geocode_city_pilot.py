import copy
import json
from pathlib import Path
import unittest
from geocode_city_pilot import resolve_block, cached_fetch, CacheMiss

ROOT = Path(__file__).parent / 'data' / 'geocoding'
ORIGINAL = '500 BLOCK N HANOVER ST'


def response(number=500, **changes):
    parts = dict(city='ANAHEIM', state='CA', preDirection='N', streetName='HANOVER',
                 suffixType='ST', fromAddress=str(number), toAddress=str(number))
    parts.update(changes)
    return {'result': {'addressMatches': [{'addressComponents': parts,
            'coordinates': {'x': -117.97, 'y': 33.84}, 'matchedAddress': f'{number} N HANOVER ST'}]}}


class BlockFallbackTests(unittest.TestCase):
    def resolve(self, fetch, original=ORIGINAL):
        calls = []
        def tracked(city, number, street):
            calls.append((city, number, street))
            return fetch(number)
        return resolve_block('Anaheim', original, tracked), calls

    def test_first_match_stops_search(self):
        result, calls = self.resolve(lambda n: response(n))
        self.assertEqual(len(calls), 1)
        self.assertEqual(result['selected_query_address'], '500 N HANOVER ST')
        self.assertEqual(result['original_location'], ORIGINAL)
        self.assertEqual(result['location_label'], 'Approximate location')

    def test_advances_sequentially(self):
        result, calls = self.resolve(lambda n: response(n) if n == 502 else {'result': {'addressMatches': []}})
        self.assertEqual([c[1] for c in calls], [500, 501, 502])
        self.assertTrue(all(c[0] == 'Anaheim' and c[2] == 'N HANOVER ST' for c in calls))
        self.assertEqual(result['selected_query_address'], '502 N HANOVER ST')
        self.assertFalse(result['approved_for_import'])

    def test_rejects_city_direction_street_and_state_mismatch(self):
        for changes in [dict(city='FULLERTON'), dict(preDirection=''), dict(streetName='OTHER'), dict(state='NY')]:
            with self.subTest(changes=changes):
                result, calls = self.resolve(lambda n: response(n, **changes) if n == 500 else response(n))
                self.assertEqual(len(calls), 2)

    def test_ambiguous_match_is_skipped(self):
        ambiguous = response()
        ambiguous['result']['addressMatches'] *= 2
        result, calls = self.resolve(lambda n: ambiguous if n == 500 else response(n))
        self.assertEqual(result['selected_query_address'], '501 N HANOVER ST')

    def test_range_parity(self):
        result, calls = self.resolve(lambda n: response(n, fromAddress='501', toAddress='599'))
        self.assertEqual(result['selected_query_address'], '501 N HANOVER ST')

    def test_does_not_cross_block(self):
        result, calls = self.resolve(lambda n: {'result': {'addressMatches': []}})
        self.assertEqual([c[1] for c in calls], list(range(500, 600)))
        self.assertEqual(result['status'], 'needs_review')
        self.assertNotIn('selected_query_address', result)

    def test_last_number_can_match(self):
        result, calls = self.resolve(lambda n: response(n) if n == 599 else {'result': {'addressMatches': []}})
        self.assertEqual(result['selected_query_address'], '599 N HANOVER ST')

    def test_request_failure_stops_for_retry(self):
        def unavailable(n):
            raise TimeoutError('offline')
        result, calls = self.resolve(unavailable)
        self.assertEqual(result['status'], 'request_failed')
        self.assertEqual(len(calls), 1)

    def test_uncached_lookup_is_pending(self):
        def uncached(n):
            raise CacheMiss()
        result, calls = self.resolve(uncached)
        self.assertEqual(result["status"], "lookup_pending")
        self.assertEqual(len(calls), 1)

    def test_invalid_response_is_failure(self):
        result, calls = self.resolve(lambda n: {'errors': ['service unavailable']})
        self.assertEqual(result['status'], 'request_failed')
        self.assertEqual(len(calls), 1)

    def test_invalid_coordinates_rejected(self):
        invalid = response()
        invalid['result']['addressMatches'][0]['coordinates']['x'] = 190
        result, calls = self.resolve(lambda n: invalid if n == 500 else response(n))
        self.assertEqual(len(calls), 2)

    def test_unsupported_location_requires_review(self):
        result, calls = self.resolve(lambda n: response(n), 'N HANOVER ST / W LINCOLN AVE')
        self.assertEqual(calls, [])
        self.assertEqual(result['status'], 'needs_review')

    def test_original_hanover_cache_rejected_for_direction(self):
        original = json.loads((ROOT / 'census-response-04.json').read_text())
        result, calls = self.resolve(lambda n: copy.deepcopy(original) if n == 500 else response(n))
        self.assertEqual(result['selected_query_address'], '501 N HANOVER ST')
        self.assertFalse(result['attempts'][0]['candidates'][0]['checks']['street_matches'])


if __name__ == '__main__':
    unittest.main()
