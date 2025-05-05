from flask import Blueprint, render_template, request, redirect, url_for, flash, session, Response
from app.utils.db import get_db_connection
from app.utils.decorators import admin_required
from app.utils.logging import log_action
import csv
from io import StringIO
from datetime import datetime

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    conn = get_db_connection()
    user_count = conn.execute('SELECT COUNT(*) FROM User WHERE is_deleted = 0').fetchone()[0]
    doc_count = conn.execute('SELECT COUNT(*) FROM Document WHERE is_deleted = 0').fetchone()[0]
    search_count = conn.execute('SELECT COUNT(*) FROM Search WHERE is_deleted = 0').fetchone()[0]
    notification_count = conn.execute('SELECT COUNT(*) FROM Notification WHERE is_deleted = 0').fetchone()[0]
    conn.close()
    log_action('Admin', session['user_id'], 'VIEW_DASHBOARD', 'Admin viewed dashboard')
    return render_template('admin/dashboard.html', 
                         user_count=user_count, 
                         doc_count=doc_count, 
                         search_count=search_count, 
                         notification_count=notification_count)

@admin_bp.route('/users')
@admin_required
def users():
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM User WHERE is_deleted = 0').fetchall()
    conn.close()
    log_action('Admin', session['user_id'], 'VIEW_USERS', 'Admin viewed users list')
    return render_template('admin/users.html', users=users)

@admin_bp.route('/users/delete/<int:user_id>', methods=['POST'])
@admin_required
def delete_user(user_id):
    conn = get_db_connection()
    conn.execute('UPDATE User SET is_deleted = 1, updated_by = ?, updated_date = CURRENT_TIMESTAMP WHERE id = ?',
                (session['email'], user_id))
    conn.commit()
    conn.close()
    flash('User deleted successfully.', 'success')
    log_action('User', user_id, 'DELETE', f'User {user_id} deleted by admin {session["email"]}')
    return redirect(url_for('admin.users'))

