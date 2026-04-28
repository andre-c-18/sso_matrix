"""
rights.py — Access Matrix dengan standard_access (6 aksi) + right_config (paths + key-value)
"""
import json
from flask import Blueprint, render_template, request, jsonify, session
from utils.db import query_one, query_all, execute
from utils.decorators import login_required
from utils.auth import log_audit

rights_bp = Blueprint('rights', __name__)

ACTIONS = [
    {'key': 'view',    'label': 'View',    'icon': 'bi-eye',          'color': 'primary',   'desc': 'Lihat data'},
    {'key': 'add',    'label': 'Add',    'icon': 'bi-plus',          'color': 'primary',   'desc': 'Tambah data'},
    {'key': 'edit',    'label': 'Edit',    'icon': 'bi-pencil',       'color': 'warning',   'desc': 'Ubah data'},
    {'key': 'export',  'label': 'Export',  'icon': 'bi-download',     'color': 'success',   'desc': 'Export/unduh'},
    {'key': 'approve', 'label': 'Approve', 'icon': 'bi-check-circle', 'color': 'info',      'desc': 'Setujui data'},
    {'key': 'upload',  'label': 'Upload',  'icon': 'bi-upload',       'color': 'secondary', 'desc': 'Upload file'},
    {'key': 'delete',  'label': 'Delete',  'icon': 'bi-trash',        'color': 'danger',    'desc': 'Hapus data'},
]
ACTION_KEYS = [a['key'] for a in ACTIONS]

# ── GET /rights/ ──────────────────────────────────────────────
@rights_bp.route('/')
@login_required
def index():
    apps = query_all("SELECT id, app_id, app_name, is_active FROM applications ORDER BY app_name")

    for app in apps:
        rows = query_all(
            """SELECT r.name as role_name, am.standard_access
                FROM roles r
                LEFT JOIN access_matrix am ON am.role_id = r.id AND am.app_id = :app_id
                ORDER BY r.id""",
            {'app_id': app['id']}
        )
        for row in rows:
            sa = row['standard_access']
            if isinstance(sa, str):
                try: sa = json.loads(sa)
                except: sa = []
            row['standard_access'] = sa or []
        app['matrix_summary'] = rows

    return render_template('admin/rights/index.html', apps=apps, actions=ACTIONS)


# ── GET /rights/<app_id> ──────────────────────────────────────
@rights_bp.route('/<app_id>')
@login_required
def app_rights(app_id):
    app = query_one("SELECT * FROM applications WHERE app_id = :app_id", {'app_id': app_id})

    if not app:
        return "Aplikasi tidak ditemukan", 404

    rows = query_all(
        """SELECT r.id as role_id, r.name as role_name,
                    am.id as matrix_id, am.standard_access, am.right_config
            FROM roles r
            LEFT JOIN access_matrix am ON am.role_id = r.id AND am.app_id = :app_id
            ORDER BY r.id""",
        {'app_id': app['id']}
    )

    role_matrix = []
    for row in rows:
        sa = row['standard_access']
        if isinstance(sa, str):
            try: sa = json.loads(sa)
            except: sa = []
        sa = sa or []

        rc = row['right_config']
        if isinstance(rc, str):
            try: rc = json.loads(rc)
            except: rc = {}
        rc = rc or {}

        paths      = rc.pop('paths', [])
        extra_cfg  = rc

        role_matrix.append({
            'role_id':        row['role_id'],
            'role_name':      row['role_name'],
            'standard_access': sa,
            'paths':          paths,
            'extra_config':   extra_cfg,
            'is_saved':       row['matrix_id'] is not None,
        })

    return render_template(
        'admin/rights/app_rights.html',
        app=app,
        actions=ACTIONS,
        role_matrix=role_matrix,
    )


# ── POST /rights/<app_id>/save ────────────────────────────────
@rights_bp.route('/<app_id>/save', methods=['POST'])
@login_required
def save_matrix(app_id):
    app = query_one("SELECT id FROM applications WHERE app_id = :app_id", {'app_id': app_id})

    if not app:
        return jsonify({'error': 'Aplikasi tidak ditemukan'}), 404

    data   = request.get_json() or {}
    matrix = data.get('matrix', {})

    try:
        for role_id_str, cfg in matrix.items():
            role_id = int(role_id_str)

            raw_sa  = cfg.get('standard_access', [])
            std_acc = [a for a in raw_sa if a in ACTION_KEYS]

            paths = [p.strip() for p in cfg.get('paths', []) if p.strip()]

            extra = cfg.get('extra', {})

            right_config = {'paths': paths, **extra}

            std_acc_json = json.dumps(std_acc)
            right_cfg_json = json.dumps(right_config)

            existing = query_one(
                "SELECT id FROM access_matrix WHERE role_id = :rid AND app_id = :app_id",
                {'rid': role_id, 'app_id': app['id']}
            )
            if existing:
                execute(
                    """UPDATE access_matrix
                        SET standard_access = :sa, right_config = :rc
                        WHERE role_id = :rid AND app_id = :app_id""",
                    {'sa': std_acc_json, 'rc': right_cfg_json, 'rid': role_id, 'app_id': app['id']}
                )
            else:
                execute(
                    """INSERT INTO access_matrix (role_id, app_id, standard_access, right_config)
                        VALUES (:rid, :app_id, :sa, :rc)""",
                    {'rid': role_id, 'app_id': app['id'], 'sa': std_acc_json, 'rc': right_cfg_json}
                )

        log_audit(session['admin_user_id'], 'ACCESS_MATRIX_SAVED', f'app={app_id}', request.remote_addr)
        return jsonify({'success': True})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ── GET /rights/user───────────────────────    
