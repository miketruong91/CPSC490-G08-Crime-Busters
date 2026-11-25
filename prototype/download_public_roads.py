"""Download public Census road geometry for local intersection matching.

The query sends only a public regional bounding box, not incident records.
"""
import json,concurrent.futures
from urllib.request import urlopen,Request
from urllib.parse import urlencode
from pathlib import Path
out=Path(__file__).resolve().parent/'data'/'geocoding'/'roads'
out.mkdir(parents=True,exist_ok=True)
def load(layer):
 params={'where':'1=1','geometry':'-118.05,33.78,-117.70,33.96','geometryType':'esriGeometryEnvelope','inSR':4326,'outSR':4326,'spatialRel':'esriSpatialRelIntersects','outFields':'*','returnGeometry':'true','f':'json','resultRecordCount':100000}
 url=f'https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/Transportation/MapServer/{layer}/query?'+urlencode(params)
 cache=out/f'tiger-layer-{layer}.json'
 if cache.exists():return
 with urlopen(Request(url,headers={'User-Agent':'CrimeBusters-AcademicPrototype/1.0'}),timeout=100) as s: d=json.load(s)
 if d.get('error') or d.get('exceededTransferLimit'):raise ValueError(str(d.get('error') or 'Truncated road geometry'))
 cache.write_text(json.dumps(d,separators=(',',':')))
 print(layer,len(d.get('features',[])),'roads',flush=True)
if __name__=='__main__':
    with concurrent.futures.ThreadPoolExecutor(3) as pool:list(pool.map(load,[8,6,2]))
