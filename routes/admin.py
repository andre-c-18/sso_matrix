import os
import secrets
from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, flash
from utils.db import query_one, query_all, execute
from utils.auth import hash_password, check_password, log_audit
from utils.decorators import login_required, superadmin_required

admin_bp = Blueprint('admin', __name__)
SSO_BASE = os.getenv('SSO_BASE_URL', 'http://localhost:5000')


# =============================================
# LOGIN / LOGOUT ADMIN
# =============================================
@admin_bp.route('/login', methods=['GET', 'POST'])
def login_page():
    if 'admin_user_id' in session:
        return redirect(url_for('admin.dashboard'))
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        user = query_one(
            """SELECT u.*, r.name as role_name FROM users u
               JOIN roles r ON r.id = u.role_id
               WHERE (u.username = :u OR u.email = :u) AND u.is_active = 1""",
            {'u': username}
        )
        if user and check_password(password, user['password_hash']):
            if user['role_name'] not in ('superadmin', 'admin'):
                error = 'Anda tidak memiliki akses ke panel admin'
            else:
                session['admin_user_id'] = user['id']
                session['admin_username'] = user['username']
                session['admin_role']     = user['role_name']
                execute("UPDATE users SET last_login = NOW() WHERE id = :id", {'id': user['id']})
                log_audit(user['id'], 'ADMIN_LOGIN', None, request.remote_addr)
                return redirect(url_for('admin.dashboard'))
        else:
            error = 'Username atau password salah'
    return render_template('admin/login.html', error=error)


@admin_bp.route('/logout')
def logout():
    log_audit(session.get('admin_user_id'), 'ADMIN_LOGOUT', None, request.remote_addr)
    session.clear()
    return redirect(url_for('admin.login_page'))


# =============================================
# DASHBOARD
# =============================================
@admin_bp.route('/')
@login_required
def dashboard():
    stats = {
        'total_users':   query_one("SELECT COUNT(*) as c FROM users")['c'],
        'active_users':  query_one("SELECT COUNT(*) as c FROM users WHERE is_active = 1")['c'],
        'total_apps':    query_one("SELECT COUNT(*) as c FROM applications")['c'],
        'matrix_count':  query_one("SELECT COUNT(*) as c FROM access_matrix")['c'],
    }
    recent_logs = query_all(
        """SELECT al.*, u.username FROM audit_logs al
           LEFT JOIN users u ON u.id = al.user_id
           ORDER BY al.created_at DESC LIMIT 10"""
    )
    return render_template('admin/dashboard.html', stats=stats, recent_logs=recent_logs, sso_base=SSO_BASE)


# =============================================
# USERS MANAGEMENT
# =============================================
@admin_bp.route('/users')
@login_required
def users_list():
    search      = request.args.get('q', '')
    role_filter = request.args.get('role', '')

    sql    = "SELECT u.*, r.name as role_name FROM users u JOIN roles r ON r.id = u.role_id WHERE 1=1"
    params = {}
    if search:
        sql += " AND (u.username LIKE :s OR u.email LIKE :s OR u.full_name LIKE :s)"
        params['s'] = f'%{search}%'
    if role_filter:
        sql += " AND r.name = :role"
        params['role'] = role_filter
    sql += " ORDER BY u.created_at DESC"

    users = query_all(sql, params)
    roles = query_all("SELECT * FROM roles ORDER BY id")
    return render_template('admin/users.html', users=users, roles=roles,
                           search=search, role_filter=role_filter)


@admin_bp.route('/users/create', methods=['GET', 'POST'])
@login_required
def user_create():
    roles = query_all("SELECT * FROM roles ORDER BY id")
    error = None
    if request.method == 'POST':
        username  = request.form.get('username', '').strip()
        email     = request.form.get('email', '').strip()
        full_name = request.form.get('full_name', '').strip()
        password  = request.form.get('password', '')
        role_id   = request.form.get('role_id', 4)

        if not all([username, email, full_name, password]):
            error = 'Semua field wajib diisi'
        elif query_one(
            "SELECT id FROM users WHERE username = :u OR email = :e",
            {'u': username, 'e': email}
        ):
            error = 'Username atau email sudah digunakan'
        else:
            execute(
                """INSERT INTO users (username, email, password_hash, full_name, role_id, is_email_verified)
                   VALUES (:username, :email, :pw, :full_name, :role_id, 1)""",
                {'username': username, 'email': email, 'pw': hash_password(password),
                 'full_name': full_name, 'role_id': role_id}
            )
            log_audit(session['admin_user_id'], 'USER_CREATED', f'username={username}', request.remote_addr)
            flash('User berhasil dibuat', 'success')
            return redirect(url_for('admin.users_list'))
    return render_template('admin/user_form.html', roles=roles, error=error, user=None)


