# from flask import render_template, request, redirect, url_for, flash, jsonify
# from app import app
# from app.forms.login_form import LoginForm
# from app.forms.signup_form import SignupForm
# from app.forms.upload_form import UploadForm
# from app.utils.db import execute_query, fetch_one, fetch_all
# from app.utils.indexing import add_to_index
# from app.utils.spellcheck import check_spelling, add_to_custom_dict
# from app.utils.indexing import search_documents
# from datetime import datetime
# import os

# @app.route('/')
# def index():
#     """Render the home page with a search form."""
#     return render_template('index.html')

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     """Handle login form submission."""
#     form = LoginForm()
#     if form.validate_on_submit():
#         email = form.email.data
#         password = form.password.data
#         # Check if email and password match (database query)
#         user = fetch_one("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))
#         if user:
#             # Successful login
#             return redirect(url_for('dashboard'))
#         else:
#             flash('Invalid credentials', 'danger')
#     return render_template('login.html', form=form)

# @app.route('/signup', methods=['GET', 'POST'])
# def signup():
#     """Handle signup form submission."""
#     form = SignupForm()
#     if form.validate_on_submit():
#         email = form.email.data
#         email = form.email.data
#         password = form.password.data
#         # Add user to the database (ensure user doesn't already exist)
#         execute_query("INSERT INTO users (email, email, password) VALUES (?, ?, ?)", (email, email, password))
#         flash('Account created successfully!', 'success')
#         return redirect(url_for('login'))
#     return render_template('signup.html', form=form)

# @app.route('/upload', methods=['GET', 'POST'])
# def upload_document():
#     """Handle document upload."""
#     form = UploadForm()
#     if form.validate_on_submit():
#         document = form.document.data
#         filename = document.filename
#         filepath = os.path.join('uploads', filename)
#         document.save(filepath)

#         # Add the document to the index
#         upload_date = datetime.now()
#         add_to_index(filename, document.read().decode(), upload_date)

#         flash('Document uploaded and indexed successfully!', 'success')
#         return redirect(url_for('index'))
#     return render_template('upload.html', form=form)

# @app.route('/search', methods=['GET'])
# def search():
#     """Handle search queries."""
#     query_string = request.args.get('query')
#     date_filter = request.args.get('date_filter')  # e.g., 'today', 'week', 'month'
#     type_filter = request.args.get('type_filter')  # e.g., '.txt', '.csv'
    
#     if query_string:
#         results = search_documents(query_string, date_filter=date_filter, type_filter=type_filter)
#         return render_template('search_results.html', query=query_string, results=results)
#     return redirect(url_for('index'))

# @app.route('/spellcheck', methods=['POST'])
# def spellcheck():
#     """Handle spell check for a given text."""
#     text = request.form.get('text')
#     suggestions = check_spelling(text)
#     return jsonify(suggestions)

# @app.route('/add_custom_word', methods=['POST'])
# def add_custom_word():
#     """Add a custom word to the spell checker."""
#     word = request.form.get('word')
#     add_to_custom_dict(word)
#     return jsonify({'message': 'Word added to dictionary.'})
