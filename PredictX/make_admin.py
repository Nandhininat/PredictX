import sqlite3
from database.database import DB_NAME, create_database

create_database()
email = input("Enter registered user email: ").strip().lower()

conn = sqlite3.connect(DB_NAME)
cur = conn.cursor()
cur.execute("UPDATE users SET role='admin' WHERE email=?", (email,))
conn.commit()

if cur.rowcount:
    print("Admin role updated successfully!")
else:
    print("User email not found. Register the user first.")

conn.close()
