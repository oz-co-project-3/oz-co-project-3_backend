from fastapi import APIRouter, Depends

from app.models.job_posting_models import JobPosting
from app.models.user_models import CorporateUser, SeekerUser
from app.schemas.jobposting_schemas import JobPostingCreateUpdate, JobPostingResponse
from app.services.jobposting_services import JobPostingService
from app.utils.exception import CustomException

job_posting_router = APIRouter(
    prefix="/job_posting",
    tags=["job_posting"],  # 스웨거 표시 태그
)


async def fake_current_user():
    corporate = await CorporateUser.get(pk=1).prefetch_related("user")
    return SeekerUser


@job_posting_router.post(
    "/{company_id}/",
    response_model=JobPostingResponse,
    status_code=201,
    summary="구인 공고 작성",
    description="""
             - `401` `code`: `invalid_token` 로그인이 필요합니다.\n
             - `403` `code`: `permission_denied` 해당 작업을 수행할 권한이 없습니다.\n
             """,
)
async def create_job_posting(
    data: JobPostingCreateUpdate,  # 요청 데이터 검증
    user: dict = Depends(fake_current_user),  # 인증된 사용자 정보
):
    return await JobPostingService.create_job_posting(user, data)


@job_posting_router.patch(
    "/{notification_id}/",
    response_model=JobPostingResponse,
    status_code=200,
    summary="구인 공고 수정",
    description="""
             - `401` `code`: `invalid_token` 로그인이 필요합니다.\n
             - `403` `code`: `permission_denied` 해당 작업을 수행할 권한이 없습니다.\n
             - `404` `code`: `notification_not_found` 공고를 찾을 수 없습니다.\n
             """,
)
async def patch_job_posting(
    job_posting_id: int,  # 공고 ID를 경로 파라미터로 받음
    updated_data: JobPostingCreateUpdate,  # 수정할 데이터
    user: dict = Depends(fake_current_user),  # 인증된 사용자 정보
):
    # JobPosting을 가져오기
    job_posting = await JobPosting.get(id=job_posting_id)

    # 작성자인지 확인
    if job_posting.user_id != user["id"]:
        raise CustomException(
            error="해당 작업을 수행할 권한이 없습니다.", code="permission_denied", status_code=403
        )
    return await JobPostingService().patch_job_posting(user, job_posting, updated_data)
