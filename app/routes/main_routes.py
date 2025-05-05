from flask import Blueprint, render_template, request, redirect, url_for, flash, session, send_file, jsonify
from app.utils.db import get_db_connection
from app.utils.indexing import index_document, search_documents
from app.utils.spellcheck import check_spelling, add_to_dictionary
from werkzeug.utils import secure_filename
from app.forms.upload_form import UploadForm
import os
from flask import current_app
import uuid
from datetime import datetime

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    return render_template('home.html')

@main_bp.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        query = request.form.get('query')
        date_filter = request.form.get('date_filter')
        type_filter = request.form.get('type_filter')
        
        if not query:
            flash('Please enter a search query.', 'error')
            return redirect(url_for('main.home'))
        
        # Perform search
        results = search_documents(query, date_filter, type_filter)
        
        # Save search record
        conn = get_db_connection()
        search_id = conn.execute(
            'INSERT INTO Search (query, user_id, created_by, updated_by) VALUES (?, ?, ?, ?)',
            (query, session.get('user_id'), session.get('username', 'System'), session.get('username', 'System'))
        ).lastrowid
        
        # Save search results
        for result in results:
            conn.execute(
                'INSERT INTO SearchResult (search_id, document_id, relevance_score, snippet, created_by, updated_by) VALUES (?, ?, ?, ?, ?, ?)',
                (search_id, result['doc_id'], result['score'], result['snippet'], session.get('username', 'System'), session.get('username', 'System'))
            )
        
        # Log search action
        conn.execute(
            'INSERT INTO Logs (table_name, record_id, action, system_remarks, created_by, updated_by) VALUES (?, ?, ?, ?, ?, ?)',
            ('Search', search_id, 'SEARCH', f'Search performed for query: {query}',
             session.get('username', 'System'), session.get('username', 'System'))
        )
        
        conn.commit()
        conn.close()
        
        return render_template('results.html', results=results, query=query)
    
    return redirect(url_for('main.home'))

def search_documents(query, date_filter=None, type_filter=None):
    query = query.lower().strip()
    
    # Split query into words and allow any word, even single characters
    keywords = [word for word in query.split() if word]  # Remove empty strings
    
    if not keywords:
        return []

    # Allow partial matches by searching for keywords in both document content and filename
    placeholders = ','.join(['?'] * len(keywords))

    # Combined query for DocumentIndex and Document tables
    sql = f'''
        SELECT d.id as doc_id, d.filename, d.file_path,
               COALESCE(SUM(di.frequency), 0) as score
        FROM Document d
        LEFT JOIN DocumentIndex di
            ON di.document_id = d.id
            AND di.keyword IN ({placeholders})
        WHERE LOWER(d.filename) LIKE ?
    '''

    params = keywords + [f"%{query}%"]  # Add the query as a pattern for filename matching

    if date_filter:
        sql += " AND date(d.created_at) = ?"
        params.append(date_filter)

    if type_filter:
        sql += " AND LOWER(d.file_path) LIKE ?"
        params.append(f"%{type_filter.lower()}")

    sql += '''
        GROUP BY d.id
        ORDER BY score DESC
    '''

    try:
        with get_db_connection() as conn:
            rows = conn.execute(sql, params).fetchall()
            results = []

            # Process and return results
            for row in rows:
                snippet = f"Matched file: {row['filename']}"
                results.append({
                    'doc_id': row['doc_id'],
                    'filename': row['filename'],  # Include filename in results
                    'score': row['score'],
                    'snippet': snippet
                })

    except Exception as e:
        return []

    return results

@main_bp.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'user_id' not in session:
        flash('Please log in to upload documents.', 'error')
        return redirect(url_for('auth.login'))

    form = UploadForm()
    if form.validate_on_submit():
        files = request.files.getlist('files')
        if not files:
            flash('No files uploaded.', 'error')
            return render_template('upload.html', form=form)

        with get_db_connection() as conn:
            for file in files:
                if file and os.path.splitext(file.filename)[1].lower() in current_app.config['SUPPORTED_FORMATS']:
                    original_filename = secure_filename(file.filename)
                    filename = f"{uuid.uuid4()}_{original_filename}"
                    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

                    file.save(file_path)

                    # Save to Document table
                    doc_id = conn.execute(
                        'INSERT INTO Document (user_id, filename, file_path, created_by, updated_by) VALUES (?, ?, ?, ?, ?)',
                        (session['user_id'], original_filename, file_path, session['email'], session['email'])
                    ).lastrowid

                    # Notification
                    notification_id = conn.execute(
                        'INSERT INTO Notification (message, type, created_by, updated_by) VALUES (?, ?, ?, ?)',
                        (f'Document {original_filename} uploaded successfully.', 'success', session['email'], session['email'])
                    ).lastrowid

                    # Notification Receiver
                    conn.execute(
                        'INSERT INTO NotificationReceiver (notification_id, user_id, created_by, updated_by) VALUES (?, ?, ?, ?)',
                        (notification_id, session['user_id'], session['email'], session['email'])
                    )

                    # Logging
                    conn.execute(
                        'INSERT INTO Logs (table_name, record_id, action, system_remarks, created_by, updated_by) VALUES (?, ?, ?, ?, ?, ?)',
                        ('Document', doc_id, 'UPLOAD', f'Document {original_filename} uploaded by user {session["email"]}',
                         session['email'], session['email'])
                    )

                    conn.commit()
                    
                    # Index the document (uses separate connection)
                    index_document(doc_id, file_path, original_filename)
                else:
                    flash(f'Invalid file format for {file.filename}.', 'error')

        flash('Documents uploaded successfully.', 'success')
        return redirect(url_for('main.home'))

    return render_template('upload.html', form=form)

