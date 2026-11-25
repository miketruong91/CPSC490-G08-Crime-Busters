"""Rebuild full location matches locally from the saved Census responses.

No network requests. Case IDs and other incident details are joined only by
build_map_db.py, after address-only geocoding has completed.
"""
import csv
import io
import json
import math
import re

import geocode_all as g
import street_geometry as s


def saved_rows():
    known=set(g.locations())
    for request in sorted(g.CACHE.glob('*.request.csv')):
        jobs={}
        for row in csv.reader(io.StringIO(request.read_text())):
            number,street=row[1].split(' ',1);number=int(number)
            original=f'{number//100*100} BLOCK {street}'
            if row[2]=='Moreno Valley':
                original='26300 BLOCK IRIS AVE MORENO VALLEY'
            elif (row[2],original) not in known:
                raise ValueError('Saved query does not belong to a source block')
            jobs[row[0]]={'city':row[2],'original':original,'number':number,'street':street}
        response=request.with_name(request.name.replace('.request.csv','.csv'))
        seen=set()
        for row in csv.reader(io.StringIO(response.read_text())):
            if row[0] not in jobs or row[0] in seen:
                raise ValueError('Unexpected or duplicate batch response identifier')
            seen.add(row[0]);yield jobs[row[0]],row
        if seen!=jobs.keys():raise ValueError('Missing batch response identifiers')


def corroborate(job,row,roads,cache):
    if len(row)<8 or row[2]!='Match':return None
    parts=[part.strip() for part in row[4].split(',')]
    if len(parts)<3 or parts[1].upper()!=job['city'].upper() or parts[2]!='CA':return None
    try:
        number,returned_street=parts[0].split(' ',1)
        lon,lat=map(float,row[5].split(','))
    except ValueError:return None
    if not(all(math.isfinite(v) for v in [lon,lat]) and -90<=lat<=90 and -180<=lon<=180):return None
    if int(number)!=job['number']:return None
    wanted=s.road_key(job['street']).split();found=s.road_key(returned_street).split()
    if not wanted or not found:return None
    if len(wanted)>2 and len(found)>2 and wanted[0] in s.DIRECTIONS and found[0] in s.DIRECTIONS and wanted[0]!=found[0]:return None
    if wanted[-1] in s.SUFFIXES and found[-1] in s.SUFFIXES and wanted[-1]!=found[-1]:return None
    if s.base_key(job['street'])!=s.base_key(returned_street):return None
    key=job['street']
    if key not in cache:cache[key]=[f for f in roads if s.road_matches(key,f)]
    roadset=cache[key]
    direction_unverified=False
    if len(wanted)>2 and wanted[0] in s.DIRECTIONS and not(len(found)>2 and found[0] in s.DIRECTIONS):
        bare=' '.join(wanted[1:]);cachekey='bare:'+bare
        if cachekey not in cache:cache[cachekey]=[f for f in roads if s.road_key(f['attributes']['NAME'] or '')==bare]
        nearest_named=min((s.point_to_road([lon,lat],f) for f in roadset),default=float('inf'))
        if not roadset or nearest_named<=500:
            roadset=roadset+cache[cachekey]
            direction_unverified=bool(cache[cachekey])
    distance=min((s.point_to_road([lon,lat],f) for f in roadset),default=float('inf'))
    if distance>60:return None
    return {'city_context':job['city'],'original_location':job['original'],
            'status':'candidate_needs_map_review','precision':'block',
            'provider':'US Census Geocoder + TIGERweb roads','location_label':'Approximate location',
            'method':('census_block_query_road_corroborated_direction_unverified' if direction_unverified
                      else 'census_block_query_road_corroborated'),
            'selected_query_address':f"{job['number']} {job['street']}",
            'selected_query_number':job['number'],'request_url':g.ENDPOINT,'benchmark':g.BENCHMARK,
            'candidates':[{'latitude':lat,'longitude':lon,'matched_address':row[4],
                           'road_distance_meters':round(distance,2),
                           'checks':{'number_matches':True,'city_matches':True,'street_basename_matches':True,
                                     'no_opposite_direction':True,'reported_street_geometry_within_60m':True}}]}


def run():
    roads=s.read_roads();selected={};review={};cache={};rows=list(saved_rows())
    for job,row in rows:
        result=g.assess_row(row,job)
        if result:
            if result['city_context']=='Moreno Valley':
                result['city_context']='Fullerton';result['matched_city']='Moreno Valley'
                result['method']='explicit_out_of_city_address_block_query'
                result['status']='needs_location_review'
                result['review_reason']='Reported address explicitly names a different city than its source dataset; verify before plotting'
                key=(result['city_context'],result['original_location'])
                if key not in review or result['selected_query_number']<review[key]['selected_query_number']:review[key]=result
                continue
            key=(result['city_context'],result['original_location'])
            if key not in selected or result['selected_query_number']<selected[key]['selected_query_number']:
                selected[key]=result
    strict=set(selected)
    for job,row in rows:
        key=(job['city'],job['original'])
        if key in strict or job['city']=='Moreno Valley':continue
        result=corroborate(job,row,roads,cache)
        if result and (key not in selected or result['selected_query_number']<selected[key]['selected_query_number']):
            selected[key]=result
    for city,original in g.locations():
        if '/' in original:
            result=s.intersection(city,original,roads)
            if result:selected[(city,original)]=result
    result={'provider':'US Census Geocoder and US Census TIGERweb',
            'privacy':'Census requests contained only synthetic job IDs, representative addresses, cities and CA. Original case IDs, dates and descriptions were retained locally.',
            'results':list(selected.values()), 'review_candidates':list(review.values()),
            'unresolved':[{'city':city,'original_location':original,'reason':(review[(city,original)]['review_reason'] if (city,original) in review else 'No consistent address-range match or unique road crossing')}
                          for city,original in g.locations() if (city,original) not in selected]}
    (g.ROOT/'data/geocoding/resolved-locations.json').write_text(json.dumps(result,indent=2)+'\n')
    print(f"Resolved {len(selected)} / {len(g.locations())} distinct city locations.")
    return result


if __name__=='__main__':run()