@admin_bp.route('/users/<int:uid>/edit', methods=['GET', 'POST'])
@login_required
def user_edit(uid):
    user = query_one(
        "SELECT u.*, r.name as role_name FROM users u JOIN roles r ON r.id = u.role_id WHERE u.id = :uid",
        {'uid': uid}
    )
    if not user:
        flash('User tidak ditemukan', 'error')
        return redirect(url_for('admin.users_list'))

    roles = query_all("SELECT * FROM roles ORDER BY id")
    error = None

    if request.method == 'POST':
        full_name    = request.form.get('full_name', '').strip()
        email        = request.form.get('email', '').strip()
        role_id      = request.form.get('role_id')
        is_active    = 1 if request.form.get('is_active') else 0
        new_password = request.form.get('new_password', '')

        existing = query_one(
            "SELECT id FROM users WHERE email = :email AND id != :uid",
            {'email': email, 'uid': uid}
        )
        if existing:
            error = 'Email sudah digunakan user lain'
        else:
            execute(
                "UPDATE users SET full_name = :fn, email = :email, role_id = :rid, is_active = :active WHERE id = :uid",
                {'fn': full_name, 'email': email, 'rid': role_id, 'active': is_active, 'uid': uid}
            )
            if new_password:
                execute("UPDATE users SET password_hash = :pw WHERE id = :uid",
                        {'pw': hash_password(new_password), 'uid': uid})
            log_audit(session['admin_user_id'], 'USER_UPDATED', f'user_id={uid}', request.remote_addr)
            flash('User berhasil diupdate', 'success')
            return redirect(url_for('admin.users_list'))

    return render_template('admin/user_form.html', roles=roles, error=error, user=user)


@admin_bp.route('/users/<int:uid>/toggle', methods=['POST'])
@login_required
def user_toggle(uid):
    if uid == session.get('admin_user_id'):
        return jsonify({'error': 'Tidak bisa menonaktifkan diri sendiri'}), 400
    user = query_one("SELECT is_active FROM users WHERE id = :uid", {'uid': uid})
    if user:
        new_status = 0 if user['is_active'] else 1
        execute("UPDATE users SET is_active = :s WHERE id = :uid", {'s': new_status, 'uid': uid})
        log_audit(session['admin_user_id'], 'USER_TOGGLE', f'user_id={uid},active={new_status}', request.remote_addr)
        return jsonify({'success': True, 'is_active': new_status})
    return jsonify({'error': 'User tidak ditemukan'}), 404


@admin_bp.route('/users/<int:uid>/reset-password', methods=['POST'])
@login_required
def admin_reset_password(uid):
    """Admin force reset password user langsung dari panel"""
    new_password = request.form.get('new_password', '')
    if len(new_password) < 8:
        flash('Password minimal 8 karakter', 'error')
        return redirect(url_for('admin.user_edit', uid=uid))
    execute("UPDATE users SET password_hash = :pw WHERE id = :uid",
            {'pw': hash_password(new_password), 'uid': uid})
    log_audit(session['admin_user_id'], 'ADMIN_RESET_PASSWORD', f'user_id={uid}', request.remote_addr)
    flash('Password berhasil direset', 'success')
    return redirect(url_for('admin.user_edit', uid=uid))


# =============================================
# APPLICATIONS MANAGEMENT
# =============================================
@admin_bp.route('/apps')
@login_required
def apps_list():
    apps = query_all(
        """SELECT a.*, u.username as creator FROM applications a
           LEFT JOIN users u ON u.id = a.created_by
           ORDER BY a.created_at DESC"""
    )
    return render_template('admin/apps.html', apps=apps, sso_base=SSO_BASE)


