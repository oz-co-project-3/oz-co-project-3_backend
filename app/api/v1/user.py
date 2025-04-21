from typing import Union

from fastapi import APIRouter, Body, Depends, status
from pydantic import BaseModel, EmailStr

from app.core.token import get_current_user
from app.domain.user.services.auth_recovery_services import (
    find_email,
    find_password,
    reset_password,
)
from app.domain.user.services.auth_services import (
    login_user,
    logout_user,
    refresh_access_token,
    verify_user_password,
)
from app.domain.user.services.business_verify_services import verify_business_number
from app.domain.user.services.email_services import (
    resend_verification_email,
    verify_email_code,
)
from app.domain.user.services.social_services import (
    generate_kakao_auth_url,
    generate_naver_auth_url,
    get_kakao_access_token,
    get_kakao_user_info,
    get_naver_access_token,
    get_naver_user_info,
    kakao_social_login,
    naver_social_login,
)
from app.domain.user.services.user_profile_services import (
    get_user_profile,
    update_user_profile,
)
from app.domain.user.services.user_register_services import (
    delete_user,
    register_company_user,
    register_user,
)
from app.domain.user.user_models import BaseUser
from app.domain.user.user_schema import (
    BusinessVerifyRequest,
    BusinessVerifyResponse,
    CompanyRegisterRequest,
    CompanyRegisterResponse,
    CorporateProfileUpdateRequest,
    FindEmailRequest,
    FindPasswordRequest,
    LoginRequest,
    LoginResponse,
    MessageResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    ResendEmailRequest,
    ResetPasswordRequest,
    SeekerProfileUpdateRequest,
    SocialCallbackRequest,
    UserDeleteRequest,
    UserProfileResponse,
    UserProfileUpdateResponse,
    UserRegisterRequest,
    UserRegisterResponse,
    VerifyPasswordRequest,
)

router = APIRouter(prefix="/api/services", tags=["services"])


# 이메일 인증 요청 부분
class EmailVerifyRequest(BaseModel):
    email: EmailStr
    verification_code: str


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


@router.delete(
    "/profile/",
    status_code=status.HTTP_200_OK,
    summary="회원 탈퇴",
    description="""
- `400` `code`:`invalid_password` : 비밀번호가 일치하지 않습니다.
""",
)
async def delete_profile(
    request: UserDeleteRequest,
    current_user: BaseUser = Depends(get_current_user),
):
    if not request.is_active:
        return await delete_user(current_user=current_user, password=request.password)
    return {"message": "탈퇴 요청이 취소되었습니다."}


@router.post(
    "/find-email/",
    status_code=status.HTTP_200_OK,
    summary="아이디(이메일) 찾기",
    description="""
- `404` `code`:`user_not_found` : 일치하는 사용자 정보가 없습니다
""",
)
async def find_email_route(request: FindEmailRequest):
    return await find_email(name=request.name, phone_number=request.phone_number)


@router.post(
    "/find-password/",
    status_code=status.HTTP_200_OK,
    summary="비밀번호 찾기",
    description="""
- `404` `code`:`user_not_found` : 일치하는 사용자 정보가 없습니다
""",
)
async def find_password_route(request: FindPasswordRequest):
    return await find_password(
        name=request.name,
        phone_number=request.phone_number,
        email=request.email,
    )


@router.post(
    "/verify-password/",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="현재 비밀번호 확인",
)
async def verify_password(
    request: VerifyPasswordRequest,
    current_user: BaseUser = Depends(get_current_user),
):
    await verify_user_password(current_user, request.password)
    return {"message": "비밀번호가 확인되었습니다."}


@router.post(
    "/reset-password/",
    status_code=200,
    summary="비밀번호 재설정",
    description="""
- `400` `code`:`password_mismatch` : 새 비밀번호와 확인이 다름
- `400` `code`:`invalid_password` : 비밀번호 조건 불충족
- `400` `code`:`password_previously_used` : 이전 비밀번호 재사용
- `404` `code`:`user_not_found` : 이메일에 해당하는 유저 없음
""",
)
async def reset_password_route(request: ResetPasswordRequest):
    return await reset_password(
        email=request.email,
        new_password=request.new_password,
        new_password_check=request.new_password_check,
    )


@router.get(
    "/profile/",
    response_model=UserProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="로그인한 사용자 프로필 조회",
    description="""
- `401` `code`:`invalid_token` : 유효하지 않은 인증 토큰입니다
- `404` `code`:`user_not_found` : 사용자 정보를 찾을 수 없습니다
- `500` `code`:`unknown_user_type` : 알 수 없는 사용자 유형입니다
""",
)
async def profile(current_user: BaseUser = Depends(get_current_user)):
    return await get_user_profile(current_user)


