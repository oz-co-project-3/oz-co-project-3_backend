import logging
from typing import Union

from fastapi import APIRouter, Body, Depends, Query, Request, status
from pydantic import BaseModel, EmailStr

from app.core.token import get_current_user
from app.domain.services.business_verify import verify_business_number
from app.domain.services.social_account import (
    generate_kakao_auth_url,
    generate_naver_auth_url,
    get_kakao_access_token,
    get_kakao_user_info,
    get_naver_access_token,
    get_naver_user_info,
)
from app.domain.user.models import BaseUser
from app.domain.user.schema import (
    BusinessUpgradeDTO,
    BusinessUpgradeRequest,
    BusinessVerifyRequest,
    BusinessVerifyResponse,
    CorporateProfileUpdateRequest,
    EmailCheckRequest,
    EmailCheckResponseDTO,
    EmailVerificationResponseDTO,
    FindEmailRequest,
    FindEmailResponseDTO,
    FindPasswordRequest,
    FindPasswordResponseDTO,
    LoginRequest,
    LoginResponseDTO,
    MessageResponse,
    RefreshTokenRequest,
    RefreshTokenResponseDTO,
    ResendEmailRequest,
    ResendEmailResponseDTO,
    ResetPasswordRequest,
    ResetPasswordResponseDTO,
    SeekerProfileUpdateRequest,
    SocialCallbackRequest,
    UserDeleteDTO,
    UserDeleteRequest,
    UserRegisterRequest,
    UserRegisterResponseDTO,
    UserUnionResponseDTO,
    VerifyPasswordRequest,
)
from app.domain.user.services.auth_recovery_services import (
    check_email_duplicate,
    complete_email_verification,
    find_email,
    find_password,
    resend_verification_email_service,
    reset_password,
)
from app.domain.user.services.auth_services import (
    kakao_login,
    login_user,
    logout_user,
    naver_login,
    refresh_access_token,
    verify_user_password,
)
from app.domain.user.services.user_profile_services import (
    get_user_profile,
    update_user_profile,
)
from app.domain.user.services.user_register_services import (
    delete_user,
    register_user,
    upgrade_to_business,
)
from app.exceptions.server_exceptions import UnknownUserTypeException

router = APIRouter(prefix="/api/user", tags=["user"])

logger = logging.getLogger(__name__)


# 이메일 인증 요청 부분
class EmailVerifyRequest(BaseModel):
    email: EmailStr
    verification_code: str


@router.post(
    "/register/",
    response_model=UserUnionResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="회원가입(공통)",
    description="""
`400` `code`:`duplicate_email` : 이미 사용 중인 이메일입니다\n
`400` `code`:`invalid_password` : 비밀번호 형식이 올바르지 않습니다\n
`400` `code`:`password_mismatch` : 비밀번호와 비밀번호 확인이 일치하지 않습니다\n
`422` : Unprocessable Entity
""",
)
async def register(request: UserRegisterRequest):
    logger.info(f"[API] 회원가입 요청(공통)")
    result = await register_user(request)
    return result


@router.post(
    "/upgrade-to-business/",
    response_model=BusinessUpgradeDTO,
    status_code=status.HTTP_200_OK,
    summary="기업회원 업그레이드",
    description="""
`400` `code`:`already_business_user` : 이미 기업회원으로 등록된 사용자입니다\n
`400` `code`:`invalid_business_number` : 국세청에 등록되지 않은 사업자등록번호입니다\n
""",
)
async def upgrade_to_business_route(
    request: BusinessUpgradeRequest, current_user: BaseUser = Depends(get_current_user)
):
    logger.info(f"[API] 기업회원 업그레이드 요청")
    result = await upgrade_to_business(current_user, request)
    return result


@router.post(
    "/check-email/",
    response_model=EmailCheckResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="이메일 중복 확인",
    description="""
`200` `code`:`is_available=false` : 이미 존재하는 이메일입니다\n
""",
)
async def check_email(request: EmailCheckRequest):
    logger.info(f"[API] 이메일 중복확인 요청")
    return await check_email_duplicate(request.email)


@router.delete(
    "/withdrawal-user/",
    response_model=UserDeleteDTO,
    status_code=status.HTTP_200_OK,
    summary="회원 탈퇴",
    description="""
`400` `code`:`invalid_password` : 비밀번호가 일치하지 않습니다.\n
""",
)
async def delete_profile(
    request: UserDeleteRequest = Body(...),
    current_user: BaseUser = Depends(get_current_user),
):
    logger.info(f"[API] 회원 탈퇴 요청")
    if not request.is_active:
        return await delete_user(current_user=current_user, password=request.password)
    return "탈퇴 요청이 취소되었습니다."


