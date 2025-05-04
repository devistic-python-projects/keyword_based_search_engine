CREATE TABLE IF NOT EXISTS Admin (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT NOT NULL,
    updated_by TEXT NOT NULL,
    is_deleted INTEGER DEFAULT 0
);

-- Creating User table
CREATE TABLE User (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT NOT NULL DEFAULT 'System',
    updated_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_by TEXT NOT NULL DEFAULT 'System',
    is_deleted BOOLEAN DEFAULT FALSE,
    admin_remarks TEXT
);

-- Creating UserDictionary table for custom words
CREATE TABLE UserDictionary (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    word TEXT NOT NULL,
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT NOT NULL DEFAULT 'System',
    updated_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_by TEXT NOT NULL DEFAULT 'System',
    is_deleted BOOLEAN DEFAULT FALSE,
    admin_remarks TEXT,
    FOREIGN KEY (user_id) REFERENCES User(id),
    UNIQUE(user_id, word)
);

-- Creating Document table
CREATE TABLE Document (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    filename TEXT NOT NULL,
    file_path TEXT NOT NULL,
    upload_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT NOT NULL DEFAULT 'System',
    updated_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_by TEXT NOT NULL DEFAULT 'System',
    is_deleted BOOLEAN DEFAULT FALSE,
    admin_remarks TEXT,
    FOREIGN KEY (user_id) REFERENCES User(id)
);

-- Creating DocumentIndex table for storing indexed keywords
CREATE TABLE DocumentIndex (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL,
    keyword TEXT NOT NULL,
    frequency INTEGER NOT NULL,
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT NOT NULL DEFAULT 'System',
    updated_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_by TEXT NOT NULL DEFAULT 'System',
    is_deleted BOOLEAN DEFAULT FALSE,
    admin_remarks TEXT,
    FOREIGN KEY (document_id) REFERENCES Document(id)
);

-- Creating Notification table
CREATE TABLE Notification (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message TEXT NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('success', 'error', 'info')),
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT NOT NULL DEFAULT 'System',
    updated_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_by TEXT NOT NULL DEFAULT 'System',
    is_deleted BOOLEAN DEFAULT FALSE,
    admin_remarks TEXT
);

-- Creating NotificationReceiver table
CREATE TABLE NotificationReceiver (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    notification_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT NOT NULL DEFAULT 'System',
    updated_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_by TEXT NOT NULL DEFAULT 'System',
    is_deleted BOOLEAN DEFAULT FALSE,
    admin_remarks TEXT,
    FOREIGN KEY (notification_id) REFERENCES Notification(id),
    FOREIGN KEY (user_id) REFERENCES User(id)
);

-- Creating Search table
CREATE TABLE Search (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query TEXT NOT NULL,
    user_id INTEGER,
    search_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT NOT NULL DEFAULT 'System',
    updated_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_by TEXT NOT NULL DEFAULT 'System',
    is_deleted BOOLEAN DEFAULT FALSE,
    admin_remarks TEXT,
    FOREIGN KEY (user_id) REFERENCES User(id)
);

-- Creating SearchResult table
CREATE TABLE SearchResult (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    search_id INTEGER NOT NULL,
    document_id INTEGER NOT NULL,
    relevance_score REAL NOT NULL,
    snippet TEXT,
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT NOT NULL DEFAULT 'System',
    updated_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_by TEXT NOT NULL DEFAULT 'System',
    is_deleted BOOLEAN DEFAULT FALSE,
    admin_remarks TEXT,
    FOREIGN KEY (search_id) REFERENCES Search(id),
    FOREIGN KEY (document_id) REFERENCES Document(id)
);

CREATE TABLE IF NOT EXISTS Logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    table_name TEXT NOT NULL,
    record_id INTEGER NOT NULL,
    action TEXT NOT NULL,
    system_remarks TEXT,
    error_code TEXT,
    request_time REAL,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT NOT NULL DEFAULT 'System',
    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by TEXT NOT NULL DEFAULT 'System',
    is_deleted INTEGER DEFAULT 0,
    admin_remarks TEXT
);