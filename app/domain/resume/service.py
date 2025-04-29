from typing import Any

from app.domain.resume.models import Resume, WorkExp
from app.domain.resume.schema import ResumeResponseSchema, WorkExpResponseSchema
from app.domain.services.verification import check_existing, check_superuser
from app.domain.user.user_models import SeekerUser
from app.exceptions.auth_exceptions import PermissionDeniedException
from app.exceptions.resume_exceptions import (
    ResumeDeleteFailedException,
    ResumeNotFoundException,
)


def check_permission(resume, current_user):
    if not resume.user or resume.user.id != current_user.id:
        check_superuser(current_user)


def serialize_resume(resume):
    work_experience_schemas = [
        WorkExpResponseSchema.model_validate(work_exp)  # WorkExpResponseSchema로 변환
        for work_exp in (resume.work_experiences or [])
    ]

    resume_data = ResumeResponseSchema.model_validate(resume)  # ResumeResponseSchema 변환
    return ResumeResponseSchema(
        id=resume_data.id,
        user=resume_data.user,
        title=resume_data.title,
        visibility=resume_data.visibility,
        name=resume_data.name,
        phone_number=resume_data.phone_number,
        email=resume_data.email,
        image_url=resume_data.image_url,
        interests=resume_data.interests,
        desired_area=resume_data.desired_area,
        education=resume_data.education,
        school_name=resume_data.school_name,
        graduation_status=resume_data.graduation_status,
        introduce=resume_data.introduce,
        status=resume_data.status,
        document_url=resume_data.document_url,
        work_experiences=work_experience_schemas,
        created_at=resume_data.created_at,
        updated_at=resume_data.updated_at,
    )


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

        await resume.fetch_related("work_experiences")

        return serialize_resume(resume)

    @staticmethod
    async def get_resume_by_id_service(resume_id: int, current_user: SeekerUser):
        resume = (
            await Resume.filter(id=resume_id)
            .select_related("user")
            .prefetch_related("work_experiences")
            .first()
        )
        if resume.user.id != current_user.id:
            raise PermissionDeniedException()
        return serialize_resume(resume)

    @staticmethod
    async def get_all_resume_service(
        current_user: Any, offset: int = 0, limit: int = 10
    ):
        resumes = (
            Resume.filter(user_id=current_user.id)
            .select_related("user")
            .prefetch_related("work_experiences")
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
    async def update_resume_service(resume_id: int, data: dict, current_user: Any):
        # 이력서 조회
        resume = await Resume.filter(id=resume_id).select_related("user").first()
        if not resume:
            raise ResumeNotFoundException()

        # 권한 확인
        if resume.user.id != current_user.id:
            raise PermissionDeniedException()

        # 관계 필드 처리
        for key, value in data.items():
            if key in ["user", "work_experiences"]:
                continue
            setattr(resume, key, value)

        await resume.save()

        # 관계 데이터를 미리 로드
        await resume.fetch_related("work_experiences")
        return serialize_resume(resume)

    @staticmethod
    async def delete_resume_service(resume_id: int, current_user: Any):
        # 이력서 조회
        resume = await Resume.filter(id=resume_id).select_related("user").first()
        check_existing(resume, ResumeNotFoundException)

        # 권한 확인
        check_permission(resume, current_user)

        # 관련된 경력 사항 삭제 및 이력서 삭제
        await WorkExp.filter(resume_id=resume_id).delete()
        if not await Resume.filter(id=resume_id).delete():
            raise ResumeDeleteFailedException()

        return {"message": "이력서가 성공적으로 삭제되었습니다."}
