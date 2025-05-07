import logging
from typing import Any

from app.domain.admin.repositories.resume_repository import get_resume_by_id
from app.domain.resume.models import WorkExp
from app.domain.resume.repository import (
    create_resume,
    delete_resume,
    delete_work_experiences_by_resume_id,
    get_resumes_by_user_id,
    get_total_resume_count_by_user_id,
    update_resume,
)
from app.domain.resume.schema import ResumeResponseSchema
from app.domain.services.permission import check_author
from app.domain.user.models import SeekerUser
from app.exceptions.auth_exceptions import PermissionDeniedException
from app.exceptions.resume_exceptions import (
    ResumeDeleteFailedException,
    ResumeNotFoundException,
)

logger = logging.getLogger(__name__)


async def create_resume_service(data: dict) -> ResumeResponseSchema:
    work_experiences = data.pop("work_experiences", [])

    resume = await create_resume(data)

    if work_experiences:
        work_exp_objects = []
        for work_exp in work_experiences:
            work_exp["resume_id"] = resume.id
            work_exp_objects.append(WorkExp(**work_exp))
        await WorkExp.bulk_create(work_exp_objects)

    await resume.fetch_related("work_experiences")

    return ResumeResponseSchema.model_validate(resume)


async def get_resume_by_id_service(
    resume_id: int, current_user: SeekerUser
) -> ResumeResponseSchema:
    resume = await get_resume_by_id(resume_id)
    if not resume:
        logger.warning(f"[RESUME] 이력서 id {resume_id}를 찾을 수 없습니다.")
        raise ResumeNotFoundException()

    await resume.fetch_related("user", "work_experiences")

    try:
        check_author(resume, current_user)
    except PermissionDeniedException:
        logger.warning(
            f"[RESUME] 이력서 id {resume_id}에 대해 사용자 id {current_user.id}의 접근 권한이 없습니다."
        )
        raise

    return ResumeResponseSchema.model_validate(resume)


async def get_all_resume_service(
    current_user: Any, offset: int = 0, limit: int = 10
) -> dict:
    page = (offset // limit) + 1
    resumes = await get_resumes_by_user_id(current_user.id, page=page, limit=limit)
    total_count = await get_total_resume_count_by_user_id(current_user.id)

    serialized = []
    for resume in resumes:
        await resume.fetch_related("user", "work_experiences")
        serialized.append(ResumeResponseSchema.model_validate(resume))

    return {
        "total": total_count,
        "offset": offset,
        "limit": limit,
        "data": serialized,
    }


async def update_resume_service(
    resume_id: int, data: dict, current_user: Any
) -> ResumeResponseSchema:
    resume = await get_resume_by_id(resume_id)
    if not resume:
        logger.warning(f"[RESUME] 업데이트하려는 이력서 id {resume_id}가 없습니다.")
        raise ResumeNotFoundException()

    await resume.fetch_related("user", "work_experiences")

    try:
        check_author(resume, current_user)
    except PermissionDeniedException:
        logger.warning(
            f"[RESUME] 이력서 id {resume_id}의 수정 권한이 사용자 id {current_user.id}에게 없습니다."
        )
        raise

    # 업데이트 가능한 필드만 처리 // user 및 work_experiences 필드 제외
    updatable_fields = {
        k: v for k, v in data.items() if k not in ["user", "work_experiences"]
    }
    updated_resume = await update_resume(resume_id, updatable_fields)

    if updated_resume:
        await updated_resume.fetch_related("user", "work_experiences")
        return ResumeResponseSchema.from_orm(updated_resume)
    else:
        logger.warning(f"[RESUME] 이력서 id {resume_id} 업데이트에 실패했습니다.")
        raise ResumeNotFoundException()


async def delete_resume_service(resume_id: int, current_user: Any) -> None:
    resume = await get_resume_by_id(resume_id)
    if not resume:
        logger.warning(f"[RESUME] 삭제하려는 이력서 id {resume_id}가 없습니다.")
        raise ResumeNotFoundException()

    try:
        check_author(resume, current_user)
    except PermissionDeniedException:
        logger.warning(
            f"[RESUME] 이력서 id {resume_id} 삭제 권한이 사용자 id {current_user.id}에게 없습니다."
        )
        raise

    deleted_work_exps = await delete_work_experiences_by_resume_id(resume_id)
    if deleted_work_exps is False:
        logger.warning(f"[RESUME] 이력서 id {resume_id}의 경력 사항 삭제에 문제가 발생했습니다.")

    deleted = await delete_resume(resume_id)
    if not deleted:
        logger.warning(f"[RESUME] 이력서 id {resume_id} 삭제에 실패했습니다.")
        raise ResumeDeleteFailedException()
