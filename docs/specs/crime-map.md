# Specification — Interactive Crime Map

> Epic: #12 · Stories: #13, #21, #22
> Owner: Julian Chavez · Sprint: 2 · Status: draft

## Scope

**In Scope:**
- Display publicly available crime incidents on an interactive map.
- Allows users to zoom and navigate the map.
- Allows users to filter incidents by crime type, date, and time.
- Allows users to select a location and search radius.
- Display crime incident detail when a marker is selected.
- Retrieve matching crime incident records from the application's database.
  
**Out of Scope:** 
- Tracking live police activity.
- Allowing users to submit crime reports.
- Providing real-time emergency alerts.


## Functional requirements
| ID   | Requirement                                                                                                                                                            | Story |
| ---- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----- |
| FR-1 | When the map page loads, the system shall display an interactive map that users can zoom and pan.                                                                      | #13   |
| FR-2 | When crime incident records with valid geographic coordinates are available, the system shall display their locations as markers on the map.                           | #13   |
| FR-3 | When a user selects an incident marker, the system shall display available incident information, including crime type, date, time, and location description.                                                                                                                                                                    | #13   |
| FR-4 | When a user selects a crime category, the system shall display only incidents matching that category.                                                                  | #21   |
| FR-5 | When a user specifies a date or time range, the system shall display only incidents within that range.                                                                                                                                                                          | #21   |
| FR-6 | When a user selects a geographic location or area, the system shall allow the user to filter incidents by that location.                                               | #21   |
| FR-7 | When a user selects a center point and search radius, the system shall identify incidents located within the specified distance.                                       | #22   |
| FR-8 | When a radius search is applied, the system shall display the search boundary and matching crime incidents on the map.                                                 | #22   |
| FR-9 | When no incidents match the selected filters or radius, the system shall display a message indicating that no matching incidents were found.                           | #21, #22 |


## Non-functional requirements

| ID    | Requirement                                                                                  | Why it matters here                                                  |
| ----- | ----------------------------------------------------------------------------------           | -------------------------------------------------------------------- |
| NFR-1 | The map interface shall provide clearly labeled controls for filtering and radius selection. | Users need to understand how to use the map without technical knowledge.         |
| NFR-2 | The application shall function in a modern desktop web browser. | The application is designed as a browser-based system. |
| NFR-3 | The system shall exclude incidents with missing or invalid geographic coordinates from map markers and radius-search results. | Invalid coordinates could cause incidents to appear in incorrect locations. |
| NFR-4 | The system shall display only information available in the standardized crime records and shall not invent missing values. | Public crime datasets may contain incomplete information. |
| NFR-5 | The system shall use consistent distance units and geographic calculations for radius searches. | Radius results must accurately represent the selected geographic area. |
## Acceptance criteria (epic level)

- [ ] Given a valid crime incident dataset, the application displays an interactive map containing markers for incidents with usable geographic coordinates.
- [ ] When a user zooms or pans the map, the displayed geographic region changes accordingly.
- [ ] When a user selects an incident marker, the application displays the available information for that incident.
- [ ] When a user selects a crime category, only incidents matching that category are displayed.
- [ ] When a user specifies a date or time range, only incidents within the specified range are displayed.
- [ ] When a user selects a location and search radius, the application displays only incidents within that distance.
- [ ] When a radius search is performed, the application visually displays the selected search boundary.
- [ ] When no incidents match the selected filters or radius, the application displays an appropriate message.
- [ ] Incidents with invalid or missing geographic coordinates are excluded from map markers and radius-search results.

## Open Questions

| Question                                                                                    | Owner                   | Needed By                              |
| ------------------------------------------------------------------------------------------- | ----------------------- | -------------------------------------- |

No open questions have been identified at this time.