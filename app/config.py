import os
from whoosh.fields import Schema, TEXT, ID, DATETIME, KEYWORD

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'lHhl0R0iH7')
    SESSION_TYPE = 'filesystem'
    
    # Use absolute paths based on project root
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, '..', 'uploads')
    INDEX_DIR = os.path.join(BASE_DIR, '..', 'indexes')
    LOGS_DIR = os.path.join(BASE_DIR, '..', 'logs')
    DATABASE = os.path.join(BASE_DIR, '..', 'database', 'search_engine.db')
    GUEST_DICT_PATH = os.path.join(BASE_DIR, '..', 'instance', 'guest_dictionary.txt')
    
    # Supported document formats
    SUPPORTED_FORMATS = {'.txt', '.csv', '.json', '.xml', '.tsv'}
    
    # Whoosh schema
    WHOOSH_SCHEMA = Schema(
        doc_id=ID(stored=True, unique=True),
        content=TEXT(stored=True),
        filename=TEXT(stored=True),
        upload_date=DATETIME(stored=True),
        user_id=ID(stored=True),
        file_type=KEYWORD(stored=True),
        keyword_freq=TEXT(stored=True)
    )
    
    # Error messages
    ERROR_MESSAGES = {
        'invalid_credentials': 'Invalid username or password.',
        'user_exists': 'Username or email already exists.',
        'invalid_file_format': 'Unsupported file format. Supported formats: txt, csv, json, xml, tsv.',
        'no_file_uploaded': 'No file uploaded.',
        'login_required': 'Please log in to access this feature.',
        'upload_failed': 'Failed to upload file. Please try again.',
        'search_empty': 'Please enter a search query.',
        'spellcheck_failed': 'Spellcheck service unavailable.',
        'db_error': 'Database error occurred. Please try again later.'
    }