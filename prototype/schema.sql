-- Crime Busters: initial SQLite schema (Task #32, Story #28, Epic #3)
-- Implements version 1 of docs/crime-data-format.md.
-- Run with foreign keys enabled on every connection:  PRAGMA foreign_keys = ON;

PRAGMA foreign_keys = ON;

-- One row per standardized source record.
CREATE TABLE IF NOT EXISTS incidents (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Identity: (source, source_record_id) identifies a repeated source record.
    source              TEXT NOT NULL CHECK (length(trim(source)) > 0),
    source_record_id    TEXT NOT NULL CHECK (length(trim(source_record_id)) > 0),

    record_kind         TEXT NOT NULL
                        CHECK (record_kind IN ('call_for_service', 'crime_incident', 'unknown')),
    crime_type          TEXT
                        CHECK (crime_type IS NULL OR crime_type IN
                               ('burglary', 'theft', 'vandalism', 'assault', 'other')),

    -- Original source values, preserved as supplied.
    source_code         TEXT,
    description         TEXT,
    location            TEXT,
    city                TEXT,
    agency              TEXT,
    disposition         TEXT,

    -- Dates and times: ISO text so SQLite's date()/time() can validate them.
    -- "IS" (not "=") so that a malformed value, where date()/time() return
    -- NULL, fails the check instead of passing as NULL.
    incident_date       TEXT CHECK (incident_date IS NULL OR date(incident_date) IS incident_date),
    incident_time       TEXT CHECK (incident_time IS NULL OR time(incident_time) IS incident_time),
    timezone            TEXT,

    -- Coordinates (EPSG:4326). Both present and in range, or both NULL.
    -- Missing coordinates are NULL, never 0.
    latitude            REAL CHECK (latitude  IS NULL OR latitude  BETWEEN  -90 AND  90),
    longitude           REAL CHECK (longitude IS NULL OR longitude BETWEEN -180 AND 180),
    location_precision  TEXT NOT NULL
                        CHECK (location_precision IN ('exact', 'block', 'approximate', 'unknown')),

    CHECK ((latitude IS NULL) = (longitude IS NULL)),

    -- A repeated source record must not be silently inserted twice. A loader
    -- that sees a conflict should flag it for review, not overwrite.
    UNIQUE (source, source_record_id)
);

-- Zero or more quality flags per incident (the format's quality_flags array).
-- Kept as a child table so records can be queried by flag.
CREATE TABLE IF NOT EXISTS incident_quality_flags (
    incident_id INTEGER NOT NULL REFERENCES incidents(id) ON DELETE CASCADE,
    flag        TEXT    NOT NULL CHECK (length(trim(flag)) > 0),
    PRIMARY KEY (incident_id, flag)
);

-- Supports the radius search: bounding-box filter first, exact distance in Python.
CREATE INDEX IF NOT EXISTS idx_incidents_coords ON incidents (latitude, longitude);
-- Supports the date and crime-type filters.
CREATE INDEX IF NOT EXISTS idx_incidents_date   ON incidents (incident_date);
CREATE INDEX IF NOT EXISTS idx_incidents_type   ON incidents (crime_type);
-- Supports finding records by flag.
CREATE INDEX IF NOT EXISTS idx_flags_flag       ON incident_quality_flags (flag);
