from typing import List

from app.domain.admin.repositories.job_posting_repository import (
    create_reject_posting_by_id,
    delete_job_posting_by_id,
    get_all_job_postings_query,
    get_job_posting_by_id_query,
    patch_job_posting_by_id,
)
from app.domain.admin.schemas.job_posting_schemas import (
    JobPostingResponseDTO,
    JobPostingUpdateSchema,
    RejectPostingCreateSchema,
    RejectPostingResponseDTO,
    StatusEnum,
)
from app.domain.services.verification import check_existing, check_superuser
from app.domain.user.models import BaseUser
from app.exceptions.job_posting_exceptions import JobPostingNotFoundException


async def get_all_job_postings_service(
    current_user: BaseUser,
    search_type: str,
    search_keyword: str,
    status: StatusEnum,
) -> List[JobPostingResponseDTO]:
    check_superuser(current_user)

    job_postings = await get_all_job_postings_query(
        search_type=search_type,
        search_keyword=search_keyword,
        status=status,
    )

    return [JobPostingResponseDTO.from_orm(p) for p in job_postings]


async def get_job_posting_by_id_service(
    id: int,
    current_user: BaseUser,
) -> JobPostingResponseDTO:
    check_superuser(current_user)
    posting = await get_job_posting_by_id_query(id)
    check_existing(posting, JobPostingNotFoundException)

    return posting


async def patch_job_posting_by_id_service(
    id: int,
    patch_job_posting: JobPostingUpdateSchema,
    current_user: BaseUser,
) -> JobPostingResponseDTO:
    check_superuser(current_user)
    posting = await get_job_posting_by_id_query(id)
    check_existing(posting, JobPostingNotFoundException)
    return await patch_job_posting_by_id(posting, patch_job_posting)


async def delete_job_posting_by_id_service(
    id: int,
    current_user: BaseUser,
):
    check_superuser(current_user)
    posting = await get_job_posting_by_id_query(id)
    check_existing(posting, JobPostingNotFoundException)
    await delete_job_posting_by_id(posting)


async def create_reject_posting_by_id_service(
    id: int, current_user: BaseUser, reject_posting: RejectPostingCreateSchema
) -> RejectPostingResponseDTO:
    check_superuser(current_user)
    posting = await get_job_posting_by_id_query(id)
    check_existing(posting, JobPostingNotFoundException)
    return await create_reject_posting_by_id(reject_posting, posting, current_user)
