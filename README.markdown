# Keyword-Based Search Engine

A Flask-based web application for uploading, indexing, and searching text documents using keyword-based search with Whoosh. The application supports user authentication, admin management, logging, and detailed reporting features.

## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Application Structure](#application-structure)
- [Contributing](#contributing)
- [License](#license)

## Features
- User authentication (signup, login, logout)
- Document upload, indexing, and keyword-based search
- Admin dashboard for user management and system monitoring
- Comprehensive logging of user and system actions
- Reporting features including user activity timelines, document usage stats, and search query trends
- Visual timeline rendering with Chart.js
- CSV export for logs and timeline data

## Installation
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd keyword-search-engine
   ```
2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Initialize the database: Create a Python script (e.g., init_db.py) with the following content:
   ```bash
   from app.utils.db import init_db
   import os
   db_path = os.path.join(os.path.dirname(__file__), 'database', 'search_engine.db')
   init_db(db_path)
   ```
   Run the script:
   ```bash
   python init_db.py
   ```
   Alternatively, run the following command, replacing instance/database.db with your desired database path:
   ```bash
   python -c "from app.utils.db import init_db; init_db('database/search_engine.db')"
   ```
5. Run the application:
   ```bash
   flask run
   ```

## Usage
- Access the app at `http://localhost:5000`.
- Sign up or log in to upload and search documents.
- Admins can access the dashboard at `/admin/dashboard` for management and reporting.

## Application Structure
The application follows a modular Flask structure, organized as follows:

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
├── index/                        # Directory for Whoosh index
├── logs/                         # Directory for log files (if exported)
├── database/schema.sql           # SQLite database schema
├── requirements.txt              # Python dependencies
├── README.md                     # Project documentation
└── run.py                        # Entry point for running the application
```

### Key Components
- **app/__init__.py**: Defines the Flask app factory, initializes extensions (e.g., Flask-Session), sets up middleware for request time logging, and registers blueprints.
- **app/config.py**: Contains configuration settings like upload folder, Whoosh schema, and database path.
- **app/routes/**: Organizes routes into blueprints for authentication, main functionality, and admin features.
- **app/templates/**: Jinja2 templates for rendering pages, with admin templates separated for clarity.
- **app/static/**: CSS and JavaScript files, including styles for responsive design and Chart.js for visualizations.
- **app/utils/**: Reusable utilities for database operations, logging, indexing, and decorators.
- **database/schema.sql**: Defines the SQLite schema for tables like `User`, `Document`, `Search`, `Logs`, etc.
- **uploads/**, **index/**, **logs/**: Directories for storing uploaded files, Whoosh index, and log exports, respectively.

## Contributing
Contributions are welcome! Please submit a pull request or open an issue to discuss proposed changes.

## License
This project is licensed under the MIT License.