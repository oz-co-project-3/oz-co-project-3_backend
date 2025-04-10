from fastapi import APIRouter, Depends, status

from app.core.token import get_current_user
from app.models.user_models import BaseUser
from app.schemas.user_schema import (
    CompanyRegisterRequest,
    CompanyRegisterResponse,
    LoginRequest,
    LoginResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    UserRegisterRequest,
    UserRegisterResponse,
)
from app.services.auth_services import login_user, logout_user, refresh_access_token
from app.services.user_register_services import register_company_user, register_user

router = APIRouter(prefix="/api/user", tags=["user"])


@router.post(
    "/register/",
    response_model=UserRegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="일반 회원가입",
    description="""
- `400` `code`:`duplicate_email` : 이미 존재하는 이메일입니다
- `400` `code`:`invalid_password` : 비밀번호는 8자 이상, 특수문자를 포함해야 합니다
- `400` `code`:`password_mismatch` : 비밀번호와 확인이 일치하지 않습니다
""",
)
async def register(request: UserRegisterRequest):
    return await register_user(request)


@router.post(
    "/register-company/",
    response_model=CompanyRegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="기업 회원가입",
    description="""
- `400` `code`:`duplicate_email` : 이미 존재하는 이메일입니다
- `400` `code`:`invalid_password` : 비밀번호는 8자 이상, 특수문자를 포함해야 합니다
- `400` `code`:`password_mismatch` : 비밀번호와 확인이 일치하지 않습니다
""",
)
async def register_company(request: CompanyRegisterRequest):
    return await register_company_user(request)


@router.post(
    "/login/",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    summary="로그인",
    description="""
- `400` `code`:`invalid_credentials` : 이메일 또는 비밀번호가 일치하지 않습니다
- `500` `code`:`unknown_user_type` : 알 수 없는 사용자 유형입니다
""",
)
async def login(request: LoginRequest):
    return await login_user(request)


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="로그아웃",
    description="""
- `401` `code`:`invalid_token` : 유효하지 않은 인증 토큰입니다
- `401` `code`:`expired_token` : 만료된 인증 토큰입니다
- `500` `code`:`SERVER_ERROR` : 서버 내부 오류가 발생했습니다
""",
)
async def logout(current_user: BaseUser = Depends(get_current_user)):
    await logout_user(current_user)
    return {"message": "로그아웃이 완료되었습니다."}


@router.post(
    "/refresh-token/",
    response_model=RefreshTokenResponse,
    status_code=status.HTTP_200_OK,
    summary="토큰 재요청",
    description="""
- `401` `code`:`invalid_refresh_token` : 유효하지 않은 리프레시 토큰입니다
- `401` `code`:`expired_refresh_token` : 만료된 리프레시 토큰입니다
""",
)
async def refresh_token(request: RefreshTokenRequest):
    return await refresh_access_token(request)
