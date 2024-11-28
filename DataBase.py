import sqlite3
from datetime import datetime

class DataBaseAccess:
    def __init__(self, db_name='social_media.db'):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.initialize_db()

    def initialize_db(self):
        # Create Users table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
        ''')
        # Create Content table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Content (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                text TEXT,
                image TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES Users (id)
            )
        ''')
        self.conn.commit()

    # User methods
    def add_user(self, username, email, password):
        self.cursor.execute('''
            INSERT INTO Users (username, email, password)
            VALUES (?, ?, ?)
        ''', (username, email, password))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_user(self, user_id):
        self.cursor.execute('SELECT * FROM Users WHERE id = ?', (user_id,))
        return self.cursor.fetchone()

    def get_all_users(self):
        self.cursor.execute('SELECT * FROM Users')
        return self.cursor.fetchall()

    def delete_user(self, user_id):
        self.cursor.execute('DELETE FROM Users WHERE id = ?', (user_id,))
        self.conn.commit()

    # Content methods
    def add_content(self, user_id, title, text, image):
        self.cursor.execute('''
            INSERT INTO Content (user_id, title, text, image)
            VALUES (?, ?, ?, ?)
        ''', (user_id, title, text, image))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_content_by_user(self, user_id):
        self.cursor.execute('SELECT * FROM Content WHERE user_id = ?', (user_id,))
        return self.cursor.fetchall()

    def get_content_by_id(self, content_id):
        self.cursor.execute('SELECT * FROM Content WHERE id = ?', (content_id,))
        return self.cursor.fetchone()

    def delete_content(self, content_id):
        self.cursor.execute('DELETE FROM Content WHERE id = ?', (content_id,))
        self.conn.commit()

    def search_content(self, query, district=None):
        sql = 'SELECT * FROM Content WHERE text LIKE ?'
        params = [f'%{query}%']
        if district:
            sql += ' AND location = ?'
            params.append(district)
        self.cursor.execute(sql, params)
        return self.cursor.fetchall()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()
