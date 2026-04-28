from jwt import encode, decode, ExpiredSignatureError, InvalidTokenError
import uuid, os
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

load_dotenv()

JWT_SECRET    = os.getenv('JWT_SECRET_KEY', 'fallback-secret-change-me')
ACCESS_EXPIRE = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRE_MINUTES', 1440))


def generate_access_token(user: dict, app_id: str) -> dict:
    now     = datetime.now(timezone.utc)
    expires = now + timedelta(minutes=ACCESS_EXPIRE)

    # right_config berisi paths + key-value lain
    right_config = user.get('right_config') or {}

    payload = {
        'iss': os.getenv('SSO_BASE_URL', 'http://localhost:5005'),
        'sub': str(user['id']),
        'aud': app_id,
        'iat': int(now.timestamp()),
        'exp': int(expires.timestamp()),
        'jti': str(uuid.uuid4()),
        # User
        'user_id':   user['id'],
        'username':  user['username'],
        'email':     user['email'],
        'full_name': user['full_name'],
        # Role
        'role':      user['role_name'],
        'role_id':   user['role_id'],
        # Access Matrix
        'standard_access': user.get('standard_access') or [],
        # ['view', 'edit', 'export', 'approve', 'upload', 'delete']
        'paths':           right_config.get('paths', []),
        # ['/dashboard', '/laporan', ...]
        'right_config':    {k: v for k, v in right_config.items() if k != 'paths'},
        # key-value lain selain paths
        'app_id': app_id,
    }

    return {
        'access_token': encode(payload, JWT_SECRET, algorithm='HS256'),
        'expires_at':   expires.isoformat(),
        'expires_in':   ACCESS_EXPIRE * 60,
    }


def verify_access_token(token: str, app_id: str = None) -> dict:
    kwargs = {'audience': app_id} if app_id else {}
    try:
        return decode(token, JWT_SECRET, algorithms=['HS256'],
                      options={'verify_exp': True}, **kwargs)
    except ExpiredSignatureError:
        raise Exception('Token sudah kadaluarsa')
    except InvalidTokenError as e:
        raise Exception(f'Token tidak valid: {str(e)}')
