import re
from datetime import datetime
from typing import Optional

from passlib.hash import bcrypt

from app.domain.services.verification import CustomException
from app.domain.user.services.email_services import send_email_code
from app.domain.user.user_models import BaseUser, CorporateUser, SeekerUser
from app.domain.user.user_schema import (
    CompanyRegisterRequest,
    CompanyRegisterResponse,
    CompanyRegisterResponseData,
    UserRegisterRequest,
    UserRegisterResponse,
    UserRegisterResponseData,
)


async def register_user(request: UserRegisterRequest) -> UserRegisterResponse:
    existing_user = await BaseUser.get_or_none(email=request.email)
    if existing_user:
        raise CustomException(
            status_code=400, error="중복된 이메일입니다.", code="duplicate_email"
        )

    if len(request.password) < 8 or not re.search(
        r"[!@#$%^&*(),.?\":{}|<>]", request.password
    ):
        raise CustomException(
            status_code=400,
            error="비밀번호는 최소 8자 이상이며 특수 문자를 포함해야 합니다.",
            code="invalid_password",
        )

    if request.password != request.password_check:
        raise CustomException(
            status_code=400,
            error="비밀번호와 비밀번호 확인이 일치하지 않습니다.",
            code="password_mismatch",
        )

    hashed_password = bcrypt.hash(request.password)

    base_user = await BaseUser.create(
        email=request.email,
        password=hashed_password,
        user_type="seeker",
        gender=request.gender,
        is_superuser=False,
        status="pending",
    )

    seeker_user = await SeekerUser.create(
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
    existing_user = await BaseUser.get_or_none(email=request.email)
    if existing_user:
        raise CustomException(
            status_code=400, error="중복된 이메일입니다.", code="duplicate_email"
        )

    manager_exists = await CorporateUser.get_or_none(
        manager_email=request.manager_email
    )
    if manager_exists:
        raise CustomException(
            status_code=400, error="중복된 관리자 이메일입니다.", code="duplicate_manager_email"
        )

    if len(request.password) < 8 or not re.search(
        r"[!@#$%^&*(),.?\":{}|<>]", request.password
    ):
        raise CustomException(
            status_code=400,
            error="비밀번호는 최소 8자 이상이며 특수 문자를 포함해야 합니다.",
            code="invalid_password",
        )

    if request.password != request.password_check:
        raise CustomException(
            status_code=400,
            error="비밀번호와 비밀번호 확인이 일치하지 않습니다.",
            code="password_mismatch",
        )

    hashed_password = bcrypt.hash(request.password)
    base_user = await BaseUser.create(
        email=request.email,
        password=hashed_password,
        user_type="business",
        gender=request.gender,
        status="pending",
    )

    corp_user = await CorporateUser.create(
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
        raise CustomException(
            status_code=400, error="비밀번호가 일치하지 않습니다.", code="invalid_password"
        )

    current_user.deleted_at = datetime.utcnow()
    current_user.email_verified = False
    current_user.status = "delete"

    if reason:
        current_user.reason = reason  # 탈퇴 사유 추가

    await current_user.save()

    return {"message": "회원 탈퇴가 완료되었습니다."}
