import os
from datetime import datetime, timedelta

import jwt
from dotenv import load_dotenv
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from app.domain.services.verification import CustomException
from app.domain.user.user_models import BaseUser

load_dotenv()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/user/login/")

ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 1
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"


# JWT 생성
def create_token(data: dict, expires_delta: timedelta) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")


def create_jwt_tokens(user_id: str) -> tuple[str, str]:
    access_token = create_token(
        {"sub": str(user_id)}, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    refresh_token = create_token(
        {"sub": str(user_id)}, timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )
    return access_token, refresh_token


async def get_current_user(token: str = Depends(oauth2_scheme)) -> BaseUser:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise CustomException(
                status_code=401,
                error="유효하지 않은 인증 토큰입니다.",
                code="invalid_token",
            )
    except jwt.ExpiredSignatureError:
        raise CustomException(
            status_code=401,
            error="만료된 인증 토큰입니다.",
            code="expired_token",
        )
    except jwt.PyJWTError:
        raise CustomException(
            status_code=401,
            error="유효하지 않은 인증 토큰입니다.",
            code="invalid_token",
        )

    user = await BaseUser.get_or_none(id=user_id)
    if user is None:
        raise CustomException(
            status_code=401,
            error="유효하지 않은 인증 토큰입니다.",
            code="invalid_token",
        )

    return user


def create_reset_token(email: str, expires_minutes: int = 10) -> str:
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    to_encode = {"sub": email, "exp": expire}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_reset_token(token: str) -> str | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")  # email
    except jwt.ExpiredSignatureError:
        return None
    except jwt.PyJWTError:
        return None
