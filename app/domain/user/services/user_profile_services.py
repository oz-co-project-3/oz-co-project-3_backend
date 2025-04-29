from typing import Union

from app.domain.job_posting.models import Applicants
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
    UserProfileResponse,
    UserProfileUpdateResponse,
)
from app.exceptions.server_exceptions import UnknownUserTypeException


async def get_user_profile(current_user: BaseUser) -> UserProfileResponse:
    if current_user.user_type == "business":
        # 기업회원 프로필 조회
        profile = await get_corporate_profile_by_user(user=current_user)

        return UserProfileResponse(
            data=CorporateProfileResponse(
                id=current_user.id,
                email=current_user.email,
                user_type=current_user.user_type,
                company_name=profile.company_name,
                business_number=profile.business_number,
                business_start_date=profile.business_start_date,
                company_description=profile.company_description,
                manager_name=profile.manager_name,
                manager_phone_number=profile.manager_phone_number,
                manager_email=profile.manager_email,
                email_verified=current_user.email_verified,
                created_at=current_user.created_at,
                updated_at=None,
                profile_url=profile.profile_url,
            )
        )

    elif current_user.user_type == "normal":
        # 구직자 프로필 조회
        profile = await get_seeker_profile_by_user(user=current_user)

        applied_qs = await Applicants.filter(user=current_user).order_by("-id").all()
        applied_posting_ids = [a.job_posting_id for a in applied_qs]

        return UserProfileResponse(
            data=SeekerProfileResponse(
                id=current_user.id,
                email=current_user.email,
                user_type=current_user.user_type,
                name=profile.name,
                phone_number=profile.phone_number,
                birth=profile.birth,
                interests=profile.interests.split(",") if profile.interests else [],
                purposes=profile.purposes.split(",") if profile.purposes else [],
                sources=profile.sources.split(",") if profile.sources else [],
                status=profile.status,
                is_social=profile.is_social,
                email_verified=current_user.email_verified,
                applied_posting=applied_posting_ids,
                applied_posting_count=len(applied_posting_ids),
                created_at=current_user.created_at,
                updated_at=None,
                profile_url=profile.profile_url,
            )
        )

    else:
        raise UnknownUserTypeException()


# 프로필 수정
async def update_user_profile(
    current_user: BaseUser,
    update_data: Union[SeekerProfileUpdateRequest, CorporateProfileUpdateRequest],
) -> UserProfileUpdateResponse:
    if hasattr(update_data, "company_name") or hasattr(update_data, "manager_name"):
        # 기업 프로필 수정
        profile = await get_corporate_profile_by_user(user=current_user)

        if (
            hasattr(update_data, "company_name")
            and update_data.company_name is not None
        ):
            profile.company_name = update_data.company_name
        if (
            hasattr(update_data, "company_description")
            and update_data.company_description is not None
        ):
            profile.company_description = update_data.company_description
        if (
            hasattr(update_data, "manager_name")
            and update_data.manager_name is not None
        ):
            profile.manager_name = update_data.manager_name
        if (
            hasattr(update_data, "manager_phone_number")
            and update_data.manager_phone_number is not None
        ):
            profile.manager_phone_number = update_data.manager_phone_number
        if (
            hasattr(update_data, "manager_email")
            and update_data.manager_email is not None
        ):
            profile.manager_email = update_data.manager_email
        if hasattr(update_data, "profile_url") and update_data.profile_url is not None:
            profile.profile_url = update_data.profile_url

        await profile.save()

        return UserProfileUpdateResponse(
            message="회원 정보가 수정되었습니다.",
            data=CorporateProfileUpdateResponse(
                id=current_user.id,
                company_name=profile.company_name,
                email=current_user.email,
                company_description=profile.company_description,
                manager_name=profile.manager_name,
                manager_phone_number=profile.manager_phone_number,
                manager_email=profile.manager_email,
                profile_url=profile.profile_url,
            ),
        )

    else:
        # 구직자 프로필 수정
        profile = await get_seeker_profile_by_user(user=current_user)

        if hasattr(update_data, "name") and update_data.name is not None:
            profile.name = update_data.name
        if (
            hasattr(update_data, "phone_number")
            and update_data.phone_number is not None
        ):
            profile.phone_number = update_data.phone_number
        if hasattr(update_data, "birth") and update_data.birth is not None:
            profile.birth = update_data.birth
        if hasattr(update_data, "interests") and update_data.interests is not None:
            profile.interests = update_data.interests
        if hasattr(update_data, "purposes") and update_data.purposes is not None:
            profile.purposes = update_data.purposes
        if hasattr(update_data, "sources") and update_data.sources is not None:
            profile.sources = update_data.sources
        if hasattr(update_data, "status") and update_data.status is not None:
            profile.status = update_data.status
        if hasattr(update_data, "profile_url") and update_data.profile_url is not None:
            profile.profile_url = update_data.profile_url

        await profile.save()

        return UserProfileUpdateResponse(
            message="회원 정보가 수정되었습니다.",
            data=SeekerProfileUpdateResponse(
                id=current_user.id,
                name=profile.name,
                email=current_user.email,
                phone_number=profile.phone_number,
                birth=profile.birth,
                interests=eval(profile.interests)
                if isinstance(profile.interests, str)
                else profile.interests,
                status=profile.status,
                profile_url=profile.profile_url,
            ),
        )
