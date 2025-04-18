from datetime import timedelta

import jwt
from passlib.hash import bcrypt

from app.core.redis import redis
from app.core.token import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ALGORITHM,
    REFRESH_TOKEN_EXPIRE_DAYS,
    SECRET_KEY,
    create_jwt_tokens,
    create_token,
)
from app.models.user_models import BaseUser, CorporateUser, SeekerUser
from app.schemas.user_schema import (
    LoginRequest,
    LoginResponse,
    LoginResponseData,
    RefreshTokenRequest,
    RefreshTokenResponse,
    RefreshTokenResponseData,
)
from app.utils.exception import CustomException


# 비밀번호 검증
async def authenticate_user(email: str, password: str) -> BaseUser:
    user = await BaseUser.get_or_none(email=email)
    if not user or not bcrypt.verify(password, user.password):
        raise CustomException(
            status_code=401,
            error="이메일 또는 비밀번호가 일치하지 않습니다.",
            code="invalid_credentials",
        )
    return user


# 비밀번호 변경 시 비밀번호 확인
async def verify_user_password(user: BaseUser, password: str):
    if not bcrypt.verify(password, user.password):
        raise CustomException(
            status_code=400, error="비밀번호가 일치하지 않습니다.", code="invalid_password"
        )


# 로그인
async def login_user(request: LoginRequest) -> LoginResponse:
    user = await authenticate_user(request.email, request.password)

    if not user.email_verified or user.status != "active":
        raise CustomException(
            status_code=403,
            error="이메일 인증이 완료되지 않았거나 계정이 활성화되지 않았습니다.",
            code="unverified_or_inactive_account",
        )

    # 토큰 발급 함수로 변경
    access_token, refresh_token = create_jwt_tokens(str(user.id))

    # redis에 토큰 저장
    await redis.set(
        f"refresh_token:{user.id}",
        refresh_token,
        ex=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )

    await redis.set(
        f"access_token:{user.id}",
        access_token,
        ex=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )

    # 이름 정보 가져오기
    if user.user_type == "seeker":
        profile = await SeekerUser.get(user=user)
        name = profile.name
    elif user.user_type == "business":
        profile = await CorporateUser.get(user=user)
        name = profile.company_name
    else:
        raise CustomException(
            status_code=500,
            error="알 수 없는 사용자 유형입니다.",
            code="unknown_user_type",
        )

    return LoginResponse(
        message="로그인 성공",
        data=LoginResponseData(
            access_token=access_token,
            refresh_token=refresh_token,
            user_id=user.id,
            user_type=user.user_type,
            email=user.email,
            name=name,
        ),
    )


# 로그아웃
async def logout_user(user: BaseUser):
    access_deleted = await redis.delete(f"access_token:{user.id}")
    if access_deleted == 0:
        raise CustomException(
            status_code=401,
            error="유효하지 않은 인증 토큰입니다.",
            code="invalid_token",
        )

    refresh_deleted = await redis.delete(f"refresh_token:{user.id}")
    if refresh_deleted == 0:
        raise CustomException(
            status_code=401,
            error="유효하지 않은 인증 토큰입니다.",
            code="invalid_token",
        )


# 리프레시 토큰 재발급
async def refresh_access_token(request: RefreshTokenRequest) -> RefreshTokenResponse:
    try:
        payload = jwt.decode(request.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")

        if user_id is None:
            raise CustomException(
                status_code=401,
                error="유효하지 않은 리프레시 토큰입니다.",
                code="invalid_refresh_token",
            )

    except jwt.ExpiredSignatureError:
        raise CustomException(
            status_code=401,
            error="만료된 리프레시 토큰입니다.",
            code="expired_refresh_token",
        )
    except jwt.PyJWTError:
        raise CustomException(
            status_code=401,
            error="유효하지 않은 리프레시 토큰입니다.",
            code="invalid_refresh_token",
        )

    # Redis에 저장된 refresh_token과 비교
    stored_token = await redis.get(f"refresh_token:{user_id}")
    if stored_token != request.refresh_token:
        raise CustomException(
            status_code=401,
            error="유효하지 않은 리프레시 토큰입니다.",
            code="invalid_refresh_token",
        )

    # access_token 재생성
    new_access_token = create_token(
        {"sub": user_id},
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    return RefreshTokenResponse(
        message="토큰이 갱신되었습니다.",
        data=RefreshTokenResponseData(access_token=new_access_token),
    )