@router.post(
    "/find-email/",
    response_model=FindEmailResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="아이디(이메일) 찾기",
    description="""
`404` `code`:`user_not_found` : 일치하는 사용자 정보가 없습니다\n
""",
)
async def find_email_route(request: FindEmailRequest):
    logger.info(f"[API] 아이디(이메일)찾기 요청")
    return await find_email(name=request.name, phone_number=request.phone_number)


@router.post(
    "/find-password/",
    response_model=FindPasswordResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="비밀번호 찾기",
    description="""
`404` `code`:`user_not_found` : 일치하는 사용자 정보가 없습니다\n
""",
)
async def find_password_route(request: FindPasswordRequest):
    logger.info(f"[API] 비밀번호 찾기 요청")
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
    logger.info(f"[API] 현재 비밀번호 확인 요청")
    await verify_user_password(current_user, request.password)
    return MessageResponse(message="비밀번호가 확인되었습니다.")


@router.post(
    "/reset-password/",
    response_model=ResetPasswordResponseDTO,
    status_code=200,
    summary="비밀번호 재설정",
    description="""
`400` `code`:`password_mismatch` : 새 비밀번호와 확인이 다름\n
`400` `code`:`invalid_password` : 비밀번호 조건 불충족\n
`400` `code`:`password_previously_used` : 이전 비밀번호 재사용\n
`404` `code`:`user_not_found` : 이메일에 해당하는 유저 없음\n
""",
)
async def reset_password_route(request: ResetPasswordRequest):
    logger.info(f"[API] 비밀번호 재설정 요청")
    return await reset_password(
        email=request.email,
        new_password=request.new_password,
        new_password_check=request.new_password_check,
    )


@router.get(
    "/profile/",
    response_model=UserUnionResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="로그인한 사용자 프로필 조회",
    description="""
`401` `code`:`invalid_token` : 유효하지 않은 인증 토큰입니다\n
`404` `code`:`user_not_found` : 사용자 정보를 찾을 수 없습니다\n
`500` `code`:`unknown_user_type` : 알 수 없는 사용자 유형입니다\n
""",
)
async def profile(
    current_user: BaseUser = Depends(get_current_user),
):
    logger.info(f"[API] 사용자 프로필 조회 요청")
    return await get_user_profile(current_user)


@router.patch(
    "/profile/update/",
    response_model=UserUnionResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="유저 프로필 수정 (일반/기업 통합)",
    description="""
`target_type=normal` : 일반회원 프로필 수정\n
`target_type=business` : 기업회원 프로필 수정\n
""",
)
async def update_profile(
    body: Union[SeekerProfileUpdateRequest, CorporateProfileUpdateRequest] = Body(...),
    target_type: str = Query("normal"),
    current_user: BaseUser = Depends(get_current_user),
):
    logger.info(f"[API] 사용자 프로필 업데이트 요청(일반/기업)")

    if target_type == "normal":
        update_data = SeekerProfileUpdateRequest(**body.dict())
    elif target_type == "business":
        update_data = CorporateProfileUpdateRequest(**body.dict())
    else:
        raise UnknownUserTypeException()

    return await update_user_profile(current_user, update_data, target_type)


@router.post(
    "/login/",
    response_model=LoginResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="로그인",
    description="""
`400` `code`:`invalid_credentials` : 이메일 또는 비밀번호가 일치하지 않습니다\n
`403` `code`:`unverified_or_inactive_account` : 이메일 인증이 완료되지 않았거나 계정이 활성화되지 않았습니다\n
`404` `code`:`user_not_found` : 유저를 찾을 수 없습니다\n
""",
)
async def login(request: LoginRequest):
    logger.info(f"[API] 사용자 로그인 요청")
    result = await login_user(email=request.email, password=request.password)
    return result


@router.post(
    "/logout/",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="로그아웃",
    description="""
`401` `code`:`invalid_token` : 유효하지 않은 인증 토큰입니다\n
`401` `code`:`expired_token` : 만료된 인증 토큰입니다\n
`500` `code`:`SERVER_ERROR` : 서버 내부 오류가 발생했습니다\n
""",
)
async def logout(current_user: BaseUser = Depends(get_current_user)):
    logger.info(f"[API] 사용자 로그아웃 요청")
    await logout_user(current_user)
    return MessageResponse(message="로그아웃이 완료되었습니다.")


