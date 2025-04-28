import re
from datetime import datetime
from typing import Optional

from passlib.hash import bcrypt

from app.domain.services.email_detail import send_email_code
from app.domain.user.models import BaseUser
from app.domain.user.repository import (
    create_base_user,
    create_corporate_profile,
    create_seeker_profile,
    get_user_by_email,
)
from app.domain.user.schema import (
    CompanyRegisterRequest,
    CompanyRegisterResponse,
    CompanyRegisterResponseData,
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
        user_type="seeker",
        gender=request.gender,
        is_superuser=False,
        status="pending",
    )

    seeker_user = await create_seeker_profile(
        user=base_user,
        name=request.name,
        phone_number=request.phone_number,
        birth=request.birth,
        gender=request.gender,
        interests=request.interests,
        purposes=request.purposes,
        sources=request.sources,
        status=request.status,
        is_social=False,
    )
    # 회원가입 성공 시 인증메일 전송
    await send_email_code(email=base_user.email, purpose="회원가입")

    return UserRegisterResponse(
        message="회원가입이 완료되었습니다.",
        data=UserRegisterResponseData(
            id=base_user.id,
            email=base_user.email,
            name=seeker_user.name,
            user_type=base_user.user_type,
            email_verified=base_user.email_verified,
            created_at=base_user.created_at,
        ),
    )


async def register_company_user(
    request: CompanyRegisterRequest,
) -> CompanyRegisterResponse:
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
        user_type="business",
        gender=request.gender,
        status="pending",
    )

    corp_user = await create_corporate_profile(
        user=base_user,
        company_name=request.company_name,
        business_number=request.business_number,
        business_start_date=request.business_start_date,
        company_description=request.company_description,
        manager_name=request.manager_name,
        manager_phone_number=request.manager_phone_number,
        manager_email=request.manager_email,
        gender=request.gender,
    )

    # 회원가입 성공 시 인증메일 발송
    await send_email_code(email=base_user.email, purpose="기업 회원가입")

    return CompanyRegisterResponse(
        message="기업 회원가입이 완료되었습니다.",
        data=CompanyRegisterResponseData(
            id=base_user.id,
            email=base_user.email,
            company_name=corp_user.company_name,
            manager_name=corp_user.manager_name,
            user_type=base_user.user_type,
            email_verified=base_user.email_verified,
            created_at=base_user.created_at,
        ),
    )


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
