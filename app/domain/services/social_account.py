import logging

import httpx

from app.core.settings import settings

logger = logging.getLogger(__name__)


# 카카오 url 이동
async def generate_kakao_auth_url() -> dict:
    kakao_client_id = settings.KAKAO_CLIENT_ID
    redirect_uri = settings.KAKAO_REDIRECT_URI
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
        "client_id": settings.KAKAO_CLIENT_ID,
        "client_secret": settings.KAKAO_CLIENT_SECRET,
        "redirect_uri": settings.KAKAO_REDIRECT_URI,
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


# 네이버
# 네이버 인가 URL 생성
async def generate_naver_auth_url() -> dict:
    naver_client_id = settings.NAVER_CLIENT_ID
    redirect_uri = settings.NAVER_REDIRECT_URI
    state = settings.NAVER_STATE

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
        "client_id": settings.NAVER_CLIENT_ID,
        "client_secret": settings.NAVER_CLIENT_SECRET,
        "code": code,
        "state": state,
    }
    response = await httpx.AsyncClient().post(url, data=payload)
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
