from whoosh.index import open_dir
from whoosh.qparser import QueryParser
from whoosh import scoring
from flask import current_app, session
from datetime import datetime, timedelta
from app.utils.db import get_db_connection
import os

def index_document(doc_id, file_path, filename):
    ix = open_dir(current_app.config['INDEX_DIR'])
    writer = ix.writer()
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Calculate keyword frequencies
    words = content.lower().split()
    keyword_freq = {}
    for word in words:
        if word.isalnum():
            keyword_freq[word] = keyword_freq.get(word, 0) + 1
    
    writer.add_document(
        doc_id=str(doc_id),
        content=content,
        filename=filename,
        upload_date=datetime.now(),
        user_id=str(session.get('user_id', '0')),
        file_type=os.path.splitext(filename)[1].lower(),
        keyword_freq=str(keyword_freq)  # Store as string for Whoosh
    )
    writer.commit()

    # Store frequencies in DocumentIndex table
    conn = get_db_connection()
    for keyword, freq in keyword_freq.items():
        conn.execute(
            'INSERT INTO DocumentIndex (document_id, keyword, frequency, created_by, updated_by) VALUES (?, ?, ?, ?, ?)',
            (doc_id, keyword, freq, session.get('username', 'System'), session.get('username', 'System'))
        )
    conn.execute(
        'INSERT INTO Logs (table_name, record_id, action, system_remarks, created_by, updated_by) VALUES (?, ?, ?, ?, ?, ?)',
        ('DocumentIndex', doc_id, 'INDEX', f'Document {filename} indexed',
         session.get('username', 'System'), session.get('username', 'System'))
    )
    conn.commit()
    conn.close()

def search_documents(query_str, date_filter=None, type_filter=None):
    ix = open_dir(current_app.config['INDEX_DIR'])
    with ix.searcher(weighting=scoring.BM25F()) as searcher:
        query = QueryParser("content", ix.schema).parse(query_str)
        results = searcher.search(query, limit=20)
        
        filtered_results = []
        now = datetime.now()
        for hit in results:
            upload_date = hit['upload_date']
            file_type = hit.get('file_type', '')
            
            # Apply date filter
            date_match = True
            if date_filter == 'today':
                date_match = upload_date.date() == now.date()
            elif date_filter == 'week':
                date_match = upload_date >= now - timedelta(days=7)
            elif date_filter == 'month':
                date_match = upload_date >= now - timedelta(days=30)
                
            # Apply type filter
            type_match = True
            if type_filter:
                type_match = file_type == type_filter.lower()
                
            if date_match and type_match:
                # Calculate custom score: BM25 + recency boost
                days_old = (now - upload_date).days
                recency_boost = max(1.0, 10.0 / (days_old + 1))  # Newer docs get higher boost
                score = hit.score * recency_boost
                filtered_results.append({
                    'doc_id': hit['doc_id'],
                    'filename': hit['filename'],
                    'snippet': hit.highlights('content'),
                    'score': score
                })
        
        # Sort by custom score
        filtered_results.sort(key=lambda x: x['score'], reverse=True)
        return filtered_results