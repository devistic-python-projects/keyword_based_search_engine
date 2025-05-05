
# Keyword-Based Search Engine for Text Documents

A Flask-based web application for uploading, indexing, and searching text documents using keyword-based search with Whoosh. The application supports user authentication, admin management, logging, and detailed reporting features.

## Setup and Configuration

### Installation

1. **Create a virtual environment**:
   ```bash
   python -m venv venv
   ```

2. **Activate the virtual environment**:
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On MacOS/Linux:
     ```bash
     source venv/bin/activate
     ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

   ```bash
   pip install email_validator==2.2.0
   ```

4. **Initialize the database**:
   ```bash
   python init_db.py
   ```

5. **Run the Flask application**:
   ```bash
   flask run
   ```

---

## Project Structure

```
keyword-search-engine/
├── app/
│   ├── __init__.py               # Application factory and configuration
│   ├── config.py                 # Configuration settings (e.g., upload folder, Whoosh schema)
│   ├── forms/                    # WTForms for form validation
│   │   ├── login_form.py         # Login form
│   │   ├── signup_form.py        # Signup form
│   │   └── upload_form.py        # Document upload form
│   ├── routes/                   # Blueprint-based route handlers
│   │   ├── auth_routes.py        # Authentication routes (login, signup, logout)
│   │   ├── main_routes.py        # Core routes (home, upload, search, profile)
│   │   └── admin_routes.py       # Admin routes (dashboard, logs, reports, timeline)
│   ├── static/                   # Static assets
│   │   ├── css/
│   │   │   └── styles.css        # Application-wide CSS
│   │   └── js/
│   │       └── main.js           # Client-side JavaScript
│   ├── templates/                # Jinja2 templates
│   │   ├── admin/                # Admin-specific templates
│   │   │   ├── dashboard.html    # Admin dashboard
│   │   │   ├── logs.html         # System logs with filtering and pagination
│   │   │   ├── monitor.html      # User activity monitoring
│   │   │   ├── reports.html      # Summary reports (action counts, errors, etc.)
│   │   │   ├── timeline.html     # User activity timeline with Chart.js visualization
│   │   │   ├── document_usage.html # Document usage statistics
│   │   │   ├── search_trends.html # Search query trends with Chart.js
│   │   │   └── users.html        # User management
│   │   ├── layout.html           # Base template with navigation and scripts
│   │   ├── login.html            # Login page
│   │   ├── signup.html           # Signup page
│   │   ├── home.html             # Home page with search
│   │   ├── upload.html           # Document upload page
│   │   ├── profile.html          # User profile
│   │   ├── notifications.html    # User notifications
│   │   ├── faq.html              # FAQ page
│   │   ├── about.html            # About page
│   │   └── error.html            # Error page
│   ├── utils/                    # Utility modules
│   │   ├── db.py                 # Database connection and initialization
│   │   ├── decorators.py         # Custom decorators (e.g., admin_required)
│   │   ├── indexing.py           # Whoosh indexing functions
│   │   └── logging.py            # Logging utility for standardized log entries
├── uploads/                      # Directory for uploaded documents
├── logs/                         # Directory for log files (if exported)
├── database/schema.sql           # SQLite database schema
├── requirements.txt              # Python dependencies
├── README.md                     # Project documentation
└── run.py                        # Entry point for running the application
```

---

## Key Components

- **app/__init__.py**: Defines the Flask app factory, initializes extensions (e.g., Flask-Session), sets up middleware for request time logging, and registers blueprints.
- **app/config.py**: Contains configuration settings like the upload folder, Whoosh schema, and database path.
- **app/routes/**: Organizes routes into blueprints for authentication, main functionality, and admin features.
- **app/templates/**: Jinja2 templates for rendering pages, with admin templates separated for clarity.
- **app/static/**: CSS and JavaScript files, including styles for responsive design and Chart.js for visualizations.
- **app/utils/**: Reusable utilities for database operations, logging, indexing, and decorators.
- **database/schema.sql**: Defines the SQLite schema for tables like `User`, `Document`, `Search`, `Logs`, etc.
- **uploads/**, **index/**, **logs/**: Directories for storing uploaded files, Whoosh index, and log exports, respectively.

---

This structure ensures maintainability, modularity, and scalability for the keyword-based search engine.
