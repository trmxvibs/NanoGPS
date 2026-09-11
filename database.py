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

    @staticmethod
    def fetch_recent_hits(limit=100, hit_type=None):
        """Fetch recent hits as dicts for the admin JSON API."""
        try:
            limit = max(1, min(int(limit or 100), 500))
        except (TypeError, ValueError):
            limit = 100
        allowed = ("GEOLOCATION", "DEEP_TELEMETRY")
        try:
            conn = sqlite3.connect(DatabaseManager.get_db_path())
            cursor = conn.cursor()
            if hit_type in allowed:
                cursor.execute(
                    "SELECT id, timestamp, ip, hit_type, payload, extra_info "
                    "FROM hits WHERE hit_type = ? ORDER BY id DESC LIMIT ?",
                    (hit_type, limit),
                )
            else:
                cursor.execute(
                    "SELECT id, timestamp, ip, hit_type, payload, extra_info "
                    "FROM hits ORDER BY id DESC LIMIT ?",
                    (limit,),
                )
            rows = cursor.fetchall()
            conn.close()
            return [
                {
                    "id": r[0],
                    "timestamp": r[1],
                    "ip": r[2],
                    "hit_type": r[3],
                    "payload": r[4],
                    "extra_info": r[5],
                }
                for r in rows
            ]
        except Exception:
            return []

    @staticmethod
    def get_hit_stats():
        """Return {total, geo, telemetry} counts for the admin API."""
        stats = {"total": 0, "geo": 0, "telemetry": 0}
        try:
            conn = sqlite3.connect(DatabaseManager.get_db_path())
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM hits")
            stats["total"] = cursor.fetchone()[0] or 0
            cursor.execute("SELECT COUNT(*) FROM hits WHERE hit_type = 'GEOLOCATION'")
            stats["geo"] = cursor.fetchone()[0] or 0
            cursor.execute("SELECT COUNT(*) FROM hits WHERE hit_type = 'DEEP_TELEMETRY'")
            stats["telemetry"] = cursor.fetchone()[0] or 0
            conn.close()
        except Exception:
            pass
        return stats