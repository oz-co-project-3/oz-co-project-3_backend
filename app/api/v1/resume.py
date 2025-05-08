import logging

from fastapi import APIRouter, Depends, status

from app.core.token import get_current_user
from app.domain.resume.repository import get_seeker_user
from app.domain.resume.schema import (
    PaginatedResumeResponse,
    ResumeRequestSchema,
    ResumeResponseSchema,
)
from app.domain.resume.service import (
    create_resume_service,
    delete_resume_service,
    get_all_resume_service,
    get_resume_by_id_service,
    update_resume_service,
)
from app.domain.services.verification import check_existing
from app.domain.user.models import BaseUser, SeekerUser
from app.exceptions.resume_exceptions import ResumeNotFoundException
from app.exceptions.user_exceptions import UserNotFoundException

resume_router = APIRouter(prefix="/api/resume", tags=["resumes"])

logger = logging.getLogger(__name__)


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
async def create_resume_endpoint(
    resume_data: ResumeRequestSchema,
    current_user: BaseUser = Depends(get_current_user),
):
    logger.info(f"[API] 이력서 생성 요청 : current_user_id={current_user.id}")
    seeker_user = await get_seeker_user(current_user)
    check_existing(seeker_user, ResumeNotFoundException)
    resume_data.user = seeker_user
    result = await create_resume_service(resume_data.model_dump())
    logger.info(f"[API] 이력서 생성 완료 : seeker_user_id={seeker_user.id}")
    return result


@resume_router.get(
    "/",
    response_model=PaginatedResumeResponse,
    status_code=status.HTTP_200_OK,
    summary="이력서 전체 조회",
    description="""
`401` `code`:`auth_required` 인증이 필요합니다.\n
`401` `code`:`invalid_token` 유효하지 않은 토큰입니다.\n
`404` `code`:`user_not_found` 유저가 없습니다\n
    """,
)
async def get_all_resumes_endpoint(
    offset: int = 0,
    limit: int = 10,
    current_user: BaseUser = Depends(get_current_user),
):
    logger.info(
        f"[API] 이력서 전체 조회 요청 : current_user_id={current_user.id}, offset={offset}, limit={limit}"
    )
    seeker_user = await get_seeker_user(current_user)
    check_existing(seeker_user, UserNotFoundException)
    result = await get_all_resume_service(
        current_user=seeker_user, offset=offset, limit=limit
    )
    logger.info(f"[API] 이력서 전체 조회 완료 : seeker_user_id={seeker_user.id}")
    return result


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
async def get_resume_endpoint(
    resume_id: int,
    current_user: BaseUser = Depends(get_current_user),
):
    logger.info(
        f"[API] 이력서 상세 조회 요청 : resume_id={resume_id}, current_user_id={current_user.id}"
    )
    seeker_user = await get_seeker_user(current_user)
    check_existing(seeker_user, ResumeNotFoundException)
    result = await get_resume_by_id_service(resume_id, seeker_user)
    logger.info(
        f"[API] 이력서 상세 조회 완료 : resume_id={resume_id}, seeker_user_id={seeker_user.id}"
    )
    return result


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
async def update_resume_enpoint(
    resume_id: int,
    resume_data: ResumeRequestSchema,
    current_user: BaseUser = Depends(get_current_user),
):
    logger.info(
        f"[API] 이력서 수정 요청 : resume_id={resume_id}, current_user_id={current_user.id}"
    )
    seeker_user = await get_seeker_user(current_user)
    check_existing(seeker_user, ResumeNotFoundException)
    result = await update_resume_service(
        resume_id=resume_id, data=resume_data.model_dump(), current_user=seeker_user
    )
    logger.info(
        f"[API] 이력서 수정 완료 : resume_id={resume_id}, seeker_user_id={seeker_user.id}"
    )
    return result


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
async def delete_resume_endpoint(
    resume_id: int,
    current_user: SeekerUser = Depends(get_current_user),
):
    seeker_user = await get_seeker_user(current_user)
    check_existing(seeker_user, ResumeNotFoundException)
    logger.info(
        f"[API] 이력서 삭제 요청 : resume_id={resume_id}, seeker_user_id={seeker_user.id}"
    )
    await delete_resume_service(resume_id, seeker_user)
    logger.info(
        f"[API] 이력서 삭제 완료 : resume_id={resume_id}, seeker_user_id={seeker_user.id}"
    )
    return {"message": "삭제가 완료되었습니다."}
