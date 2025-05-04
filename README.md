# Keyword-Based Search Engine

A Flask-based search engine for text documents with keyword and phrase search, spell-checking, and admin management.

## Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd keyword_based_search_engine
   ```

2. **Create a Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Environment Variables**
   Create a `.env` file in the root directory:
   ```
   SECRET_KEY=your-secret-key
   ```

5. **Initialize the Database**
   The database will be created automatically on first run.

6. **Run the Application**
   ```bash
   python run.py
   ```

7. **Access the Application**
   Open a browser and navigate to `http://localhost:5000`.


8. **To run the tests**
    ```bash
   pytest tests/test_app.py
   ```

## Features
- Search: Keyword and phrase search with Whoosh indexing, ranked by relevance and recency.
- Upload: Supports .txt, .csv, .json, .xml, .tsv files (requires login).
- Spell-Checking: Real-time spell-checking with suggestions and user dictionary.
- Document Previews: View the first 1000 characters of documents.
- User Profile: View uploaded documents and manage custom dictionary words.
- Notifications: User-specific notifications for uploads and other actions.
- Admin Dashboard: Manage users, view logs, and monitor notifications.
- Accessibility: Responsive design with semantic HTML.
- Logging: Tracks all actions (upload, download, search, etc.) in SQLite.

## Directory Structure
- `app/`: Flask application code
- `uploads/`: Uploaded documents
- `indexes/`: Whoosh indexes
- `logs/`: System logs
- `database/`: SQLite database

## 📁 Project Structure
keyword_search_engine/
│
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth_routes.py
│   │   ├── main_routes.py
│   │   ├── admin_routes.py
│   ├── templates/
│   │   ├── layout.html
│   │   ├── login.html
│   │   ├── signup.html
│   │   ├── home.html
│   │   ├── upload.html
│   │   ├── results.html
│   │   ├── admin/
│   │   │   ├── dashboard.html
│   │   │   ├── logs.html
│   │   │   ├── users.html
│   │   │   ├── notifications.html
│   ├── static/
│   │   ├── css/
│   │   │   └── styles.css
│   │   ├── js/
│   │   │   └── main.js
│   ├── utils/
│   │   ├── db.py
│   │   ├── indexing.py
│   │   ├── spellcheck.py
│   │   ├── decorators.py
│   │   ├── validation.py
│   ├── forms/
│   │   ├── login_form.py
│   │   ├── signup_form.py
│   │   ├── upload_form.py
│
├── uploads/                 ← uploaded documents stored here
├── indexes/                ← Whoosh index stored here
├── logs/                   ← system logs here
│
├── database/
│   ├── schema.sql          ← All table creation SQL scripts
│   └── search_engine.db    ← Main SQLite DB (created at runtime)
│
├── .env
├── run.py
├── requirements.txt
├── README.md
