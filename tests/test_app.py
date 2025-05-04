import unittest
from app import create_app
from app.utils.db import get_db_connection
import os
from werkzeug.security import generate_password_hash
from io import BytesIO

class TestSearchEngine(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
        self.app.config['TESTING'] = True
        self.app.config['DATABASE'] = 'database/test_search_engine.db'
        
        # Initialize test database
        with self.app.app_context():
            conn = get_db_connection()
            with self.app.open_resource('schema.sql') as f:
                conn.executescript(f.read().decode('utf8'))
            # Create test user
            conn.execute(
                'INSERT INTO User (username, email, password_hash, created_by, updated_by) VALUES (?, ?, ?, ?, ?)',
                ('testuser', 'test@example.com', generate_password_hash('testpassword'), 'System', 'System')
            )
            # Create test admin
            conn.execute(
                'INSERT INTO Admin (username, email, password_hash, created_by, updated_by) VALUES (?, ?, ?, ?, ?)',
                ('admin', 'admin@example.com', generate_password_hash('adminpassword'), 'System', 'System')
            )
            conn.commit()
            conn.close()

    def tearDown(self):
        os.remove(self.app.config['DATABASE'])

    def test_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome to the Keyword-Based Search Engine', response.data)

    def test_login(self):
        response = self.client.post('/login', data={
            'username': 'testuser',
            'password': 'testpassword'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login successful!', response.data)

    def test_admin_login(self):
        response = self.client.post('/login', data={
            'username': 'admin',
            'password': 'adminpassword'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Admin login successful!', response.data)

    def test_upload(self):
        # Log in first
        self.client.post('/login', data={
            'username': 'testuser',
            'password': 'testpassword'
        })
        
        # Create a test file
        data = {'files': (BytesIO(b'Test content'), 'test.txt')}
        response = self.client.post('/upload', content_type='multipart/form-data', data=data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Documents uploaded successfully.', response.data)

    def test_search(self):
        # Log in and upload a document
        self.client.post('/login', data={
            'username': 'testuser',
            'password': 'testpassword'
        })
        data = {'files': (BytesIO(b'Test content with keyword'), 'test.txt')}
        self.client.post('/upload', content_type='multipart/form-data', data=data)
        
        # Perform search
        response = self.client.post('/search', data={'query': 'keyword'}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'test.txt', response.data)

    def test_spellcheck(self):
        response = self.client.post('/spellcheck', json={'word': 'teh'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {'is_correct': False, 'suggestions': ['the']})

    def test_admin_dashboard(self):
        # Log in as admin
        self.client.post('/login', data={
            'username': 'admin',
            'password': 'adminpassword'
        })
        
        response = self.client.get('/admin/dashboard')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Admin Dashboard', response.data)

if __name__ == '__main__':
    unittest.main()