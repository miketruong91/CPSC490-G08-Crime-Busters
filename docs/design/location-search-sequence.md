
# Sprint 2 — Location Search UML Sequence Diagram
> Epic: #3. Stories: #4, #5. Task: #70
This diagram illustrates the planned interaction when a user searches for crime incidents near a selected location.

```mermaid
sequenceDiagram
    actor User
    participant Map as Leaflet Map / Browser
    participant API as Flask API
    participant DB as SQLite Database

    User->>Map: Select location and search radius
    Map->>Map: Read coordinates and radius
    Map->>API: HTTP request (latitude, longitude, radius)
    API->>API: Validate search parameters
    API->>DB: Query incidents matching location and radius
    DB-->>API: Return matching incident records
    API-->>Map: JSON response with incident data
    Map->>Map: Update map markers and results
    Map-->>User: Display nearby crime incidents

    opt No matching incidents
        Map-->>User: Display no results message
    end

    opt Invalid search parameters
        API-->>Map: Return validation error
        Map-->>User: Display error message
    end
```

**Note:** This is the planned interaction. Exact Flask endpoints, geographic filtering logic, and error handling should be verified against the implemented backend.
