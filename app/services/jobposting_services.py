from app.models.job_posting_models import JobPosting
from app.models.user_models import BaseUser, CorporateUser
from app.schemas.jobposting_schemas import JobPostingCreateUpdate, JobPostingResponse
from app.utils.exception import CustomException


def ensure_resource_exists(
    resource, error_message: str, error_code: str, status_code: int = 404
):
    """리소스 존재 여부 확인 헬퍼 함수"""
    if not resource:
        raise CustomException(
            error=error_message,
            code=error_code,
            status_code=status_code,
        )


def ensure_corporate_user(user: BaseUser):
    """기업 회원인지 확인"""
    if not user or user.user_type != BaseUser.UserType.BUSINESS.value:
        raise CustomException(
            error="해당 작업을 수행할 권한이 없습니다.",
            code="permission_denied",
            status_code=403,
        )


def ensure_authenticated_user(user: BaseUser):
    """인증된 사용자 확인"""
    if not user:
        raise CustomException(
            error="로그인이 필요합니다.",
            code="invalid_token",
            status_code=401,
        )


class JobPostingService:
    @staticmethod
    async def validate_user_permissions(
        user: BaseUser, company_id: int = None, job_posting: JobPosting = None
    ):
        """
        사용자 권한 및 리소스 검증
        """
        # 사용자 인증 및 권한 확인
        ensure_authenticated_user(user)
        ensure_corporate_user(user)

        # 회사 존재 확인
        if company_id:
            company = await CorporateUser.get_or_none(id=company_id)
            ensure_resource_exists(
                company,
                error_message="회사를 찾을 수 없습니다.",
                error_code="company_not_found",
            )

        # 공고 존재 및 권한 확인
        if job_posting:
            ensure_resource_exists(
                job_posting,
                error_message="공고를 찾을 수 없습니다.",
                error_code="notification_not_found",
            )
            if job_posting.user != user.id:
                raise CustomException(
                    error="해당 작업을 수행할 권한이 없습니다.",
                    code="permission_denied",
                    status_code=403,
                )

    @staticmethod
    def job_posting_response(job_posting: JobPosting) -> JobPostingResponse:
        """
        JobPosting 객체를 JobPostingResponse 스키마로 변환
        """
        return JobPostingResponse(
            id=job_posting.id,
            title=job_posting.title,
            location=job_posting.location,
            employment_type=job_posting.employment_type,
            employ_method=job_posting.employ_method,
            position=job_posting.position,
            history=job_posting.history,
            recruitment_count=job_posting.recruitment_count,
            education=job_posting.education,
            deadline=job_posting.deadline,
            salary=job_posting.salary,
            summary=job_posting.summary,
            description=job_posting.description,
            status=job_posting.status,
            view_count=job_posting.view_count,
            report=job_posting.report,
        )

    @staticmethod
    async def create_job_posting(
        current_user: BaseUser, data: JobPostingCreateUpdate
    ) -> dict:
        # 권한 확인
        await JobPostingService.validate_user_permissions(current_user)

        # JobPosting 생성
        job_posting = JobPosting(user_id=current_user.id, **data.model_dump())
        await job_posting.save()

        return {
            "message": "구인 공고가 등록되었습니다.",
            "data": JobPostingService.job_posting_response(job_posting),
        }

    @staticmethod
    async def patch_job_posting(
        user: CorporateUser,
        job_posting: JobPosting,
        updated_data: JobPostingCreateUpdate,
    ) -> dict:
        # 권한 확인
        await JobPostingService.validate_user_permissions(user, job_posting=job_posting)

        # 공고 업데이트
        for field, value in updated_data.model_dump(exclude_unset=True).items():
            setattr(job_posting, field, value)
        await job_posting.save()

        return {
            "message": "구인 공고가 성공적으로 수정되었습니다.",
            "data": JobPostingService.job_posting_response(job_posting),
        }

    @staticmethod
    async def get_job_postings_by_company(user: BaseUser, company_id: int) -> dict:
        # 사용자 권한 확인
        await JobPostingService.validate_user_permissions(user, company_id=company_id)

        # 회사 및 공고 조회
        job_postings = await JobPosting.filter(company_id=company_id).all()
        ensure_resource_exists(
            job_postings,
            error_message="등록된 공고를 찾을 수 없습니다.",
            error_code="notification_not_found",
        )

        postings = [
            {
                "id": job.id,
                "title": job.title,
                "status": job.status,
                "created_at": job.created_at,
            }
            for job in job_postings
        ]

        return {
            "message": "조회에 성공했습니다.",
            "company_id": company_id,
            "postings": postings,
        }

    @staticmethod
    async def get_specific_job_posting(
        user: BaseUser, company_id: int, job_posting_id: int
    ) -> dict:
        # 사용자 권한 및 특정 공고 조회
        await JobPostingService.validate_user_permissions(user, company_id=company_id)

        job_posting = await JobPosting.get_or_none(
            company_id=company_id, id=job_posting_id
        )
        ensure_resource_exists(
            job_posting,
            error_message="공고를 찾을 수 없습니다.",
            error_code="notification_not_found",
        )

        return {
            "message": "공고 조회에 성공했습니다.",
            "data": JobPostingService.job_posting_response(job_posting),
        }
