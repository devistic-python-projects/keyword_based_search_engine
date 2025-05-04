from flask import session
from .db import get_db_connection
import sqlite3

def check_spelling(word, user_id=None):
    # Simulate spellcheck with common mistakes
    common_mistakes = {
        'teh': ['the'],
        'recieve': ['receive'],
        'definately': ['definitely'],
        'seperate': ['separate'],
        'occured': ['occurred']
    }
    
    # Check user dictionary
    if user_id:
        conn = get_db_connection()
        custom_word = conn.execute(
            'SELECT word FROM UserDictionary WHERE user_id = ? AND word = ? AND is_deleted = 0',
            (user_id, word.lower())
        ).fetchone()
        conn.close()
        if custom_word:
            return {'is_correct': True, 'suggestions': []}
    
    # Check common mistakes
    if word.lower() in common_mistakes:
        return {'is_correct': False, 'suggestions': common_mistakes[word.lower()]}
    
    # Assume correct if not in common mistakes or dictionary
    return {'is_correct': True, 'suggestions': []}

def add_to_dictionary(word, user_id):
    conn = get_db_connection()
    try:
        conn.execute(
            'INSERT INTO UserDictionary (user_id, word, created_by, updated_by) VALUES (?, ?, ?, ?)',
            (user_id, word.lower(), session.get('username', 'System'), session.get('username', 'System'))
        )
        conn.execute(
            'INSERT INTO Logs (table_name, record_id, action, system_remarks, created_by, updated_by) VALUES (?, last_insert_rowid(), ?, ?, ?, ?)',
            ('UserDictionary', 'ADD', f'Added word {word} to dictionary for user {user_id}',
             session.get('username', 'System'), session.get('username', 'System'))
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()
        