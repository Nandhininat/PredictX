import sqlite3
import hashlib
from database.database import DB_NAME

def hash_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def register_user(name, email, password):
    conn = sqlite3.connect(DB_NAME)
    try:
        conn.execute("""
            INSERT INTO users (name, email, password, role)
            VALUES (?, ?, ?, 'user')
        """, (name.strip(), email.strip().lower(), hash_password(password)))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def login_user(email, password):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        SELECT id, name, email, role
        FROM users
        WHERE email = ? AND password = ?
    """, (email.strip().lower(), hash_password(password)))
    user = cur.fetchone()
    conn.close()
    return user
