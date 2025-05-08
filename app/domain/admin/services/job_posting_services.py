import logging
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
from app.exceptions.search_exceptions import (
    InvalidQueryParamsException,
    SearchKeywordTooLongException,
)

logger = logging.getLogger(__name__)


async def get_all_job_postings_service(
    current_user: BaseUser,
    search_type: str,
    search_keyword: str,
    status: StatusEnum,
) -> List[JobPostingResponseDTO]:
    check_superuser(current_user)

    if search_keyword and len(search_keyword) > 50:
        logger.warning(f"[LIST] 검색 키워드 길이 초과, 길이제한 : 50")
        raise SearchKeywordTooLongException(50)

    if search_type and search_keyword:
        allowed_search_fields = {
            "company",
            "title",
            "location",
            "employment_type",
            "employ_method",
            "work_time",
            "position",
            "history",
            "education",
            "deadline",
            "salary",
            "summary",
            "description",
            "status",
            "career",
        }

        if search_type not in allowed_search_fields:
            logger.warning(f"[LIST] 허용되지 않는 검색 타입: '{search_type}'")
            raise InvalidQueryParamsException("허용되지 않는 검색 타입입니다.")

    allowed_status = {"모집중", "마감 임박", "모집 종료", "블라인드", "대기중", "반려됨"}
    if status and status not in allowed_status:
        logger.warning(f"[LIST] 허용되지 않는 상태: '{status}'")
        raise InvalidQueryParamsException("허용되지 않는 공고 상태입니다.")

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
