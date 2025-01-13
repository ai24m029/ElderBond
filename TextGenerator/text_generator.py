import pika
import json
import os
import sqlite3
import requests

DB_PATH = "/app/elder_social_media.db"


def generate_text(prompt):
    """
    Generate text from a prompt using the Hugging Face API.
    """
    print(f"[INFO] Generating text for prompt: {prompt}", flush=True)


    HF_API_TOKEN = os.getenv("HF_API_TOKEN")
    response = requests.post(
        "https://api-inference.huggingface.co/models/gpt2",
        headers={
            "Authorization": f"Bearer {HF_API_TOKEN}",
            "Content-Type": "application/json",
        },
        json={"inputs": prompt},
    )

    if response.status_code == 200:
        generated_text = response.json()[0]["generated_text"]
        return generated_text.strip()
    else:
        print(f"[ERROR] Failed to generate text: {response.text}", flush=True)
        raise Exception("Text generation failed")


def update_database(content_id, generated_text):
    """
    Update the database with the generated text.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE ContentTable
        SET text = ?
        WHERE id = ?
    ''', (generated_text, content_id))
    conn.commit()
    conn.close()
    print(f"[INFO] Database updated for content ID {content_id}", flush=True)


def callback(ch, method, properties, body):
    """
    Callback function for processing RabbitMQ messages.
    """
    data = json.loads(body)
    content_id = data["content_id"]
    prompt = data["prompt"]

    try:
        generated_text = generate_text(prompt)
        update_database(content_id, generated_text)
        print(f"[INFO] Successfully processed content ID {content_id}", flush=True)
    except Exception as e:
        print(f"[ERROR] Failed to process content ID {content_id}: {e}", flush=True)


def main():
    """
    Listen to RabbitMQ and process messages.
    """
    connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))
    channel = connection.channel()
    channel.queue_declare(queue="text_generation")

    print("[INFO] Waiting for messages...", flush=True)
    channel.basic_consume(queue="text_generation", on_message_callback=callback, auto_ack=True)
    channel.start_consuming()


if __name__ == "__main__":
    main()
