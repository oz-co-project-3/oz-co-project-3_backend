import logging

from fastapi import APIRouter, Depends, Path, Query, status

from app.core.token import get_current_user
from app.domain.posting.schemas import (
    ApplicantCreateUpdateSchema,
    ApplicantResponseDTO,
    JobPostingResponseDTO,
    PaginatedJobPostingsResponseDTO,
)
from app.domain.posting.services import (
    create_applicant_service,
    get_all_postings_service,
    get_posting_by_id_service,
    patch_posting_applicant_by_id_service,
)
from app.domain.user.models import BaseUser

posting_router = APIRouter(
    prefix="/api/postings",
    tags=["postings"],
)

logger = logging.getLogger(__name__)


@posting_router.get(
    "/",
    response_model=PaginatedJobPostingsResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="공고 전체 조회",
    description="""
`400` `code`:``search_too_long` 너무 긴 검색어 입력.\n
`400` `code`:``invalid_employment_type` employment_type은 ['공공', '일반'] 이어야 합니다.\n
`400` `code`:``invalid_career_type` career는 ['신입', '경력직', '경력무관'] 이어야 합니다.\n
`400` `code`:``invalid_employ_method` employ_method는 ['정규직', '계약직', '일용직', '프리랜서', '파견직'] 이어야 합니다.\n
`400` `code`:``too_many_positions` 포지션은 최대 100개까지 지정할 수 있습니다.\n
`400` `code`:``invalid_view_count` view_count는 0 이상이어야 합니다.\n
`400` `code`:``invalid_offset` offset은 0 이상이어야 합니다.\n
`400` `code`:``invalid_limit` limit는 1 이상 100 이하로 입력해주세요.\n
`401` `code`:`invalid_token` 유효하지 않은 토큰입니다.\n
    """,
)
async def get_list_postings(
    search_keyword: str = Query("", description="검색 키워드 (제목, 회사, 요약, 위치 등)"),
    location: str = Query("", description="지역 필터"),
    employment_type: str = Query("", description="고용 형태: 공공, 일반(,로 구분하여 다중 가능)"),
    position: str = Query("", description="포지션 키워드 (,로 구분하여 다중 가능)"),
    career: str = Query("", description="신입, 경력직, 경력무관(,로 구분하여 다중 가능)"),
    education: str = Query("", description="학력 조건 필터"),
    view_count: int = Query(0, description="최소 조회수"),
    offset: int = Query(0, description="페이지 번호 (0부터 시작)"),
    limit: int = Query(10, description="페이지당 항목 수"),
    employ_method: str = Query(
        "", description="근로 형태: 정규직, 계약직, 일용직, 프리랜서, 파견직, (,로 구분하여 다중 가능)"
    ),
):
    logger.info(
        f"[API] 공고 전체 조회 요청 (search={search_keyword}, location={location}, position={position})"
    )
    return await get_all_postings_service(
        search_keyword=search_keyword,
        location=location,
        employment_type=employment_type,
        position=position,
        career=career,
        education=education,
        view_count=view_count,
        employ_method=employ_method,
        offset=offset,
        limit=limit,
    )


@posting_router.get(
    "/{id}/",
    response_model=JobPostingResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="공고 상세 조회",
    description="""
`401` `code`:`invalid_token` 유효하지 않은 토큰입니다.\n
`404` `code`:`posting_not_found` 공고를 찾지 못했습니다..\n
`422` : Unprocessable Entity
    """,
)
async def get_posting(
    id: int = Path(
        ..., gt=0, le=2147483647, description="job_posting ID (1 ~ 2147483647)"
    ),
):
    logger.info(f"[API] 공고 상세 조회 요청: job_posting_id={id}")
    return await get_posting_by_id_service(id)


@posting_router.post(
    "/{id}/applicant/",
    response_model=ApplicantResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="공고 지원자 생성",
    description="""
`401` `code`:`invalid_token` 유효하지 않은 토큰입니다.\n
`404` `code`:`posting_not_found` 공고를 찾지 못했습니다.\n
`422` : Unprocessable Entity
    """,
)
async def create_applicant(
    applicant: ApplicantCreateUpdateSchema,
    current_user: BaseUser = Depends(get_current_user),
    id: int = Path(
        ..., gt=0, le=2147483647, description="job_posting ID (1 ~ 2147483647)"
    ),
):
    logger.info(f"[API] 공고 지원자 생성 요청: user_id={current_user.id}, job_posting_id={id}")
    return await create_applicant_service(id, current_user, applicant)


@posting_router.patch(
    "/{id}/applicant/{applicant_id}/",
    response_model=ApplicantResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="공고 지원자 수정",
    description="""
`401` `code`:`invalid_token` 유효하지 않은 토큰입니다.\n
`403` `code`:`permission_denied` 유효하지 않은 토큰입니다.\n
`404` `code`:`posting_not_found` 공고를 찾지 못했습니다.\n
`404` `code`:`applicant_not_found` 공고를 찾지 못했습니다.\n
`404` `code`:`resume_not_found` 이력서를 찾지 못했습니다.\n
`422` : Unprocessable Entity
""",
)
async def patch_posting_applicant(
    patch_applicant: ApplicantCreateUpdateSchema,
    current_user: BaseUser = Depends(get_current_user),
    id: int = Path(
        ..., gt=0, le=2147483647, description="job_posting ID (1 ~ 2147483647)"
    ),
    applicant_id: int = Path(
        ..., gt=0, le=2147483647, description="job_posting ID (1 ~ 2147483647)"
    ),
):
    logger.info(
        f"[API] 공고 지원자 수정 요청: user_id={current_user.id}, job_posting_id={id}, applicant_id={applicant_id}"
    )
    return await patch_posting_applicant_by_id_service(
        id, current_user, patch_applicant, applicant_id
    )
