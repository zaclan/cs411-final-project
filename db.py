# weather/db.py
import sqlite3

# Path to the database file
DB_PATH = "db/weather.db"

# Function to create a database connection
def db():
    conn = sqlite3.connect(DB_PATH)
    return conn
