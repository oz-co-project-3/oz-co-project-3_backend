from typing import Any

from app.domain.resume.models import Resume
from app.domain.user.models import BaseUser


async def get_resumes_by_name(name: str):
    return (
        await Resume.filter(name__icontains=name)
        .select_related("user")
        .prefetch_related("work_experiences")
        .all()
    )


async def get_all_resumes_query(user: Any):
    return (
        await Resume.filter(user=user)
        .select_related("user")
        .prefetch_related("work_experiences")
    )


async def get_resume_by_id(id: int):
    return (
        await Resume.filter(id=id)
        .select_related("user")
        .prefetch_related("work_experiences")
        .first()
    )


async def delete_resume_by_id(id: int):
    await Resume.filter(id=id).delete()


async def get_user_by_id(id: int):
    return await BaseUser.filter(id=id).first()
