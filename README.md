# 🔐 MySSO — Simple Single Sign-On

Aplikasi SSO sederhana menggunakan **Python 3.9 + Flask + MySQL**.

---

## 📁 Struktur Project

```
sso_app/
├── app.py                   # Entry point Flask
├── requirements.txt         # Dependencies
├── schema.sql               # Database schema MySQL
├── .env.example             # Template konfigurasi
├── example_client_app.py    # Contoh integrasi di app client
│
├── routes/
│   ├── sso.py               # Login/logout SSO (halaman untuk end-user)
│   ├── api.py               # REST API (verify, refresh, revoke token)
│   └── admin.py             # Dashboard manajemen
│
├── utils/
│   ├── db.py                # Helper koneksi MySQL
│   ├── token.py             # JWT generate & verify
│   ├── auth.py              # Password hashing, reset token, email
│   ├── decorators.py        # Route protection decorators
│   └── context.py           # Template context processors
│
└── templates/
    ├── base.html            # Layout admin
    ├── sso/
    │   ├── login.html       # Halaman login SSO (yang dilihat user)
    │   └── confirm.html     # Halaman konfirmasi setelah login
    └── admin/
        ├── login.html       # Login admin panel
        ├── dashboard.html   # Dashboard overview
        ├── users.html       # List users
        ├── user_form.html   # Form tambah/edit user
        ├── apps.html        # List aplikasi
        ├── app_form.html    # Form daftar/edit aplikasi
        ├── forgot_password.html
        ├── reset_password.html
        └── logs.html        # Audit logs
```

---

## 🔗 URL Penting

| URL | Deskripsi |
|-----|-----------|
| `http://localhost:5000/admin` | Dashboard admin |
| `http://localhost:5000/sso/login?app_id=YOUR_APP_ID` | Halaman login SSO |
| `http://localhost:5000/api/verify` | Verifikasi token |
| `http://localhost:5000/api/refresh` | Refresh token |
| `http://localhost:5000/api/revoke` | Revoke token |
| `http://localhost:5000/api/user` | Info user dari token |

---

## 🔄 Flow SSO

```
1. User akses App Client
2. App Client redirect ke:
   GET /sso/login?app_id=YOUR_APP_ID
3. User isi username + password di halaman SSO
4. Jika auto_redirect = ON:
   → Langsung redirect ke callback_url?access_token=...&refresh_token=...
   Jika auto_redirect = OFF:
   → Tampilkan halaman konfirmasi, user klik "Lanjutkan"
5. App Client terima token di callback URL
6. App Client verifikasi token ke SSO:
   POST /api/verify  (dengan X-App-ID dan X-App-Secret header)
7. SSO return data user + role
8. App Client simpan token di session
```

---

## 🎫 Format JWT Token

Token yang dikirim ke aplikasi client berisi payload:

```json
{
  "iss": "http://192.168.1.3:5000",
  "sub": "1",
  "aud": "app_id_aplikasi",
  "iat": 1234567890,
  "exp": 1234571490,
  "jti": "uuid-unik",

  "user_id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  "full_name": "John Doe",

  "role": "admin",
  "role_id": 2,
  "app_id": "app_id_aplikasi"
}
```

---

## 🛡️ Roles

| Role | ID | Deskripsi |
|------|----|-----------|
| `superadmin` | 1 | Akses penuh ke semua fitur |
| `admin` | 2 | Manajemen user & aplikasi |
| `manager` | 3 | Akses terbatas |
| `user` | 4 | Pengguna biasa |

Role dikirim di dalam JWT token, sehingga aplikasi client bisa langsung menggunakannya untuk kontrol akses.

---

## 📡 API Reference

### POST `/api/verify`
Verifikasi access token.

**Headers:**
```
X-App-ID: your_app_id
X-App-Secret: your_app_secret
Content-Type: application/json
```

**Body:**
```json
{"access_token": "eyJ..."}
```

**Response (valid):**
```json
{
  "valid": true,
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "full_name": "John Doe",
    "role": "admin",
    "role_id": 2
  }
}
```

---

### POST `/api/refresh`
Refresh access token menggunakan refresh token.

**Headers:** (sama dengan /verify)

**Body:**
```json
{"refresh_token": "abc123..."}
```

**Response:**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "xyz...",
  "expires_in": 3600,
  "expires_at": "2024-01-01T12:00:00"
}
```

---

### POST `/api/revoke`
Cabut token (logout dari sisi client).

**Body:**
```json
{"access_token": "eyJ..."}
```

---

### GET `/api/user`
Ambil info user dari access token.

**Headers:**
```
Authorization: Bearer eyJ...
```

---

## 🔧 Konfigurasi Aplikasi Client

Di SSO Admin Panel, setiap aplikasi punya pengaturan:

- **Callback URL**: URL tujuan redirect setelah login berhasil
- **Auto Redirect**: Jika ON, langsung redirect tanpa halaman konfirmasi
- **Allowed Origins**: Daftar origin yang diizinkan (CORS)

---

## 👥 Manajemen User

Fitur di Admin Panel:
- ✅ Tambah / edit user
- ✅ Aktif / nonaktif user (session otomatis dicabut)
- ✅ Reset password oleh admin
- ✅ Self-service forgot password via email
- ✅ Semua aktivitas tercatat di Audit Log

---

## 🔒 Keamanan

- Password di-hash dengan **bcrypt** (cost factor 12)
- JWT signed dengan **HS256**
- Reset password token expire **2 jam**
- Saat password diubah, **semua session dicabut**
- Audit log untuk semua aksi penting
- App Secret bisa di-regenerate kapan saja
