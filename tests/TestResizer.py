import unittest
from unittest.mock import patch, MagicMock
import os
import sqlite3
from PIL import Image
import json
from image_resizer import resize_image, update_database, callback


class TestImageResizer(unittest.TestCase):

    def setUp(self):
        """
        Setup temporary environment for testing.
        """
        self.test_db_path = "/tmp/test_elder_social_media.db"
        self.test_image_dir = "/tmp/static/images"
        self.test_resized_dir = "/tmp/static/images/resized"

        os.makedirs(self.test_resized_dir, exist_ok=True)

        # Create a test database
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ContentTable (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                text TEXT NOT NULL,
                image TEXT,
                location TEXT,
                reduced_image TEXT,
                time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()

        # Create a test image
        self.test_image_path = os.path.join(self.test_image_dir, "test_image.png")
        os.makedirs(self.test_image_dir, exist_ok=True)
        with Image.new("RGB", (500, 500), color="blue") as img:
            img.save(self.test_image_path)

    def tearDown(self):
        """
        Cleanup temporary environment.
        """
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
        if os.path.exists(self.test_image_path):
            os.remove(self.test_image_path)
        if os.path.exists(self.test_resized_dir):
            os.rmdir(self.test_resized_dir)
        if os.path.exists(self.test_image_dir):
            os.rmdir(self.test_image_dir)

    @patch("image_resizer.DB_PATH", new="/tmp/test_elder_social_media.db")
    def test_resize_image(self):
        """
        Test the resize_image function.
        """
        resized_path = resize_image("test_image.png")

        # Assert resized image exists
        self.assertTrue(os.path.exists(resized_path))

        # Assert resized image dimensions
        with Image.open(resized_path) as img:
            self.assertLessEqual(img.width, 300)
            self.assertLessEqual(img.height, 300)

    @patch("image_resizer.DB_PATH", new="/tmp/test_elder_social_media.db")
    def test_update_database(self):
        """
        Test the update_database function.
        """
        # Insert a test content row
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO ContentTable (user_id, title, text, image, location)
            VALUES (?, ?, ?, ?, ?)
        ''', (1, "Test Title", "Test Text", "test_image.png", "Test Location"))
        content_id = cursor.lastrowid
        conn.commit()
        conn.close()

        # Call update_database
        update_database(content_id, "static/images/resized/test_image.png")

        # Assert the database is updated
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT reduced_image FROM ContentTable WHERE id = ?", (content_id,))
        reduced_image = cursor.fetchone()[0]
        conn.close()

        self.assertEqual(reduced_image, "static/images/resized/test_image.png")

    @patch("image_resizer.resize_image")
    @patch("image_resizer.update_database")
    def test_callback(self, mock_update_database, mock_resize_image):
        """
        Test the callback function.
        """
        mock_resize_image.return_value = "static/images/resized/test_image.png"
        mock_update_database.return_value = None

        body = json.dumps({"content_id": 1, "image_path": "test_image.png"})
        callback(None, None, None, body)

        # Assert resize_image and update_database were called
        mock_resize_image.assert_called_once_with("test_image.png")
        mock_update_database.assert_called_once_with(1, "static/images/resized/test_image.png")


if __name__ == "__main__":
    unittest.main()
