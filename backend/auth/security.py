import os
import bcrypt
from datetime import datetime, timedelta, timezone
from jose import jwt

SECRET_KEY = os.getenv("SECRET_KEY", "aicfo-secret-key-for-jwt-signing-2026")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def hash_password(password: str) -> str:
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    pwd_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    try:
        return bcrypt.checkpw(pwd_bytes, hashed_bytes)
    except Exception:
        return False

def validate_password(password: str) -> bool:
    # Require: minimum 8 characters, at least one digit
    if len(password) < 8:
        return False
    if not any(char.isdigit() for char in password):
        return False
    return True

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp())
    })
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
