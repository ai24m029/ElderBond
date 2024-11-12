import sqlite3
from datetime import datetime

class DataBaseAccess:
    def __init__(self, db_name='social_media.db'):
        # Initialize the connection and cursor
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.initialize_db()
    
    def initialize_db(self):
        # Set up the posts table, explicitly specifying timestamp as DATETIME
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                image TEXT,
                text TEXT,
                user TEXT,
                timestamp DATETIME
            )
        ''')
        self.conn.commit()
    
    def add_post(self, image, text, user):
        # Manually set the current timestamp for each post
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.cursor.execute('''
            INSERT INTO Posts (image, text, user, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (image, text, user, timestamp))
        self.conn.commit()
    
    def get_latest_post(self):
        # Retrieve the latest post by ordering by timestamp DESC
        self.cursor.execute('''
            SELECT * FROM Posts
            ORDER BY id DESC LIMIT 1
        ''')
        return self.cursor.fetchone()
    
    def get_all_posts(self):
        # Retrieve all posts ordered by timestamp DESC
        self.cursor.execute('SELECT * FROM Posts ORDER BY timestamp DESC')
        return self.cursor.fetchall()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()
