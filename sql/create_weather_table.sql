DROP TABLE IF EXISTS weather;
CREATE TABLE weather (
    city TEXT PRIMARY KEY,
    lat REAL NOT NULL,
    lon REAL NOT NULL,
    elevation REAL NOT NULL,
    timezone TEXT NOT NULL,
    utc_offset_seconds INTEGER NOT NULL,
    time TEXT NOT NULL,        
    temperature REAL NOT NULL,
    humidity REAL NOT NULL,
    windspeed REAL NOT NULL,
    precipitation REAL NOT NULL
);
