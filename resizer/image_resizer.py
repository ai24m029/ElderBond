import pika
import json
from PIL import Image
import os
import sqlite3

# Updated to use absolute path
DB_PATH = "/app/elder_social_media.db"  # Absolute path for DB in Docker container

def resize_image(image_path):
    """
    Resizes the image to a maximum size of 300x300 pixels and saves it in the resized directory.
    """
    # Correct the full path to the original image
    # Remove any leading "images/" from the provided image_path to avoid duplication
    cleaned_image_path = image_path.lstrip("images/")  # Remove leading "images/" if present
    full_path = os.path.join('/app/static/images', cleaned_image_path)

    # Directory for resized images
    resized_dir = os.path.join('/app/static/images/resized')
    os.makedirs(resized_dir, exist_ok=True)

    # Path for the resized image
    resized_path = os.path.join(resized_dir, os.path.basename(cleaned_image_path))

    # Debugging outputs
    print(f"[DEBUG] Original image path: {image_path}", flush=True)
    print(f"[DEBUG] Cleaned image path: {cleaned_image_path}", flush=True)
    print(f"[DEBUG] Full path: {full_path}", flush=True)
    print(f"[DEBUG] Resized directory: {resized_dir}", flush=True)
    print(f"[DEBUG] Resized path: {resized_path}", flush=True)

    # Check if the original image exists
    if not os.path.exists(full_path):
        print(f"[ERROR] Image not found at path: {full_path}", flush=True)  # More descriptive error
        raise FileNotFoundError(f"Image not found at path: {full_path}")

    # Resize the image and save it
    with Image.open(full_path) as img:
        img.thumbnail((300, 300))
        img.save(resized_path)

    return resized_path


def update_database(content_id, resized_path):
    """
    Updates the database with the path of the resized image.
    """
    # Convert full path to relative path for storage in the database
    relative_resized_path = os.path.relpath(resized_path, '/app/static')
    print(f"[DEBUG] Relative resized path for DB: {relative_resized_path}", flush=True)

    try:
        # Update the SQLite database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE ContentTable
            SET reduced_image = ?
            WHERE id = ?
        ''', (relative_resized_path, content_id))
        conn.commit()
        conn.close()
        print(f"[DEBUG] Database updated for content_id {content_id}", flush=True)
    except sqlite3.Error as e:
        print(f"[ERROR] Database error: {e}", flush=True)


def callback(ch, method, properties, body):
    """
    Callback function to handle messages from the RabbitMQ queue.
    """
    try:
        data = json.loads(body)
        content_id = data["content_id"]
        image_path = data["image_path"]

        # Debugging received message
        print(f"[DEBUG] Received message: content_id={content_id}, image_path={image_path}", flush=True)

        # Process the image
        resized_path = resize_image(image_path)

        # Update the database with the resized image path
        update_database(content_id, resized_path)

        # Debugging success message
        print(f"Processed content_id {content_id}, resized image saved at {resized_path}", flush=True)

    except Exception as e:
        print(f"[ERROR] Failed to process message: {e}", flush=True)


def main():
    """
    Main function to set up RabbitMQ and start consuming messages.
    """
    connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
    channel = connection.channel()
    channel.queue_declare(queue='image_resize')

    print("[INFO] Waiting for messages...", flush=True)

    channel.basic_consume(queue='image_resize', on_message_callback=callback, auto_ack=True)
    channel.start_consuming()


if __name__ == "__main__":
    main()