@admin_bp.route('/apps/create', methods=['GET', 'POST'])
@login_required
def app_create():
    error = None
    if request.method == 'POST':
        app_name        = request.form.get('app_name', '').strip()
        description     = request.form.get('description', '').strip()
        callback_url    = request.form.get('callback_url', '').strip()
        allowed_origins = request.form.get('allowed_origins', '').strip()
        auto_redirect   = 1 if request.form.get('auto_redirect') else 0

        if not all([app_name, callback_url]):
            error = 'Nama aplikasi dan callback URL wajib diisi'
        else:
            app_id     = app_name.lower().replace(' ', '_') + '_' + secrets.token_hex(4)
            app_secret = secrets.token_urlsafe(32)
            execute(
                """INSERT INTO applications
                   (app_id, app_secret, app_name, description, callback_url,
                    allowed_origins, auto_redirect, created_by)
                   VALUES (:app_id, :secret, :name, :desc, :cb, :origins, :ar, :created_by)""",
                {
                    'app_id': app_id, 'secret': app_secret, 'name': app_name,
                    'desc': description, 'cb': callback_url, 'origins': allowed_origins,
                    'ar': auto_redirect, 'created_by': session['admin_user_id']
                }
            )
            log_audit(session['admin_user_id'], 'APP_CREATED', f'app_id={app_id}', request.remote_addr)
            flash(f'Aplikasi berhasil dibuat. App ID: {app_id}', 'success')
            return redirect(url_for('admin.apps_list'))
    return render_template('admin/app_form.html', error=error, app=None)


@admin_bp.route('/apps/<app_id>/edit', methods=['GET', 'POST'])
@login_required
def app_edit(app_id):
    app = query_one("SELECT * FROM applications WHERE app_id = :app_id", {'app_id': app_id})
    if not app:
        flash('Aplikasi tidak ditemukan', 'error')
        return redirect(url_for('admin.apps_list'))
    error = None
    if request.method == 'POST':
        execute(
            """UPDATE applications SET app_name = :name, description = :desc,
               callback_url = :cb, allowed_origins = :origins,
               auto_redirect = :ar, is_active = :active
               WHERE app_id = :app_id""",
            {
                'name':    request.form.get('app_name', '').strip(),
                'desc':    request.form.get('description', '').strip(),
                'cb':      request.form.get('callback_url', '').strip(),
                'origins': request.form.get('allowed_origins', '').strip(),
                'ar':      1 if request.form.get('auto_redirect') else 0,
                'active':  1 if request.form.get('is_active') else 0,
                'app_id':  app_id,
            }
        )
        log_audit(session['admin_user_id'], 'APP_UPDATED', f'app_id={app_id}', request.remote_addr)
        flash('Aplikasi berhasil diupdate', 'success')
        return redirect(url_for('admin.apps_list'))
    return render_template('admin/app_form.html', error=error, app=app)


@admin_bp.route('/apps/<app_id>/regenerate-secret', methods=['POST'])
@login_required
def app_regenerate_secret(app_id):
    new_secret = secrets.token_urlsafe(32)
    execute("UPDATE applications SET app_secret = :s WHERE app_id = :app_id",
            {'s': new_secret, 'app_id': app_id})
    log_audit(session['admin_user_id'], 'APP_SECRET_REGENERATED', f'app_id={app_id}', request.remote_addr)
    return jsonify({'success': True, 'new_secret': new_secret})


@admin_bp.route('/apps/<app_id>/delete', methods=['POST'])
@login_required
def app_delete(app_id):
    execute("DELETE FROM applications WHERE app_id = :app_id", {'app_id': app_id})
    log_audit(session['admin_user_id'], 'APP_DELETED', f'app_id={app_id}', request.remote_addr)
    flash('Aplikasi berhasil dihapus', 'success')
    return redirect(url_for('admin.apps_list'))


# =============================================
# AUDIT LOGS
# =============================================
@admin_bp.route('/logs')
@login_required
def audit_logs():
    page     = int(request.args.get('page', 1))
    per_page = 50
    offset   = (page - 1) * per_page
    logs = query_all(
        """SELECT al.*, u.username FROM audit_logs al
           LEFT JOIN users u ON u.id = al.user_id
           ORDER BY al.created_at DESC
           LIMIT :limit OFFSET :offset""",
        {'limit': per_page, 'offset': offset}
    )
    total = query_one("SELECT COUNT(*) as c FROM audit_logs")['c']
    return render_template('admin/logs.html', logs=logs, page=page,
                           per_page=per_page, total=total)
