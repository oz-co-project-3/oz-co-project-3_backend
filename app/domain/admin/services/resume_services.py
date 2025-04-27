from typing import Any, List

from app.domain.admin.repositories.resume_repository import (
    delete_resume_by_id,
    get_all_resumes_query,
    get_resume_by_id,
    get_resumes_by_name,
)
from app.domain.admin.schemas.resume_schemas import ResumeResponseDTO
from app.domain.services.verification import check_existing, check_superuser
from app.exceptions.user_exceptions import ResumeNotFoundException


async def get_all_resumes_service(
    current_user: Any, name: str
) -> List[ResumeResponseDTO]:
    check_superuser(current_user)

    if name:
        return await get_resumes_by_name(name)
    return await get_all_resumes_query()


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
