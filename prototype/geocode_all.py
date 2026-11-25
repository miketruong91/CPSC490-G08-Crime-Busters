"""Census batch geocoding for the saved city blocks, with local result joins.

Only synthetic job IDs, representative addresses, city, CA and an empty ZIP
are sent. No incident IDs, dates, categories or descriptions leave the project.
Run with --live only after authorizing those address-only Census requests.
"""
import argparse
import csv
from datetime import datetime, timezone
import hashlib
import io
import json
import math
from pathlib import Path
import re
import time
from urllib.request import Request, urlopen
import uuid

from normalize_city import normalize_records

ROOT = Path(__file__).resolve().parent
CACHE = ROOT / 'data' / 'geocoding' / 'batch'
ENDPOINT = 'https://geocoding.geo.census.gov/geocoder/locations/addressbatch'
BENCHMARK = 'Public_AR_Current'

# Equivalent USPS-style street spellings. Directional prefixes are preserved.
ALIASES = {'STREET':'ST', 'AVENUE':'AVE', 'BOULEVARD':'BLVD', 'ROAD':'RD',
           'DRIVE':'DR', 'LANE':'LN', 'PLACE':'PL', 'COURT':'CT', 'CIRCLE':'CIR',
           'PARKWAY':'PKWY', 'HIGHWAY':'HWY', 'TERRACE':'TER', 'TRAIL':'TRL',
           'CIRC':'CIR', 'CAMINO':'CAM', 'NORTH':'N', 'SOUTH':'S', 'EAST':'E', 'WEST':'W'}


def street_key(value):
    value = value.upper().replace('LA PALMA PARK WAY', 'LA PALMA PKWY').replace('CEDAR GLENN', 'CEDAR GLEN').replace('CENTER STREET PROMENADE', 'CENTER ST').replace(' NINTH ', ' 9TH ')
    return ' '.join(ALIASES.get(part, part) for part in re.findall(r'[A-Z0-9]+', value))


def locations():
    result = set()
    for city, filename in [('Anaheim','anaheim-september-2026-raw.json'),
                           ('Fullerton','fullerton-november-2026-raw.json')]:
        accepted, held = normalize_records(json.loads((ROOT/'data'/filename).read_text()),city.lower())
        if held:
            raise ValueError('Source records failed normalization')
        result.update((city, record['location']) for record in accepted)
    return sorted(result)


