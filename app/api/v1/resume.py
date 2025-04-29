from typing import List

from fastapi import APIRouter, Depends, status

from app.core.token import get_current_user
from app.domain.resume.schema import (
    PaginatedResumeResponse,
    ResumeRequestSchema,
    ResumeResponseSchema,
)
from app.domain.resume.service import ResumeService
from app.domain.user.user_models import BaseUser, SeekerUser
from app.exceptions.auth_exceptions import PermissionDeniedException

resume_router = APIRouter(prefix="/api/resume", tags=["resumes"])


async def get_seeker_user(current_user: BaseUser) -> SeekerUser:
    seeker_user = await SeekerUser.get_or_none(user=current_user)
    if not seeker_user:
        raise PermissionDeniedException
    return seeker_user


@resume_router.post(
    "/",
    response_model=ResumeResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="이력서 생성",
    description="""
`400` `code`:`required_field` 필수 필드 누락\n
`401` `code`:`auth_required` 인증이 필요합니다.\n
`401` `code`:`invalid_token` 유효하지 않은 토큰입니다.\n
    """,
)
async def create_resume(
    resume_data: ResumeRequestSchema,
    current_user: SeekerUser = Depends(get_current_user),
):
    seeker_user = await get_seeker_user(current_user)
    resume_data.user = seeker_user
    """
    이력서를 생성합니다.

    - 필수 입력 필드를 모두 작성해야 성공적으로 생성됩니다.
    """
    return await ResumeService.create_resume_service(resume_data.model_dump())


@resume_router.get(
    "/{user_id}/",
    response_model=PaginatedResumeResponse,
    status_code=status.HTTP_200_OK,
    summary="이력서 전체 조회",
    description="""
`401` `code`:`auth_required` 인증이 필요합니다.\n
`401` `code`:`invalid_token` 유효하지 않은 토큰입니다.\n
    """,
)
async def get_all_resumes(
    offset: int = 0,
    limit: int = 10,
    current_user: SeekerUser = Depends(get_current_user),
):
    seeker_user = await get_seeker_user(current_user)
    return await ResumeService.get_all_resume_service(
        current_user=seeker_user, offset=offset, limit=limit
    )


@resume_router.get(
    "/{resume_id}/",
    response_model=ResumeResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="이력서 상세 조회",
    description="""
`401` `code`:`auth_required` 인증이 필요합니다.\n
`401` `code`:`invalid_token` 유효하지 않은 토큰입니다.\n
`404` `code`:`resume_not_found` 존재하지 않는 이력서입니다.\n
    """,
)
async def get_resume(
    resume_id: int,
    current_user: SeekerUser = Depends(get_current_user),
):
    seeker_user = await get_seeker_user(current_user)
    """
    특정 ID의 이력서를 조회합니다.

    - 작성자 또는 관리자가 아닌 경우 권한이 거부됩니다.
    """
    return await ResumeService.get_resume_by_id_service(resume_id, seeker_user)


@resume_router.patch(
    "/{resume_id}/",
    response_model=ResumeResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="이력서 수정",
    description="""
`401` `code`:`auth_required` 인증이 필요합니다.\n
`401` `code`:`invalid_token` 유효하지 않은 토큰입니다.\n
`403` `code`:`permission_denied` 권한이 없습니다, 작성자가 아닙니다.\n
`404` `code`:`resume_not_found` 존재하지 않는 이력서입니다.\n
    """,
)
async def update_resume(
    resume_id: int,
    resume_data: ResumeRequestSchema,
    current_user: SeekerUser = Depends(get_current_user),
):
    seeker_user = await get_seeker_user(current_user)
    """
    특정 ID의 이력서를 수정합니다.

    - 작성자 또는 관리자가 아닌 경우 권한이 거부됩니다.
    """
    return await ResumeService.update_resume_service(
        resume_id=resume_id, data=resume_data.model_dump(), current_user=seeker_user
    )


@resume_router.delete(
    "/{resume_id}/",
    status_code=status.HTTP_200_OK,
    summary="이력서 삭제",
    description="""
    특정 ID의 이력서를 삭제합니다.

    작성자 또는 관리자가 아닌 경우 권한이 거부됩니다.
    """,
    responses={
        401: {"description": "인증이 필요합니다."},
        403: {"description": "작성자가 아니므로 권한이 없습니다."},
        404: {"description": "존재하지 않는 이력서입니다."},
    },
)
async def delete_resume(
    resume_id: int,
    current_user: SeekerUser = Depends(get_current_user),
):
    seeker_user = await get_seeker_user(current_user)
    await ResumeService.delete_resume_service(resume_id, seeker_user)
    return {"message": "삭제가 완료되었습니다."}
