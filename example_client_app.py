"""
=======================================================
CONTOH INTEGRASI SSO DI APLIKASI CLIENT
Flask - Python 3.9
=======================================================

Ini adalah contoh bagaimana aplikasi Anda menggunakan SSO.
Salin file ini ke aplikasi Anda dan sesuaikan.
"""

import os
import requests
from functools import wraps
from typing import Optional
from flask import Flask, request, redirect, session, jsonify, render_template_string

app = Flask(__name__)
app.secret_key = 'secret-aplikasi-client-anda'

# ====================================================
# Konfigurasi SSO - dapatkan dari SSO Admin Panel
# ====================================================
SSO_URL      = 'http://localhost:5005'          # URL SSO Server
APP_ID       = 'example_c44ad528'         # App ID dari SSO Admin
APP_SECRET   = 'Jf1XPwdQxrReFJLgIVh_WDzLRgvVkkcaZMxu5eHEy64'     # App Secret dari SSO Admin
CALLBACK_URL = 'http://localhost:8080/auth/callback'  # URL callback app ini


# ====================================================
# Helper: verifikasi token ke SSO server
# ====================================================
def verify_sso_token(access_token: str) -> Optional[dict]:
    """Verifikasi token ke SSO server, return user data atau None"""
    try:
        resp = requests.post(
            f'{SSO_URL}/api/verify',
            json={'access_token': access_token},
            headers={
                'X-App-ID': APP_ID,
                'X-App-Secret': APP_SECRET,
                'Content-Type': 'application/json',
            },
            timeout=5
        )
        data = resp.json()
        if resp.ok and data.get('valid'):
            return data['user']
    except Exception as e:
        print(f'SSO verify error: {e}')
    return None


def refresh_sso_token(refresh_token: str) -> Optional[dict]:
    """Refresh access token"""
    try:
        resp = requests.post(
            f'{SSO_URL}/api/refresh',
            json={'refresh_token': refresh_token},
            headers={
                'X-App-ID': APP_ID,
                'X-App-Secret': APP_SECRET,
            },
            timeout=5
        )
        if resp.ok:
            return resp.json()
    except Exception:
        pass
    return None


# ====================================================
# Decorator: proteksi route dengan SSO
# ====================================================
def sso_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        access_token = session.get('access_token')
        if not access_token:
            # Redirect ke SSO login
            return redirect(f'{SSO_URL}/sso/login?app_id={APP_ID}&redirect={CALLBACK_URL}')

        user = verify_sso_token(access_token)
        if not user:
            # Token expired, coba refresh
            refresh_tok = session.get('refresh_token')
            if refresh_tok:
                new_tokens = refresh_sso_token(refresh_tok)
                if new_tokens:
                    session['access_token'] = new_tokens['access_token']
                    session['refresh_token'] = new_tokens['refresh_token']
                    user = verify_sso_token(new_tokens['access_token'])

        if not user:
            session.clear()
            return redirect(f'{SSO_URL}/sso/login?app_id={APP_ID}&redirect={CALLBACK_URL}')

        request.current_user = user
        return f(*args, **kwargs)
    return decorated


def role_required(*roles):
    """Decorator role-based access"""
    def decorator(f):
        @wraps(f)
        @sso_required
        def decorated(*args, **kwargs):
            if request.current_user.get('role') not in roles:
                return jsonify({'error': 'Akses ditolak', 'required_role': list(roles)}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator


# ====================================================
# Route: Callback dari SSO
# ====================================================
@app.route('/auth/callback')
def sso_callback():
    """
    SSO akan redirect ke sini setelah login berhasil.
    URL: /auth/callback?access_token=...&refresh_token=...&expires_in=...
    """
    access_token  = request.args.get('access_token')
    refresh_token = request.args.get('refresh_token')
    expires_in    = request.args.get('expires_in')

    if not access_token:
        return 'Login gagal: token tidak ditemukan', 400

    # Verifikasi token
    user = verify_sso_token(access_token)
    if not user:
        return 'Login gagal: token tidak valid', 401

    # Simpan ke session
    session['access_token']  = access_token
    session['refresh_token'] = refresh_token
    session['user']          = user

    # Redirect ke halaman utama
    return redirect('/')


# ====================================================
# Route: Logout
# ====================================================
@app.route('/logout')
def logout():
    # Revoke token di SSO
    if session.get('access_token'):
        try:
            requests.post(f'{SSO_URL}/api/revoke',
                          json={'access_token': session['access_token']}, timeout=3)
        except Exception:
            pass
    session.clear()
    # Redirect ke logout SSO juga (opsional)
    return redirect(f'{SSO_URL}/sso/logout?redirect=http://localhost:8080')


# ====================================================
# Contoh routes yang diproteksi
# ====================================================
@app.route('/')
@sso_required
def home():
    user = request.current_user
    return render_template_string('''
    <h1>Halo, {{ user.full_name }}!</h1>
    <p>Email: {{ user.email }}</p>
    <p>Role: <strong>{{ user.role }}</strong></p>
    <a href="/dashboard">Dashboard</a> |
    <a href="/admin-only">Admin Only</a> |
    <a href="/logout">Logout</a>
    ''', user=user)


@app.route('/dashboard')
@sso_required
def dashboard():
    return jsonify({
        'message': f"Dashboard untuk {request.current_user['full_name']}",
        'user': request.current_user
    })


@app.route('/admin-only')
@role_required('superadmin', 'admin')
def admin_only():
    return jsonify({
        'message': 'Halaman khusus admin',
        'user': request.current_user
    })


@app.route('/manager-up')
@role_required('superadmin', 'admin', 'manager')
def manager_up():
    return jsonify({'message': 'Akses manager ke atas'})


# ====================================================
# Contoh: verifikasi token via API (untuk SPA/mobile)
# ====================================================
@app.route('/api/me')
def api_me():
    """Endpoint untuk SPA/mobile: kirim Bearer token di header"""
    auth = request.headers.get('Authorization', '')
    if not auth.startswith('Bearer '):
        return jsonify({'error': 'Unauthorized'}), 401

    user = verify_sso_token(auth[7:])
    if not user:
        return jsonify({'error': 'Token tidak valid'}), 401

    return jsonify({'user': user})


if __name__ == '__main__':
    app.run(port=8080, debug=True)
