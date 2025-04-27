from typing import Any, List

from app.domain.admin.repositories.user_repository import (
    get_corp_user_by_user_id,
    get_corp_users,
    get_seeker_user_by_user_id,
    get_seeker_users,
    get_user_by_id_query,
    patch_user_by_id,
)
from app.domain.admin.schemas.user_schemas import (
    CorpUserResponseSchema,
    SeekerUserResponseSchema,
    UserResponseDTO,
    UserUnionResponseDTO,
    UserUpdateSchema,
)
from app.domain.services.verification import check_existing, check_superuser
from app.exceptions.user_exceptions import UserNotFoundException


async def get_user_all_service(
    current_user: Any, seeker: bool, corp: bool, search: str
) -> List[UserUnionResponseDTO]:
    check_superuser(current_user)
    result: List[UserUnionResponseDTO] = []

    if seeker or (not seeker and not corp):
        seeker_users = await get_seeker_users(search)
        for s in seeker_users:
            result.append(
                UserUnionResponseDTO(
                    base=UserResponseDTO.from_orm(s.user),
                    seeker=SeekerUserResponseSchema.from_orm(s),
                )
            )

    if corp or (not seeker and not corp):
        corp_users = await get_corp_users(search)
        for c in corp_users:
            result.append(
                UserUnionResponseDTO(
                    base=UserResponseDTO.from_orm(c.user),
                    corp=CorpUserResponseSchema.from_orm(c),
                )
            )

    return result


async def get_user_by_id_service(
    current_user: Any,
    id: int,
) -> UserUnionResponseDTO:
    check_superuser(current_user)

    user = await get_user_by_id_query(id)
    check_existing(user, UserNotFoundException)

    seeker_user = await get_seeker_user_by_user_id(id)
    corp_user = await get_corp_user_by_user_id(id)

    return UserUnionResponseDTO(
        base=UserResponseDTO.from_orm(user),
        seeker=SeekerUserResponseSchema.from_orm(seeker_user) if seeker_user else None,
        corp=CorpUserResponseSchema.from_orm(corp_user) if corp_user else None,
    )


async def patch_user_by_id_service(
    id: int,
    patch_user: UserUpdateSchema,
    current_user: Any,
) -> UserResponseDTO:
    check_superuser(current_user)
    user = await get_user_by_id_query(id)
    check_existing(user, UserNotFoundException)

    user = await patch_user_by_id(user, patch_user)

    return user
