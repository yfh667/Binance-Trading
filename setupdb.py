import requests
import sqlite3
from datetime import datetime
import time
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


def init_db(db_name='test1.db'):
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT,
                address TEXT UNIQUE,
                creationTime TEXT
            );
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                token_id INTEGER,
                price REAL,
                timestamp DATETIME,
                FOREIGN KEY(token_id) REFERENCES tokens(id)
            );
        ''')
        conn.commit()
init_db()
