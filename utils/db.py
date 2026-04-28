"""
Database utility - wrapper SQLAlchemy
Fungsi query_one, query_all, execute dipertahankan agar
routes tidak perlu banyak diubah.
"""
from extensions import db
from sqlalchemy import text
from datetime import datetime, timezone


def _utc_now_str():
    return datetime.now(timezone.utc)


def query_one(sql, params=None):
    """Ambil satu baris, return dict atau None"""
    with db.engine.connect() as conn:
        conn.execute(text("SET time_zone = '+00:00'"))
        result = conn.execute(text(sql), params or {})
        row = result.mappings().first()
        return dict(row) if row else None


def query_all(sql, params=None):
    """Ambil semua baris, return list of dict"""
    with db.engine.connect() as conn:
        conn.execute(text("SET time_zone = '+00:00'"))
        result = conn.execute(text(sql), params or {})
        return [dict(row) for row in result.mappings()]


def execute(sql, params=None):
    """Eksekusi INSERT/UPDATE/DELETE, return lastrowid"""
    with db.engine.begin() as conn:
        conn.execute(text("SET time_zone = '+00:00'"))
        result = conn.execute(text(sql), params or {})
        return result.lastrowid


def execute_many(sql, params_list):
    """Batch INSERT/UPDATE"""
    with db.engine.begin() as conn:
        conn.execute(text("SET time_zone = '+00:00'"))
        result = conn.execute(text(sql), params_list)
        return result.rowcount
