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
from app.domain.services.social_account import (
    get_kakao_access_token,
    get_kakao_user_info,
    get_naver_access_token,
    get_naver_user_info,
)
from app.domain.user.models import BaseUser, Gender, SeekerStatus, UserStatus, UserType
from app.domain.user.repository import (
    create_base_user,
    create_seeker_profile,
    get_corporate_profile_by_user,
    get_seeker_profile_by_user,
    get_user_by_email,
)
from app.domain.user.schema import (
    LoginRequest,
    LoginResponse,
    LoginResponseData,
    RefreshTokenRequest,
    RefreshTokenResponse,
    RefreshTokenResponseData,
)
from app.exceptions.auth_exceptions import (
    ExpiredRefreshTokenException,
    InvalidRefreshTokenException,
    InvalidTokenException,
    PasswordMismatchException,
)
from app.exceptions.server_exceptions import UnknownUserTypeException
from app.exceptions.user_exceptions import UnverifiedOrInactiveAccountException


# 비밀번호 검증
async def authenticate_user(email: str, password: str) -> BaseUser:
    user = await get_user_by_email(email=email)
    if not user or not bcrypt.verify(password, user.password):
        raise PasswordMismatchException()
    return user


# 비밀번호 변경 시 비밀번호 확인
async def verify_user_password(user: BaseUser, password: str):
    if not bcrypt.verify(password, user.password):
        raise PasswordMismatchException()


# 로그인
async def login_user(request: LoginRequest) -> LoginResponse:
    user = await authenticate_user(request.email, request.password)

    if not user.email_verified or user.status != "active":
        raise UnverifiedOrInactiveAccountException()

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
        profile = await get_seeker_profile_by_user(user)
        name = profile.name
    elif user.user_type == "business":
        profile = await get_corporate_profile_by_user(user)
        name = profile.company_name
    else:
        raise UnknownUserTypeException()

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
        raise InvalidTokenException()

    refresh_deleted = await redis.delete(f"refresh_token:{user.id}")
    if refresh_deleted == 0:
        raise InvalidTokenException()


# 리프레시 토큰 재발급
async def refresh_access_token(request: RefreshTokenRequest) -> RefreshTokenResponse:
    try:
        payload = jwt.decode(request.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")

        if user_id is None:
            raise InvalidRefreshTokenException()

    except jwt.ExpiredSignatureError:
        raise ExpiredRefreshTokenException()

    except jwt.PyJWTError:
        raise InvalidRefreshTokenException()

    # Redis에 저장된 refresh_token과 비교
    stored_token = await redis.get(f"refresh_token:{user_id}")
    if stored_token != request.refresh_token:
        raise InvalidRefreshTokenException()

    # access_token 재생성
    new_access_token = create_token(
        {"sub": user_id},
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    return RefreshTokenResponse(
        message="토큰이 갱신되었습니다.",
        data=RefreshTokenResponseData(access_token=new_access_token),
    )


# 카카오/네이버 로그인
async def kakao_login(code: str) -> LoginResponse:
    access_token = await get_kakao_access_token(code)
    kakao_info = await get_kakao_user_info(access_token)

    email = kakao_info["kakao_account"].get("email")
    nickname = kakao_info["kakao_account"]["profile"].get("nickname") or "카카오유저"

    user = await get_user_by_email(email=email)

    if not user:
        user = await create_base_user(
            email=email,
            password="kakao_social_login",
            user_type=UserType.SEEKER,
            status=UserStatus.ACTIVE,
            email_verified=True,
            gender=Gender.MALE,
        )
        await create_seeker_profile(
            user=user,
            name=nickname,
            phone_number="",
            birth=None,
            interests="",
            purposes="",
            sources="",
            status=SeekerStatus.SEEKING,
            is_social=True,
        )

    access_token, refresh_token = create_jwt_tokens(str(user.id))
    await redis.set(f"refresh_token:{user.id}", refresh_token)

    return LoginResponse(
        message="소셜 로그인 성공",
        data=LoginResponseData(
            access_token=access_token,
            refresh_token=refresh_token,
            user_id=user.id,
            user_type=user.user_type.value,
            email=user.email,
            name=nickname,
        ),
    )


async def naver_login(code: str, state: str) -> LoginResponse:
    access_token = await get_naver_access_token(code, state)
    naver_info = await get_naver_user_info(access_token)

    email = naver_info.get("email")
    nickname = naver_info.get("nickname") or naver_info.get("name") or "네이버유저"

    user = await get_user_by_email(email=email)

    if not user:
        user = await create_base_user(
            email=email,
            password="naver_social_login",
            user_type=UserType.SEEKER,
            status=UserStatus.ACTIVE,
            email_verified=True,
            gender=Gender.MALE,
        )
        await create_seeker_profile(
            user=user,
            name=nickname,
            phone_number="",
            birth=None,
            interests="",
            purposes="",
            sources="",
            status=SeekerStatus.SEEKING,
            is_social=True,
        )

    access_token, refresh_token = create_jwt_tokens(str(user.id))
    await redis.set(f"refresh_token:{user.id}", refresh_token)

    return LoginResponse(
        message="소셜 로그인 성공",
        data=LoginResponseData(
            access_token=access_token,
            refresh_token=refresh_token,
            user_id=user.id,
            user_type=user.user_type.value,
            email=user.email,
            name=nickname,
        ),
    )
