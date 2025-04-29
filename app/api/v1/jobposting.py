from fastapi import APIRouter, Depends

from app.core.token import get_current_user  # 인증된 사용자 가져오기 서비스 함수
from app.domain.job_posting.schema import (
    JobPostingCreateUpdate,
    JobPostingResponse,
    JobPostingSummaryResponse,
)
from app.domain.job_posting.services import JobPostingService
from app.domain.user.user_models import BaseUser, CorporateUser
from app.exceptions.auth_exceptions import PermissionDeniedException

job_posting_router = APIRouter(
    prefix="/api/job_posting",
    tags=["job_posting"],  # 스웨거 표시 태그
)


async def get_corporate_user(
    current_user: BaseUser = Depends(get_current_user),
) -> CorporateUser:
    corporate_user = await CorporateUser.get_or_none(user=current_user)
    if not corporate_user:
        raise PermissionDeniedException()
    return corporate_user


@job_posting_router.post(
    "/",
    response_model=JobPostingResponse,
    status_code=201,
    summary="구인 공고 작성",
    description="""
`401` `code`: `invalid_token` 로그인이 필요합니다.\n
`403` `code`: `permission_denied` 해당 작업을 수행할 권한이 없습니다.\n
""",
)
async def create_job_posting(
    data: JobPostingCreateUpdate,
    current_user: BaseUser = Depends(get_current_user),
):
    corporate_user = await get_corporate_user(current_user)
    return await JobPostingService.create_job_posting(corporate_user, data)


@job_posting_router.get(
    "/my_company/job_postings/",
    response_model=list[JobPostingSummaryResponse],
    summary="내 회사의 전체 공고 조회",
)
async def get_my_company_job_postings(
    current_user: CorporateUser = Depends(get_corporate_user),
):
    return await JobPostingService.get_job_postings_by_company_user(current_user)


@job_posting_router.get(
    "/post/{job_posting_id}/",
    response_model=JobPostingResponse,
    status_code=200,
    summary="특정 공고 조회",
    description="""
`401` `code`: `invalid_token` 로그인이 필요합니다.\n
`403` `code`: `permission_denied` 해당 작업을 수행할 권한이 없습니다.\n
`404` `code`: `notification_not_found` 해당 공고를 찾을 수 없습니다.\n
""",
)
async def get_specific_job_posting(
    job_posting_id: int,
    current_user: CorporateUser = Depends(get_corporate_user),
):
    job_posting = await JobPostingService.get_specific_job_posting(
        current_user, job_posting_id
    )
    return job_posting


@job_posting_router.patch(
    "/{job_posting_id}/",
    response_model=JobPostingResponse,
    status_code=200,
    summary="구인 공고 수정",
    description="""
`401` `code`: `invalid_token` 로그인이 필요합니다.\n
`403` `code`: `permission_denied` 해당 작업을 수행할 권한이 없습니다.\n
`404` `code`: `notification_not_found` 공고를 찾을 수 없습니다.\n
""",
)
async def patch_job_posting(
    job_posting_id: int,
    updated_data: JobPostingCreateUpdate,
    current_user: CorporateUser = Depends(get_corporate_user),
):
    return await JobPostingService.patch_job_posting(
        current_user, job_posting_id, updated_data
    )


@job_posting_router.delete(
    "/{job_posting_id}/",
    status_code=200,
    summary="구인 공고 삭제",
    description="""
`401` `code`: `invalid_token` 유효하지 않은 토큰입니다.\n
`403` `code`: `permission_denied` 해당 작업을 처리할 권한이 없습니다.\n
`404` `code`: `notification_not_found` 공고를 찾을 수 없습니다.\n
""",
)
async def delete_job_posting_endpoint(
    job_posting_id: int,
    current_user: CorporateUser = Depends(get_corporate_user),
):
    # CorporateUser 객체 자체를 전달
    await JobPostingService.delete_job_posting(current_user, job_posting_id)
    return {"message": "공고가 삭제되었습니다."}
