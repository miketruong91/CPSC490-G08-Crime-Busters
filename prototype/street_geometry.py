"""Match reported intersections locally against saved public Census road lines.

No incident information is transmitted. Road geometry is a public-area extract.
Geometric crossings are approximate and may be grade-separated intersections.
"""
import json
import math
from pathlib import Path
import re

from geocode_all import street_key, ALIASES

ROADS = Path(__file__).with_name('data') / 'geocoding' / 'roads'
REQUIRED_ROAD_LAYERS = (2, 6, 8)
SOURCE = 'https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/Transportation/MapServer'
SUFFIXES = {'ST','AVE','BLVD','RD','DR','LN','PL','CT','CIR','PKWY','HWY','FWY','WAY','TER','TRL'}
DIRECTIONS = {'N','S','E','W','NE','NW','SE','SW'}


def road_key(name):
    tokens = re.findall(r'[A-Z0-9]+', name.upper().replace('NINTH','9TH'))
    if len(tokens)>2 and tokens[0] in {'NORTH','SOUTH','EAST','WEST'}:
        tokens[0]={'NORTH':'N','SOUTH':'S','EAST':'E','WEST':'W'}[tokens[0]]
    aliases={k:v for k,v in ALIASES.items() if k not in {'NORTH','SOUTH','EAST','WEST'}}
    return ' '.join(aliases.get(t,t) for t in tokens)


def base_key(name):
    parts = road_key(name).split()
    if len(parts)>2 and parts[0] in DIRECTIONS:
        parts = parts[1:]
    if len(parts)>1 and parts[-1] in SUFFIXES:
        parts = parts[:-1]
    return ' '.join(parts)


def road_matches(query, feature):
    attrs = feature['attributes']
    name = attrs.get('NAME') or ''
    if re.fullmatch(r'91 (FWY|FREEWAY)',query):
        return name.upper() in {'STATE HWY 91','STATE RT 91','CA-91','RIVERSIDE FWY','RIVERSIDE FREEWAY'}
    q,n=road_key(query),road_key(name)
    if q==n:
        return True
    qparts=q.split();nparts=n.split()
    if qparts and nparts and qparts[-1] in SUFFIXES and nparts[-1] in SUFFIXES and qparts[-1]!=nparts[-1]:
        return False
    # A missing suffix/direction in the report is allowed, but an explicitly
    # specified direction must agree with the road's recorded direction.
    if len(qparts)>2 and qparts[0] in DIRECTIONS:
        if not nparts or nparts[0]!=qparts[0]:
            return False
    return base_key(q)==base_key(n)


def crossing(a,b,c,d):
    """Return the crossing of two finite segments, excluding parallel lines."""
    rx,ry=b[0]-a[0],b[1]-a[1];sx,sy=d[0]-c[0],d[1]-c[1]
    denominator=rx*sy-ry*sx
    if abs(denominator)<1e-18:
        # An exact shared endpoint also covers collinear street transitions.
        return next((p for p in [a,b] if p in [c,d]),None)
    qx,qy=c[0]-a[0],c[1]-a[1]
    t=(qx*sy-qy*sx)/denominator;u=(qx*ry-qy*rx)/denominator
    if -1e-8<=t<=1+1e-8 and -1e-8<=u<=1+1e-8:
        return [a[0]+t*rx,a[1]+t*ry]
    # Small gaps between road endpoints can occur in the public linework.
    ta=max(0,min(1,t));ub=max(0,min(1,u))
    pa=[a[0]+ta*rx,a[1]+ta*ry];pb=[c[0]+ub*sx,c[1]+ub*sy]
    angle=abs(denominator)/(math.hypot(rx,ry)*math.hypot(sx,sy))
    if angle>=0.15 and meters(pa,pb)<=12:
        return [(pa[0]+pb[0])/2,(pa[1]+pb[1])/2]
    return None


def meters(a,b):
    return math.hypot((a[0]-b[0])*92300,(a[1]-b[1])*111100)


def read_roads():
    files=[ROADS/f'tiger-layer-{layer}.json' for layer in REQUIRED_ROAD_LAYERS]
    missing=[file.name for file in files if not file.is_file()]
    if missing:
        raise ValueError('Incomplete public road extract; missing: '+', '.join(missing))
    features=[]
    for file in files:
        document=json.loads(file.read_text())
        if (not isinstance(document,dict) or document.get('error') or
                document.get('exceededTransferLimit') or
                not isinstance(document.get('features'),list) or not document['features']):
            raise ValueError(f'Incomplete public road extract: {file.name}')
        features.extend(document['features'])
    return features


def intersection(city,original,features, allow_omitted_directions=False):
    parts=[p.strip() for p in original.split('/')]
    if len(parts)!=2 or not all(parts):
        return None
    def matches(query,feature):
        if road_matches(query,feature):return True
        query_tokens=road_key(query).split()
        return (allow_omitted_directions and len(query_tokens)>2 and query_tokens[0] in DIRECTIONS and
                road_key(feature['attributes'].get('NAME') or '')==' '.join(query_tokens[1:]))
    left=[f for f in features if matches(parts[0],f)]
    right=[f for f in features if matches(parts[1],f)]
    points=[];evidence=set()
    for a in left:
        for b in right:
            for pa in a.get('geometry',{}).get('paths',[]):
                for pb in b.get('geometry',{}).get('paths',[]):
                    for p,q in zip(pa,pa[1:]):
                        for r,s in zip(pb,pb[1:]):
                            hit=crossing(p,q,r,s)
                            if hit is not None:
                                if not any(meters(hit,old)<1 for old in points):points.append(hit)
                                evidence.update([a['attributes']['NAME'],b['attributes']['NAME']])
    if not points or any(meters(points[0],p)>150 for p in points):
        return intersection(city,original,features,True) if not allow_omitted_directions else None
    lon=sum(p[0] for p in points)/len(points);lat=sum(p[1] for p in points)/len(points)
    # Broad city-context bounds reject distant duplicate street names. These
    # are consistency checks, not authoritative municipal boundary checks.
    bounds={'Anaheim':(33.77,33.88,-118.03,-117.70),'Fullerton':(33.85,33.95,-118.02,-117.82)}[city]
    if not(bounds[0]<=lat<=bounds[1] and bounds[2]<=lon<=bounds[3]):return None
    return {'city_context':city,'original_location':original,'status':'candidate_needs_map_review',
            'precision':'approximate','location_label':'Approximate intersection',
            'provider':'US Census TIGERweb road geometry','method':('local_road_geometry_crossing_direction_unverified' if allow_omitted_directions else 'local_road_geometry_crossing'),
            'selected_query_address':original,'request_url':SOURCE,
            'benchmark':'Saved TIGERweb Transportation road extract',
            'candidates':[{'latitude':lat,'longitude':lon,'matched_address':' / '.join(sorted(evidence)),
                           'checks':{'both_reported_streets_matched':True,'single_crossing_cluster':True,'within_city_context':True},
                           'crossing_count':len(points)}]}


def point_to_road(point,feature):
    """Distance in meters to the closest segment of one road feature."""
    best=float('inf')
    for path in feature.get('geometry',{}).get('paths',[]):
        for a,b in zip(path,path[1:]):
            ax,ay=(a[0]-point[0])*92300,(a[1]-point[1])*111100
            bx,by=(b[0]-point[0])*92300,(b[1]-point[1])*111100
            vx,vy=bx-ax,by-ay
            length=vx*vx+vy*vy
            t=max(0,min(1,-(ax*vx+ay*vy)/length)) if length else 0
            best=min(best,math.hypot(ax+t*vx,ay+t*vy))
    return best
