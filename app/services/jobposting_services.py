from app.models.job_posting_models import JobPosting
from app.models.user_models import BaseUser, CorporateUser
from app.schemas.jobposting_schemas import (
    JobPostingCreateUpdate,
    JobPostingResponse,
    JobPostingSummaryResponse,
)
from app.utils.exception import CustomException


def ensure_corporate_user(user: BaseUser):
    """기업 회원인지 검토"""
    if not hasattr(user, "UserType") or user.UserType != "business":
        raise CustomException(
            error="해당 작업을 수행할 권한이 없습니다.", code="permission_denied", status_code=403
        )


def ensure_job_posting_exists(job_posting: JobPosting):
    """공고 존재 여부 확인"""
    if not job_posting:
        raise CustomException(
            error="공고를 찾을 수 없습니다.", code="notification_not_found", status_code=404
        )


def ensure_company_exists(company: CorporateUser):
    """회사 존재 여부 확인"""
    if not company:
        raise CustomException(
            error="회사를 찾을 수 없습니다.", code="company_not_found", status_code=404
        )


def ensure_authenticated_user(user: BaseUser):
    """인증된 사용자 확인"""
    if not user:
        raise CustomException(
            error="로그인이 필요합니다.", code="invalid_token", status_code=401
        )


class JobPostingService:
    @staticmethod
    async def create_job_posting(
        current_user: BaseUser, data: JobPostingCreateUpdate
    ) -> dict:
        # 인증 및 권한 확인
        ensure_authenticated_user(current_user)
        ensure_corporate_user(current_user)

        # JobPosting 생성
        job_posting = JobPosting(user_id=current_user.id, **data.dict())
        await job_posting.save()

        # 원하는 반환 형태 구성
        return {
            "message": "구인 공고가 등록되었습니다.",
            "data": {
                "id": job_posting.id,
                "title": job_posting.title,
                "status": job_posting.status.value
                if hasattr(job_posting.status, "value")
                else job_posting.status,
            },
        }

    @staticmethod
    async def patch_job_posting(
        user: CorporateUser,
        job_posting: JobPosting,
        updated_data: JobPostingCreateUpdate,
    ) -> dict:
        # 인증 및 권한 확인
        ensure_authenticated_user(user)
        ensure_job_posting_exists(job_posting)

        # 권한 검사: 작성자인지 확인
        if job_posting.user_id != user.id:
            raise CustomException(
                error="해당 작업을 수행할 권한이 없습니다.", code="permission_denied", status_code=403
            )

        # JobPosting 업데이트 로직
        for field, value in updated_data.dict(exclude_unset=True).items():
            setattr(job_posting, field, value)
        await job_posting.save()

        return {
            "message": "구인 공고가 성공적으로 수정되었습니다.",
            "data": {
                "id": job_posting.id,
                "title": job_posting.title,
                "status": job_posting.status.value,
            },
        }

    @staticmethod
    async def get_job_postings_by_company(
        company_id: int,
    ) -> list[JobPostingSummaryResponse]:
        # 회사 존재 여부 확인
        company = await CorporateUser.get_or_none(id=company_id)
        ensure_company_exists(company)

        # 공고 조회
        job_postings = await JobPosting.filter(company_id=company_id).all()
        if not job_postings:
            raise CustomException(
                error="등록된 공고를 찾을 수 없습니다.",
                code="notification_not_found",
                status_code=404,
            )
        return [
            JobPostingSummaryResponse(
                id=job.id,
                title=job.title,
                status=job.status,
                created_at=job.created_at,
            )
            for job in job_postings
        ]
