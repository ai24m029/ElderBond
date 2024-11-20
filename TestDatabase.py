import unittest
from ElderBond import app  
from DataBase import DataBaseAccess

class TestFlaskApp(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up the test client and test database"""
        app.config['TESTING'] = True
        cls.client = app.test_client()  # Flask test client
        cls.db_name = "test_social_media.db"
        cls.db = DataBaseAccess(cls.db_name)

    def setUp(self):
        """Ensure the database is clean before each test"""
        with self.db.conn:
            self.db.cursor.execute("DELETE FROM Posts")
            self.db.conn.commit()

    def test_add_post_api(self):
        """Test adding a post via the API"""
        response = self.client.post('/api/posts', json={
            'image': 'test_image.jpg',
            'text': 'Test post text',
            'user': 'TestUser'
        })
        self.assertEqual(response.status_code, 201)
        self.assertIn('Post added successfully', response.get_json()['message'])

        # Check if the post was added to the database
        self.db.cursor.execute("SELECT * FROM Posts WHERE user = 'TestUser'")
        post = self.db.cursor.fetchone()
        self.assertIsNotNone(post)
        self.assertEqual(post[1], 'test_image.jpg')
        self.assertEqual(post[2], 'Test post text')
        self.assertEqual(post[3], 'TestUser')

    def test_list_posts_api(self):
        """Test listing all posts via the API"""
        # Add sample data
        self.db.add_post('image1.jpg', 'Post 1', 'User1')
        self.db.add_post('image2.jpg', 'Post 2', 'User2')

        # Request all posts
        response = self.client.get('/api/posts')
        self.assertEqual(response.status_code, 200)

        # Verify the response data
        posts = response.get_json()
        self.assertEqual(len(posts), 2)
        self.assertEqual(posts[0]['text'], 'Post 1')
        self.assertEqual(posts[1]['user'], 'User2')

    def test_search_posts_api(self):
        """Test searching for posts by user"""
        # Add sample data
        self.db.add_post('image1.jpg', 'Post 1', 'TestUser')
        self.db.add_post('image2.jpg', 'Post 2', 'AnotherUser')

        # Search for posts by TestUser
        response = self.client.get('/api/posts/search?user=TestUser')
        self.assertEqual(response.status_code, 200)

        # Verify the response data
        posts = response.get_json()
        self.assertEqual(len(posts), 1)
        self.assertEqual(posts[0]['user'], 'TestUser')
        self.assertEqual(posts[0]['text'], 'Post 1')

    def test_homepage(self):
        """Test the homepage (GET /)"""
        # Add sample data
        self.db.add_post('image1.jpg', 'Post 1', 'User1')

        # Request the homepage
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

        # Check if the page contains the post content
        html = response.get_data(as_text=True)
        self.assertIn('Post 1', html)
        self.assertIn('User1', html)

    def test_add_post_page(self):
        """Test adding a post via the web form"""
        # Send a POST request to the /add_post endpoint
        response = self.client.post('/add_post', data={
            'image': 'image3.jpg',
            'text': 'Post 3',
            'user': 'WebUser'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # Check if the new post appears on the homepage
        html = response.get_data(as_text=True)
        self.assertIn('Post 3', html)
        self.assertIn('WebUser', html)

    def test_search_posts_page(self):
        """Test searching for posts via the search page"""
        # Add sample data
        self.db.add_post('image1.jpg', 'Post 1', 'SearchUser')
        self.db.add_post('image2.jpg', 'Post 2', 'OtherUser')

        # Send a GET request to /search with a query parameter
        response = self.client.get('/search?user=SearchUser')
        self.assertEqual(response.status_code, 200)

        # Verify the response contains only the searched user's posts
        html = response.get_data(as_text=True)
        self.assertIn('Post 1', html)
        self.assertIn('SearchUser', html)
        self.assertNotIn('Post 2', html)

    @classmethod
    def tearDownClass(cls):
        """Clean up by closing the database connection and deleting the test DB"""
        cls.db.conn.close()
        import os
        os.remove(cls.db_name)

if __name__ == '__main__':
    unittest.main()
