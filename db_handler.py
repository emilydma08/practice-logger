import sqlite3
import os

# utils/db_handler.py
import sqlite3
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), '../user_data')

def get_user_db_path(username):
    return os.path.join(DATA_DIR, f"{username}.db")

def init_user_db(username):
    path = get_user_db_path(username)
    if not os.path.exists(path):
        conn = sqlite3.connect(path)
        c = conn.cursor()
        # Initialize schema for new user
        c.execute('''CREATE TABLE IF NOT EXISTS categories (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL
                     )''')
        c.execute('''CREATE TABLE IF NOT EXISTS entries (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        category_id INTEGER,
                        content TEXT,
                        timestamp TEXT,
                        FOREIGN KEY (category_id) REFERENCES categories(id)
                     )''')
        conn.commit()
        conn.close()

def get_connection(username):
    path = get_user_db_path(username)
    return sqlite3.connect(path)
