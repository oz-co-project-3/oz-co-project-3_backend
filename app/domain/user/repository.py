from typing import Optional

from app.domain.user.models import BaseUser, CorporateUser, SeekerUser


async def get_user_by_email(email: str) -> Optional[BaseUser]:
    return await BaseUser.get_or_none(email=email)


async def create_base_user(**kwargs) -> BaseUser:
    return await BaseUser.create(**kwargs)


async def get_seeker_profile_by_user(user: BaseUser) -> Optional[SeekerUser]:
    return await SeekerUser.get_or_none(user=user)


async def get_corporate_profile_by_user(user: BaseUser) -> Optional[CorporateUser]:
    return await CorporateUser.get_or_none(user=user)


async def get_seeker_by_name_and_phone(
    name: str, phone_number: str
) -> Optional[SeekerUser]:
    return await SeekerUser.get_or_none(
        name=name, phone_number=phone_number
    ).prefetch_related("user")


async def get_corporate_by_manager_name_and_phone(
    name: str, phone_number: str
) -> Optional[CorporateUser]:
    return await CorporateUser.get_or_none(
        manager_name=name, manager_phone_number=phone_number
    ).prefetch_related("user")


async def get_user_with_profiles_by_email(email: str) -> Optional[BaseUser]:
    return (
        await BaseUser.filter(email=email)
        .prefetch_related("seeker_profiles", "corporate_profiles")
        .first()
    )


async def create_seeker_profile(**kwargs) -> SeekerUser:
    return await SeekerUser.create(**kwargs)


async def create_corporate_profile(**kwargs) -> CorporateUser:
    return await CorporateUser.create(**kwargs)


async def get_seeker_profile_by_info(name: str, phone_number: str) -> SeekerUser:
    return await SeekerUser.get_or_none(name=name, phone_number=phone_number)


async def get_corporate_profile_by_info(name: str, phone_number: str) -> CorporateUser:
    return await CorporateUser.get_or_none(
        manager_name=name, manager_phone_number=phone_number
    )


async def get_user_by_id(user_id: str) -> BaseUser:
    return await BaseUser.get_or_none(id=user_id)
