from datetime import datetime, timedelta
from typing import Optional

import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from fastapi.security.utils import get_authorization_scheme_param
from starlette.requests import Request

from app.core.redis import get_redis
from app.core.settings import settings
from app.domain.user.models import BaseUser
from app.exceptions.auth_exceptions import (
    AuthRequiredException,
    ExpiredTokenException,
    InvalidTokenException,
)


class CustomOAuth2PasswordBearer(OAuth2PasswordBearer):
    async def __call__(self, request: Request) -> Optional[str]:
        # 1. 먼저 Authorization 헤더 확인
        authorization = request.headers.get("Authorization")
        scheme, param = get_authorization_scheme_param(authorization)

        if authorization and scheme.lower() == "bearer":
            return param

        # 2. Authorization 없으면 access_token 쿠키 시도
        token = request.cookies.get("access_token")
        if token:
            return token

        if self.auto_error:
            raise AuthRequiredException()
        return None


oauth2_scheme = CustomOAuth2PasswordBearer(tokenUrl="/api/user/login/")
oauth2_optional = CustomOAuth2PasswordBearer(
    tokenUrl="/api/user/login/", auto_error=False
)

ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 1
REFRESH_TOKEN_EXPIRE_SECONDS = REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"


# JWT 생성
def create_token(data: dict, expires_delta: timedelta) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")


def create_jwt_tokens(user_id: int, user_type: str) -> tuple[str, str]:
    access_token = create_token(
        {"sub": str(user_id), "user_type": user_type},
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    refresh_token = create_token(
        {"sub": str(user_id)}, timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )
    return access_token, refresh_token


async def get_current_user(token: str = Depends(oauth2_scheme)) -> BaseUser:
    # 블랙리스트 체크
    is_blacklisted = await get_redis().get(f"blacklist:{token}")
    if is_blacklisted:
        raise InvalidTokenException()

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise InvalidTokenException()
    except jwt.ExpiredSignatureError:
        raise ExpiredTokenException()
    except jwt.PyJWTError:
        raise InvalidTokenException()

    user = await BaseUser.get_or_none(id=user_id)
    if user is None:
        raise InvalidTokenException()

    return user


async def get_optional_user(
    token: Optional[str] = Depends(oauth2_optional),
) -> Optional[BaseUser]:
    if not token:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        user = await BaseUser.get_or_none(id=user_id)
        return user
    except jwt.PyJWTError:
        return None


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
