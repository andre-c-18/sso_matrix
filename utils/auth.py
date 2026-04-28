import bcrypt
import os
from utils.db import execute, query_one

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(12)).decode('utf-8')

def check_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def log_audit(user_id, action, detail=None, ip=None, app_id=None):
    try:
        execute(
            "INSERT INTO audit_logs (user_id, app_id, action, detail, ip_address) VALUES (:uid, :app_id, :action, :detail, :ip)",
            {'uid': user_id, 'app_id': app_id, 'action': action, 'detail': detail, 'ip': ip}
        )
    except Exception:
        pass
