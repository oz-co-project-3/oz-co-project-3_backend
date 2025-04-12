from typing import List

from fastapi import APIRouter, Depends, Query, status

from app.core.token import get_current_user
from app.models.user_models import BaseUser
from app.schemas.admin.admin_resume_schemas import ResumeResponseSchema
from app.schemas.admin.admin_user_schemas import (
    UserResponseSchema,
    UserUnionResponseSchema,
    UserUpdateSchema,
)
from app.services.admin.admin_resume_services import (
    delete_resume_by_id,
    get_all_resumes,
    get_resume_by_id,
)
from app.services.admin.admin_user_services import (
    get_user_all,
    get_user_by_id,
    patch_user_by_id,
)

admin_router = APIRouter(prefix="/api/admin", tags=["admin"])


@admin_router.get(
    "/user/",
    response_model=List[UserUnionResponseSchema],
    status_code=status.HTTP_200_OK,
    summary="관리자 유저 전체 조회",
    description="""
        - `401` `code`:`auth_required` 인증이 필요합니다.\n
        - `401` `code`:`invalid_token` 유효하지 않은 토큰입니다.\n
        - `403` `code`:`permission_denied` 권한이 없습니다.\n
        """,
)
async def get_list_user(
    current_user: BaseUser = Depends(get_current_user),
    seeker: bool = Query(default=False),
    corp: bool = Query(default=False),
    search: str = Query(default=None),
):
    return await get_user_all(current_user, seeker, corp, search)


@admin_router.get(
    "/user/{id}/",
    response_model=UserUnionResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="관리자 유저 상세 조회",
    description="""
        - `401` `code`:`auth_required` 인증이 필요합니다.\n
        - `401` `code`:`invalid_token` 유효하지 않은 토큰입니다.\n
        - `403` `code`:`permission_denied` 권한이 없습니다.\n
        """,
)
async def get_user(
    id: int,
    current_user: BaseUser = Depends(get_current_user),
):
    return await get_user_by_id(id=id, current_user=current_user)


@admin_router.patch(
    "/user/{id}/",
    response_model=UserResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="관리자 유저 상세 조회",
    description="""
    - `401` `code`:`auth_required` 인증이 필요합니다.\n
    - `401` `code`:`invalid_token` 유효하지 않은 토큰입니다.\n
    - `403` `code`:`permission_denied` 권한이 없습니다.\n
    """,
)
async def patch_user(
    id: int,
    patch_user: UserUpdateSchema,
    current_user: BaseUser = Depends(get_current_user),
):
    return await patch_user_by_id(
        id=id, patch_user=patch_user, current_user=current_user
    )


@admin_router.get(
    "/resume/",
    response_model=List[ResumeResponseSchema],
    status_code=status.HTTP_200_OK,
    summary="관리자 이력서 전체 조회",
    description="""
        - `401` `code`:`auth_required` 인증이 필요합니다.\n
        - `401` `code`:`invalid_token` 유효하지 않은 토큰입니다.\n
        - `403` `code`:`permission_denied` 권한이 없습니다.\n
        """,
)
async def get_list_resumes(
    current_user: BaseUser = Depends(get_current_user), name=Query(default=None)
):
    return await get_all_resumes(current_user, name)


@admin_router.get(
    "/resume/{id}/",
    response_model=ResumeResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="관리자 이력서 상세 조회",
    description="""
        - `401` `code`:`auth_required` 인증이 필요합니다.\n
        - `401` `code`:`invalid_token` 유효하지 않은 토큰입니다.\n
        - `403` `code`:`permission_denied` 권한이 없습니다.\n
        - `404` `code`:`resume_not_found` 권한이 없습니다.\n
        """,
)
async def get_resume(
    id: int,
    current_user: BaseUser = Depends(get_current_user),
):
    return await get_resume_by_id(id=id, current_user=current_user)


@admin_router.delete(
    "/resume/{id}/",
    status_code=status.HTTP_200_OK,
    summary="관리자 이력서 삭제",
    description="""
        - `401` `code`:`auth_required` 인증이 필요합니다.\n
        - `401` `code`:`invalid_token` 유효하지 않은 토큰입니다.\n
        - `403` `code`:`permission_denied` 권한이 없습니다.\n
        - `404` `code`:`resume_not_found` 권한이 없습니다.\n
        """,
)
async def delete_resume(
    id: int,
    current_user: BaseUser = Depends(get_current_user),
):
    await delete_resume_by_id(id=id, current_user=current_user)

    return {"message": "이력서 삭제가 완료되었습니다."}
