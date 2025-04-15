from typing import List

from fastapi import APIRouter, Depends, status

from app.core.token import get_current_user
from app.models.user_models import BaseUser
from app.schemas.jobs_schemas import JobPostingResponse
from app.services.jobs_services import get_all_job_posting, get_job_posting_by_id

jobs_router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@jobs_router.get(
    "/",
    response_model=List[JobPostingResponse],
    status_code=status.HTTP_200_OK,
    summary="공고 전체 조회",
    description="""
- `401` `code`: `invalid_token` 유효하지 않은 인증 토큰입니다.\n
	""",
)
async def get_list_job_posting(current_user: BaseUser = Depends(get_current_user)):
    return await get_all_job_posting()


@jobs_router.get(
    "/{id}/",
    response_model=JobPostingResponse,
    status_code=status.HTTP_200_OK,
    summary="공고 상세 조회",
    description="""
- `401` `code`: `invalid_token` 유효하지 않은 인증 토큰입니다.\n
- `404` `code`: `job_posting_not_found` 공고를 찾을 수 없습니다.\n
	""",
)
async def get_detail_job_posting(
    id: int, current_user: BaseUser = Depends(get_current_user)
):
    return await get_job_posting_by_id(id)
