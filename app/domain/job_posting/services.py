from tortoise.queryset import QuerySet

from app.domain.job_posting.models import JobPosting
from app.domain.job_posting.repository import JobPostingRepository
from app.domain.job_posting.schema import (
    JobPostingCreateUpdate,
    JobPostingResponse,
    JobPostingSummaryResponse,
)
from app.domain.user.user_models import BaseUser, CorporateUser
from app.exceptions.auth_exceptions import PermissionDeniedException
from app.exceptions.job_posting_exceptions import (
    NotificationNotFoundException,
    SameTitleExistException,
)


class JobPostingService:
    @staticmethod
    async def validate_user_permissions(
        user: BaseUser, corporate_user: CorporateUser, job_posting=None
    ):
        """권한 검증을 위한 메서드"""
        if not corporate_user:
            raise PermissionDeniedException()

        # job_posting이 있는 경우 소유권 검증
        if job_posting:
            if isinstance(job_posting, QuerySet):
                job_posting = await job_posting.first()

            if job_posting.user_id != corporate_user.id and not user.is_superuser:
                raise PermissionDeniedException()

    @staticmethod
    async def get_corporate_user_by_base_user(user: BaseUser) -> CorporateUser:
        """BaseUser로부터 CorporateUser를 조회하는 메서드"""
        corporate_user = await CorporateUser.get_or_none(user_id=user.id)
        if not corporate_user:
            raise PermissionDeniedException()
        return corporate_user

    @staticmethod
    def format_job_posting_response(job_posting: JobPosting) -> JobPostingResponse:
        """JobPosting 객체를 응답 형식으로 변환"""
        return JobPostingResponse.from_orm(job_posting)

    @staticmethod
    async def create_job_posting(
        current_user: BaseUser, data: JobPostingCreateUpdate
    ) -> dict:
        corporate_user = await JobPostingService.get_corporate_user_by_base_user(
            current_user
        )

        # JobPosting 생성
        job_posting = await JobPostingRepository.create_job_posting(
            corporate_user=corporate_user, data=data.model_dump()
        )

        return JobPostingService.format_job_posting_response(job_posting)

    @staticmethod
    async def patch_job_posting(
        corporate_user: CorporateUser,
        job_posting_id: int,
        updated_data: JobPostingCreateUpdate,
    ) -> JobPostingResponse:
        # 구인 공고 가져오기
        job_posting = await JobPostingRepository.get_job_posting_by_id(job_posting_id)

        # 권한 검증
        await JobPostingService.validate_user_permissions(
            corporate_user.user, corporate_user, job_posting
        )

        # 제목 중복 확인
        updated_fields = updated_data.model_dump(exclude_unset=True)
        if "title" in updated_fields:
            await JobPostingService._check_title_duplication(
                updated_fields["title"], job_posting.id
            )

        # 구인 공고 업데이트
        updated_job_posting = await JobPostingRepository.update_job_posting(
            job_posting, updated_fields
        )

        return JobPostingService.format_job_posting_response(updated_job_posting)

    @staticmethod
    async def _check_title_duplication(title: str, exclude_id: int = None):
        """제목 중복 검사 헬퍼 메서드"""
        query = JobPosting.filter(title=title)
        if exclude_id:
            query = query.exclude(id=exclude_id)

        existing_posting = await query.first()
        if existing_posting:
            raise SameTitleExistException()

    @staticmethod
    async def get_job_postings_by_company_user(
        user: CorporateUser,
    ) -> list[JobPostingSummaryResponse]:
        job_postings = await JobPostingRepository.get_job_postings_by_user(user)
        return [JobPostingSummaryResponse.from_orm(posting) for posting in job_postings]

    @staticmethod
    async def get_specific_job_posting(
        corporate_user: CorporateUser, job_posting_id: int
    ) -> JobPosting:
        job_posting = await JobPostingRepository.get_job_posting_by_company_and_id(
            user_id=corporate_user.id, job_posting_id=job_posting_id
        )

        if not job_posting:
            raise NotificationNotFoundException()

        return job_posting

    @staticmethod
    async def delete_job_posting(
        corporate_user: CorporateUser, job_posting_id: int
    ) -> dict:
        # 구인 공고 가져오기
        job_posting = await JobPostingRepository.get_job_posting_by_id(job_posting_id)

        # 권한 검증
        await JobPostingService.validate_user_permissions(
            corporate_user.user, corporate_user, job_posting
        )

        # 구인 공고 삭제
        await JobPostingRepository.delete_job_posting(job_posting)

        return {"message": "공고 삭제에 성공했습니다.", "data": job_posting_id}