@main_bp.route('/download/<doc_id>')
def download(doc_id):
    conn = get_db_connection()
    doc = conn.execute(
        'SELECT file_path, filename FROM Document WHERE id = ? AND is_deleted = 0',
        (doc_id,)
    ).fetchone()
    conn.close()
    if doc:
        conn = get_db_connection()
        conn.execute(
            'INSERT INTO Logs (table_name, record_id, action, system_remarks, created_by, updated_by) VALUES (?, ?, ?, ?, ?, ?)',
            ('Document', doc_id, 'DOWNLOAD', f'Document {doc["filename"]} downloaded',
             session.get('email', 'System'), session.get('email', 'System'))
        )
        conn.commit()
        conn.close()
        return send_file(doc['file_path'], download_name=doc['filename'], as_attachment=True)
    flash('Document not found.', 'error')
    return redirect(url_for('main.home'))

@main_bp.route('/preview/<doc_id>')
def preview(doc_id):
    conn = get_db_connection()
    doc = conn.execute(
        'SELECT file_path, filename FROM Document WHERE id = ? AND is_deleted = 0',
        (doc_id,)
    ).fetchone()
    conn.close()
    if doc:
        try:
            with open(doc['file_path'], 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()[:1000]  # Limit to first 1000 characters
            conn = get_db_connection()
            conn.execute(
                'INSERT INTO Logs (table_name, record_id, action, system_remarks, created_by, updated_by) VALUES (?, ?, ?, ?, ?, ?)',
                ('Document', doc_id, 'PREVIEW', f'Document {doc["filename"]} previewed',
                 session.get('email', 'System'), session.get('email', 'System'))
            )
            conn.commit()
            conn.close()
            return jsonify({'filename': doc['filename'], 'content': content})
        except Exception as e:
            return jsonify({'error': 'Unable to preview document.'}), 500
    return jsonify({'error': 'Document not found.'}), 404

@main_bp.route('/spellcheck', methods=['POST'])
def spellcheck():
    data = request.get_json()
    word = data.get('word')
    if not word:
        return jsonify({'error': 'No word provided.'}), 400
    result = check_spelling(word, session.get('user_id'))
    return jsonify(result)

@main_bp.route('/add-to-dictionary', methods=['POST'])
def add_to_dict_route():
    data = request.get_json()
    word = data.get('word', '').strip().lower()
    user_id = session.get('user_id')
    
    if not word:
        return jsonify({'status': 'error', 'message': 'No word provided'}), 400

    add_to_dictionary(word, user_id)
    return jsonify({'status': 'success'})

@main_bp.route('/notifications')
def notifications():
    if 'user_id' not in session:
        flash('Please log in to view notifications.', 'error')
        return redirect(url_for('auth.login'))
    conn = get_db_connection()
    notifications = conn.execute(
        'SELECT n.*, nr.is_read FROM Notification n JOIN NotificationReceiver nr ON n.id = nr.notification_id '
        'WHERE nr.user_id = ? AND n.is_deleted = 0 AND nr.is_deleted = 0 ORDER BY n.created_date DESC',
        (session['user_id'],)
    ).fetchall()
    conn.close()
    return render_template('notifications.html', notifications=notifications)

@main_bp.route('/profile')
def profile():
    if 'user_id' not in session:
        flash('Please log in to view your profile.', 'error')
        return redirect(url_for('auth.login'))
    conn = get_db_connection()
    documents = conn.execute(
        'SELECT id, filename, upload_date FROM Document WHERE user_id = ? AND is_deleted = 0 ORDER BY upload_date DESC',
        (session['user_id'],)
    ).fetchall()
    dictionary = conn.execute(
        'SELECT id, word, created_date FROM UserDictionary WHERE user_id = ? AND is_deleted = 0 ORDER BY created_date DESC',
        (session['user_id'],)
    ).fetchall()
    conn.close()
    return render_template('profile.html', documents=documents, dictionary=dictionary)

@main_bp.route('/profile/delete_word/<int:word_id>', methods=['POST'])
def delete_word(word_id):
    if 'user_id' not in session:
        flash('Please log in to perform this action.', 'error')
        return redirect(url_for('auth.login'))
    conn = get_db_connection()
    conn.execute(
        'UPDATE UserDictionary SET is_deleted = 1, updated_by = ?, updated_date = CURRENT_TIMESTAMP WHERE id = ? AND user_id = ?',
        (session['email'], word_id, session['user_id'])
    )
    conn.execute(
        'INSERT INTO Logs (table_name, record_id, action, system_remarks, created_by, updated_by) VALUES (?, ?, ?, ?, ?, ?)',
        ('UserDictionary', word_id, 'DELETE', f'Word {word_id} deleted from dictionary',
         session['email'], session['email'])
    )
    conn.commit()
    conn.close()
    flash('Word deleted successfully.', 'success')
    return redirect(url_for('main.profile'))

@main_bp.route('/faq')
def faq():
    return render_template('faq.html')

@main_bp.route('/about')
def about():
    return render_template('about.html')