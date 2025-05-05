from flask import Flask, render_template, request
from flask_session import Session
from .config import Config
from .utils.db import init_db
from .utils.logging import log_action
from whoosh.index import create_in
import os
import time

def create_app():
    app = Flask(__name__)
    app.config['DEBUG'] = True
    app.config.from_object(Config)

    # Initialize session
    Session(app)

    # Create necessary directories
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['INDEX_DIR'], exist_ok=True)
    os.makedirs(app.config['LOGS_DIR'], exist_ok=True)

    # Initialize database within app context
    with app.app_context():
        init_db()

    # Initialize Whoosh index
    if not os.path.exists(os.path.join(app.config['INDEX_DIR'], 'index')):
        create_in(app.config['INDEX_DIR'], schema=app.config['WHOOSH_SCHEMA'])

    # Register blueprints
    from .routes.auth_routes import auth_bp
    from .routes.main_routes import main_bp
    from .routes.admin_routes import admin_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)

    # Middleware to log request time and page views
    @app.before_request
    def before_request():
        request.start_time = time.time()
        if request.endpoint and request.endpoint != 'static':
            log_action('System', 0, 'PAGE_VIEW', f'Visited {request.path}', request_time=0)

    @app.after_request
    def after_request(response):
        if hasattr(request, 'start_time') and request.endpoint != 'static':
            request_time = time.time() - request.start_time
            log_action('System', 0, 'REQUEST_COMPLETED', 
                      f'Completed {request.path} in {request_time:.3f}s',
                      request_time=request_time)
        return response

    # Error handling for logging
    @app.errorhandler(Exception)
    def handle_error(error):
        request_time = time.time() - getattr(request, 'start_time', time.time()) if hasattr(request, 'start_time') else None
        error_code = getattr(error, 'code', 'UNKNOWN')
        log_action('System', 0, 'ERROR', f'Unexpected error: {str(error)}', 
                  error_code=error_code, request_time=request_time)
        return render_template('error.html', message='An unexpected error occurred.'), 500

    return app