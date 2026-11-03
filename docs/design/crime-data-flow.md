
# Sprint 2 — Crime Data Flow Diagram (DFD)

> Epic: #3. Stories: #4, #5. Task: #69

This diagram shows the planned flow of public crime data through the Crime-Busters application.

```mermaid
flowchart TD
    A["Public Crime Data Source"]
    B["Python Import Script"]
    C["Validation and Normalization"]
    D[("SQLite Database")]
    E["Flask Backend API"]
    F["Leaflet Map"]
    G["User"]

    A -->|"Crime incident records"| B
    B -->|"Raw imported records"| C
    C -->|"Cleaned incident records"| D

    G -->|"Select location and radius"| F
    F -->|"HTTP request with search criteria"| E
    E -->|"SQL query with filters"| D
    D -->|"Matching crime incidents"| E
    E -->|"JSON response"| F
    F -->|"Map markers and results"| G
```

**Note:** This diagram represents the planned Sprint 2 architecture. Exact API routes, data fields, and filtering implementation should be verified against the application code.
