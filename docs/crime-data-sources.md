Related issues: Epic #3; Story #4; Tasks #8 and #9

# Crime Data Sources

## Selection status

Costa Mesa's PoliceIncidents Burglary layer 57 has been identified
as technically suitable for evaluating record parsing, map markers,
date/time filters, and radius searches.

The inspected response contains 19 historical burglary-related
calls for service with dates, times, descriptions, block-level
locations, and coordinates. These are not confirmed crime counts.

Final team adoption and reuse terms remain unresolved. This
evaluation does not establish completion of Story #4 or Task #9.

## Candidate sources

| Candidate | URL | Evaluation status |
|---|---|---|
| Costa Mesa Police Incidents | https://apps.costamesaca.gov/gis1/rest/services/PoliceIncidents/MapServer | Sample query verified; final selection pending |
| Fullerton Police Calls for Service | https://www2.cityoffullerton.com/webdata/apps/cfs/ | Under evaluation |
| Community Crime Map | https://www.communitycrimemap.com/ | Under evaluation |

### Costa Mesa source evaluation

Reviewed by: Alex Reyes
Review date: October 20, 2026

### Publisher and dataset

City of Costa Mesa / Costa Mesa Police Department.
PoliceIncidents service, Burglary layer 57.

Layer URL:
https://apps.costamesaca.gov/gis1/rest/services/PoliceIncidents/MapServer/57

The source describes calls for service, including burglary-related calls.
These records must not be treated as confirmed crimes.

### Access method

Open the layer URL, select Query, and use:

| Parameter | Value |
|---|---|
| Where | 1=1 |
| Out Fields | * |
| Return Geometry | True |
| Output Spatial Reference | 4326 |
| Format | JSON |

### Available fields

| Field | Observed content |
|---|---|
| FID | Object identifier |
| ID | Call identifier |
| CallDate | Date in MM/DD/YYYY format |
| CallTime | Time in HH:MM:SS format |
| Type | Numeric code; meaning not yet verified |
| Code | Call code |
| Nature | Call description |
| Location | Block-level address |
| City | City name |
| Agency | Agency identifier |
| Dispo | Disposition text; may be blank |
| geometry.x | Longitude in EPSG:4326 output |
| geometry.y | Latitude in EPSG:4326 output |

### Sample-query evidence
Reproducible query:
[Burglary layer 57 — JSON sample](https://apps.costamesaca.gov/gis1/rest/services/PoliceIncidents/MapServer/57/query?where=1%3D1&outFields=%2A&returnGeometry=true&outSR=4326&f=pjson)

Results may change; the findings below describe the response inspected.
The query returned 19 features. All contained populated ID, CallDate,
CallTime, Nature, Location, City, and Agency fields and numeric coordinates.
One Dispo value contained only whitespace.

All returned records identified COSTA MESA as the city and CMPD as the
agency. Their dates ranged from July 14 through July 27, 2025.

These findings describe this response only, not the entire service.
The returned dates are historical despite the layer's Past 14 Days label.

### Suitability and limitations

The sample contains fields that support initial testing of map markers,
category and date/time filters, and geographic searches.

Locations use block-level addresses. Coordinate accuracy and exact
incident positions have not been verified.

The sample includes a canceled call and records marked NO REPORT REQUIRED.
Counting every call as a confirmed crime would misrepresent the data.

Update frequency, timezone, reuse terms, and access restrictions remain
unverified. Public accessibility alone does not establish reuse permission.

## Selection outcome

The inspected Costa Mesa sample provides the fields needed for
initial technical evaluation. Nature and Code describe the call
category, CallDate and CallTime provide date and time values, and
geometry provides coordinates in EPSG:4326.

The source is suitable for testing with historical call records;
it has not been verified as a current crime feed. Block-level
locations limit spatial precision, and dispositions require careful
interpretation before producing crime statistics.

The published service metadata contains no license information:
https://apps.costamesaca.gov/gis1/rest/services/PoliceIncidents/MapServer/info/iteminfo

Reuse terms and final team adoption remain unresolved. This document
does not claim permission to redistribute the records.

Fullerton and Community Crime Map were listed as alternatives but
have not been evaluated.

## Remaining work

- Confirm reuse terms and access restrictions.
- Investigate the historical dates and update frequency.
- Confirm timezone and location accuracy.
- Agree on the source and collection scope with the team.
- Complete broader collection and field validation under Story #4 and Task #9.
