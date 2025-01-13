import sqlite3
import os


class DataBaseAcess:

    def __init__(self, db_name='elder_social_media.db'):
        self.db_path = os.getenv('SQLITE_DB_PATH', 'app/elder_social_media.db')  # Default path if env variable is missing
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.db_name = db_name
        self.initialize_database()



    def initialize_database(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        # Create UserTable
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS UserTable (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')

        # Create ContentTable
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ContentTable (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                text TEXT NOT NULL,
                image TEXT,
                location TEXT,
                reduced_image TEXT,
                time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES UserTable (id)
            )
        ''')

        conn.commit()
        conn.close()

    def insert_user(self, username, email, password):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO UserTable (username, email, password)
            VALUES (?, ?, ?)
        ''', (username, email, password))
        conn.commit()
        conn.close()

    def update_reduced_image_path(self, content_id, reduced_image_path):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE ContentTable
            SET reduced_image = ?
            WHERE id = ?
        ''', (reduced_image_path, content_id))
        conn.commit()
        conn.close()

    def insert_content(self, user_id, title, text, image, location, reduced_image=None):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO ContentTable (user_id, title, text, image, location, reduced_image)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, title, text, image, location, reduced_image))
        conn.commit()
        conn.close()

    def get_content_by_user(self, user_id):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM ContentTable WHERE user_id = ?
        ''', (user_id,))
        rows = cursor.fetchall()
        conn.close()
        return rows

    def get_all_content(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM ContentTable')
        content = cursor.fetchall()
        conn.close()
        return content

    def get_all_users(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM UserTable')
        content = cursor.fetchall()
        conn.close()
        return content

    def get_user_by_email(self, email):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM UserTable WHERE email = ?", (email,))
        user = cursor.fetchone()
        conn.close()
        return user

    def get_user_by_username(self, username):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM UserTable WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()
        return user

    def delete_user(self, id):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM UserTable WHERE id = ?", (id,))
            conn.commit()
            conn.close()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting user: {e}")
            return False