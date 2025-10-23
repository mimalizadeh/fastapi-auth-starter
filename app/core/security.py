import hashlib
from datetime import datetime, timedelta, UTC

from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from passlib.context import CryptContext
from app.core.config import get_settings

settings = get_settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/signin")

pwd_context = CryptContext(
    schemes=["bcrypt"],
    bcrypt__ident="2b",
    deprecated="auto",
)


def _normalize_password(password: str) -> str:
    """
    This def encode and hash the password.
    Note : I was thinking this function can be help for bcrypt lib password length error but not Worked!
    :param password:
    :return: hashed password
    """
    if isinstance(password, str):
        password = password.encode("utf-8")
    return hashlib.sha256(password).hexdigest()


def hash_password(password: str) -> str:
    """
    This function is used to hash the password
    """
    normalized = _normalize_password(password)
    return pwd_context.hash(normalized)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """This Function is used to verify the password"""
    normalized = _normalize_password(plain_password)
    return pwd_context.verify(normalized, hashed_password)


def decode_token(token: str) -> dict:
    """This function is used to decode the token"""
    return jwt.decode(token, settings.jwt_secret_key, algorithms=["HS256"])


def _create_token(data: dict, expires_data: timedelta, secret_kry: str) -> str:
    """This function is used to create a new token"""
    to_encode = data.copy()
    expire = datetime.now(UTC) + expires_data
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, secret_kry, algorithm="HS256")


def create_access_token(data: dict,
                        expires_data: timedelta = timedelta(settings.access_token_expire_minutes),
                        secret_kry: str = settings.jwt_secret_key) -> str:
    """This function is used to create a new access token, default access token expire time is 15 minutes
    :param data:
    :param expires_data: Default expires time is 15 minutes
    :param secret_kry:
    """
    return _create_token(data,
                         expires_data=expires_data,
                         secret_kry=secret_kry)


def create_refresh_token(data: dict,
                         expires_data: timedelta = timedelta(settings.refresh_token_expire_days),
                         secret_kry: str = settings.jwt_refresh_secret_key) -> str:
    """This function is used to create a new refresh token, default refresh token expire time is 7 days
    :param data:
    :param expires_data: Default expires time is 7 days
    :param secret_kry:
    """
    return _create_token(data,
                         expires_data=expires_data,
                         secret_kry=secret_kry)
