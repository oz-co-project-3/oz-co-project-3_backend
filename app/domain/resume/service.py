from typing import Any

from app.domain.resume.models import Resume, WorkExp
from app.domain.resume.schema import ResumeResponseSchema, WorkExpResponseSchema
from app.domain.services.verification import (
    CustomException,
    check_existing,
    check_superuser,
)


def check_permission(resume, current_user):
    if not resume.user or resume.user.id != current_user.id:
        check_superuser(current_user)


def serialize_resume(resume):
    work_experience_schemas = [
        WorkExpResponseSchema.model_validate(work_exp)
        for work_exp in (resume.work_experiences or [])
    ]
    resume_data = ResumeResponseSchema.model_validate(resume)
    resume_data.work_experiences = work_experience_schemas
    return resume_data


class ResumeService:
    @staticmethod
    async def create_resume_service(data: dict):
        # 이력서 생성
        work_experiences = data.pop("work_experiences", [])
        resume = await Resume.create(**data)

        # 경력 사항 생성
        for work_exp in work_experiences:
            work_exp["resume_id"] = resume.id
            await WorkExp.create(**work_exp)

        return serialize_resume(resume)

    @staticmethod
    async def get_resume_by_id_service(resume_id: int, current_user: Any):
        # 이력서 조회
        resume = (
            await Resume.filter(id=resume_id)
            .select_related("user")
            .prefetch_related("work_experiences")
            .first()
        )
        check_existing(resume, error_message="이력서를 찾을 수 없습니다.", code="resume_not_found")

        # 권한 확인
        check_permission(resume, current_user)

        return serialize_resume(resume)

    @staticmethod
    async def get_all_resume_service(
        current_user: Any, offset: int = 0, limit: int = 10
    ):
        # 이력서 조회
        resumes = (
            Resume.filter(user_id=current_user.id)
            .select_related("user")
            .order_by("-created_at")
        )

        total_count = await resumes.count()
        paginated_resumes = await resumes.offset(offset).limit(limit).all()

        return {
            "total": total_count,
            "offset": offset,
            "limit": limit,
            "data": [serialize_resume(resume) for resume in paginated_resumes],
        }

    @staticmethod
    async def delete_resume_service(resume_id: int, current_user: Any):
        # 이력서 조회
        resume = await Resume.filter(id=resume_id).select_related("user").first()
        check_existing(resume, error_message="이력서를 찾을 수 없습니다.", code="resume_not_found")

        # 권한 확인
        check_permission(resume, current_user)

        # 관련된 경력 사항 삭제 및 이력서 삭제
        await WorkExp.filter(resume_id=resume_id).delete()
        if not await Resume.filter(id=resume_id).delete():
            raise CustomException(
                error="이력서 삭제에 실패했습니다.",
                code="resume_delete_failed",
                status_code=500,
            )

        return {"message": "이력서가 성공적으로 삭제되었습니다."}
