from typing import Any, Optional

from app.domain.posting.repository import (
    create_posting_applicant,
    get_applicant_query,
    get_posting_query,
    get_postings_query,
    get_resume_id_by_applicant_id,
    get_resume_query,
    paginate_query,
    patch_posting_applicant_by_id,
)
from app.domain.posting.schemas import (
    ApplicantResponseDTO,
    JobPostingResponseDTO,
    PaginatedJobPostingsResponseDTO,
)
from app.domain.services.permission import check_author
from app.domain.services.verification import check_existing
from app.exceptions.applicant_exceptions import ApplicantNotFoundException
from app.exceptions.job_posting_exceptions import JobPostingNotFoundException
from app.exceptions.resume_exceptions import ResumeNotFoundException


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
) -> PaginatedJobPostingsResponseDTO:
    query = await get_postings_query(
        search_keyword,
        location,
        employment_type,
        position,
        career,
        education,
        view_count,
    )
    return await paginate_query(query, offset, limit)


async def get_posting_by_id_service(id: int) -> JobPostingResponseDTO:
    posting = await get_posting_query(id)
    check_existing(posting, JobPostingNotFoundException)
    return posting


async def create_applicant_service(
    id: int, current_user: Any, applicant: Any
) -> ApplicantResponseDTO:
    posting = await get_posting_query(id)
    check_existing(posting, JobPostingNotFoundException)
    resume = await get_resume_query(applicant.resume)
    check_existing(resume, ResumeNotFoundException)

    created_applicant = await create_posting_applicant(
        applicant, current_user, resume, posting
    )

    return ApplicantResponseDTO(
        id=created_applicant["id"],
        job_posting=created_applicant["job_posting_id"],
        resume=created_applicant["resume_id"],
        user=created_applicant["user_id"],
        status=created_applicant["status"],
        memo=created_applicant["memo"],
    )


async def patch_posting_applicant_by_id_service(
    id: int,
    current_user: Any,
    patch_applicant: Any,
    applicant_id: int,
) -> ApplicantResponseDTO:
    posting = await get_posting_query(id)
    check_existing(posting, JobPostingNotFoundException)

    applicant = await get_applicant_query(applicant_id)
    check_existing(applicant, ApplicantNotFoundException)

    resume_id = await get_resume_id_by_applicant_id(applicant_id)
    resume = await get_resume_query(resume_id)
    check_existing(resume, ResumeNotFoundException)

    await check_author(applicant, current_user)

    patch_applicant = await patch_posting_applicant_by_id(
        applicant, resume, patch_applicant
    )

    return ApplicantResponseDTO(
        id=patch_applicant["id"],
        job_posting=patch_applicant["job_posting_id"],
        resume=patch_applicant["resume_id"],
        user=patch_applicant["user_id"],
        status=patch_applicant["status"],
        memo=patch_applicant["memo"],
    )
