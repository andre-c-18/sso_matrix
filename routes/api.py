from flask import Blueprint, request, jsonify
from utils.db import query_one, query_all
from utils.token import verify_access_token, generate_access_token
from utils.auth import log_audit

api_bp = Blueprint('api', __name__)


def _app_auth():
    app_id     = request.headers.get('X-App-ID')
    app_secret = request.headers.get('X-App-Secret')

    if not app_id and request.is_json and request.json:
        app_id     = request.json.get('app_id')
        app_secret = request.json.get('app_secret')

    if not app_id:
        app_id     = request.form.get('app_id')
        app_secret = request.form.get('app_secret')

    if not app_id or not app_secret:
        return None, jsonify({'error': 'X-App-ID dan X-App-Secret wajib'}), 401

    app = query_one(
        "SELECT * FROM applications WHERE app_id = :app_id AND app_secret = :secret AND is_active = 1",
        {'app_id': app_id, 'secret': app_secret}
    )
    if not app:
        return None, jsonify({'error': 'Aplikasi tidak valid'}), 401

    return app, None, None


# =============================================
# POST /api/verify
# Verifikasi access token — cukup validasi JWT
# Tidak perlu cek DB lagi
# =============================================
@api_bp.route('/verify', methods=['POST'])
def verify_token():
    app, err_resp, err_code = _app_auth()
    if err_resp:
        return err_resp, err_code

    data  = request.get_json() or {}
    token = data.get('access_token')
    if not token:
        return jsonify({'error': 'access_token wajib'}), 400

    try:
        payload = verify_access_token(token, app['app_id'])
    except Exception as e:
        return jsonify({'valid': False, 'error': str(e)}), 401

    # Ambil data user terbaru dari DB untuk pastikan user masih aktif
    user = query_one(
        """SELECT u.id, u.username, u.email, u.full_name, u.is_active,
                  r.name as role_name, r.id as role_id
           FROM users u JOIN roles r ON r.id = u.role_id
           WHERE u.id = :uid""",
        {'uid': payload['user_id']}
    )

    if not user or not user['is_active']:
        return jsonify({'valid': False, 'error': 'User tidak aktif'}), 401
    
    from routes.rights import get_merged_access 
    permissions, source = get_merged_access(user['id'], app['id'])

    print(f"DEBUG: User ID: {user['id']}, App ID: {app['id']}")
    print(f"DEBUG: Permissions result: {permissions}")
    print(f"DEBUG: Source: {source}")

    return jsonify({
        'valid': True,
        'user': {
            'id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'full_name': user['full_name'],
            'role': user['role_name'],
            'role_id': user['role_id'],

            'standard_access': permissions['standard_access'] if permissions else [],
            'paths': permissions['paths'] if permissions else [],
            'extra_config': permissions['extra_config'] if permissions else {},
            'data_source': source
        },
        'token_info': {
            'expires_at': payload.get('exp'),
            'issued_at':  payload.get('iat'),
            'app_id':     payload.get('app_id'),
        }
    })


# =============================================
# POST /api/revoke — tetap ada tapi no-op
# Agar aplikasi client tidak error saat panggil
# =============================================
@api_bp.route('/revoke', methods=['POST'])
def revoke_token():
    # Tanpa token_sessions, revoke tidak bisa dilakukan
    # Token akan expired sendiri sesuai JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    return jsonify({
        'success': True,
        'message': 'Token akan expired sesuai waktu berlakunya'
    })


