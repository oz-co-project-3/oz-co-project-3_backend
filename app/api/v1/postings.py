from fastapi import APIRouter, Depends, status

from app.core.token import get_current_user
from app.domain.posting.postings_schemas import (
    ApplicantCreateUpdateSchema,
    ApplicantResponseSchema,
    JobPostingResponseSchema,
    PaginatedJobPostingsResponseSchema,
)
from app.domain.posting.postings_services import (
    create_posting_applicant_by_id,
    get_all_postings,
    get_posting_by_id,
    patch_posting_applicant_by_id,
)
from app.domain.user.user_models import BaseUser

posting_router = APIRouter(
    prefix="/api/postings",
    tags=["postings"],
)


@posting_router.get(
    "/",
    response_model=PaginatedJobPostingsResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="공고 전체 조회",
    description="""
    - `401` `code`:`invalid_token` 유효하지 않은 토큰입니다.\n
    """,
)
async def get_list_postings(
    search_keyword=None,
    filter_type=None,
    filter_keyword=None,
    offset: int = 0,
    limit: int = 10,
):
    return await get_all_postings(
        search_keyword, filter_type, filter_keyword, offset, limit
    )


@posting_router.get(
    "/{id}/",
    response_model=JobPostingResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="공고 상세 조회",
    description="""
    - `401` `code`:`invalid_token` 유효하지 않은 토큰입니다.\n
    - `404` `code`:`posting_not_found` 공고를 찾지 못했습니다..\n
    """,
)
async def get_posting(id: int):
    return await get_posting_by_id(id)


@posting_router.post(
    "/{id}/applicant/",
    response_model=ApplicantResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="공고 지원자 생성",
    description="""
    - `401` `code`:`invalid_token` 유효하지 않은 토큰입니다.\n
    - `404` `code`:`posting_not_found` 공고를 찾지 못했습니다.\n
    """,
)
async def create_posting_applicant(
    id: int,
    applicant: ApplicantCreateUpdateSchema,
    current_user: BaseUser = Depends(get_current_user),
):
    return await create_posting_applicant_by_id(id, current_user, applicant)


@posting_router.patch(
    "/{id}/applicant/{applicant_id}/",
    response_model=ApplicantResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="공고 지원자 수정",
    description="""
    - `401` `code`:`invalid_token` 유효하지 않은 토큰입니다.\n
    - `403` `code`:`permission_denied` 유효하지 않은 토큰입니다.\n
    - `404` `code`:`posting_not_found` 공고를 찾지 못했습니다.\n
    - `404` `code`:`applicant_not_found` 공고를 찾지 못했습니다.\n
    - `404` `code`:`resume_not_found` 이력서를 찾지 못했습니다.\n
    """,
)
async def patch_posting_applicant(
    id: int,
    applicant_id: int,
    applicant: ApplicantCreateUpdateSchema,
    current_user: BaseUser = Depends(get_current_user),
):
    return await patch_posting_applicant_by_id(
        id, current_user, applicant, applicant_id
    )
