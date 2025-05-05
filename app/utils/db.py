import sqlite3
import os
from flask import current_app
from datetime import datetime
from werkzeug.security import generate_password_hash

def get_db_connection():
    conn = sqlite3.connect(current_app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path=None):
    if db_path is None:
        db_path = current_app.config['DATABASE']
    
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    db_exists = os.path.exists(db_path)

    if db_exists:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='User'")
        table_exists = cursor.fetchone() is not None
        conn.close()

        if table_exists:
            print("Database and 'User' table already exist. Skipping initialization.")
            return

    conn = sqlite3.connect(db_path)
    try:
        schema_path = os.path.join('database', 'schema.sql')
        with open(schema_path) as f:
            conn.executescript(f.read())

        # Check if an admin already exists
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Admin WHERE is_deleted = 0")
        admin_count = cursor.fetchone()[0]

        if admin_count > 0:
            print("Admin already exists. Skipping admin insertion.")
        else:
            now = datetime.utcnow().isoformat()
            password_hash = generate_password_hash('admin123')
            conn.execute('''
                INSERT INTO Admin (
                    username, email, password_hash,
                    created_date, updated_date,
                    created_by, updated_by, is_deleted
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                'Admin',
                'admin@gmail.com',
                password_hash,
                now, now,
                'system', 'system', 0
            ))
            print("Default admin inserted.")

        conn.commit()
        print("✅ Database initialized successfully.")
    finally:
        conn.close()
