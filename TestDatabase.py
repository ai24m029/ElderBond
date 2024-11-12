import unittest
import os
from DataBase import DataBaseAccess

class TestDataBaseAccess(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Use a test database so we don't interfere with production data
        cls.db = DataBaseAccess("test_social_media.db")

    def setUp(self):
        # Ensure the database is clean before each test
        self.db.cursor.execute("DELETE FROM Posts")
        self.db.conn.commit()

    def test_initialize_db(self):
        # Check if the Posts table exists
        self.db.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Posts'")
        table = self.db.cursor.fetchone()
        self.assertIsNotNone(table, "The Posts table should be created on initialization")

    def test_add_post(self):
        # Add a post and check if it exists in the database
        self.db.add_post("test_image.jpg", "Test post text", "TestUser")
        self.db.cursor.execute("SELECT * FROM Posts")
        post = self.db.cursor.fetchone()
        
        self.assertIsNotNone(post, "A post should be present after adding one")
        self.assertEqual(post[1], "test_image.jpg")
        self.assertEqual(post[2], "Test post text")
        self.assertEqual(post[3], "TestUser")

    def test_get_latest_post(self):
        # Add two posts and retrieve the latest one
        self.db.add_post("old_image.jpg", "Old post text", "OldUser")
        self.db.add_post("new_image.jpg", "New post text", "NewUser")

        latest_post = self.db.get_latest_post()

        # Check if the latest post has the expected data
        self.assertIsNotNone(latest_post, "The latest post should be retrievable")
        self.assertEqual(latest_post[1], "new_image.jpg")
        self.assertEqual(latest_post[2], "New post text")
        self.assertEqual(latest_post[3], "NewUser")

    @classmethod
    def tearDownClass(cls):
        # Close the database connection and delete the test database file
        cls.db.conn.close()
        os.remove("test_social_media.db")

if __name__ == "__main__":
    unittest.main()
