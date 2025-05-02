import logging
from typing import Any, List, Optional

from app.domain.resume.models import Resume, WorkExp
from app.domain.resume.repository import ResumeRepository, WorkExpRepository
from app.domain.resume.schema import ResumeResponseSchema
from app.domain.services.permission import check_author
from app.domain.user.models import SeekerUser
from app.exceptions.auth_exceptions import PermissionDeniedException
from app.exceptions.resume_exceptions import (
    ResumeDeleteFailedException,
    ResumeNotFoundException,
)

logger = logging.getLogger(__name__)


class ResumeService:
    @staticmethod
    async def create_resume_service(data: dict) -> ResumeResponseSchema:
        work_experiences = data.pop("work_experiences", [])

        resume = await ResumeRepository.create_resume(data)

        # work_experiences가 있다면 벌크 생성 진행
        if work_experiences:
            work_exp_objects = []
            for work_exp in work_experiences:
                work_exp["resume_id"] = resume.id
                work_exp_objects.append(WorkExp(**work_exp))
            # bulk_create 호출
            await WorkExp.bulk_create(work_exp_objects)

        await resume.fetch_related("work_experiences")

        return ResumeResponseSchema.from_orm(resume)

    @staticmethod
    async def get_resume_by_id_service(
        resume_id: int, current_user: SeekerUser
    ) -> ResumeResponseSchema:
        resume = await ResumeRepository.get_resume_by_id(resume_id)
        if not resume:
            logger.warning(f"[RESUME] 이력서 id {resume_id}를 찾을 수 없습니다.")
            raise ResumeNotFoundException()
        await resume.fetch_related("user", "work_experiences")
        if resume.user.id != current_user.id:
            logger.warning(
                f"[RESUME] 이력서 id {resume_id}에 대해 사용자 id {current_user.id}의 접근 권한이 없습니다."
            )
            raise PermissionDeniedException()
        return ResumeResponseSchema.from_orm(resume)

    @staticmethod
    async def get_all_resume_service(
        current_user: Any, offset: int = 0, limit: int = 10
    ) -> dict:
        page = (offset // limit) + 1
        resumes = await ResumeRepository.get_resumes_by_user_id(
            current_user.id, page=page, limit=limit
        )
        total_count = await ResumeRepository.get_total_resume_count_by_user_id(
            current_user.id
        )
        serialized = []
        for resume in resumes:
            await resume.fetch_related("user", "work_experiences")
            serialized.append(ResumeResponseSchema.from_orm(resume))
        return {
            "total": total_count,
            "offset": offset,
            "limit": limit,
            "data": serialized,
        }

    @staticmethod
    async def update_resume_service(
        resume_id: int, data: dict, current_user: Any
    ) -> ResumeResponseSchema:
        resume = await ResumeRepository.get_resume_by_id(resume_id)
        if not resume:
            logger.warning(f"[RESUME] 이력서 id {resume_id}를 찾을 수 없습니다.")
            raise ResumeNotFoundException()
        await resume.fetch_related("user", "work_experiences")
        if resume.user.id != current_user.id:
            logger.warning(
                f"[RESUME] 이력서 id {resume_id}의 수정 권한이 사용자 id {current_user.id}에게 없습니다."
            )
            raise PermissionDeniedException()
        # 업데이트 가능한 필드만 처리 (user 및 work_experiences 제외)
        updatable_fields = {
            k: v for k, v in data.items() if k not in ["user", "work_experiences"]
        }
        updated_resume = await ResumeRepository.update_resume(
            resume_id, updatable_fields
        )
        if updated_resume:
            await updated_resume.fetch_related("user", "work_experiences")
            return ResumeResponseSchema.from_orm(updated_resume)
        else:
            logger.warning(f"[RESUME] 이력서 id {resume_id}의 업데이트에 실패했습니다.")
            raise ResumeNotFoundException()

    @staticmethod
    async def delete_resume_service(resume_id: int, current_user: Any) -> None:
        resume = await ResumeRepository.get_resume_by_id(resume_id)
        if not resume:
            logger.warning(f"[RESUME] 이력서 id {resume_id}를 찾을 수 없습니다.")
            raise ResumeNotFoundException()
        check_author(resume, current_user)
        deleted_work_exps = (
            await WorkExpRepository.delete_work_experiences_by_resume_id(resume_id)
        )
        if deleted_work_exps is False:
            logger.warning(f"[RESUME] 이력서 id {resume_id}의 경력 사항 삭제가 진행되지 않았습니다.")
        deleted = await ResumeRepository.delete_resume(resume_id)
        if not deleted:
            logger.warning(f"[RESUME] 이력서 id {resume_id} 삭제에 실패했습니다.")
            raise ResumeDeleteFailedException()
