import sqlite3
import os

DB_NAME = os.path.join(os.path.dirname(__file__), "predictx.db")

def get_connection():
    return sqlite3.connect(DB_NAME)

def create_database():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user'
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS machines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            machine_id TEXT UNIQUE NOT NULL,
            machine_name TEXT NOT NULL,
            machine_type TEXT NOT NULL,
            location TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS sensor_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            machine_id TEXT NOT NULL,
            temperature REAL,
            vibration REAL,
            speed REAL,
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            machine_id TEXT NOT NULL,
            health_score INTEGER,
            rul INTEGER,
            alert TEXT,
            recommendation TEXT,
            predicted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS maintenance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            machine_id TEXT NOT NULL,
            maintenance_type TEXT,
            description TEXT,
            maintenance_date TEXT
        )
    """)

    conn.commit()

    # Upgrade older databases if recommendation column is missing.
    cur.execute("PRAGMA table_info(predictions)")
    prediction_columns = [row[1] for row in cur.fetchall()]
    if "recommendation" not in prediction_columns:
        cur.execute(
            "ALTER TABLE predictions ADD COLUMN recommendation TEXT"
        )

    cur.execute("PRAGMA table_info(users)")
    user_columns = [row[1] for row in cur.fetchall()]
    if "role" not in user_columns:
        cur.execute(
            "ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'user'"
        )

    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_database()
    print("PredictX database created successfully!")
