import logging

from app.domain.job_posting.models import Applicants
from app.domain.services.user_type_helper import split_user_types
from app.domain.user.models import BaseUser
from app.domain.user.repository import (
    get_corporate_profile_by_user,
    get_seeker_profile_by_user,
)
from app.domain.user.schema import (
    CorporateProfileResponse,
    CorporateProfileUpdateRequest,
    CorporateProfileUpdateResponse,
    SeekerProfileResponse,
    SeekerProfileUpdateRequest,
    SeekerProfileUpdateResponse,
    UserProfileUpdateResponseDTO,
    UserRegisterRequest,
    UserRegisterResponseDTO,
    UserResponseDTO,
    UserUnionResponseDTO,
)
from app.exceptions.server_exceptions import UnknownUserTypeException

logger = logging.getLogger(__name__)


# 프로필 조회
async def get_user_profile(current_user: BaseUser) -> UserUnionResponseDTO:
    corp_profile = await get_corporate_profile_by_user(user=current_user)
    seeker_profile = await get_seeker_profile_by_user(user=current_user)

    applied_qs = await Applicants.filter(user=current_user).order_by("-id").all()
    applied_posting_ids = [a.job_posting_id for a in applied_qs]

    seeker_profile.applied_posting = applied_posting_ids
    seeker_profile.applied_posting_count = len(applied_posting_ids)

    return UserUnionResponseDTO(
        base=UserResponseDTO.from_orm(current_user),
        seeker=SeekerProfileResponse.from_orm(seeker_profile),
        corp=CorporateProfileResponse.from_orm(corp_profile),
    )


# 프로필 수정 일반 / 기업 유저 나누어서 작성
# 구직자 유저
async def update_seeker_profile(
    current_user: BaseUser, update_data: SeekerProfileUpdateRequest
) -> UserProfileUpdateResponseDTO:
    profile = await get_seeker_profile_by_user(user=current_user)

    if update_data.name is not None:
        profile.name = update_data.name
    if update_data.phone_number is not None:
        profile.phone_number = update_data.phone_number
    if update_data.birth is not None:
        profile.birth = update_data.birth
    if update_data.interests is not None:
        profile.interests = (
            ",".join(update_data.interests)
            if isinstance(update_data.interests, list)
            else update_data.interests
        )
    if update_data.purposes is not None:
        profile.purposes = (
            ",".join(update_data.purposes)
            if isinstance(update_data.purposes, list)
            else update_data.purposes
        )
    if update_data.sources is not None:
        profile.sources = (
            ",".join(update_data.sources)
            if isinstance(update_data.sources, list)
            else update_data.sources
        )
    if update_data.status is not None:
        profile.status = update_data.status
    if update_data.profile_url is not None:
        profile.profile_url = update_data.profile_url

    await profile.save()

    seeker_data = SeekerProfileUpdateResponse(
        id=current_user.id,
        name=profile.name,
        email=current_user.email,
        phone_number=profile.phone_number,
        birth=profile.birth,
        interests=profile.interests.split(",")
        if isinstance(profile.interests, str)
        else profile.interests,
        status=profile.status,
        profile_url=profile.profile_url,
    )

    return UserProfileUpdateResponseDTO(success=True, data=seeker_data)


# 기업 유저
async def update_corporate_profile(
    current_user: BaseUser, update_data: CorporateProfileUpdateRequest
) -> UserProfileUpdateResponseDTO:
    profile = await get_corporate_profile_by_user(user=current_user)

    if update_data.company_name is not None:
        profile.company_name = update_data.company_name
    if update_data.company_description is not None:
        profile.company_description = update_data.company_description
    if update_data.manager_name is not None:
        profile.manager_name = update_data.manager_name
    if update_data.manager_phone_number is not None:
        profile.manager_phone_number = update_data.manager_phone_number
    if update_data.manager_email is not None:
        profile.manager_email = update_data.manager_email
    if update_data.profile_url is not None:
        profile.profile_url = update_data.profile_url

    await profile.save()

    corp_data = CorporateProfileUpdateResponse(
        id=current_user.id,
        company_name=profile.company_name,
        email=current_user.email,
        company_description=profile.company_description,
        manager_name=profile.manager_name,
        manager_phone_number=profile.manager_phone_number,
        manager_email=profile.manager_email,
        profile_url=profile.profile_url,
    )

    return UserProfileUpdateResponseDTO(success=True, data=corp_data)


async def update_user_profile(
    current_user: BaseUser, update_data, target_type: str
) -> UserProfileUpdateResponseDTO:
    user_types = split_user_types(current_user.user_type)

    if target_type == "normal" and "normal" in user_types:
        return await update_seeker_profile(current_user, update_data)
    elif target_type == "business" and "business" in user_types:
        return await update_corporate_profile(current_user, update_data)
    else:
        raise UnknownUserTypeException()