def make_jobs(items, fallback=False):
    """Synthetic IDs are stable within a request, unrelated to case IDs."""
    jobs = {}
    for city, original in items:
        match = re.fullmatch(r'(\d+) BLOCK (.+)', original or '')
        if not match:
            continue
        start, street = int(match[1]), match[2]
        numbers = range(start+1,(start//100+1)*100) if fallback else [start]
        for number in numbers:
            jobs[str(len(jobs)+1)] = {'city':city, 'original':original,
                                    'number':number, 'street':street}
    return jobs


def address_csv(jobs):
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    for identifier, job in jobs.items():
        writer.writerow([identifier, f"{job['number']} {job['street']}", job['city'], 'CA', ''])
    return buffer.getvalue()


def batch_fetch(jobs, live=False):
    """Cache by exact address-only request content; no implicit network use."""
    payload = address_csv(jobs)
    digest = hashlib.sha256(payload.encode()).hexdigest()
    CACHE.mkdir(parents=True,exist_ok=True)
    response_file = CACHE / f'{digest}.csv'
    if response_file.exists():
        return response_file.read_text()
    # A changed subset/order can reuse individual rows from earlier batches.
    saved={}
    for request in CACHE.glob('*.request.csv'):
        previous={r[0]:(r[2],r[1]) for r in csv.reader(io.StringIO(request.read_text()))}
        prior=request.with_name(request.name.replace('.request.csv','.csv'))
        if not prior.exists():continue
        for row in csv.reader(io.StringIO(prior.read_text())):
            if row and row[0] in previous:saved.setdefault(previous[row[0]],row)
    reused=[]
    for identifier,job in jobs.items():
        key=(job['city'],f"{job['number']} {job['street']}")
        if key not in saved:break
        row=saved[key][:];row[0]=identifier;reused.append(row)
    if len(reused)==len(jobs):
        buffer=io.StringIO();csv.writer(buffer).writerows(reused)
        return buffer.getvalue()
    if not live:
        raise FileNotFoundError('No saved Census batch response; authorize and use --live')
    boundary = uuid.uuid4().hex
    body = (f'--{boundary}\r\nContent-Disposition: form-data; name="benchmark"\r\n\r\n{BENCHMARK}\r\n'
            f'--{boundary}\r\nContent-Disposition: form-data; name="addressFile"; filename="addresses.csv"\r\nContent-Type: text/csv\r\n\r\n').encode()
    body += payload.encode() + f'\r\n--{boundary}--\r\n'.encode()
    req = Request(ENDPOINT, data=body,headers={
        'Content-Type':'multipart/form-data; boundary='+boundary,
        'User-Agent':'CrimeBusters-AcademicPrototype/1.0'})
    with urlopen(req,timeout=180) as stream:
        response = stream.read().decode('utf-8-sig')
    # Do not cache an HTML error page as if it were a successful batch.
    returned = list(csv.reader(io.StringIO(response)))
    if len(returned) != len(jobs) or any(not row or row[0] not in jobs for row in returned):
        raise ValueError('Census batch response does not cover the submitted job IDs')
    response_file.write_text(response)
    (CACHE/f'{digest}.request.csv').write_text(payload)
    return response


def assess_row(row, job):
    if len(row) < 8 or row[2] != 'Match' or row[3] not in {'Exact','Non_Exact'}:
        return None
    parts = [part.strip() for part in row[4].split(',')]
    if len(parts) < 3:
        return None
    try:
        lon,lat = map(float,row[5].split(','))
    except ValueError:
        return None
    expected = f"{job['number']} {job['street']}"
    returned_key, expected_key = street_key(parts[0]), street_key(expected)
    # If the source omits a direction, an added provider direction does not
    # contradict it. Explicit source directions must still match.
    tokens=returned_key.split(); wanted=expected_key.split()
    added_direction=(len(tokens)>2 and tokens[1] in {'N','S','E','W'} and
                     (len(wanted)<2 or wanted[1] not in {'N','S','E','W'}) and
                     ' '.join(tokens[:1]+tokens[2:]) == expected_key)
    checks = {'provider_match':True,
              'street_and_number_match':returned_key == expected_key or added_direction,
              'city_label_matches':parts[1].upper() == job['city'].upper(),
              'state_matches':parts[2]=='CA',
              'valid_coordinates':all(math.isfinite(v) for v in [lat,lon]) and -90<=lat<=90 and -180<=lon<=180,
              'within_city_region':(33.65<=lat<=34.0 and -118.1<=lon<=-117.5 if job['city']!='Moreno Valley' else 33.80<=lat<=34.1 and -117.35<=lon<=-117.10)}
    if not all(checks.values()):
        return None
    return {'city_context':job['city'], 'original_location':job['original'],
            'status':'candidate_needs_map_review', 'precision':'block',
            'provider':'US Census Geocoder', 'location_label':'Approximate location',
            'method':'sequential_block_batch_query', 'selected_query_address':expected,
            'selected_query_number':job['number'], 'request_url':ENDPOINT,
            'benchmark':BENCHMARK, 'candidates':[{'latitude':lat,'longitude':lon,
             'matched_address':row[4], 'tiger_line':{'id':row[6],'side':row[7]},'checks':checks}]}


def collect(jobs, response, selected):
    seen=set()
    for row in csv.reader(io.StringIO(response)):
        if not row or row[0] not in jobs or row[0] in seen:
            raise ValueError('Unexpected or duplicate batch job ID')
        seen.add(row[0])
        job=jobs[row[0]]
        result=assess_row(row,job)
        if result:
            key=(job['city'],job['original'])
            if key not in selected or result['selected_query_number'] < selected[key]['selected_query_number']:
                selected[key]=result
    if seen != jobs.keys():
        raise ValueError('Missing batch job IDs')


def run(live=False):
    all_locations=locations()
    selected={}
    first=make_jobs(all_locations)
    collect(first,batch_fetch(first,live),selected)
    missing=[key for key in all_locations if key not in selected and re.fullmatch(r'\d+ BLOCK .+',key[1] or '')]
    print(f'First-number pass: {len(selected)} of {len(first)} blocks matched; {len(missing)} require within-block fallback.',flush=True)
    fallback=make_jobs(missing,True)
    jobs_list=list(fallback.values())
    for start in range(0,len(jobs_list),10000):
        chunk={str(i+1):job for i,job in enumerate(jobs_list[start:start+10000])}
        collect(chunk,batch_fetch(chunk,live),selected)
        print(f'Fallback pass: {len(selected)} blocks now matched.',flush=True)
        if live:time.sleep(1)
    result={'provider':'US Census Geocoder', 'benchmark':BENCHMARK,
            'retrieved_utc':datetime.now(timezone.utc).isoformat(),
            'privacy':'Only synthetic job IDs, addresses and city/state labels were submitted.',
            'results':list(selected.values()), 'unresolved':[{'city':city,'original_location':original} for city,original in all_locations if (city,original) not in selected]}
    (ROOT/'data/geocoding/expanded-results.json').write_text(json.dumps(result,indent=2)+'\n')
    return result


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--live',action='store_true',help='Send address-only batches to Census; requires user authorization')
    result=run(parser.parse_args().live)
    print(f"{len(result['results'])} unique block locations matched; {len(result['unresolved'])} locations unresolved.")
