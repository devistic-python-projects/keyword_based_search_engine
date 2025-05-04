import sqlite3
import os
from flask import current_app

def get_db_connection():
    conn = sqlite3.connect(current_app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path=None):
    if db_path is None:
        db_path = current_app.config['DATABASE']
    
    # Ensure the database directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    db_exists = os.path.exists(db_path)

    if db_exists:
        # Check if 'User' table already exists
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='User'")
        table_exists = cursor.fetchone() is not None
        conn.close()

        if table_exists:
            print("Database and 'User' table already exist. Skipping initialization.")
            return  # Exit early; DB already initialized

    # If DB doesn't exist or 'User' table is missing, initialize
    conn = sqlite3.connect(db_path)
    try:
        schema_path = os.path.join('database', 'schema.sql')
        with open(schema_path) as f:
            conn.executescript(f.read())
        conn.commit()
        print("Database initialized successfully.")
    finally:
        conn.close()
