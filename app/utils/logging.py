from flask import session
from .db import get_db_connection
import time

def log_action(table_name, record_id, action, remarks, error_code=None, request_time=None):
    conn = get_db_connection()
    try:
        conn.execute(
            'INSERT INTO Logs (table_name, record_id, action, system_remarks, error_code, request_time, created_by, updated_by) '
            'VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
            (table_name, record_id, action, remarks, error_code, request_time,
             session.get('username', 'System'), session.get('username', 'System'))
        )
        conn.commit()
    finally:
        conn.close()