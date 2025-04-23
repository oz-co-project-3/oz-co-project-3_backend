from typing import Any

from app.domain.resume.repository import ResumeRepository, WorkExpRepository
from app.domain.resume.schema import ResumeResponseSchema, WorkExpResponseSchema
from app.utils.exception import check_existing, check_superuser


class ResumeService:
    @staticmethod
    async def create_resume_service(data: dict):
        # 이력서 생성
        work_experiences = data.pop("work_experiences", [])
        resume = await ResumeRepository.create_resume(data)

        # 경력 사항 생성
        for work_exp in work_experiences:
            work_exp["resume_id"] = resume.id
            await WorkExpRepository.create_work_experience(work_exp)

        return ResumeResponseSchema.model_validate(resume)

    @staticmethod
    async def get_resume_by_id_service(resume_id: int, current_user: Any):
        # 이력서 조회
        resume = await ResumeRepository.get_resume_by_id(resume_id)
        check_existing(resume, error_message="이력서를 찾을 수 없습니다.", code="resume_not_found")
        if resume.user != current_user.id:
            check_superuser(current_user)

        # 경력 사항 조회 및 매핑
        work_experiences = await WorkExpRepository.get_work_experiences_by_resume_id(
            resume_id
        )
        work_experience_schemas = [
            WorkExpResponseSchema.model_validate(work_exp)
            for work_exp in work_experiences
        ]

        resume_data = ResumeResponseSchema.model_validate(resume)
        resume_data.work_experiences = work_experience_schemas
        return resume_data

    @staticmethod
    async def update_resume_service(resume_id: int, data: dict, current_user: Any):
        # 이력서 수정
        resume = await ResumeRepository.get_resume_by_id(resume_id)
        check_existing(resume, error_message="이력서를 찾을 수 없습니다.", code="resume_not_found")
        if resume.user != current_user.id:
            check_superuser(current_user)

        work_experiences = data.pop("work_experiences", [])
        updated_resume = await ResumeRepository.update_resume(resume_id, data)

        # 경력 사항 수정
        await WorkExpRepository.delete_work_experiences_by_resume_id(resume_id)
        for work_exp in work_experiences:
            work_exp["resume_id"] = resume_id
            await WorkExpRepository.create_work_experience(work_exp)

        return ResumeResponseSchema.model_validate(updated_resume)
