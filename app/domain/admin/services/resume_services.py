from typing import Any, List

from app.domain.admin.repositories.resume_repository import (
    delete_resume_by_id,
    get_all_resumes_query,
    get_resume_by_id,
    get_resumes_by_name,
    get_user_by_id,
)
from app.domain.admin.schemas.resume_schemas import ResumeResponseDTO
from app.domain.services.verification import check_existing, check_superuser
from app.exceptions.resume_exceptions import ResumeNotFoundException
from app.exceptions.user_exceptions import UserNotFoundException


async def get_all_resumes_service(
    current_user: Any, user_id: int
) -> List[ResumeResponseDTO]:
    check_superuser(current_user)
    user = await get_user_by_id(user_id)
    check_existing(user, UserNotFoundException)

    return await get_all_resumes_query(user_id)


async def get_resume_by_id_service(current_user: Any, id: int) -> ResumeResponseDTO:
    check_superuser(current_user)

    resume = await get_resume_by_id(id)
    check_existing(resume, ResumeNotFoundException)

    return resume


async def delete_resume_by_id_service(current_user: Any, id: int):
    check_superuser(current_user)
    resume = await get_resume_by_id(id)
    check_existing(resume, ResumeNotFoundException)
    await delete_resume_by_id(id)
