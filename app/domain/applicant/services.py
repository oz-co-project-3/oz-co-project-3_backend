from typing import List

from app.domain.applicant.repository import ApplicantRepository
from app.domain.applicant.schema import ApplicantResponse
from app.domain.applicant.utils import format_applicant_response
from app.domain.job_posting.repository import JobPostingRepository
from app.domain.job_posting.services import JobPostingService
from app.domain.user.user_models import BaseUser, CorporateUser
from app.exceptions.auth_exceptions import PermissionDeniedException
from app.exceptions.job_posting_exceptions import NotificationNotFoundException


class ApplicantService:
    @staticmethod
    async def get_applicants_by_job_posting(
        user: BaseUser, job_posting_id: int
    ) -> List[ApplicantResponse]:
        """기업 사용자용: 특정 공고에 대한 모든 지원자 조회"""
        job_posting = await JobPostingRepository.get_job_posting_by_id(job_posting_id)
        await JobPostingService.validate_user_permissions(user, job_posting)

        applicants = await ApplicantRepository.get_applicants_by_job_posting(
            job_posting_id
        )
        if not applicants:
            raise NotificationNotFoundException()

        return [format_applicant_response(app) for app in applicants]

    @staticmethod
    async def get_all_applicants_by_corporate_user(
        current_user: BaseUser,
    ) -> List[ApplicantResponse]:
        corporate_user: CorporateUser = await CorporateUser.get_or_none(
            user_id=current_user
        )
        if not corporate_user:
            raise PermissionDeniedException

        await JobPostingService.validate_user_permissions(
            corporate_user, corporate_user
        )

        applicants = await ApplicantRepository.get_applicants_by_corporate_user(
            corporate_user.id
        )
        if not applicants:
            raise NotificationNotFoundException()

        return [format_applicant_response(app) for app in applicants]

    @staticmethod
    async def get_applicants_by_seeker_user(
        user: BaseUser,
    ) -> List[ApplicantResponse]:
        """구직자가 지원한 모든 공고 조회"""
        applicants = await ApplicantRepository.get_applicants_by_seeker_user(user.id)
        if not applicants:
            raise NotificationNotFoundException()

        return [format_applicant_response(app) for app in applicants]

    @staticmethod
    async def get_applicant_detail(
        user: BaseUser, applicant_id: int
    ) -> ApplicantResponse:
        """구직자용: 특정 지원 내역 상세 조회"""
        applicant = await ApplicantRepository.get_applicant_by_id(applicant_id, user.id)
        if not applicant:
            raise NotificationNotFoundException()

        return format_applicant_response(applicant)
