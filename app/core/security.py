from datetime import datetime, timedelta
from jose import jwt
# from passlib.context import CryptContext
from pwdlib import PasswordHash
import secrets



def generate_email_token():
    return secrets.token_urlsafe(32)



ph = PasswordHash.recommended()

SECRET_KEY = "secretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str):
    return ph.hash(password)



def verify_password(password, hashed):
    return ph.verify(password, hashed)


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)



