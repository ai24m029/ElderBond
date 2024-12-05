import unittest
from app.ElderBond import app
from app.DataBase import DataBaseAcess


class FlaskAppTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Initialize the test database
        cls.db = DataBaseAcess('test_elder_social_media.db')
        cls.db.initialize_database()

    @classmethod
    def tearDownClass(cls):
        # Clean up test database
        import os
        if os.path.exists('test_elder_social_media.db'):
            os.remove('test_elder_social_media.db')

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        app.config['TESTING'] = True
        app.config['DATABASE'] = 'test_elder_social_media.db'

    def test_home_route_redirects_to_login(self):
        """Test that the home route redirects to the login page if not logged in."""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.location)

    def test_signup_user(self):
        """Test user signup."""
        response = self.app.post('/signup', data={
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Account created successfully', response.data)

    def test_login_user(self):
        """Test user login."""
        # Add a test user to the database
        self.db.insert_user('testuser', 'testuser@example.com', 'hashedpassword')

        # Attempt login
        response = self.app.post('/login', data={
            'email': 'testuser@example.com',
            'password': 'hashedpassword'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'testuser', response.data)

    def test_add_content(self):
        """Test adding content for a user."""
        # Log in as test user
        with self.app.session_transaction() as sess:
            sess['user_id'] = 1

        # Add content
        response = self.app.post('/add_content', data={
            'title': 'Test Post',
            'text': 'This is a test post.',
            'location': 'Vienna'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Post', response.data)

    def test_search_user(self):
        """Test searching for a user."""
        # Add a user and some content
        self.db.insert_user('testsearch', 'searchuser@example.com', 'password')
        user = self.db.get_user_by_username('testsearch')
        self.db.insert_content(user[0], 'Search Post', 'Content for search test', None, 'Berlin')

        # Search for the user
        response = self.app.post('/search_user', data={
            'username': 'testsearch'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Search Post', response.data)

    def test_delete_user(self):
        """Test deleting a user."""
        # Add a test user
        self.db.insert_user('deleteuser', 'deleteuser@example.com', 'password')
        user = self.db.get_user_by_email('deleteuser@example.com')

        # Delete the user
        response = self.app.post(f'/user/delete/{user[0]}', data={'_method': 'DELETE'}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Your account has been deleted successfully.', response.data)