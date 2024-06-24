import sqlite3
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_name='uniclip.db'):
        self.db_name = db_name
        self.conn = None
        self.cursor = None

    def init_db(self):
        self.conn = sqlite3.connect(self.db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id TEXT,
                content TEXT,
                sender_ip TEXT,
                timestamp DATETIME
            )
        ''')
        self.conn.commit()

    def record_message(self, group_id, content, sender_ip):
        self.cursor.execute('''
            INSERT INTO messages (group_id, content, sender_ip, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (group_id, content, sender_ip, datetime.now()))
        self.conn.commit()

    def get_messages(self, group_id, limit=10):
        self.cursor.execute('''
            SELECT * FROM messages
            WHERE group_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (group_id, limit))
        return self.cursor.fetchall()
