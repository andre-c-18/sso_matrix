"""
Decorators untuk proteksi route
"""
from functools import wraps
from flask import session, redirect, url_for, request, jsonify
from utils.token import verify_access_token
from utils.db import query_one


def login_required(f):
    """Proteksi route - harus login ke SSO dashboard"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'admin_user_id' not in session:
            return redirect(url_for('admin.login_page', next=request.url))
        return f(*args, **kwargs)
    return decorated


def superadmin_required(f):
    """Hanya superadmin"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'admin_user_id' not in session:
            return redirect(url_for('admin.login_page'))
        if session.get('admin_role') != 'superadmin':
            return jsonify({'error': 'Akses ditolak'}), 403
        return f(*args, **kwargs)
    return decorated


def api_token_required(f):
    """Proteksi API endpoint dengan Bearer token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Token tidak ditemukan'}), 401
        token = auth_header[7:]
        try:
            payload = verify_access_token(token)
            request.token_payload = payload
        except Exception as e:
            return jsonify({'error': str(e)}), 401
        return f(*args, **kwargs)
    return decorated
