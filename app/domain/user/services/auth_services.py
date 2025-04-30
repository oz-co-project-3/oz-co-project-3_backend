from datetime import timedelta

import jwt
from passlib.hash import bcrypt

from app.core.redis import redis
from app.core.token import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ALGORITHM,
    REFRESH_TOKEN_EXPIRE_SECONDS,
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
from app.domain.user.models import (
    BaseUser,
    Gender,
    SeekerStatus,
    SignInEnum,
    UserStatus,
    UserTypeEnum,
)
from app.domain.user.repository import (
    create_base_user,
    create_seeker_profile,
    get_user_by_email,
    get_user_by_id,
)
from app.domain.user.schema import (
    LoginResponseData,
    LoginResponseDTO,
    LogoutResponseDTO,
    RefreshTokenRequest,
    RefreshTokenResponseDTO,
)
from app.exceptions.auth_exceptions import (
    ExpiredRefreshTokenException,
    InvalidRefreshTokenException,
    InvalidTokenException,
    PasswordMismatchException,
)
from app.exceptions.user_exceptions import (
    PasswordInvalidException,
    UnverifiedOrInactiveAccountException,
    UserNotFoundException,
)


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
async def login_user(email: str, password: str) -> LoginResponseDTO:
    user = await BaseUser.get_or_none(email=email)

    if not user:
        raise UserNotFoundException()

    if not user.email_verified or user.status != "active":
        raise UnverifiedOrInactiveAccountException()

    if not bcrypt.verify(password, user.password):
        raise PasswordInvalidException()

    # user_id + user_type 둘 다 넣어서 토큰 발급 = 프론트 요청사항
    user_type = user.user_type[0] if user.user_type else "normal"

    access_token, refresh_token = create_jwt_tokens(str(user.id), user_type)

    await redis.set(
        f"refresh_token:{user.id}", refresh_token, ex=REFRESH_TOKEN_EXPIRE_SECONDS * 60
    )

    return LoginResponseDTO(
        success=True,
        data=LoginResponseData(
            access_token=access_token,
            refresh_token=refresh_token,
            user_id=str(user.id),
            user_type=[user.user_type],
            email=user.email,
            name=None,
        ),
    )


# 로그아웃
async def logout_user(user: BaseUser) -> LogoutResponseDTO:
    refresh_deleted = await redis.delete(f"refresh_token:{user.id}")
    if refresh_deleted == 0:
        raise InvalidTokenException()

    return LogoutResponseDTO(
        success=True,
    )


# 리프레쉬 토큰 발급
async def refresh_access_token(request: RefreshTokenRequest) -> RefreshTokenResponseDTO:
    try:
        payload = jwt.decode(request.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise InvalidRefreshTokenException()

    except jwt.ExpiredSignatureError:
        raise ExpiredRefreshTokenException()
    except jwt.PyJWTError:
        raise InvalidRefreshTokenException()

    stored_token = await redis.get(f"refresh_token:{str(user_id)}")
    if stored_token != request.refresh_token:
        raise InvalidRefreshTokenException()

    # BaseUser 조회 추가
    user = await get_user_by_id(user_id=user_id)
    if not user:
        raise InvalidRefreshTokenException()

    # access_token 새로 생성 (user_id + user_type 넣기)
    new_access_token = create_token(
        {"sub": user_id, "user_type": user.user_type},  # 리스트니까 첫 번째 꺼냄
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    return RefreshTokenResponseDTO(success=True, access_token=new_access_token)


# 카카오/네이버 로그인
async def kakao_login(kakao_info: dict) -> LoginResponseDTO:
    kakao_account = kakao_info.get("kakao_account", {})
    profile = kakao_account.get("profile", {})

    email = kakao_account.get("email")
    nickname = profile.get("nickname") or "카카오유저"

    user = await get_user_by_email(email=email)

    if not user:
        user = await create_base_user(
            email=email,
            password="kakao_social_login",
            user_type=UserTypeEnum.NORMAL.value,
            signinMethod=SignInEnum.Kakao.value,
            status=UserStatus.ACTIVE.value,
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

    access_token, refresh_token = create_jwt_tokens(str(user.id), user.user_type)
    await redis.set(f"refresh_token:{user.id}", refresh_token)

    return LoginResponseDTO(
        success=True,
        data=LoginResponseData(
            access_token=access_token,
            refresh_token=refresh_token,
            user_id=str(user.id),
            user_type=[user.user_type],
            email=user.email,
            name=nickname,
        ),
    )


async def naver_login(code: str, state: str) -> LoginResponseDTO:
    access_token = await get_naver_access_token(code, state)
    naver_info = await get_naver_user_info(access_token)

    email = naver_info.get("email")
    nickname = naver_info.get("nickname") or naver_info.get("name") or "네이버유저"

    user = await get_user_by_email(email=email)

    if not user:
        user = await create_base_user(
            email=email,
            password="naver_social_login",
            user_type=UserTypeEnum.NORMAL.value,  # 수정
            signinMethod="naver",  # 추가
            status="active",
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

    access_token, refresh_token = create_jwt_tokens(str(user.id), user.user_type)
    await redis.set(f"refresh_token:{user.id}", refresh_token)

    return LoginResponseDTO(
        success=True,
        data=LoginResponseData(
            access_token=access_token,
            refresh_token=refresh_token,
            user_id=str(user.id),
            user_type=[user.user_type],
            email=user.email,
            name=nickname,
        ),
    )
