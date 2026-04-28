"""
reset_admin.py — Reset password superadmin
Jalankan sekali: python reset_admin.py
"""
import bcrypt
from app import create_app
from extensions import db
from sqlalchemy import text

password = 'Admin@1234'
hashed   = bcrypt.hashpw(password.encode(), bcrypt.gensalt(12)).decode()

app = create_app()
with app.app_context():
    with db.engine.begin() as conn:
        conn.execute(
            text("UPDATE users SET password_hash = :pw WHERE username = 'superadmin'"),
            {'pw': hashed}
        )
    print(f"✓ Password superadmin berhasil direset ke: {password}")
    print(f"  Hash: {hashed}")
