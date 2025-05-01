from typing import List

from app.domain.applicant.schema import ApplicantResponse
from app.domain.applicant.utils import format_applicant_response
from app.domain.job_posting.models import Applicants, JobPosting
from app.domain.user.user_models import BaseUser, CorporateUser
from app.exceptions.job_posting_exceptions import NotificationNotFoundException


class ApplicantRepository:
    @staticmethod
    async def _get_or_raise(model, **filters):
        """공통적으로 사용되는 get_or_none 후 예외 던지는 로직"""
        instance = await model.get_or_none(**filters)
        if not instance:
            raise NotificationNotFoundException(
                f"{model.__name__} 이 누락되었습니다.: {filters}"
            )
        return instance

    @staticmethod
    async def get_applicants_by_job_posting(job_posting_id: int) -> List[Applicants]:
        """특정 공고에 지원한 모든 지원자 조회"""
        return (
            await Applicants.filter(job_posting_id=job_posting_id)
            .prefetch_related("resume", "user")
            .all()
        )

    @staticmethod
    async def get_applicants_by_corporate_user(
        corporate_user_id: int,
    ) -> List[Applicants]:
        """기업 사용자가 올린 모든 공고에 대한 지원자 조회"""
        if not await JobPosting.filter(user_id=corporate_user_id).exists():
            raise NotificationNotFoundException

        job_posting_ids = await JobPosting.filter(
            user_id=corporate_user_id
        ).values_list("id", flat=True)

        return (
            await Applicants.filter(job_posting_id__in=job_posting_ids)
            .prefetch_related("resume", "user", "job_posting")
            .all()
        )

    @staticmethod
    async def get_applicants_by_seeker_user(user: BaseUser) -> List[Applicants]:
        """사용자가 지원한 모든 지원서를 조회"""
        applicants = (
            await Applicants.filter(user=user).prefetch_related("job_posting").all()
        )

        if not applicants:
            raise NotificationNotFoundException()

        return await applicants

    @staticmethod
    async def get_applicant_by_id(applicant_id: int, user_id: int) -> Applicants:
        """특정 지원 내역 조회"""
        return await Applicants.get_or_none(
            id=applicant_id, user_id=user_id
        ).prefetch_related("job_posting")

    @staticmethod
    async def get_applicant_detail(
        user: BaseUser, applicant_id: int
    ) -> ApplicantResponse:
        """구직자용: 특정 지원 내역 상세 조회"""
        applicant = await ApplicantRepository.get_applicant_by_id(applicant_id, user.id)

        if not applicant:
            raise NotificationNotFoundException

        return format_applicant_response(applicant)
