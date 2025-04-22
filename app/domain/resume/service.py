from typing import Any

from app.domain.resume.repository import ResumeRepository, WorkExpRepository
from app.domain.resume.schema import ResumeResponseSchema, WorkExpResponseSchema
from app.utils.exception import CustomException, check_existing, check_superuser


class ResumeService:
    @staticmethod
    async def create_resume_service(data: dict):
        # 이력서 생성
        resume = await ResumeRepository.create_resume(data)
        return ResumeResponseSchema.from_orm(resume)

    @staticmethod
    async def get_resume_by_id_service(resume_id: int, current_user: Any):
        # 이력서 조회
        resume = await ResumeRepository.get_resume_by_id(resume_id)
        check_existing(
            resume, error_message="Resume not found.", code="resume_not_found"
        )

        # 작성자 또는 관리자 권한 확인
        if resume.user != current_user.id:
            check_superuser(current_user)

        return ResumeResponseSchema.from_orm(resume)

    @staticmethod
    async def update_resume_service(resume_id: int, data: dict, current_user: Any):
        # 이력서 수정
        resume = await ResumeRepository.get_resume_by_id(resume_id)
        check_existing(
            resume, error_message="Resume not found.", code="resume_not_found"
        )

        # 작성자 또는 관리자 권한 확인
        if resume.user != current_user.id:
            check_superuser(current_user)

        updated_resume = await ResumeRepository.update_resume(resume_id, data)
        return ResumeResponseSchema.from_orm(updated_resume)

    @staticmethod
    async def delete_resume_service(resume_id: int, current_user: Any):
        # 이력서 삭제
        resume = await ResumeRepository.get_resume_by_id(resume_id)
        check_existing(
            resume, error_message="Resume not found.", code="resume_not_found"
        )

        # 작성자 또는 관리자 권한 확인
        if resume.user != current_user.id:
            check_superuser(current_user)

        if not await ResumeRepository.delete_resume(resume_id):
            raise CustomException(
                error="Resume deletion failed.",
                code="resume_delete_failed",
                status_code=500,
            )

        return {"message": "Resume deleted successfully."}

    @staticmethod
    async def get_all_resumes_service(offset: int = 0, limit: int = 10):
        # 이력서 전체 조회
        resumes = await ResumeRepository.get_all_resumes(offset, limit)
        return {
            "total": len(resumes),
            "offset": offset,
            "limit": limit,
            "data": [ResumeResponseSchema.from_orm(resume) for resume in resumes],
        }


class WorkExpService:
    @staticmethod
    async def create_work_experience_service(data: dict):
        # 경력 생성
        work_exp = await WorkExpRepository.create_work_experience(data)
        return WorkExpResponseSchema.from_orm(work_exp)

    @staticmethod
    async def get_work_experience_by_id_service(work_exp_id: int):
        # 경력 조회
        work_exp = await WorkExpRepository.get_work_experience_by_id(work_exp_id)
        check_existing(
            work_exp,
            error_message="Work experience not found.",
            code="work_exp_not_found",
        )
        return WorkExpResponseSchema.from_orm(work_exp)

    @staticmethod
    async def delete_work_experience_service(work_exp_id: int):
        # 경력 삭제
        work_exp = await WorkExpRepository.get_work_experience_by_id(work_exp_id)
        check_existing(
            work_exp,
            error_message="Work experience not found.",
            code="work_exp_not_found",
        )

        if not await WorkExpRepository.delete_work_experience(work_exp_id):
            raise CustomException(
                error="Work experience deletion failed.",
                code="work_exp_delete_failed",
                status_code=500,
            )
        return {"message": "Work experience deleted successfully."}

    @staticmethod
    async def get_work_experiences_by_resume_id_service(resume_id: int):
        # 이력서 ID로 경력 조회
        work_experiences = await WorkExpRepository.get_work_experiences_by_resume_id(
            resume_id
        )
        return [
            WorkExpResponseSchema.from_orm(work_exp) for work_exp in work_experiences
        ]
