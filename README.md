# 🔐 MySSO — Simple Single Sign-On

Aplikasi SSO sederhana menggunakan **Python 3.9 + Flask + MySQL**.

---

## 🔗 URL Penting

| URL | Deskripsi |
|-----|-----------|
| `http://localhost:5000/admin` | Dashboard admin |
| `http://localhost:5000/sso/login?app_id=YOUR_APP_ID` | Halaman login SSO |
| `http://localhost:5000/api/verify` | Verifikasi token |
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
- ✅ Semua aktivitas tercatat di Audit Log

---

## 🔒 Keamanan

- Password di-hash dengan **bcrypt** (cost factor 12)
- JWT signed dengan **HS256**
- Audit log untuk semua aksi penting
- App Secret bisa di-regenerate kapan saja