@rights_bp.route('/user-overrides')
@login_required
def user_override_list():
    users = query_all("""
        SELECT u.id, u.username, u.full_name, r.name as role_name 
        FROM users u 
        JOIN roles r ON u.role_id = r.id 
        ORDER BY u.full_name ASC
    """)
    
    apps = query_all("SELECT id, app_id, app_name FROM applications WHERE is_active = 1")
    
    return render_template('admin/rights/user_list.html', users=users, apps=apps)
    
# ── GET /rights/user/<user_id>/<app_id> ───────────────────────
@rights_bp.route('/user/<int:user_id>/<app_id>')
@login_required
def user_rights_detail(user_id, app_id):
    user = query_one("""
        SELECT u.id, u.username, u.full_name, r.name as role_name 
        FROM users u 
        JOIN roles r ON u.role_id = r.id 
        WHERE u.id = :uid""", {'uid': user_id})
    
    app = query_one("SELECT id, app_id, app_name FROM applications WHERE app_id = :app_id", {'app_id': app_id})

    row = query_one(
        "SELECT standard_access, right_config FROM user_access_overrides WHERE user_id = :uid AND app_id = :aid",
        {'uid': user_id, 'aid': app['id']}
    )

    sa = []
    rc = {}

    if row:
        if isinstance(row['standard_access'], str):
            try: sa = json.loads(row['standard_access'])
            except: sa = []
        
        if isinstance(row['right_config'], str):
            try: rc = json.loads(row['right_config'])
            except: rc = {}

    paths = rc.pop('paths', [])
    extra_config = rc

    return render_template(
        'admin/rights/user_override.html',
        user=user,
        app=app,
        actions=ACTIONS,
        standard_access=sa,
        paths=paths,
        extra_config=extra_config
    )

# ── POST /rights/user/save ────────────────────────────────────
@rights_bp.route('/user/save', methods=['POST'])
@login_required
def save_user_override():
    data = request.get_json()
    user_id = data.get('user_id')
    app_id = data.get('app_internal_id')
    
    std_acc = json.dumps(data.get('standard_access', []))
    right_cfg = json.dumps(data.get('right_config', {}))

    existing = query_one("SELECT id FROM user_access_overrides WHERE user_id = :uid AND app_id = :aid",
                        {'uid': user_id, 'aid': app_id})
    
    if existing:
        execute("""UPDATE user_access_overrides SET standard_access = :sa, right_config = :rc 
                    WHERE user_id = :uid AND app_id = :aid""",
                {'sa': std_acc, 'rc': right_cfg, 'uid': user_id, 'aid': app_id})
    else:
        execute("""INSERT INTO user_access_overrides (user_id, app_id, standard_access, right_config) 
                    VALUES (:uid, :aid, :sa, :rc)""",
                {'uid': user_id, 'aid': app_id, 'sa': std_acc, 'rc': right_cfg})

    return jsonify({'success': True})

# ── POST /rights/user/delete ──────────────────────────────────
@rights_bp.route('/user/delete', methods=['POST'])
@login_required
def delete_user_override():
    data = request.get_json()
    user_id = data.get('user_id')
    app_id = data.get('app_id')

    if not user_id or not app_id:
        return jsonify({'success': False, 'error': 'Parameter tidak lengkap'}), 400

    try:
        execute(
            "DELETE FROM user_access_overrides WHERE user_id = :uid AND app_id = :aid",
            {'uid': user_id, 'aid': app_id}
        )
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ── GET /rights/api/<app_id> — untuk aplikasi client ─────────
def get_merged_access(user_id, app_id):
    row = query_one(
        "SELECT standard_access, right_config FROM user_access_overrides WHERE user_id = :uid AND app_id = :aid",
        {'uid': user_id, 'aid': app_id}
    )
    source = "USER_OVERRIDE"    

    if not row:
        row = query_one("""
            SELECT am.standard_access, am.right_config 
            FROM access_matrix am
            JOIN users u ON u.role_id = am.role_id
            WHERE u.id = :uid AND am.app_id = :aid""",
            {'uid': user_id, 'aid': app_id})
        source = "ROLE_DEFAULT"

    if not row:
        return None, "NONE"

    try:
        sa = json.loads(row['standard_access']) if row['standard_access'] else []
    except:
        sa = []

    try:
        rc = json.loads(row['right_config']) if row['right_config'] else {}
    except:
        rc = {}

    paths = rc.pop('paths', [])
    
    return {
        'standard_access': sa,
        'paths': paths,
        'extra_config': rc
    }, source
