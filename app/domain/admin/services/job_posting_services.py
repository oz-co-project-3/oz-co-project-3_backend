from typing import List

from fastapi import status

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
from app.domain.job_posting.job_posting_models import JobPosting, RejectPosting
from app.domain.services.verification import (
    CustomException,
    check_existing,
    check_superuser,
)
from app.domain.user.user_models import BaseUser


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
    check_existing(posting, "해당 이력서를 찾지 못했습니다.", "job_posting_not_found")

    return posting


async def patch_job_posting_by_id_service(
    id: int,
    patch_job_posting: JobPostingUpdateSchema,
    current_user: BaseUser,
) -> JobPostingResponseDTO:
    check_superuser(current_user)
    posting = await get_job_posting_by_id_query(id)
    check_existing(posting, "해당 이력서를 찾지 못했습니다.", "job_posting_not_found")
    return await patch_job_posting_by_id(posting, patch_job_posting)


async def delete_job_posting_by_id_service(
    id: int,
    current_user: BaseUser,
):
    check_superuser(current_user)
    posting = await get_job_posting_by_id_query(id)
    check_existing(posting, "해당 이력서를 찾지 못했습니다.", "job_posting_not_found")
    await delete_job_posting_by_id(posting)


async def create_reject_posting_by_id_service(
    id: int, current_user: BaseUser, reject_posting: RejectPostingCreateSchema
) -> RejectPostingResponseDTO:
    check_superuser(current_user)
    posting = await get_job_posting_by_id_query(id)
    check_existing(posting, "해당 이력서를 찾지 못했습니다.", "job_posting_not_found")
    return await create_reject_posting_by_id(reject_posting, posting, current_user)
