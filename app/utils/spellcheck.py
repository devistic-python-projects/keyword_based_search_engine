from flask import current_app, session
from .db import get_db_connection
import sqlite3
from spellchecker import SpellChecker
import os

# Initialize the spell checker
spell = SpellChecker()

# Common mistakes
common_mistakes = {
    'teh': ['the'],
    'recieve': ['receive'],
    'definately': ['definitely'],
    'seperate': ['separate'],
    'occured': ['occurred']
}

def get_guest_dict_path():
    return current_app.config['GUEST_DICT_PATH']

def check_spelling(word, user_id=None):
    word = word.lower()

    try:
        # --- Check user dictionary from DB ---
        if user_id:
            conn = get_db_connection()
            try:
                custom_word = conn.execute(
                    'SELECT word FROM UserDictionary WHERE user_id = ? AND word = ? AND is_deleted = 0',
                    (user_id, word)
                ).fetchone()
                if custom_word:
                    return {'is_correct': True, 'suggestions': []}
            except Exception as db_error:
                print(f"[DB Error] While checking custom dictionary: {db_error}")
            finally:
                conn.close()
        else:
            # --- Check guest dictionary file ---
            guest_dict_path = get_guest_dict_path()
            if os.path.exists(guest_dict_path):
                try:
                    with open(guest_dict_path, 'r') as f:
                        guest_words = {line.strip().lower() for line in f}
                    if word in guest_words:
                        return {'is_correct': True, 'suggestions': []}
                except Exception as file_error:
                    print(f"[File Error] While reading guest dictionary: {file_error}")
    except Exception as outer_error:
        print(f"[Unexpected Error] in check_spelling: {outer_error}")

    try:
        # --- Check base spellchecker ---
        if word in spell:
            return {'is_correct': True, 'suggestions': []}

        # --- Check common mistakes ---
        if word in common_mistakes:
            suggestions = [s.title() for s in common_mistakes[word]]
            return {'is_correct': False, 'suggestions': suggestions}

        # --- Fallback suggestions ---
        suggestions = [s.title() for s in spell.candidates(word)]
        return {'is_correct': False, 'suggestions': suggestions}
    except Exception as spell_error:
        print(f"[SpellChecker Error]: {spell_error}")
        return {'is_correct': False, 'suggestions': []}

def add_to_dictionary(word, user_id):
    if user_id:
        conn = get_db_connection()
        try:
            conn.execute(
                'INSERT INTO UserDictionary (user_id, word, created_by, updated_by) VALUES (?, ?, ?, ?)',
                (user_id, word.lower(), session.get('email', 'System'), session.get('email', 'System'))
            )
            conn.execute(
                'INSERT INTO Logs (table_name, record_id, action, system_remarks, created_by, updated_by) VALUES (?, last_insert_rowid(), ?, ?, ?, ?)',
                ('UserDictionary', 'ADD', f'Added word {word} to dictionary for user {user_id}',
                session.get('email', 'System'), session.get('email', 'System'))
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    else:
        # Guest: Add to file
        guest_dict_path = get_guest_dict_path()
        os.makedirs(os.path.dirname(guest_dict_path), exist_ok=True)
        if os.path.exists(guest_dict_path):
            with open(guest_dict_path, 'r') as f:
                guest_words = {line.strip().lower() for line in f}
        else:
            guest_words = set()

        if word not in guest_words:
            with open(guest_dict_path, 'a') as f:
                f.write(word + '\n')
