DROP TABLE IF EXISTS weather;
CREATE TABLE weather (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    meal TEXT NOT NULL UNIQUE,
    cuisine TEXT NOT NULL,
    price REAL NOT NULL,
    difficulty TEXT CHECK(difficulty IN ('HIGH', 'MED', 'LOW')),
    battles INTEGER DEFAULT 0,
    wins INTEGER DEFAULT 0,
    deleted BOOLEAN DEFAULT FALSE
);
