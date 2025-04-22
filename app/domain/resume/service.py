from app.domain.resume.repository import ResumeRepository, WorkExpRepository
from app.domain.resume.schema import ResumeResponseSchema, WorkExpResponseSchema
from app.utils.exception import CustomException


class ResumeService:
    @staticmethod
    async def create_resume_service(data: dict):
        resume = await ResumeRepository.create_resume(data)
        return ResumeResponseSchema.from_orm(resume)

    @staticmethod
    async def get_resume_by_id_service(resume_id: int):
        resume = await ResumeRepository.get_resume_by_id(resume_id)
        if not resume:
            raise CustomException(
                error="Resume not found.", code="resume_not_found", status_code=404
            )
        return ResumeResponseSchema.from_orm(resume)

    @staticmethod
    async def update_resume_service(resume_id: int, data: dict):
        updated_resume = await ResumeRepository.update_resume(resume_id, data)
        if not updated_resume:
            raise CustomException(
                error="Resume not found or update failed.",
                code="resume_update_failed",
                status_code=404,
            )
        return ResumeResponseSchema.from_orm(updated_resume)

    @staticmethod
    async def delete_resume_service(resume_id: int):
        if not await ResumeRepository.delete_resume(resume_id):
            raise CustomException(
                error="Resume not found or delete failed.",
                code="resume_delete_failed",
                status_code=404,
            )
        return {"message": "Resume deleted successfully."}

    @staticmethod
    async def get_all_resumes_service(offset: int = 0, limit: int = 10):
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
        work_exp = await WorkExpRepository.create_work_experience(data)
        return WorkExpResponseSchema.from_orm(work_exp)

    @staticmethod
    async def delete_work_experience_service(work_exp_id: int):
        if not await WorkExpRepository.delete_work_experience(work_exp_id):
            raise CustomException(
                error="Work experience not found or delete failed.",
                code="work_exp_delete_failed",
                status_code=404,
            )
        return {"message": "Work experience deleted successfully."}

    @staticmethod
    async def get_work_experiences_by_resume_id_service(resume_id: int):
        work_experiences = await WorkExpRepository.get_work_experiences_by_resume_id(
            resume_id
        )
        return [
            WorkExpResponseSchema.from_orm(work_exp) for work_exp in work_experiences
        ]
