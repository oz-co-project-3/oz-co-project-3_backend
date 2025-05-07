import logging
from datetime import datetime, timedelta

import jwt
from fastapi import Request
from fastapi.responses import JSONResponse
from passlib.hash import bcrypt

from app.core.redis import get_redis
from app.core.token import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ALGORITHM,
    REFRESH_TOKEN_EXPIRE_SECONDS,
    SECRET_KEY,
    create_jwt_tokens,
    create_token,
)
from app.domain.services.social_account import (
    get_naver_access_token,
    get_naver_user_info,
)
from app.domain.user.models import (
    BaseUser,
    CorporateUser,
    Gender,
    SeekerStatus,
    SeekerUser,
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

logger = logging.getLogger(__name__)


# 비밀번호 검증
async def authenticate_user(email: str, password: str) -> BaseUser:
    user = await get_user_by_email(email=email)
    if not user or not bcrypt.verify(password, user.password):
        logger.warning(f"[CHECK] 인증 실패: 이메일 또는 비밀번호 불일치")
        raise PasswordMismatchException()
    return user


# 비밀번호 변경 시 비밀번호 확인
async def verify_user_password(user: BaseUser, password: str):
    if not bcrypt.verify(password, user.password):
        logger.warning(f"[CHECK] 현재 비밀번호 불일치 - 유저 ID:{user.id}")
        raise PasswordMismatchException()


# 로그인
async def login_user(email: str, password: str) -> tuple[LoginResponseDTO, str, str]:
    user = await BaseUser.get_or_none(email=email)

    if not user:
        logger.warning(f"[CHECK] 로그인 실패 - 유저 없음: {email}")
        raise UserNotFoundException()

    if not user.email_verified or user.status != "active":
        logger.warning(f"[CHECK] 로그인 실패 - 미인증 또는 비활성 상태: {email}")
        raise UnverifiedOrInactiveAccountException()

    if not bcrypt.verify(password, user.password):
        logger.warning(f"[CHECK] 로그인 실패 - 비밀번호 불일치: {email}")
        raise PasswordInvalidException()

    # user_id + user_type 둘 다 넣어서 토큰 발급 = 프론트 요청사항
    user_type = user.user_type[0] if user.user_type else "normal"

    access_token, refresh_token = create_jwt_tokens(user.id, user_type)

    await get_redis().set(
        f"refresh_token:{user.id}", refresh_token, ex=REFRESH_TOKEN_EXPIRE_SECONDS * 60
    )

    name = "소셜 유저"

    if user.user_type == "normal":
        seeker = await SeekerUser.get_or_none(user=user)
        if seeker and seeker.name:
            name = seeker.name

    elif user.user_type == "corporate":
        corp = await CorporateUser.get_or_none(user=user)
        if corp and corp.manager_name:
            name = corp.manager_name

    dto = LoginResponseDTO(
        user_id=user.id,
        user_type=user.user_type,
        email=user.email,
        name=name,
        access_token=access_token,
    )

    return dto, access_token, refresh_token


# 로그아웃
async def logout_user(user: BaseUser, access_token: str) -> LogoutResponseDTO:
    refresh_deleted = await get_redis().delete(f"refresh_token:{user.id}")
    if refresh_deleted == 0:
        logger.warning(f"[CHECK] 로그아웃 실패 - 토큰 없음: 유저 ID {user.id}")
        raise InvalidTokenException()

    try:
        payload = jwt.decode(access_token, options={"verify_signature": False})
        exp = payload.get("exp")
        ttl = exp - int(datetime.utcnow().timestamp())
        if ttl > 0:
            await get_redis().setex(f"blacklist:{access_token}", ttl, "1")
    except Exception as e:
        logger.error(f"[ERROR] access_token 블랙리스트 등록 실패: {e}")

    return LogoutResponseDTO(success=True)


# 리프레쉬 토큰 발급
async def refresh_access_token(request: Request) -> tuple[RefreshTokenResponseDTO, str]:
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        logger.warning("[CHECK] 리프레시 토큰 없음 (쿠키)")
        raise InvalidRefreshTokenException()
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            logger.warning(f"[CHECK] 리프레시 토큰 디코딩 실패 - sub 없음")
            raise InvalidRefreshTokenException()

    except jwt.ExpiredSignatureError:
        logger.warning(f"[CHECK] 리프레시 토큰 만료됨")
        raise ExpiredRefreshTokenException()
    except jwt.PyJWTError:
        logger.warning(f"[CHECK] 리프레시 토큰 디코딩 오류")
        raise InvalidRefreshTokenException()

    stored_token = await get_redis().get(f"refresh_token:{str(user_id)}")
    if stored_token != refresh_token:
        logger.warning(f"[CHECK] 리프레시 토큰 불일치: {user_id}")
        raise InvalidRefreshTokenException()

    # BaseUser 조회 추가
    user = await get_user_by_id(user_id=user_id)
    if not user:
        logger.warning(f"[CHECK] 사용자 없음 ID:{user_id}")
        raise InvalidRefreshTokenException()

    # access_token 새로 생성 (user_id + user_type 넣기)
    new_access_token = create_token(
        {"sub": user_id, "user_type": user.user_type},  # 리스트니까 첫 번째 꺼냄
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    dto = RefreshTokenResponseDTO(
        access_token=new_access_token,
    )
    return dto, new_access_token


# 카카오/네이버 로그인
async def kakao_login(kakao_info: dict) -> tuple[LoginResponseDTO, str, str]:
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
        )
    else:
        if SignInEnum.Kakao.value not in user.signinMethod:
            user.signinMethod += ",Kakao"
            await user.save()

    access_token, refresh_token = create_jwt_tokens(user.id, user.user_type)
    await get_redis().set(f"refresh_token:{user.id}", refresh_token)

    dto = LoginResponseDTO(
        access_token=access_token,
        user_id=user.id,
        user_type=user.user_type,
        email=user.email,
        name=nickname,
    )
    return dto, access_token, refresh_token


async def naver_login(code: str, state: str) -> tuple[LoginResponseDTO, str, str]:
    access_token = await get_naver_access_token(code, state)
    naver_info = await get_naver_user_info(access_token)

    email = naver_info.get("email")
    nickname = naver_info.get("nickname") or naver_info.get("name") or "네이버유저"

    user = await get_user_by_email(email=email)

    if not user:
        user = await create_base_user(
            email=email,
            password="naver_social_login",
            user_type=UserTypeEnum.NORMAL.value,
            signinMethod=SignInEnum.Naver.value,
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
        )
    else:
        if SignInEnum.Naver.value not in user.signinMethod:
            user.signinMethod += ",Naver"
            await user.save()

    access_token, refresh_token = create_jwt_tokens(user.id, user.user_type)
    await get_redis().set(f"refresh_token:{user.id}", refresh_token)

    dto = LoginResponseDTO(
        access_token=access_token,
        user_id=user.id,
        user_type=user.user_type,
        email=user.email,
        name=nickname,
    )
    return dto, access_token, refresh_token
