import logging
import re
from datetime import datetime
from typing import Optional

from passlib.hash import bcrypt

from app.core.token import create_jwt_tokens
from app.domain.services.business_verify import verify_business_number
from app.domain.services.email_detail import send_email_code
from app.domain.user.models import BaseUser, CorporateUser
from app.domain.user.repository import (
    check_duplicate_phone_number,
    create_base_user,
    create_seeker_profile,
    get_corporate_profile_by_user,
    get_seeker_profile_by_user,
    get_user_by_email,
)
from app.domain.user.schema import (
    BusinessUpgradeDTO,
    BusinessUpgradeRequest,
    CorporateProfileResponse,
    SeekerProfileResponse,
    UserDeleteDTO,
    UserRegisterRequest,
    UserRegisterResponseDTO,
    UserResponseDTO,
    UserUnionResponseDTO,
)
from app.exceptions.auth_exceptions import (
    InvalidPasswordException,
    PasswordMismatchException,
)
from app.exceptions.email_exceptions import DuplicateEmailException
from app.exceptions.user_exceptions import (
    AlreadyBusinessUserException,
    DuplicatePhoneNumberException,
    InvalidBusinessNumberException,
)

logger = logging.getLogger(__name__)


async def register_user(request: UserRegisterRequest) -> UserUnionResponseDTO:
    existing_user = await get_user_by_email(email=request.email)
    if existing_user:
        logger.warning(f"[CHECK] 동일한 이메일 발견: {request.email}")
        raise DuplicateEmailException()

    if not check_duplicate_phone_number(request):
        raise DuplicatePhoneNumberException()

    if len(request.password) < 8 or not re.search(
        r"[!@#$%^&*(),.?\":{}|<>]", request.password
    ):
        logger.warning(f"[CHECK] 부적절한 패스워드: {request.password}")
        raise InvalidPasswordException()

    if request.password != request.password_check:
        logger.warning(f"[CHECK] 패스워드 같지 않음: {request.password}")
        raise PasswordMismatchException()

    hashed_password = bcrypt.hash(request.password)

    base_user = await create_base_user(
        email=request.email,
        password=hashed_password,
        user_type="normal",
        gender=request.gender,
        status="pending",
        signinMethod=request.signinMethod,
    )

    interests = (
        ",".join(request.interests)
        if isinstance(request.interests, list)
        else request.interests
    )
    purposes = (
        ",".join(request.purposes)
        if isinstance(request.purposes, list)
        else request.purposes
    )
    sources = (
        ",".join(request.sources)
        if isinstance(request.sources, list)
        else request.sources
    )

    await create_seeker_profile(
        user=base_user,
        name=request.name,
        phone_number=request.phone_number,
        birth=request.birth,
        gender=request.gender,
        interests=interests,
        purposes=purposes,
        sources=sources,
        status=request.status,
    )

    # 여기서 인증메일 발송
    await send_email_code(email=base_user.email, purpose="회원가입")

    corp_profile = await get_corporate_profile_by_user(user=base_user)
    seeker_profile = await get_seeker_profile_by_user(user=base_user)

    return UserUnionResponseDTO(
        base=UserResponseDTO.from_orm(base_user),
        seeker=SeekerProfileResponse.from_orm(seeker_profile)
        if seeker_profile
        else None,
        corp=CorporateProfileResponse.from_orm(corp_profile) if corp_profile else None,
    )


# 기업회원 업그레이드
async def upgrade_to_business(
    user: BaseUser, request: BusinessUpgradeRequest
) -> BusinessUpgradeDTO:
    # 이미 business 등록된 경우 막기
    if user.user_type == "business":
        logger.warning(f"[CHECK] 이미 존재하는 비지니스 유저: {user.user_type}")
        raise AlreadyBusinessUserException()

    # 사업자번호 인증
    result = await verify_business_number(request.business_number)
    if not result.get("is_valid"):
        logger.warning(f"[CHECK] 국세청에 등록되어 있지 않은 사업자 등록번호: {request.business_number}")
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

    return BusinessUpgradeDTO(
        access_token=access_token,
        refresh_token=refresh_token,
        user_id=user.id,
        user_type=user.user_type,
        email=user.email,
    )


async def delete_user(
    current_user: BaseUser, password: str, reason: Optional[str] = None
) -> UserDeleteDTO:
    if not bcrypt.verify(password, current_user.password):
        logger.warning(f"[CHECK] 패스워드 같지 않음: {password}")
        raise PasswordMismatchException()

    current_user.deleted_at = datetime.utcnow()
    current_user.email_verified = False
    current_user.status = "delete"

    if reason:
        current_user.leave_reason = reason

    await current_user.save()

    return UserDeleteDTO(
        user_id=current_user.id,
        email=current_user.email,
        reason=current_user.leave_reason,
        deleted_at=current_user.deleted_at,
    )