@admin_bp.route('/logs')
@admin_required
def logs():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    table_filter = request.args.get('table_filter', '')
    action_filter = request.args.get('action_filter', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    
    conn = get_db_connection()
    query = 'SELECT * FROM Logs WHERE is_deleted = 0'
    params = []
    
    if table_filter:
        query += ' AND table_name = ?'
        params.append(table_filter)
    if action_filter:
        query += ' AND action = ?'
        params.append(action_filter)
    if date_from:
        query += ' AND created_date >= ?'
        params.append(date_from)
    if date_to:
        query += ' AND created_date <= ?'
        params.append(date_to + ' 23:59:59')
    
    query += ' ORDER BY created_date DESC LIMIT ? OFFSET ?'
    params.extend([per_page, (page - 1) * per_page])
    
    logs = conn.execute(query, params).fetchall()
    total_logs = conn.execute('SELECT COUNT(*) FROM Logs WHERE is_deleted = 0').fetchone()[0]
    conn.close()
    
    total_pages = (total_logs + per_page - 1) // per_page
    log_action('Admin', session['user_id'], 'VIEW_LOGS', f'Admin viewed logs (page {page})')
    
    return render_template('admin/logs.html', logs=logs, page=page, total_pages=total_pages,
                         table_filter=table_filter, action_filter=action_filter,
                         date_from=date_from, date_to=date_to)

@admin_bp.route('/logs/export')
@admin_required
def export_logs():
    table_filter = request.args.get('table_filter', '')
    action_filter = request.args.get('action_filter', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    
    conn = get_db_connection()
    query = 'SELECT * FROM Logs WHERE is_deleted = 0'
    params = []
    
    if table_filter:
        query += ' AND table_name = ?'
        params.append(table_filter)
    if action_filter:
        query += ' AND action = ?'
        params.append(action_filter)
    if date_from:
        query += ' AND created_date >= ?'
        params.append(date_from)
    if date_to:
        query += ' AND created_date <= ?'
        params.append(date_to + ' 23:59:59')
    
    logs = conn.execute(query, params).fetchall()
    conn.close()
    
    si = StringIO()
    writer = csv.writer(si)
    writer.writerow(['ID', 'Table', 'Record ID', 'Action', 'Remarks', 'Error Code', 'Request Time', 'Created Date', 'Created By'])
    for log in logs:
        writer.writerow([
            log['id'], log['table_name'], log['record_id'], log['action'], log['system_remarks'],
            log['error_code'], log['request_time'], log['created_date'], log['created_by']
        ])
    
    log_action('Admin', session['user_id'], 'EXPORT_LOGS', 'Admin exported logs to CSV')
    
    return Response(
        si.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment;filename=logs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'}
    )

@admin_bp.route('/reports')
@admin_required
def reports():
    conn = get_db_connection()
    
    # Action counts
    action_counts = conn.execute(
        'SELECT action, COUNT(*) as count FROM Logs WHERE is_deleted = 0 GROUP BY action'
    ).fetchall()
    
    # Error counts
    error_counts = conn.execute(
        'SELECT error_code, COUNT(*) as count FROM Logs WHERE error_code IS NOT NULL AND is_deleted = 0 GROUP BY error_code'
    ).fetchall()
    
    # Average request time
    avg_request_time = conn.execute(
        'SELECT AVG(request_time) as avg_time FROM Logs WHERE request_time IS NOT NULL AND is_deleted = 0'
    ).fetchone()['avg_time'] or 0
    
    # Top users by activity
    top_users = conn.execute(
        'SELECT created_by, COUNT(*) as count FROM Logs WHERE is_deleted = 0 GROUP BY created_by ORDER BY count DESC LIMIT 5'
    ).fetchall()
    
    # Users for timeline report
    users = conn.execute('SELECT email FROM User WHERE is_deleted = 0').fetchall()
    
    conn.close()
    
    log_action('Admin', session['user_id'], 'VIEW_REPORTS', 'Admin viewed log reports')
    
    return render_template('admin/reports.html', 
                         action_counts=action_counts, 
                         error_counts=error_counts, 
                         avg_request_time=avg_request_time, 
                         top_users=top_users,
                         users=users)

@admin_bp.route('/reports/timeline')
@admin_required
def timeline():
    page = request.args.get('page', 1, type=int)
    per_page = 50
    user_filter = request.args.get('user_filter', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    
    conn = get_db_connection()
    query = 'SELECT * FROM Logs WHERE is_deleted = 0'
    params = []
    
    if user_filter:
        query += ' AND created_by = ?'
        params.append(user_filter)
    if date_from:
        query += ' AND created_date >= ?'
        params.append(date_from)
    if date_to:
        query += ' AND created_date <= ?'
        params.append(date_to + ' 23:59:59')
    
    query += ' ORDER BY created_date DESC LIMIT ? OFFSET ?'
    params.extend([per_page, (page - 1) * per_page])
    
    activities = conn.execute(query, params).fetchall()
    
    # Action breakdown
    action_breakdown = conn.execute(
        'SELECT action, COUNT(*) as count FROM Logs WHERE is_deleted = 0' +
        (' AND created_by = ?' if user_filter else '') +
        (' AND created_date >= ?' if date_from else '') +
        (' AND created_date <= ?' if date_to else '') +
        ' GROUP BY action',
        [p for p in [user_filter, date_from, date_to + ' 23:59:59' if date_to else None] if p]
    ).fetchall()
    
    total_activities = conn.execute(
        'SELECT COUNT(*) FROM Logs WHERE is_deleted = 0' +
        (' AND created_by = ?' if user_filter else '') +
        (' AND created_date >= ?' if date_from else '') +
        (' AND created_date <= ?' if date_to else ''),
        [p for p in [user_filter, date_from, date_to + ' 23:59:59' if date_to else None] if p]
    ).fetchone()[0]
    
    users = conn.execute('SELECT email FROM User WHERE is_deleted = 0').fetchall()
    conn.close()
    
    total_pages = (total_activities + per_page - 1) // per_page
    log_action('Admin', session['user_id'], 'VIEW_TIMELINE', f'Admin viewed user activity timeline for {user_filter or "all users"} (page {page})')
    
    # Prepare data for Chart.js
    timeline_data = [
        {
            'date': str(activity['created_date']),
            'action': activity['action'],
            'remarks': activity['system_remarks'],
            'table': activity['table_name'],
            'record_id': activity['record_id']
        } for activity in activities
    ]
    
    return render_template('admin/timeline.html', 
                         activities=activities, 
                         timeline_data=timeline_data,
                         action_breakdown=action_breakdown,
                         page=page, 
                         total_pages=total_pages,
                         user_filter=user_filter, 
                         date_from=date_from, 
                         date_to=date_to, 
                         users=users)

@admin_bp.route('/reports/timeline/export')
@admin_required
def export_timeline():
    user_filter = request.args.get('user_filter', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    
    conn = get_db_connection()
    query = 'SELECT * FROM Logs WHERE is_deleted = 0'
    params = []
    
    if user_filter:
        query += ' AND created_by = ?'
        params.append(user_filter)
    if date_from:
        query += ' AND created_date >= ?'
        params.append(date_from)
    if date_to:
        query += ' AND created_date <= ?'
        params.append(date_to + ' 23:59:59')
    
    activities = conn.execute(query, params).fetchall()
    conn.close()
    
    si = StringIO()
    writer = csv.writer(si)
    writer.writerow(['Date', 'User', 'Action', 'Table', 'Record ID', 'Remarks', 'Error Code', 'Request Time'])
    for activity in activities:
        writer.writerow([
            activity['created_date'], activity['created_by'], activity['action'], 
            activity['table_name'], activity['record_id'], activity['system_remarks'],
            activity['error_code'] or '', activity['request_time'] or ''
        ])
    
    log_action('Admin', session['user_id'], 'EXPORT_TIMELINE', f'Admin exported timeline for {user_filter or "all users"}')
    
    return Response(
        si.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment;filename=timeline_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'}
    )

@admin_bp.route('/reports/documents')
@admin_required
def document_usage():
    conn = get_db_connection()
    
    # Document upload stats
    upload_stats = conn.execute(
        'SELECT d.filename, COUNT(*) as upload_count, MIN(l.created_date) as first_upload, MAX(l.created_date) as last_upload ' +
        'FROM Logs l JOIN Document d ON l.record_id = d.id ' +
        'WHERE l.action = "UPLOAD" AND l.is_deleted = 0 AND d.is_deleted = 0 ' +
        'GROUP BY d.id'
    ).fetchall()
    
    # Document download stats
    download_stats = conn.execute(
        'SELECT d.filename, COUNT(*) as download_count ' +
        'FROM Logs l JOIN Document d ON l.record_id = d.id ' +
        'WHERE l.action = "DOWNLOAD" AND l.is_deleted = 0 AND d.is_deleted = 0 ' +
        'GROUP BY d.id'
    ).fetchall()
    
    # Document preview stats
    preview_stats = conn.execute(
        'SELECT d.filename, COUNT(*) as preview_count ' +
        'FROM Logs l JOIN Document d ON l.record_id = d.id ' +
        'WHERE l.action = "PREVIEW" AND l.is_deleted = 0 AND d.is_deleted = 0 ' +
        'GROUP BY d.id'
    ).fetchall()
    
    conn.close()
    
    log_action('Admin', session['user_id'], 'VIEW_DOCUMENT_REPORT', 'Admin viewed document usage report')
    
    return render_template('admin/document_usage.html', 
                         upload_stats=upload_stats, 
                         download_stats=download_stats, 
                         preview_stats=preview_stats)

@admin_bp.route('/reports/search_trends')
@admin_required
def search_trends():
    conn = get_db_connection()
    
    # Top search queries
    top_queries = conn.execute(
        'SELECT query, COUNT(*) as count FROM Search WHERE is_deleted = 0 GROUP BY query ORDER BY count DESC LIMIT 10'
    ).fetchall()
    
    # Search frequency over time (last 30 days)
    search_frequency = conn.execute(
        'SELECT DATE(search_date) as date, COUNT(*) as count ' +
        'FROM Search WHERE is_deleted = 0 AND search_date >= date("now", "-30 days") ' +
        'GROUP BY DATE(search_date) ORDER BY date'
    ).fetchall()
    
    conn.close()
    
    log_action('Admin', session['user_id'], 'VIEW_SEARCH_TRENDS', 'Admin viewed search trends report')
    
    # Prepare data for Chart.js
    search_freq_data = {
        'labels': [row['date'] for row in search_frequency],
        'data': [row['count'] for row in search_frequency]
    }
    
    return render_template('admin/search_trends.html', 
                         top_queries=top_queries, 
                         search_freq_data=search_freq_data)
    

@admin_bp.route('/monitor')
@admin_required
def monitor():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    user_filter = request.args.get('user_filter', '')
    
    conn = get_db_connection()
    query = 'SELECT * FROM Logs WHERE is_deleted = 0 AND (table_name IN ("User", "Document", "Search", "UserDictionary") OR action = "PAGE_VIEW")'
    params = []
    
    if user_filter:
        query += ' AND created_by = ?'
        params.append(user_filter)
    
    query += ' ORDER BY created_date DESC LIMIT ? OFFSET ?'
    params.extend([per_page, (page - 1) * per_page])
    
    activities = conn.execute(query, params).fetchall()
    total_activities = conn.execute(
        'SELECT COUNT(*) FROM Logs WHERE is_deleted = 0 AND (table_name IN ("User", "Document", "Search", "UserDictionary") OR action = "PAGE_VIEW")'
    ).fetchone()[0]
    users = conn.execute('SELECT username FROM User WHERE is_deleted = 0').fetchall()
    conn.close()
    
    total_pages = (total_activities + per_page - 1) // per_page
    log_action('Admin', session['user_id'], 'VIEW_MONITOR', f'Admin viewed user activity monitor (page {page})')
    
    return render_template('admin/monitor.html', activities=activities, page=page, total_pages=total_pages,
                         user_filter=user_filter, users=users)