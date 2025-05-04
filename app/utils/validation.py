from flask import current_app
import re
import os

def validate_email(email):
    """Validate email address format."""
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email)

def validate_password(password):
    """Validate password strength."""
    return len(password) >= 8  # example: min length check

def validate_file_extension(filename):
    """Validate file extension for uploads."""
    allowed_extensions = ['.txt', '.csv', '.json', '.xml', '.tsv']
    extension = os.path.splitext(filename)[1]
    return extension in allowed_extensions

def validate_file_extension(filename):
    return os.path.splitext(filename)[1].lower() in current_app.config['SUPPORTED_FORMATS']

def validate_query(query):
    return bool(query and query.strip())