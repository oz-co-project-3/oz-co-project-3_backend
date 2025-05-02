import logging
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
from app.domain.posting.schemas import (
    ApplicantCreateUpdateSchema,
    ApplicantResponseDTO,
    JobPostingResponseDTO,
    PaginatedJobPostingsResponseDTO,
)
from app.domain.services.permission import check_author
from app.domain.services.verification import check_existing
from app.exceptions.applicant_exceptions import ApplicantNotFoundException
from app.exceptions.job_posting_exceptions import (
    InvalidCareerTypeException,
    InvalidEmploymentTypeException,
    InvalidEmployMethodException,
    JobPostingNotFoundException,
    TooManyPositionsException,
)
from app.exceptions.resume_exceptions import ResumeNotFoundException
from app.exceptions.search_exceptions import (
    InvalidLimitException,
    InvalidOffsetException,
    InvalidViewCountException,
    SearchKeywordTooLongException,
)
from app.utils.pagination import paginate_query

VALID_EMPLOYMENT_TYPES = {"공공", "일반"}
VALID_CAREER_TYPES = {"신입", "경력직", "경력무관"}
VALID_EMPLOY_METHODS = {"정규직", "계약직", "일용직", "프리랜서", "파견직"}

MAX_POSITION_COUNT = 10
MAX_SEARCH_KEYWORD_LENGTH = 100
MAX_LOCATION_LENGTH = 50
MAX_EDUCATION_LENGTH = 50

logger = logging.getLogger(__name__)


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
    employ_method: Optional[str] = "",
) -> PaginatedJobPostingsResponseDTO:
    # 문자열 길이 검증
    if len(search_keyword) > MAX_SEARCH_KEYWORD_LENGTH:
        logger.warning(
            f"[LIST] 검색 키워드 길이 초과, 길이제한 : 100, len(search_keyword) = {len(search_keyword)}"
        )
        raise SearchKeywordTooLongException(100)
    if len(location) > MAX_LOCATION_LENGTH:
        logger.warning(
            f"[LIST] 검색 키워드 길이 초과, 길이제한 : 50, len(location) = {len(location)}"
        )
        raise SearchKeywordTooLongException(50)
    if len(education) > MAX_EDUCATION_LENGTH:
        logger.warning(
            f"[LIST] 검색 키워드 길이 초과, 길이제한 : 50, len(education) = {len(education)}"
        )
        raise SearchKeywordTooLongException(50)

    if employment_type:
        types = [t.strip() for t in employment_type.split(",")]
        invalid_types = [t for t in types if t not in VALID_EMPLOYMENT_TYPES]
        if invalid_types:
            logger.warning(f"[SEARCH-TYPE] 허용되지 않는 employment_type : {invalid_types}")
            raise InvalidEmploymentTypeException()

    if career:
        careers = [c.strip() for c in career.split(",")]
        invalid_careers = [c for c in careers if c not in VALID_CAREER_TYPES]
        if invalid_careers:
            logger.warning(f"[SEARCH-TYPE] 허용되지 않는 career : {invalid_careers}")
            raise InvalidCareerTypeException()

    if employ_method:
        methods = [m.strip() for m in employ_method.split(",")]
        invalid_methods = [m for m in methods if m not in VALID_EMPLOY_METHODS]
        if invalid_methods:
            logger.warning(f"[SEARCH-TYPE] 허용되지 않는 employ_method : {invalid_methods}")
            raise InvalidEmployMethodException()

    # view_count, offset, limit 범위 검증
    if view_count is not None and view_count < 0:
        logger.warning(f"[SEARCH-TYPE] view_count는 0이상 이어야 합니다 : {employment_type}")
        raise InvalidViewCountException()
    if offset < 0:
        logger.warning(f"[SEARCH-TYPE] offset는 0이상 이어야 합니다 : {offset}")
        raise InvalidOffsetException()
    if not (1 <= limit <= 100):
        logger.warning(f"[SEARCH-TYPE] limit 1이상 100 이하 이어야 합니다 : {limit}")
        raise InvalidLimitException()

    # position 다중 값 파싱 및 개수 제한
    position_list = [p.strip() for p in position.split(",") if p.strip()]
    if len(position_list) > MAX_POSITION_COUNT:
        logger.warning(f"[SEARCH-TYPE] position 10개 이하 여야 합니다 : {len(position_list)}")
        raise TooManyPositionsException(MAX_POSITION_COUNT)

    query = await get_postings_query(
        search_keyword,
        location,
        employment_type,
        position,
        career,
        education,
        view_count,
        employ_method,
    )
    return await paginate_query(query, offset, limit, JobPostingResponseDTO)


async def get_posting_by_id_service(id: int) -> JobPostingResponseDTO:
    posting = await get_posting_query(id)
    check_existing(posting, JobPostingNotFoundException)
    return posting


async def create_applicant_service(
    id: int, current_user: Any, applicant: ApplicantCreateUpdateSchema
) -> ApplicantResponseDTO:
    posting = await get_posting_query(id)
    check_existing(posting, JobPostingNotFoundException)
    resume = await get_resume_query(applicant.resume)
    check_existing(resume, ResumeNotFoundException)

    created_applicant = await create_posting_applicant(
        applicant, current_user, resume, posting
    )

    return created_applicant


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

    return patch_applicant
