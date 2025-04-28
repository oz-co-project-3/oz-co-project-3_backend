import os

import httpx

from app.core.redis import redis
from app.core.token import create_jwt_tokens
from app.domain.user.repositories.user_repository import (
    create_base_user,
    create_seeker_profile,
    get_user_by_email,
)
from app.domain.user.schemas.user_schema import LoginResponse, LoginResponseData
from app.domain.user.user_models import (
    BaseUser,
    Gender,
    SeekerStatus,
    SeekerUser,
    UserStatus,
    UserType,
)
from app.exceptions.social_login_exceptions import (
    KakaoEmailRequiredException,
    NaverEmailRequiredException,
)


# 카카오 url 이동
async def generate_kakao_auth_url() -> dict:
    kakao_client_id = os.getenv("KAKAO_CLIENT_ID")
    redirect_uri = os.getenv("KAKAO_REDIRECT_URI")
    url = (
        f"https://kauth.kakao.com/oauth/authorize?"
        f"client_id={kakao_client_id}&redirect_uri={redirect_uri}&response_type=code"
    )
    return {"auth_url": url}


# 카카오 콜백 access_token 발급
async def get_kakao_access_token(code: str) -> str:
    url = "https://kauth.kakao.com/oauth/token"
    payload = {
        "grant_type": "authorization_code",
        "client_id": os.getenv("KAKAO_CLIENT_ID"),
        "client_secret": os.getenv("KAKAO_CLIENT_SECRET"),
        "redirect_uri": os.getenv("KAKAO_REDIRECT_URI"),
        "code": code,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, data=payload)
        response.raise_for_status()
        return response.json()["access_token"]


# 카카오 access_token으로 유저정보 요청
async def get_kakao_user_info(access_token: str) -> dict:
    url = "https://kapi.kakao.com/v2/user/me"
    headers = {"Authorization": f"Bearer {access_token}"}

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        return response.json()


# 카카오 로그인
async def kakao_social_login(kakao_info: dict) -> LoginResponse:
    email = kakao_info["kakao_account"].get("email")
    nickname = kakao_info["kakao_account"]["profile"].get("nickname")
    name = nickname or "카카오유저"

    if not email:
        raise KakaoEmailRequiredException()

    user = await get_user_by_email(email=email)

    # 신규 유저라면 BaseUser/SeekerUser 생성
    if not user:
        user = await create_base_user(
            email=email,
            password="kakao_social_login",  # 소셜 로그인은 패스워드 안 씀
            user_type=UserType.SEEKER,
            status=UserStatus.ACTIVE,
            email_verified=True,
            gender=Gender.MALE,  # 기본값, 성별 나중에 추가입력받게 할 수 있음
        )
        seeker = await create_seeker_profile(
            user=user,
            name=nickname or "소셜유저",
            phone_number="",
            birth=None,
            interests="",
            purposes="",
            sources="",
            status=SeekerStatus.SEEKING,
            is_social=True,
        )
        is_new_user = True
        requires_additional_info = True  # 추가 정보 입력이 필요한 플래그
    else:
        is_new_user = False
        requires_additional_info = False

    # JWT 토큰 발급 (네 프로젝트 토큰 생성 함수로)
    access_token, refresh_token = create_jwt_tokens(str(user.id))
    # redis에 refresh_token 저장
    await redis.set(f"refresh_token:{user.id}", refresh_token)

    return LoginResponse(
        message="소셜 로그인 성공",
        data=LoginResponseData(
            access_token=access_token,
            refresh_token=refresh_token,
            user_id=user.id,
            user_type=user.user_type.value,
            email=user.email,
            name=name,
        ),
    )


# 네이버
# 네이버 인가 URL 생성
async def generate_naver_auth_url() -> dict:
    naver_client_id = os.getenv("NAVER_CLIENT_ID")
    redirect_uri = os.getenv("NAVER_REDIRECT_URI")
    state = os.getenv("NAVER_STATE", "naver_login_test_2025")

    url = (
        f"https://nid.naver.com/oauth2.0/authorize"
        f"?response_type=code"
        f"&client_id={naver_client_id}"
        f"&redirect_uri={redirect_uri}"
        f"&state={state}"
    )

    return {"auth_url": url}


# 네이버 access_token 발급
async def get_naver_access_token(code: str, state: str) -> str:
    url = "https://nid.naver.com/oauth2.0/token"
    payload = {
        "grant_type": "authorization_code",
        "client_id": os.getenv("NAVER_CLIENT_ID"),
        "client_secret": os.getenv("NAVER_CLIENT_SECRET"),
        "code": code,
        "state": state,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, data=payload)
        response.raise_for_status()
        return response.json()["access_token"]


# 네이버 access_token으로 유저 정보 요청
async def get_naver_user_info(access_token: str) -> dict:
    url = "https://openapi.naver.com/v1/nid/me"
    headers = {"Authorization": f"Bearer {access_token}"}

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        return response.json()["response"]


# 네이버 로그인 처리
async def naver_social_login(naver_info: dict) -> LoginResponse:
    email = naver_info.get("email")
    nickname = naver_info.get("nickname") or naver_info.get("name")
    name = nickname or "네이버유저"

    if not email:
        raise NaverEmailRequiredException()

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
            name=name,
            phone_number="",
            birth=None,
            interests="",
            purposes="",
            sources="",
            status=SeekerStatus.SEEKING,
            is_social=True,
        )
        is_new_user = True
        requires_additional_info = True
    else:
        is_new_user = False
        requires_additional_info = False

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
            name=name,
        ),
    )
