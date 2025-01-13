import unittest
from unittest.mock import patch, MagicMock
from ..TextGenerator.text_generator import generate_text, update_database, callback

class TestTextGenerator(unittest.TestCase):
    @patch("text_generator.requests.post")
    def test_generate_text_success(self, mock_post):
        """
        Test successful text generation using the Hugging Face API.
        """
        # Mock the response from the API
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"generated_text": "This is a generated text."}]
        mock_post.return_value = mock_response

        # Call the function
        prompt = "Write a poem about nature"
        result = generate_text(prompt)

        # Assertions
        self.assertEqual(result, "This is a generated text.")
        mock_post.assert_called_once_with(
            "https://api-inference.huggingface.co/models/gpt2",
            headers={
                "Authorization": "Bearer your_hf_api_token_here",
                "Content-Type": "application/json",
            },
            json={"inputs": prompt},
        )

    #BLALA
    @patch("text_generator.requests.post")
    def test_generate_text_failure(self, mock_post):
        """
        Test text generation failure due to an API error.
        """
        # Mock a failed API response
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = '{"error": "Invalid request"}'
        mock_post.return_value = mock_response

        # Call the function and assert exception
        prompt = "Invalid prompt"
        with self.assertRaises(Exception) as context:
            generate_text(prompt)

        # Assertions
        self.assertIn("Text generation failed", str(context.exception))

    @patch("text_generator.sqlite3.connect")
    def test_update_database(self, mock_connect):
        """
        Test database update for generated text.
        """
        # Mock the database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Call the function
        content_id = 1
        generated_text = "This is a generated text."
        update_database(content_id, generated_text)

        # Assertions
        mock_connect.assert_called_once_with("/app/elder_social_media.db")
        mock_cursor.execute.assert_called_once_with(
            '''
            UPDATE ContentTable
            SET text = ?
            WHERE id = ?
            ''',
            (generated_text, content_id),
        )
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch("text_generator.generate_text")
    @patch("text_generator.update_database")
    def test_callback(self, mock_update_database, mock_generate_text):
        """
        Test RabbitMQ callback processing.
        """
        # Mock the generate_text function
        mock_generate_text.return_value = "This is a generated text."

        # Simulate a message from RabbitMQ
        ch = MagicMock()
        method = MagicMock()
        properties = MagicMock()
        body = '{"content_id": 1, "prompt": "Write a story about space"}'

        # Call the callback function
        callback(ch, method, properties, body)

        # Assertions
        mock_generate_text.assert_called_once_with("Write a story about space")
        mock_update_database.assert_called_once_with(1, "This is a generated text.")

if __name__ == "__main__":
    unittest.main()
