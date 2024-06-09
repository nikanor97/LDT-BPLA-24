import enum
import uuid
from datetime import timedelta, datetime

from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer

import settings
from src.db.users.models import User, UserTokenBase

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/swagger-token")


class TokenKind(str, enum.Enum):
    access = "access"
    refresh = "refresh"


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.HASHING_ALGORITHM
    )
    return encoded_jwt


def create_user_token(user: User) -> UserTokenBase:
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    refresh_token = create_token(
        data={"sub": str(user.id)}, expires_delta=refresh_token_expires
    )
    user_token_base = UserTokenBase(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        access_expires_at=datetime.now() + access_token_expires,
        refresh_expires_at=datetime.now() + refresh_token_expires,
        is_valid=True,
        user_id=user.id,
    )
    return user_token_base


def get_user_id_from_token(token: str) -> uuid.UUID:
    try:
        # This line also throws JWTError
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.HASHING_ALGORITHM]
        )
        # This line throws "ValueError: badly formed hexadecimal UUID string" if uuid is not valid
        user_id = uuid.UUID(payload.get("sub"))
        if user_id is None:
            raise JWTError()
    except Exception as e:
        # SHOULD NEVER HAPPEN CAUSE TOKEN IS ALWAYS CHECKED BEFORE EACH METHOD INVOCATION
        raise JWTError("Could not validate credentials")
    return user_id