# =============================================
# GET /api/user — info user dari Bearer token
# =============================================
@api_bp.route('/user', methods=['GET'])
def user_info():
    auth = request.headers.get('Authorization', '')
    if not auth.startswith('Bearer '):
        return jsonify({'error': 'Bearer token required'}), 401

    token = auth[7:]
    try:
        payload = verify_access_token(token)
    except Exception as e:
        return jsonify({'error': str(e)}), 401

    user = query_one(
        """SELECT u.id, u.username, u.email, u.full_name, u.last_login, u.created_at,
                  r.name as role_name, r.id as role_id, r.description as role_description
           FROM users u JOIN roles r ON r.id = u.role_id
           WHERE u.id = :uid AND u.is_active = 1""",
        {'uid': payload['user_id']}
    )
    if not user:
        return jsonify({'error': 'User tidak ditemukan'}), 404

    return jsonify({
        'id':        user['id'],
        'username':  user['username'],
        'email':     user['email'],
        'full_name': user['full_name'],
        'role': {
            'id':          user['role_id'],
            'name':        user['role_name'],
            'description': user['role_description'],
        },
        'last_login':   str(user['last_login']) if user['last_login'] else None,
        'member_since': str(user['created_at']),
    })


# =============================================
# GET /api/users — list user untuk impersonate
# =============================================
@api_bp.route('/users', methods=['GET'])
def list_users():
    app, err_resp, err_code = _app_auth()
    if err_resp:
        return err_resp, err_code

    username_filter = request.args.get('username', '')

    if username_filter:
        users = query_all(
            """SELECT u.id, u.username, u.email, u.full_name, u.is_active,
                      r.name as role_name, r.id as role_id
               FROM users u JOIN roles r ON r.id = u.role_id
               WHERE u.username LIKE :q AND u.is_active = 1
               ORDER BY u.full_name""",
            {'q': f'%{username_filter}%'}
        )
        return jsonify({'user': users[0] if len(users) == 1 else None, 'users': users})

    users = query_all(
        """SELECT u.id, u.username, u.email, u.full_name, u.is_active,
                  r.name as role_name, r.id as role_id
           FROM users u JOIN roles r ON r.id = u.role_id
           WHERE u.is_active = 1
           ORDER BY r.id ASC, u.full_name ASC"""
    )
    return jsonify({'users': users})


# =============================================
# GET /api/users/<id>
# =============================================
@api_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    app, err_resp, err_code = _app_auth()
    if err_resp:
        return err_resp, err_code

    user = query_one(
        """SELECT u.id, u.username, u.email, u.full_name, u.is_active,
                  r.name as role_name, r.id as role_id
           FROM users u JOIN roles r ON r.id = u.role_id
           WHERE u.id = :uid""",
        {'uid': user_id}
    )
    if not user:
        return jsonify({'error': 'User tidak ditemukan'}), 404
    return jsonify({'user': user})


# =============================================
# POST /api/impersonate
# =============================================
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

@api_bp.route('/impersonate', methods=['POST'])
def generate_impersonate_token():
    app, err_resp, err_code = _app_auth()
    if err_resp:
        return err_resp, err_code

    target_id = request.json.get('target_user_id')
    if not target_id:
        return jsonify({'error': 'target_user_id diperlukan'}), 400

    user = query_one(
        """SELECT u.id, u.username, u.email, u.full_name, u.is_active,
                  r.name as role_name, r.id as role_id
           FROM users u JOIN roles r ON r.id = u.role_id
           WHERE u.id = :uid""",
        {'uid': target_id}
    )

    if not user:
        return jsonify({'error': 'User tidak ditemukan'}), 404
    if user['is_active'] != 1:
        return jsonify({'error': 'Tidak dapat login ke akun yang nonaktif'}), 403
    if user['role_name'] == 'superadmin':
        return jsonify({'error': 'Tidak dapat impersonate ke sesama superadmin'}), 403

    matrix = _get_access_matrix(
        app['id'] if app else 'sso_admin', 
        user['role_id']
    )

    user_data = dict(user)
    user_data['standard_access'] = matrix['standard_access']
    user_data['right_config']    = matrix['right_config']

    app_id_from_request = request.headers.get('X-App-ID')
    token_data = generate_access_token(user_data, app_id_from_request or 'sso_admin')

    return jsonify({
        'message':      'Impersonation successful',
        'access_token': token_data['access_token'],
        'expires_in':   token_data['expires_in'],
        'expires_at':   token_data['expires_at'],
        'user':         user
    }), 200
