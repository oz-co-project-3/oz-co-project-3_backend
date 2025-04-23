from app.domain.user.user_models import BaseUser, CorporateUser, SeekerUser


async def get_seeker_users(search: str = ""):
    if search:
        return (
            await SeekerUser.filter(user__email__icontains=search)
            .select_related("user")
            .all()
        )
    return await SeekerUser.all().select_related("user")


async def get_corp_users(search: str = ""):
    if search:
        return (
            await CorporateUser.filter(user__email__icontains=search)
            .select_related("user")
            .all()
        )
    return await CorporateUser.all().select_related("user")


async def get_user_by_id_query(user_id: int):
    return await BaseUser.filter(id=user_id).first()


async def get_seeker_user_by_user_id(user_id: int):
    return await SeekerUser.filter(user_id=user_id).first()


async def get_corp_user_by_user_id(user_id: int):
    return await CorporateUser.filter(user_id=user_id).first()


async def patch_user_by_id(user, patch_user):
    user.status = patch_user.status
    await user.save()

    return user
