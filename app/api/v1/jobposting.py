from fastapi import APIRouter, Depends

from app.core.token import get_current_user  # 인증된 사용자 가져오기 서비스 함수
from app.domain.job_posting.jobposting_schemas import (
    JobPostingCreateUpdate,
    JobPostingResponse,
    JobPostingSummaryResponse,
)
from app.domain.job_posting.jobposting_services import JobPostingService
from app.domain.services.verification import CustomException
from app.domain.user.user_models import BaseUser, CorporateUser

job_posting_router = APIRouter(
    prefix="/api/job_posting",
    tags=["job_posting"],  # 스웨거 표시 태그
)


async def current_user_dependency(user: BaseUser = Depends(get_current_user)):
    if not user:
        raise CustomException(
            error="로그인이 필요합니다.",
            code="invalid_token",
            status_code=401,
        )
    return user


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
    data: JobPostingCreateUpdate,  # 요청 데이터 검증
    current_user: BaseUser = Depends(current_user_dependency),  # 인증된 사용자 정보
):
    return await JobPostingService.create_job_posting(current_user, data)


@job_posting_router.get(
    "/{company_id}/",
    response_model=list[JobPostingSummaryResponse],
    status_code=200,
    summary="특정 회사 공고 조회",
    description="""
`401` `code`: `invalid_token` 로그인이 필요합니다.\n
`403` `code`: `permission_denied` 해당 작업을 수행할 권한이 없습니다.\n
`404` `code`: `notification_not_found` 등록된 공고를 찾을 수 없습니다.\n
""",
)
async def get_job_postings_by_company(
    company_id: int,
    current_user: BaseUser = Depends(current_user_dependency),  # 인증된 사용자 정보
):
    return await JobPostingService.get_job_postings_by_company(company_id)


@job_posting_router.get(
    "/{company_id}/{job_posting_id}/",
    response_model=JobPostingResponse,
    status_code=200,
    summary="특정 회사의 특정 공고 조회",
    description="""
`401` `code`: `invalid_token` 로그인이 필요합니다.\n
`403` `code`: `permission_denied` 해당 작업을 수행할 권한이 없습니다.\n
`404` `code`: `notification_not_found` 해당 공고를 찾을 수 없습니다.\n
""",
)
async def get_specific_job_posting(
    company_id: int,
    job_posting_id: int,
    current_user: BaseUser = Depends(current_user_dependency),  # 인증된 사용자 정보
):
    job_posting = await JobPostingService.get_specific_job_posting(
        company_id, job_posting_id
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
    current_user: CorporateUser = Depends(current_user_dependency),
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
    current_user: BaseUser = Depends(current_user_dependency),  # 인증된 현재 사용자
):
    return await JobPostingService.delete_job_posting(current_user, job_posting_id)
