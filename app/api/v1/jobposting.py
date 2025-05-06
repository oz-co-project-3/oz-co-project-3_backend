import logging

from fastapi import APIRouter, Depends, Path

from app.core.token import get_current_user
from app.domain.job_posting.repository import JobPostingRepository
from app.domain.job_posting.schema import JobPostingCreateUpdate, JobPostingResponse
from app.domain.job_posting.services import JobPostingService
from app.domain.user.models import BaseUser

job_posting_router = APIRouter(
    prefix="/api/job_posting",
    tags=["job_posting"],
)
logger = logging.getLogger(__name__)


@job_posting_router.post(
    "/",
    response_model=JobPostingResponse,
    status_code=201,
    summary="구인 공고 작성",
    description="""
`401` `code`: `invalid_token` 로그인이 필요합니다.\n
`403` `code`: `permission_denied` 해당 작업을 수행할 권한이 없습니다.\n
`404` `code`: `user_not_found` 해당 유저를 찾을수 없습니다\n
`404` `code`: `not_corp_user` 비즈니스 유저가 아닙니다\n
`422` : Unprocessable Entity
""",
)
async def create_job_posting(
    data: JobPostingCreateUpdate,
    current_user: BaseUser = Depends(get_current_user),
):
    logger.info(f"[API] 구인 공고 작성 요청 : BaseUser id={current_user.id}")
    result = await JobPostingService.create_job_posting(current_user, data)
    logger.info(f"[API] 구인 공고 작성 완료 : CorporateUser id={current_user.id}")
    return result


@job_posting_router.get(
    "/",
    response_model=list[JobPostingResponse],
    summary="내 회사의 전체 공고 조회",
)
async def get_my_company_job_postings(
    current_user: BaseUser = Depends(get_current_user),
):
    logger.info(f"[API] 내 회사 전체 공고 조회 요청 : BaseUser id={current_user.id}")
    corporate_user = await JobPostingRepository.get_corporate_user_by_base_user(
        current_user
    )
    result = await JobPostingService.get_job_postings_by_company_user(corporate_user)
    logger.info(f"[API] 내 회사 전체 공고 조회 완료 : CorporateUser id={corporate_user.id}")
    return result


@job_posting_router.get(
    "/{job_posting_id}/",
    response_model=JobPostingResponse,
    status_code=200,
    summary="특정 공고 조회",
    description="""
`401` `code`: `invalid_token` 로그인이 필요합니다.\n
`403` `code`: `permission_denied` 해당 작업을 수행할 권한이 없습니다.\n
`404` `code`: `notification_not_found` 해당 공고를 찾을 수 없습니다.\n
`422` : Unprocessable Entity
""",
)
async def get_specific_job_posting(
    job_posting_id: int = Path(
        ..., gt=0, le=2147483647, description="job_posting ID (1 ~ 2147483647)"
    ),
    current_user: BaseUser = Depends(get_current_user),
):
    logger.info(
        f"[API] 특정 공고 조회 요청 : job_posting_id={job_posting_id}, BaseUser id={current_user.id}"
    )
    corporate_user = await JobPostingRepository.get_corporate_user_by_base_user(
        current_user
    )
    job_posting = await JobPostingService.get_specific_job_posting(
        corporate_user, job_posting_id
    )
    logger.info(
        f"[API] 특정 공고 조회 완료 : job_posting_id={job_posting_id}, CorporateUser id={corporate_user.id}"
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
`422` : Unprocessable Entity
""",
)
async def patch_job_posting(
    updated_data: JobPostingCreateUpdate,
    job_posting_id: int = Path(
        ..., gt=0, le=2147483647, description="job_posting ID (1 ~ 2147483647)"
    ),
    current_user: BaseUser = Depends(get_current_user),
):
    logger.info(
        f"[API] 구인 공고 수정 요청 : job_posting_id={job_posting_id}, BaseUser id={current_user.id}"
    )
    corporate_user = await JobPostingRepository.get_corporate_user_by_base_user(
        current_user
    )
    result = await JobPostingService.patch_job_posting(
        corporate_user, job_posting_id, updated_data
    )
    logger.info(
        f"[API] 구인 공고 수정 완료 : job_posting_id={job_posting_id}, CorporateUser id={corporate_user.id}"
    )
    return result


@job_posting_router.delete(
    "/{job_posting_id}/",
    status_code=200,
    summary="구인 공고 삭제",
    description="""
`401` `code`: `invalid_token` 유효하지 않은 토큰입니다.\n
`403` `code`: `permission_denied` 해당 작업을 처리할 권한이 없습니다.\n
`404` `code`: `notification_not_found` 공고를 찾을 수 없습니다.\n
`422` : Unprocessable Entity
""",
)
async def delete_job_posting_endpoint(
    job_posting_id: int = Path(
        ..., gt=0, le=2147483647, description="job_posting ID (1 ~ 2147483647)"
    ),
    current_user: BaseUser = Depends(get_current_user),
):
    logger.info(
        f"[API] 구인 공고 삭제 요청 : job_posting_id={job_posting_id}, BaseUser id={current_user.id}"
    )
    corporate_user = await JobPostingRepository.get_corporate_user_by_base_user(
        current_user
    )
    await JobPostingService.delete_job_posting(corporate_user, job_posting_id)
    logger.info(
        f"[API] 구인 공고 삭제 완료 : job_posting_id={job_posting_id}, CorporateUser id={corporate_user.id}"
    )
    return {"message": "공고가 삭제되었습니다."}


@job_posting_router.post(
    "/{id}/bookmark/",
    status_code=200,
    summary="공고 찜하기",
    description="""
`401` `code`: `invalid_token` 유효하지 않은 토큰입니다.\n
`403` `code`: `permission_denied` 해당 작업을 처리할 권한이 없습니다.\n
`404` `code`: `notification_not_found` 공고를 찾을 수 없습니다.\n
`422` : Unprocessable Entity
""",
)
async def create_job_posting_bookmark(
    current_user: BaseUser = Depends(get_current_user),
    id: int = Path(
        ..., gt=0, le=2147483647, description="job_posting ID (1 ~ 2147483647)"
    ),
):
    logger.info(f"[API] 공고 찜하기 요청 공고_id :{id}, user_id :{current_user.id}")
    is_added = await JobPostingService.toggle_bookmark(current_user, id)
    message = "북마크가 추가되었습니다." if is_added else "북마크가 해제되었습니다."
    logger.info(
        f"[JOBPOSTING-SERVICE] Bookmark {'추가' if is_added else '해제'} 완료: user_id={current_user.id}, posting_id={id}"
    )
    return {"message": message}
