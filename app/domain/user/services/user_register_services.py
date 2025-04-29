import re
from datetime import datetime
from typing import Optional

from passlib.hash import bcrypt

from app.core.token import create_jwt_tokens
from app.domain.services.business_verify import verify_business_number
from app.domain.services.email_detail import send_email_code
from app.domain.user.models import BaseUser, CorporateUser
from app.domain.user.repository import (
    create_base_user,
    create_seeker_profile,
    get_user_by_email,
)
from app.domain.user.schema import (
    BusinessUpgradeRequest,
    EmailCheckResponse,
    UserRegisterRequest,
    UserRegisterResponse,
    UserRegisterResponseData,
)
from app.exceptions.auth_exceptions import (
    InvalidPasswordException,
    PasswordMismatchException,
)
from app.exceptions.email_exceptions import DuplicateEmailException
from app.exceptions.user_exceptions import (
    AlreadyBusinessUserException,
    InvalidBusinessNumberException,
)


async def register_user(request: UserRegisterRequest) -> UserRegisterResponse:
    existing_user = await get_user_by_email(email=request.email)
    if existing_user:
        raise DuplicateEmailException()

    if len(request.password) < 8 or not re.search(
        r"[!@#$%^&*(),.?\":{}|<>]", request.password
    ):
        raise InvalidPasswordException()

    if request.password != request.password_check:
        raise PasswordMismatchException()

    hashed_password = bcrypt.hash(request.password)

    base_user = await create_base_user(
        email=request.email,
        password=hashed_password,
        user_type=request.user_type.value,
        gender=request.gender,
        is_superuser=False,
        status="pending",
        signinMethod=request.signinMethod.value,
    )

    seeker_user = await create_seeker_profile(
        user=base_user,
        name=request.name,
        phone_number=request.phone_number,
        birth=request.birth,
        gender=request.gender,
        interests=request.interests
        if isinstance(request.interests, list)
        else [request.interests],
        purposes=request.purposes
        if isinstance(request.purposes, list)
        else [request.purposes],
        sources=request.sources
        if isinstance(request.sources, list)
        else [request.sources],
        status=request.status,
        is_social=False,
    )

    # 여기서 인증메일 발송
    await send_email_code(email=base_user.email, purpose="회원가입")

    return UserRegisterResponse(
        message="회원가입이 완료되었습니다.",
        data=UserRegisterResponseData(
            id=base_user.id,
            email=base_user.email,
            name=seeker_user.name,
            user_type=request.user_type.value,
            email_verified=base_user.email_verified,
            created_at=base_user.created_at,
        ),
    )


# 기업회원 업그레이드
async def upgrade_to_business(user: BaseUser, request: BusinessUpgradeRequest):
    # 이미 business 등록된 경우 막기
    if user.user_type == "business":
        raise AlreadyBusinessUserException()

    # 사업자번호 인증
    result = await verify_business_number(request.business_number)
    if not result.get("is_valid"):
        raise InvalidBusinessNumberException()

    # CorporateUser 생성
    await CorporateUser.create(
        user=user,
        business_number=request.business_number,
        company_name=request.company_name,
        manager_name=request.manager_name,
        manager_phone_number=request.manager_phone_number,
        business_start_date=request.business_start_date,
    )

    # BaseUser user_type 업데이트 = array필드 모델 참조 (리스트였음)
    user.user_type = "business"
    await user.save()

    # 새 access_token, refresh_token 발급
    access_token, refresh_token = create_jwt_tokens(str(user.id), user.user_type)

    return {
        "message": "기업회원으로 전환이 완료되었습니다.",
        "data": {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user_id": user.id,
            "user_type": user.user_type,
            "email": user.email,
        },
    }


async def delete_user(
    current_user: BaseUser, password: str, reason: Optional[str] = None
):
    if not bcrypt.verify(password, current_user.password):
        raise PasswordMismatchException()

    current_user.deleted_at = datetime.utcnow()
    current_user.email_verified = False
    current_user.status = "delete"

    if reason:
        current_user.reason = reason  # 탈퇴 사유 추가

    await current_user.save()

    return {"message": "회원 탈퇴가 완료되었습니다."}


# 이메일 중복 검사 함수
async def check_email_duplicate(email: str) -> EmailCheckResponse:
    existing_user = await get_user_by_email(email=email)
    if existing_user:
        return EmailCheckResponse(message="이미 사용 중인 이메일입니다.", is_available=False)
    return EmailCheckResponse(message="사용 가능한 이메일입니다.", is_available=True)
