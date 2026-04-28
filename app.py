"""
SSO Application - Main Entry Point
Python 3.9 + Flask + SQLAlchemy + PyMySQL
"""
import os
from flask import Flask, redirect, url_for
from dotenv import load_dotenv

load_dotenv()

from extensions import db
from routes.sso import sso_bp
from routes.api import api_bp
from routes.admin import admin_bp
from routes.rights import rights_bp


def create_app():
    app = Flask(__name__)

    # Flask config
    app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-change-in-production')
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

    # SQLAlchemy config
    user = os.getenv('MYSQL_USER', 'root')
    pw   = os.getenv('MYSQL_PASSWORD', '')
    host = os.getenv('MYSQL_HOST', 'localhost')
    port = os.getenv('MYSQL_PORT', '3306')
    db_name = os.getenv('MYSQL_DB', 'sso_db')

    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f"mysql+pymysql://{user}:{pw}@{host}:{port}/{db_name}"
        f"?charset=utf8mb4"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_recycle': 280,   # recycle koneksi sebelum MySQL timeout (default 8 jam)
        'pool_pre_ping': True, # cek koneksi sebelum dipakai
    }

    # Init SQLAlchemy
    db.init_app(app)

    # Import models agar SQLAlchemy tahu tabel yang ada
    with app.app_context():
        from models import Role, User, Application, AuditLog, AccessMatrix

    # Register blueprints
    app.register_blueprint(sso_bp, url_prefix='/sso')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(rights_bp, url_prefix='/rights')

    # Context processors
    from utils.context import register_context_processors
    register_context_processors(app)

    @app.route('/')
    def index():
        return redirect(url_for('admin.dashboard'))

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5005)),
        debug=os.getenv('FLASK_DEBUG', 'True') == 'True'
    )
