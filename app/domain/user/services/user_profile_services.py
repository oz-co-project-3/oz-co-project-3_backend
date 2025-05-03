import logging

from app.domain.job_posting.models import Applicants
from app.domain.services.user_type_helper import split_user_types
from app.domain.user.models import BaseUser
from app.domain.user.repository import (
    get_bookmark_postings_by_repository,
    get_corporate_profile_by_user,
    get_seeker_profile_by_user,
)
from app.domain.user.schema import (
    BookMarkPostingDTO,
    CorporateProfileResponse,
    CorporateProfileUpdateRequest,
    SeekerProfileResponse,
    SeekerProfileUpdateRequest,
    UserResponseDTO,
    UserUnionResponseDTO,
)
from app.exceptions.job_posting_exceptions import NotCorpUserException

logger = logging.getLogger(__name__)


# 프로필 조회
async def get_user_profile(current_user: BaseUser) -> UserUnionResponseDTO:
    corp_profile = await get_corporate_profile_by_user(user=current_user)
    seeker_profile = await get_seeker_profile_by_user(user=current_user)

    if seeker_profile:
        applied_qs = await Applicants.filter(user=current_user).order_by("-id").all()
        applied_posting_ids = [a.job_posting_id for a in applied_qs]

        seeker_profile.applied_posting = applied_posting_ids
        seeker_profile.applied_posting_count = len(applied_posting_ids)

    return UserUnionResponseDTO(
        base=UserResponseDTO.from_orm(current_user),
        seeker=SeekerProfileResponse.from_orm(seeker_profile)
        if seeker_profile
        else None,
        corp=CorporateProfileResponse.from_orm(corp_profile) if corp_profile else None,
    )


# 프로필 수정 일반 / 기업 유저 나누어서 작성
# 구직자 유저
async def update_seeker_profile(
    current_user: BaseUser, update_data: SeekerProfileUpdateRequest
) -> UserUnionResponseDTO:
    profile = await get_seeker_profile_by_user(user=current_user)
    corp_profile = await get_corporate_profile_by_user(user=current_user)

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

    return UserUnionResponseDTO(
        base=UserResponseDTO.from_orm(current_user),
        seeker=SeekerProfileResponse.from_orm(profile) if profile else None,
        corp=CorporateProfileResponse.from_orm(corp_profile) if corp_profile else None,
    )


# 기업 유저
async def update_corporate_profile(
    current_user: BaseUser, update_data: CorporateProfileUpdateRequest
) -> UserUnionResponseDTO:
    profile = await get_corporate_profile_by_user(user=current_user)
    seeker_profile = await get_seeker_profile_by_user(user=current_user)

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

    return UserUnionResponseDTO(
        base=UserResponseDTO.from_orm(current_user),
        seeker=SeekerProfileResponse.from_orm(seeker_profile)
        if seeker_profile
        else None,
        corp=CorporateProfileResponse.from_orm(profile) if profile else None,
    )


async def update_user_profile(
    current_user: BaseUser, update_data, target_type: str
) -> UserUnionResponseDTO:
    user_types = split_user_types(current_user.user_type)

    if target_type == "normal":
        if "normal" in user_types:
            return await update_seeker_profile(current_user, update_data)
    else:
        if "business" in user_types:
            return await update_corporate_profile(current_user, update_data)
        raise NotCorpUserException()


async def get_bookmark_postings_by_service(current_user: BaseUser):
    results = await get_bookmark_postings_by_repository(current_user)
    postings = [BookMarkPostingDTO.from_orm(result) for result in results]

    return postings