@router.patch(
    "/profile/",
    response_model=UserProfileUpdateResponse,
    status_code=status.HTTP_200_OK,
    summary="회원 정보 수정",
    description="""
- `401` `code`:`invalid_token` : 유효하지 않은 인증 토큰입니다
- `400` `code`:`invalid_phone` : 올바른 형식의 전화번호를 입력해주세요
- `500` `code`:`unknown_user_type` : 알 수 없는 사용자 유형입니다
""",
)
async def update_profile(
    current_user: BaseUser = Depends(get_current_user),
    update_data: Union[
        SeekerProfileUpdateRequest, CorporateProfileUpdateRequest
    ] = Body(...),
):
    return await update_user_profile(current_user, update_data)


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
    "/logout/",
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


@router.post(
    "/verify-email/",
    status_code=status.HTTP_200_OK,
    summary="이메일 인증",
    description="""
- `400` `code`:`invalid_verification_code` : 유효하지 않은 인증코드입니다.
- `404` `code`:`user_not_found` : 사용자를 찾을 수 없습니다.
""",
)
async def verify_email(request: EmailVerifyRequest):
    return await verify_email_code(request)


@router.post(
    "/resend-email-code/",
    status_code=status.HTTP_200_OK,
    summary="재인증 코드 발송",
    description="""
- `400` `code`:`already_verified` : 이미 인증된 계정입니다.
- `404` `code`:`user_not_found` : 가입된 이메일이 아닙니다.
""",
)
async def resend_email_code(request: ResendEmailRequest):
    return await resend_verification_email(request)


@router.post(
    "/business-verify/",
    response_model=BusinessVerifyResponse,
    status_code=status.HTTP_200_OK,
    summary="사업자 등록번호 검증",
    description="""
- 국세청 API를 이용하여 사업자 등록번호의 유효성을 검증합니다.
- 결과가 '계속사업자'일 경우 `is_valid = true` 로 반환됩니다.
- `400` `code`:`invalid_business_number` : 국세청에 등록되지 않은 사업자등록번호입니다.
- `500` `code`:`external_api_error` : 국세청 API 호출 실패
""",
)
async def business_verify(request: BusinessVerifyRequest):
    return await verify_business_number(request.business_number)


@router.get(
    "/social-login/kakao/",
    summary="카카오 로그인 인가 URL 발급",
    description="카카오 소셜 로그인을 위한 인가 URL을 발급 " "이 URL로 사용자 리다이렉트",
    status_code=status.HTTP_200_OK,
)
async def get_kakao_auth_url():
    return await generate_kakao_auth_url()


@router.post(
    "/social-login/kakao/callback/",
    status_code=status.HTTP_200_OK,
    summary="카카오 로그인 콜백",
    description="""
- 카카오 로그인 후 전달받은 `code`를 이용해 access_token을 발급
- `400` `code`:`invalid_code` : 잘못된 code 또는 만료된 code입니다.
- `500` `code`:`kakao_api_error` : 카카오 서버 응답 실패
""",
    response_model=LoginResponse,
)
async def kakao_callback(request: SocialCallbackRequest):
    access_token = await get_kakao_access_token(request.code)
    kakao_info = await get_kakao_user_info(access_token)
    return await kakao_social_login(kakao_info)


@router.get(
    "/social-login/naver/",
    summary="네이버 로그인 인가 URL 발급",
    description="네이버 소셜 로그인을 위한 인가 URL을 발급\n" "이 URL로 사용자 리다이렉트",
    status_code=status.HTTP_200_OK,
)
async def get_naver_auth_url():
    return await generate_naver_auth_url()


@router.post(
    "/social-login/naver/callback/",
    status_code=status.HTTP_200_OK,
    summary="네이버 로그인 콜백",
    description="""
- 네이버 로그인 후 전달받은 `code`, `state`를 이용해 access_token 발급
- access_token으로 유저정보 조회 후 로그인 처리
- `400` `code`:`naver_email_required` : 이메일 없는 네이버 계정
""",
    response_model=LoginResponse,
)
async def naver_callback(request: SocialCallbackRequest):  # 🔁 schema 재사용!
    access_token = await get_naver_access_token(request.code, request.state)
    naver_info = await get_naver_user_info(access_token)
    return await naver_social_login(naver_info)
