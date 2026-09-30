import sqlite3
from database.database import DB_NAME

machines = [
    ("M001", "Motor 1", "Electric Motor", "Plant A"),
    ("M002", "Motor 2", "Electric Motor", "Plant A"),
    ("M003", "Pump 1", "Water Pump", "Plant B"),
    ("M004", "Pump 2", "Water Pump", "Plant B"),
    ("M005", "Compressor 1", "Compressor", "Plant C"),
    ("M006", "Motor 3", "Electric Motor", "Plant A"),
    ("M007", "Pump 3", "Water Pump", "Plant B"),
    ("M008", "Compressor 2", "Compressor", "Plant C"),
]

conn = sqlite3.connect(DB_NAME)

for machine in machines:
    try:
        conn.execute("""
            INSERT INTO machines
            (machine_id, machine_name, machine_type, location)
            VALUES (?, ?, ?, ?)
        """, machine)
    except sqlite3.IntegrityError:
        pass

conn.commit()
conn.close()
print("Machines inserted successfully!")
