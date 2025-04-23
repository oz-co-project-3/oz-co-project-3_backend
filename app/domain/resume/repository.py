from typing import List, Optional

from app.domain.resume.models import Resume, WorkExp


class ResumeRepository:
    @staticmethod
    async def create_resume(data: dict) -> Resume:
        return await Resume.create(**data)

    @staticmethod
    async def get_resume_by_id(resume_id: int) -> Optional[Resume]:
        return await Resume.filter(id=resume_id).first()

    @staticmethod
    async def update_resume(resume_id: int, data: dict) -> Optional[Resume]:
        resume = await Resume.filter(id=resume_id).first()
        if resume:
            await Resume.filter(id=resume_id).update(**data)
        return await Resume.filter(id=resume_id).first()

    @staticmethod
    async def delete_resume(resume_id: int) -> bool:
        resume = await Resume.filter(id=resume_id).first()
        if resume:
            await resume.delete()
            return True
        return False

    @staticmethod
    async def get_resumes_by_user_id(
        user_id: int, offset: int = 0, limit: int = 10
    ) -> List[Resume]:
        return await Resume.filter(user_id=user_id).offset(offset).limit(limit)

    @staticmethod
    async def get_total_resume_count_by_user_id(user_id: int) -> int:
        return await Resume.filter(user_id=user_id).count()

    @staticmethod
    async def get_total_resume_count() -> int:
        return await Resume.all().count()


class WorkExpRepository:
    @staticmethod
    async def create_work_experience(data: dict) -> WorkExp:
        return await WorkExp.create(**data)

    @staticmethod
    async def get_work_experience_by_id(work_exp_id: int) -> Optional[WorkExp]:
        return await WorkExp.filter(id=work_exp_id).first()

    @staticmethod
    async def delete_work_experience(work_exp_id: int) -> bool:
        work_exp = await WorkExp.filter(id=work_exp_id).first()
        if work_exp:
            await work_exp.delete()
            return True
        return False

    @staticmethod
    async def get_work_experiences_by_resume_id(resume_id: int) -> List[WorkExp]:
        return await WorkExp.filter(resume_id=resume_id).all()
