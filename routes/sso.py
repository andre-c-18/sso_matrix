import os
from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from utils.db import query_one, execute
from utils.auth import check_password, log_audit
from utils.token import generate_access_token, verify_access_token

sso_bp = Blueprint('sso', __name__)


def _get_access_matrix(app_id: str, role_id: int) -> dict:
    """Ambil access matrix untuk role ini di app ini."""
    import json
    row = query_one(
        """SELECT am.standard_access, am.right_config
           FROM access_matrix am
           WHERE am.app_id = :app_id AND am.role_id = :role_id""",
        {'app_id': app_id, 'role_id': role_id}
    )
    if row:
        sa = row['standard_access']
        if isinstance(sa, str):
            try: sa = json.loads(sa)
            except: sa = []
        rc = row['right_config']
        if isinstance(rc, str):
            try: rc = json.loads(rc)
            except: rc = {}
        return {
            'standard_access': sa or [],
            'right_config':    rc or {},
        }
    # Default fallback — belum dikonfigurasi = view only
    defaults = {1: ['view','edit','export','approve','upload','delete'],
                2: ['view','edit','export','approve','upload','delete'],
                3: ['view','edit','export','approve'],
                4: ['view']}
    return {
        'standard_access': defaults.get(role_id, ['view']),
        'right_config':    {},
    }


@sso_bp.route('/login', methods=['GET', 'POST'])
def login():
    app_id      = request.args.get('app_id') or request.form.get('app_id')
    redirect_to = request.args.get('redirect') or request.form.get('redirect')
    error = None
    app   = None

    if app_id:
        app = query_one(
            "SELECT * FROM applications WHERE app_id = :app_id AND is_active = 1",
            {'app_id': app_id}
        )

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        app_id   = request.form.get('app_id', '')

        if not username or not password:
            error = 'Username dan password wajib diisi'
        else:
            user = query_one(
                """SELECT u.*, r.name as role_name FROM users u
                   JOIN roles r ON r.id = u.role_id
                   WHERE (u.username = :u OR u.email = :u) AND u.is_active = 1""",
                {'u': username}
            )
            if not user or not check_password(password, user['password_hash']):
                error = 'Username atau password salah'
                log_audit(None, 'LOGIN_FAILED', f'username={username}', request.remote_addr, app_id)
            else:
                app = query_one(
                    "SELECT * FROM applications WHERE app_id = :app_id AND is_active = 1",
                    {'app_id': app_id}
                ) if app_id else None

                if app_id and not app:
                    error = 'Aplikasi tidak ditemukan atau tidak aktif'
                else:
                    # Ambil access matrix
                    matrix = _get_access_matrix(
                        app['id'] or 'sso_admin', user['role_id']
                    )

                    # Gabungkan ke user dict → masuk JWT
                    user_data = dict(user)
                    user_data['standard_access'] = matrix['standard_access']
                    user_data['right_config']    = matrix['right_config']

                    token_data = generate_access_token(user_data, app_id or 'sso_admin')

                    execute("UPDATE users SET last_login = NOW() WHERE id = :id", {'id': user['id']})
                    log_audit(user['id'], 'LOGIN_SUCCESS',
                              f"app={app_id} access={matrix['standard_access']}",
                              request.remote_addr, app_id)

                    callback_url = redirect_to or (app['callback_url'] if app else None)

                    if callback_url and app:
                        sep      = '&' if '?' in callback_url else '?'
                        full_url = (
                            f"{callback_url}{sep}"
                            f"access_token={token_data['access_token']}"
                            f"&expires_in={token_data['expires_in']}"
                        )
                        if app.get('auto_redirect'):
                            return redirect(full_url)
                        return render_template(
                            'sso/confirm.html', app=app, full_url=full_url,
                            user=user, token_data=token_data,
                        )

                    session['admin_user_id'] = user['id']
                    session['admin_username'] = user['username']
                    session['admin_role']     = user['role_name']
                    return redirect(url_for('admin.dashboard'))

    return render_template('sso/login.html', app=app, app_id=app_id,
                           error=error, redirect_to=redirect_to)


@sso_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    user_id = session.get('admin_user_id')
    if user_id:
        log_audit(user_id, 'LOGOUT', None, request.remote_addr)
    session.clear()
    return redirect(request.args.get('redirect') or url_for('sso.login'))


@sso_bp.route('/token-info', methods=['GET'])
def token_info():
    token = request.args.get('token')
    if not token:
        return jsonify({'error': 'token parameter required'}), 400
    try:
        payload = verify_access_token(token)
        return jsonify({'valid': True, 'payload': payload})
    except Exception as e:
        return jsonify({'valid': False, 'error': str(e)}), 401
