# Anaheim and Fullerton source evaluation

Related issues: Epic #3; Task #97; storage Story #28. Reviewed November 24, 2026.

## Selected prototype sources

The prototype integrates saved, publicly accessible records from Fullerton's city-hosted Calls for Service viewer and the independent Anaheim Crime website. Source evaluation covers field compatibility, sample coverage, record meaning, and published usage information. The findings below do not conclude that the datasets cannot be used.

| Source | Saved sample and fields | Technical suitability |
|---|---|---|
| [Fullerton Calls for Service](https://www2.cityoffullerton.com/webdata/apps/cfs/) | 96 unique calls, November 23–24, 2026. Call identifiers, descriptions, reported blocks/intersections, and displayed dates/times. No coordinates in the saved tables. | Integrated with the existing schema as `call_for_service`. Repeat imports do not create duplicates. The map displays 88 calls using documented approximate coordinates; 8 retain null coordinates. |
| [Anaheim Crime](https://anaheimcrime.com/) | 255 unique Anaheim Police incident records, September 18–25, 2026. Case identifiers, categories, descriptions, reported locations, dates, and agency labels. Times and coordinates are absent. | Integrated as `crime_incident`. Repeat imports do not create duplicates. The map displays 246 records using documented approximate coordinates; 9 retain null coordinates. |

These counts describe the saved samples, not full historical coverage. The sources cover different periods and record types, so their counts are not directly comparable city crime rates. Final implemented field mappings and validation rules are in [city-data-import.md](city-data-import.md); map coverage and coordinate provenance are in [multi-city-map.md](multi-city-map.md).

## Source selection and third-party platforms

I selected Fullerton's city-hosted viewer rather than collecting records through LexisNexis Community Crime Map. Anaheim's saved sample came from anaheimcrime.com, an independent public-data presentation, rather than from LexisNexis. It is not represented as an official city export.

The [Anaheim Police Community Crime Map page](https://pd.anaheim.net/280/Community-Crime-Map) identifies LexisNexis as its mapping provider. Alex's reason for avoiding that retrieval route was to avoid depending on a commercial mapping platform and its potentially separate access, automation, and reuse conditions. This records the selection rationale; no specific vendor restriction is asserted without inspecting that vendor's terms.

City-hosted records, city open-data portals, and vendor-hosted maps are distinct publication channels. Public analysis and reuse are common purposes of open-data publishing, but the applicable terms must be recorded for the specific source used. Fullerton's Calls for Service viewer has not been verified as an explicitly licensed open-data portal. Choosing a city-hosted source does not itself establish a blanket license, nor does a general website notice by itself settle the rights in individual factual records.

## Published usage information

| Source | What the review established | What remains unverified |
|---|---|---|
| Fullerton city-hosted viewer | Records are publicly accessible. The City's [general disclaimer and copyright notice](https://www.cityoffullerton.com/about-us/contact-us/disclaimer) reserves rights in website materials and includes a written-permission condition. Its [public-records page](https://www.cityoffullerton.com/government/departments/city-clerk/public-records-information) describes access to City records. | No calls-for-service-specific reuse license was verified. The application of the general website notice to this factual dataset was not established. No conclusion that the project is prohibited follows from this review. |
| Anaheim Crime | The [About](https://anaheimcrime.com/about) and [Sources](https://anaheimcrime.com/sources) pages describe an independent, unofficial presentation of public records. [Methodology](https://anaheimcrime.com/methodology) explains record definitions and location rounding. [Privacy](https://anaheimcrime.com/privacy) and [Corrections](https://anaheimcrime.com/corrections) pages were also inspected. | No explicit reuse license was found on those inspected pages. Upstream terms applicable to this historical snapshot were not independently verified. Absence of a license statement is recorded as unknown, not as a finding that use is prohibited. |

The Fullerton general notice was available through search-engine copies of the official page; direct retrieval returned HTTP 403. The viewer returned only a loading shell in text retrieval. These access limitations are not evidence of a ban on reuse. This document records source information and technical suitability, not a legal determination or a verified grant of unrestricted redistribution rights.

## Rejected candidate and provenance

A separately inspected [ArcGIS item](https://www.arcgis.com/sharing/rest/content/items/9a32b866a3204bb5b9070b5a27248301?f=json) and [table](https://services3.arcgis.com/hPs600I3X0RTaaaq/arcgis/rest/services/Crime_Mapping_/FeatureServer/0) contained no geometry. Sample and distinct-agency queries identified eight San Diego-area agencies and no Anaheim agency. That queried candidate was excluded from the Anaheim import. A city name in metadata was not treated as proof of geographic coverage.

Anaheim Crime's current sources page reports 255 records for September 18–25, matching the saved sample's count and date range. Its upstream link does not independently establish the historical identity or terms of every saved record. Original filenames, hashes, source labels, and source record fields remain preserved in the saved inputs.

## Verification and review

All 351 Anaheim/Fullerton records were imported alongside the 19 Costa Mesa records. Automated checks cover field preservation, stored counts, repeat-import duplicate prevention, and approximate-coordinate provenance. The full suite passed 96 tests plus 15 subtests. Available local repository checks passed; GitHub-dependent checks remain for CI.

Alex ran Flask locally and confirmed map rendering, city/type filtering, zooming, marker details, and recentering. Independent teammate review remains part of the PR process. Technical validation and the published-terms findings above are separate evidence; neither should be described as proving unrestricted reuse rights.

## AI assistance

ChatGPT helped draft the evaluation, implementation, tests, and documentation. Alex supplied the source samples, selected the retrieval routes, and manually tested the Flask map.

Assisted-by: ChatGPT
