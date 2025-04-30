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
    BusinessUpgradeData,
    BusinessUpgradeRequest,
    BusinessUpgradeResponseDTO,
    UserDeleteData,
    UserDeleteResponseDTO,
    UserRegisterRequest,
    UserRegisterResponseData,
    UserRegisterResponseDTO,
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


async def register_user(request: UserRegisterRequest) -> UserRegisterResponseDTO:
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

    return UserRegisterResponseDTO(
        success=True,
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
async def upgrade_to_business(
    user: BaseUser, request: BusinessUpgradeRequest
) -> BusinessUpgradeResponseDTO:
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
    user.user_type = "business,normal"
    await user.save()

    # 새 access_token, refresh_token 발급
    access_token, refresh_token = create_jwt_tokens(str(user.id), user.user_type)

    return BusinessUpgradeResponseDTO(
        success=True,
        data=BusinessUpgradeData(
            access_token=access_token,
            refresh_token=refresh_token,
            user_id=user.id,
            user_type=user.user_type,
            email=user.email,
        ),
    )


async def delete_user(
    current_user: BaseUser, password: str, reason: Optional[str] = None
) -> UserDeleteResponseDTO:
    if not bcrypt.verify(password, current_user.password):
        raise PasswordMismatchException()

    current_user.deleted_at = datetime.utcnow()
    current_user.email_verified = False
    current_user.status = "delete"

    if reason:
        current_user.reason = reason

    await current_user.save()

    return UserDeleteResponseDTO(
        success=True,
        data=UserDeleteData(
            user_id=current_user.id,
            email=current_user.email,
            reason=current_user.reason,
            deleted_at=current_user.deleted_at,
        ),
    )
