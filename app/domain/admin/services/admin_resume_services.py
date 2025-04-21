from fastapi import status

from app.domain.resume.resume_models import Resume
from app.domain.user.user_models import BaseUser
from app.utils.exception import CustomException, check_superuser


def check_resume(resume: Resume):
    if not resume:
        raise CustomException(
            status_code=status.HTTP_404_NOT_FOUND,
            code="resume_not_found",
            error="해당 이력서를 찾지 못했습니다.",
        )


async def get_all_resumes(current_user: BaseUser, name: str):
    check_superuser(current_user)

    if name:
        resumes = (
            await Resume.filter(name__icontains=name)
            .select_related("user")
            .prefetch_related("work_experiences")
            .all()
        )
    else:
        resumes = (
            await Resume.all()
            .select_related("user")
            .prefetch_related("work_experiences")
        )
    return resumes


async def get_resume_by_id(current_user: BaseUser, id: int):
    check_superuser(current_user)

    resume = (
        await Resume.filter(id=id)
        .select_related("user")
        .prefetch_related("work_experiences")
        .first()
    )
    check_resume(resume)

    return resume


async def delete_resume_by_id(current_user: BaseUser, id: int):
    check_superuser(current_user)
    resume = await Resume.filter(id=id).select_related("user").first()
    check_resume(resume)
    await resume.delete()
