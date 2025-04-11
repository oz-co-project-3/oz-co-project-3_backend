from fastapi import status

from app.models.user_models import BaseUser, CorporateUser, SeekerUser
from app.schemas.admin.admin_user_schemas import UserUpdateSchema
from app.utils.exception import CustomException, check_superuser


async def get_user_all(current_user: BaseUser, seeker: bool, corp: bool, search: str):
    check_superuser(current_user)
    result = []

    if seeker or (not seeker and not corp):
        if search:
            seeker_users = (
                await SeekerUser.filter(user__email__icontains=search)
                .select_related("user")
                .all()
            )
        else:
            seeker_users = await SeekerUser.all().select_related("user")
        for s in seeker_users:
            result.append({"base": s.user, "seeker": s})
    if corp or (not seeker and not corp):
        if search:
            corp_users = (
                await CorporateUser.filter(user__email__icontains=search)
                .select_related("user")
                .all()
            )
        else:
            corp_users = await CorporateUser.all().select_related("user")
        for c in corp_users:
            result.append({"base": c.user, "corp": c})
    return result


async def get_user_by_id(
    current_user: BaseUser,
    id: int,
):
    check_superuser(current_user)

    user = await BaseUser.filter(id=id).first()
    if not user:
        raise CustomException(
            status_code=status.HTTP_404_NOT_FOUND,
            error="존재하지 않는 유저입니다",
            code="user_not_found",
        )

    seeker_user = await SeekerUser.filter(user_id=id).first()
    corp_user = await CorporateUser.filter(user_id=id).first()

    return {
        "base": user,
        "seeker": seeker_user,
        "corp": corp_user,
    }


async def patch_user_by_id(
    id: int,
    patch_user: UserUpdateSchema,
    current_user: BaseUser,
):
    check_superuser(current_user)
    user = await BaseUser.filter(id=id).first()
    if not user:
        raise CustomException(
            status_code=status.HTTP_404_NOT_FOUND,
            error="유저가 없습니다",
            code="user_not_found",
        )

    user.is_active = patch_user.is_active
    await user.save()

    return user
