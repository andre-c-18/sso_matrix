-- =============================================
-- SSO Database Schema (tanpa token_sessions)
-- =============================================

CREATE DATABASE IF NOT EXISTS sso_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE sso_db;

CREATE TABLE IF NOT EXISTS roles (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(50) NOT NULL UNIQUE,
    description VARCHAR(255),
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO roles (name, description) VALUES
('superadmin', 'Super Administrator dengan akses penuh'),
('admin',      'Administrator dengan akses manajemen'),
('manager',    'Manager dengan akses terbatas'),
('user',       'Pengguna biasa');

CREATE TABLE IF NOT EXISTS users (
    id                INT AUTO_INCREMENT PRIMARY KEY,
    username          VARCHAR(100) NOT NULL UNIQUE,
    email             VARCHAR(255) NOT NULL UNIQUE,
    password_hash     VARCHAR(255) NOT NULL,
    full_name         VARCHAR(255) NOT NULL,
    role_id           INT NOT NULL DEFAULT 4,
    is_active         TINYINT(1) DEFAULT 1,
    is_email_verified TINYINT(1) DEFAULT 0,
    avatar_url        VARCHAR(500),
    last_login        TIMESTAMP NULL DEFAULT NULL,
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES roles(id)
);

-- Superadmin default (password: Admin@1234 — jalankan reset_admin.py dulu)
INSERT INTO users (username, email, password_hash, full_name, role_id, is_active, is_email_verified) VALUES
('superadmin', 'superadmin@sso.local', 'RUN_RESET_ADMIN_PY', 'Super Administrator', 1, 1, 1);

CREATE TABLE IF NOT EXISTS applications (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    app_id          VARCHAR(100) NOT NULL UNIQUE,
    app_secret      VARCHAR(255) NOT NULL,
    app_name        VARCHAR(255) NOT NULL,
    description     TEXT,
    callback_url    VARCHAR(500) NOT NULL,
    allowed_origins TEXT,
    auto_redirect   TINYINT(1) DEFAULT 0,
    is_active       TINYINT(1) DEFAULT 1,
    created_by      INT,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    user_id    INT,
    app_id     VARCHAR(100),
    action     VARCHAR(100) NOT NULL,
    detail     TEXT,
    ip_address VARCHAR(45),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_logs_user    ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_created ON audit_logs(created_at);


-- =============================================
-- ACCESS MATRIX
-- Tiap role per app punya: standard_access + right_config (JSON)
-- =============================================
CREATE TABLE IF NOT EXISTS access_matrix (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    role_id         INT          NOT NULL,
    app_id          VARCHAR(100) NOT NULL,
    standard_access JSON         NOT NULL DEFAULT ('[]'),  -- [view,edit,export,approve,upload,delete]
    -- own | department | all
    right_config    JSON         DEFAULT NULL,
    -- Contoh: {"can_export": true, "can_delete": false, "max_records": 1000}
    -- Bebas diisi sesuai kebutuhan aplikasi
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_role_app (role_id, app_id),
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
    FOREIGN KEY (app_id)  REFERENCES applications(app_id) ON DELETE CASCADE
);
