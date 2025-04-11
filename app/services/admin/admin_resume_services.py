from fastapi import status

from app.models.resume_models import Resume
from app.models.user_models import BaseUser
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
            await Resume.filter(name__icontains=name).prefetch_related("user").all()
        )
    else:
        resumes = await Resume.all().prefetch_related("user")
    return resumes


async def get_resume_by_id(current_user: BaseUser, id: int):
    check_superuser(current_user)

    resume = await Resume.filter(id=id).select_related("user").first()
    check_resume(resume)

    return resume


async def delete_resume_by_id(current_user: BaseUser, id: int):
    check_superuser(current_user)
    resume = await Resume.filter(id=id).select_related("user").first()
    check_resume(resume)
    await resume.delete()
