import secrets
from passlib.context import CryptContext
from config.settings import config

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)

def generate_token(n_bytes: int = 32) -> str:
    return secrets.token_urlsafe(n_bytes)
