import logging
from typing import List

from app.domain.applicant.repository import ApplicantRepository
from app.domain.applicant.schema import ApplicantResponse
from app.domain.applicant.utils import format_applicant_response
from app.domain.job_posting.repository import JobPostingRepository
from app.domain.job_posting.services import JobPostingService
from app.domain.user.user_models import BaseUser, CorporateUser
from app.exceptions.auth_exceptions import PermissionDeniedException
from app.exceptions.job_posting_exceptions import NotificationNotFoundException

logger = logging.getLogger(__name__)


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
        return [format_applicant_response(app) for app in applicants]

    @staticmethod
    async def get_all_applicants_by_corporate_user(
        current_user: BaseUser,
    ) -> List[ApplicantResponse]:
        # BaseUser를 CorporateUser로 조회 (없으면 예외 발생)
        corporate_user: CorporateUser = await CorporateUser.get_or_none(
            user_id=current_user.id
        )
        if not corporate_user:
            logger.warning(
                f"[APPLICANT-SERVICE] 요청자 BaseUser ID: {current_user.id}에 대해 CorporateUser 정보를 찾을 수 없습니다."
            )
            raise PermissionDeniedException()

        await JobPostingService.validate_user_permissions(
            corporate_user, corporate_user
        )

        applicants = await ApplicantRepository.get_applicants_by_corporate_user(
            corporate_user.id
        )
        if not applicants:
            logger.warning(
                f"[APPLICANT-SERVICE] CorporateUser ID {corporate_user.id}에 등록된 공고에 지원한 지원자가 없습니다."
            )
            raise NotificationNotFoundException()
        return [format_applicant_response(app) for app in applicants]

    @staticmethod
    async def get_applicants_by_seeker_user(user: BaseUser) -> List[ApplicantResponse]:
        applicants = await ApplicantRepository.get_applicants_by_seeker_user(user.id)
        if not applicants:
            logger.warning(
                f"[APPLICANT-SERVICE] 구직자 BaseUser ID {user.id}에 대한 지원 내역이 없습니다."
            )
            raise NotificationNotFoundException()
        return [format_applicant_response(app) for app in applicants]

    @staticmethod
    async def get_applicant_detail(
        user: BaseUser, applicant_id: int
    ) -> ApplicantResponse:
        applicant = await ApplicantRepository.get_applicant_by_id(applicant_id, user.id)
        if not applicant:
            logger.warning(
                f"[APPLICANT-SERVICE] 지원내역ID {applicant_id}를 BaseUser ID {user.id}에 대해 찾을 수 없습니다."
            )
            raise NotificationNotFoundException()
        return format_applicant_response(applicant)
