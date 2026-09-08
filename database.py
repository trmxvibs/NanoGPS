import sqlite3
import os

class DatabaseManager:
    @staticmethod
    def get_db_path():
        return os.path.join(os.path.dirname(__file__), "auratrace.db")

    @staticmethod
    def init_db():
        conn = sqlite3.connect(DatabaseManager.get_db_path())
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                ip TEXT,
                hit_type TEXT,
                payload TEXT,
                extra_info TEXT
            )
        ''')
        conn.commit()
        conn.close()
        try:
            os.chmod(DatabaseManager.get_db_path(), 0o600)
        except Exception:
            pass

    @staticmethod
    def log_hit(ip, hit_type, payload, extra_info="N/A"):
        try:
            conn = sqlite3.connect(DatabaseManager.get_db_path())
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO hits (ip, hit_type, payload, extra_info)
                VALUES (?, ?, ?, ?)
            ''', (ip, hit_type, payload, extra_info))
            conn.commit()
            conn.close()
        except Exception:
            pass

    @staticmethod
    def fetch_all_hits():
        try:
            conn = sqlite3.connect(DatabaseManager.get_db_path())
            cursor = conn.cursor()
            cursor.execute("SELECT id, timestamp, ip, hit_type, payload FROM hits ORDER BY timestamp DESC")
            rows = cursor.fetchall()
            conn.close()
            return rows
        except Exception:
            return []