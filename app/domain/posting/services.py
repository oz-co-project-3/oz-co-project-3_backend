from typing import Any, Optional

from app.domain.posting.repository import (
    create_posting_applicant,
    get_applicant_query,
    get_posting_query,
    get_postings_query,
    get_resume_id_by_applicant_id,
    get_resume_query,
    patch_posting_applicant_by_id,
)
from app.domain.posting.validator import check_author
from app.utils.exception import check_existing
from app.utils.pagination import paginate_query


async def get_all_postings_service(
    search_keyword: Optional[str] = "",
    location: Optional[str] = "",
    employment_type: Optional[str] = "",
    position: Optional[str] = "",
    career: Optional[str] = "",
    education: Optional[str] = "",
    view_count: Optional[int] = 0,
    offset: int = 0,
    limit: int = 10,
):
    query = await get_postings_query(
        search_keyword,
        location,
        employment_type,
        position,
        career,
        education,
        view_count,
    )
    total, results = await paginate_query(query, offset, limit)
    return {
        "total": total,
        "offset": offset,
        "limit": limit,
        "data": results,
    }


async def get_posting_by_id_service(id: int):
    posting = await get_posting_query(id)
    check_existing(posting, "공고를 찾을 수 없습니다.", "posting_not_found")
    return posting


async def create_applicant_service(id: int, current_user: Any, applicant: Any):
    posting = await get_posting_query(id)
    check_existing(posting, "공고를 찾을 수 없습니다.", "posting_not_found")
    resume = await get_resume_query(applicant)
    check_existing(resume, "이력서를 찾을 수 없습니다.", "resume_not_found")

    created_applicant = await create_posting_applicant(
        applicant, current_user, resume, posting
    )

    return {
        "id": created_applicant["id"],
        "job_posting": created_applicant["job_posting_id"],
        "resume": created_applicant["resume_id"],
        "user": created_applicant["user_id"],
        "status": created_applicant["status"],
        "memo": created_applicant["memo"],
    }


async def patch_posting_applicant_by_id_service(
    id: int,
    current_user: Any,
    patch_applicant: Any,
    applicant_id: int,
):
    posting = await get_posting_query(id)
    check_existing(posting, "공고를 찾을 수 없습니다.", "posting_not_found")

    applicant = await get_applicant_query(applicant_id)
    check_existing(applicant, "지원 내역이 없습니다.", "applicant_not_found")

    resume_id = await get_resume_id_by_applicant_id(applicant_id)
    check_existing(resume_id, "이력서를 찾을 수 없습니다.", "resume_not_found")

    resume = await get_resume_query(resume_id)
    check_existing(resume, "이력서를 찾을 수 없습니다.", "resume_not_found")

    await check_author(applicant, current_user)

    patch_applicant = await patch_posting_applicant_by_id(
        applicant, resume, patch_applicant
    )

    return {
        "id": patch_applicant["id"],
        "job_posting": patch_applicant["job_posting_id"],
        "resume": patch_applicant["resume_id"],
        "user": patch_applicant["user_id"],
        "status": patch_applicant["status"],
        "memo": patch_applicant["memo"],
    }
