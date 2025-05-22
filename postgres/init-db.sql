-- Enable PostGIS extension
CREATE EXTENSION postgis;

-- Create geofences table
CREATE TABLE geofences (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    area GEOMETRY(POLYGON, 4326) NOT NULL
);

-- Insert sample geofences
-- Downtown area (rectangular polygon)
INSERT INTO geofences (name, area) VALUES (
    'Downtown',
    ST_GeomFromText('POLYGON((-74.006 40.712, -74.006 40.722, -73.996 40.722, -73.996 40.712, -74.006 40.712))', 4326)
);

-- Warehouse District (rectangular polygon)
INSERT INTO geofences (name, area) VALUES (
    'Warehouse District',
    ST_GeomFromText('POLYGON((-74.016 40.702, -74.016 40.712, -74.006 40.712, -74.006 40.702, -74.016 40.702))', 4326)
);

-- Industrial Zone (rectangular polygon)
INSERT INTO geofences (name, area) VALUES (
    'Industrial Zone',
    ST_GeomFromText('POLYGON((-73.986 40.692, -73.986 40.702, -73.976 40.702, -73.976 40.692, -73.986 40.692))', 4326)
);

-- Create index for spatial queries
CREATE INDEX idx_geofences_area ON geofences USING GIST (area); 