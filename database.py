import sqlite3
import os
from datetime import datetime

class Database:
    def __init__(self, db_name='users.db'):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir) 
        data_dir = os.path.join(project_root, 'bot_data') 
        os.makedirs(data_dir, exist_ok=True)
        db_path = os.path.join(data_dir, db_name)
        self.conn = sqlite3.connect(db_path)
        self.create_tables()
        self.db_path = db_path
        
    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                first_used DATETIME,
                last_used DATETIME,
                posts_count INTEGER DEFAULT 0,
                delete_count INTEGER DEFAULT 0
            )
        ''')
        self.conn.commit()

    def add_or_update_user(self, user_id, username, full_name):
        cursor = self.conn.cursor()
        cursor.execute('SELECT id FROM users WHERE id =?', (user_id,))
        exists = cursor.fetchone()
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if exists:
            cursor.execute('UPDATE users SET username = ?, full_name = ?, last_used = ? WHERE id = ?',
                           (username, full_name, now, user_id))
        else:
            cursor.execute('INSERT INTO users (id, username, full_name, first_used, last_used) VALUES (?, ?, ?, ?, ?)',
                          (user_id, username, full_name, now, now))
        self.conn.commit()
    
    def increment_posts_count(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE users SET posts_count = posts_count + 1 WHERE id = ?', (user_id,))
        self.conn.commit()
    
    def increment_delete_requests(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE users SET delete_requests_count = delete_requests_count + 1 WHERE id = ?', (user_id,))
        self.conn.commit()
    
    def get_all_users(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM users ORDER BY last_used DESC')
        return cursor.fetchall()
    
    def close(self):
        self.conn.close()

db = Database()