@router.post(
    "/refresh-token/",
    response_model=RefreshTokenResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="토큰 재요청",
    description="""
`401` `code`:`invalid_refresh_token` : 유효하지 않은 리프레시 토큰입니다\n
`401` `code`:`expired_refresh_token` : 만료된 리프레시 토큰입니다\n
""",
)
async def refresh_token(request: RefreshTokenRequest):
    logger.info(f"[API] 사용자 토큰 재요청")
    return await refresh_access_token(request)


@router.post(
    "/verify-email/",
    response_model=EmailVerificationResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="이메일 인증",
    description="""
`400` `code`:`invalid_verification_code` : 유효하지 않은 인증코드입니다.\n
`404` `code`:`user_not_found` : 사용자를 찾을 수 없습니다.\n
""",
)
async def verify_email(request: EmailVerifyRequest):
    logger.info(f"[API] 사용자 이메일 인증 요청")
    return await complete_email_verification(
        email=request.email,
        verification_code=request.verification_code,
    )


@router.post(
    "/resend-email-code/",
    response_model=ResendEmailResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="재인증 코드 발송",
    description="""
`400` `code`:`already_verified` : 이미 인증된 계정입니다.\n
`404` `code`:`user_not_found` : 가입된 이메일이 아닙니다.\n
""",
)
async def resend_email_code(request: ResendEmailRequest):
    logger.info(f"[API] 사용자 재인증 코드발송 요청")
    return await resend_verification_email_service(request)


@router.post(
    "/business-verify/",
    response_model=BusinessVerifyResponse,
    status_code=status.HTTP_200_OK,
    summary="사업자 등록번호 검증",
    description="""
국세청 API를 이용하여 사업자 등록번호의 유효성을 검증합니다.\n
결과가 '계속사업자'일 경우 `is_valid = true` 로 반환됩니다.\n
`400` `code`:`invalid_business_number` : 국세청에 등록되지 않은 사업자등록번호입니다.\n
`500` `code`:`external_api_error` : 국세청 API 호출 실패\n
""",
)
async def business_verify(request: BusinessVerifyRequest):
    logger.info(f"[API] 사업자 등록번호 검증 요청")
    return await verify_business_number(request.business_number)


@router.get(
    "/social-login/kakao/",
    summary="카카오 로그인 인가 URL 발급",
    description="카카오 소셜 로그인을 위한 인가 URL을 발급 " "이 URL로 사용자 리다이렉트",
    status_code=status.HTTP_200_OK,
)
async def get_kakao_auth_url():
    logger.info(f"[API] 사용자 소셜 로그인(카카오) 요청")
    return await generate_kakao_auth_url()


@router.post(
    "/social-login/kakao/callback/",
    status_code=status.HTTP_200_OK,
    summary="카카오 로그인 콜백",
    description="""
카카오 로그인 후 전달받은 `code`를 이용해 access_token을 발급\n
`400` `code`:`invalid_code` : 잘못된 code 또는 만료된 code입니다.\n
`500` `code`:`kakao_api_error` : 카카오 서버 응답 실패\n
""",
    response_model=LoginResponseDTO,
)
async def kakao_callback(request: SocialCallbackRequest):
    logger.info(f"[API] 사용자 소셜 로그인(카카오) 콜백 요청")
    access_token = await get_kakao_access_token(request.code)
    kakao_info = await get_kakao_user_info(access_token)
    result = await kakao_login(kakao_info)
    return result


@router.get(
    "/social-login/naver/",
    summary="네이버 로그인 인가 URL 발급",
    description="네이버 소셜 로그인을 위한 인가 URL을 발급\n" "이 URL로 사용자 리다이렉트",
    status_code=status.HTTP_200_OK,
)
async def get_naver_auth_url():
    logger.info(f"[API] 사용자 소셜 로그인(네이버) 요청")
    return await generate_naver_auth_url()


@router.post(
    "/social-login/naver/callback/",
    status_code=status.HTTP_200_OK,
    summary="네이버 로그인 콜백",
    description="""
네이버 로그인 후 전달받은 `code`, `state`를 이용해 access_token 발급\n
access_token으로 유저정보 조회 후 로그인 처리\n
`400` `code`:`naver_email_required` : 이메일 없는 네이버 계정\n
""",
    response_model=LoginResponseDTO,
)
async def naver_callback(request: SocialCallbackRequest):
    logger.info(f"[API] 사용자 소셜 로그인(네이버) 콜백 요청")
    return await naver_login(request.code, request.state)
