import logging
from typing import List

from app.domain.applicant.repository import (
    get_applicant_by_id,
    get_applicants_by_job_posting,
    get_applicants_by_seeker_user,
    repo_get_applicants_by_corporate_user,
)
from app.domain.applicant.schema import ApplicantResponse
from app.domain.applicant.utils import format_applicant_response
from app.domain.job_posting.repository import (
    get_corporate_user_by_base_user,
    rep_get_job_posting_by_id,
)
from app.domain.job_posting.services import validate_user_permissions
from app.domain.user.models import BaseUser, CorporateUser
from app.exceptions.auth_exceptions import PermissionDeniedException
from app.exceptions.job_posting_exceptions import NotificationNotFoundException

logger = logging.getLogger(__name__)


async def get_applicants_by_job_posting_service(
    user: BaseUser, job_posting_id: int
) -> List[ApplicantResponse]:
    """기업 사용자용: 특정 공고에 대한 모든 지원자 조회"""
    job_posting = await rep_get_job_posting_by_id(job_posting_id)
    # BaseUser를 CorporateUser로 변환
    corporate_user = await get_corporate_user_by_base_user(user)
    await validate_user_permissions(corporate_user, job_posting)

    applicants = await get_applicants_by_job_posting(job_posting_id)
    return [format_applicant_response(app) for app in applicants]


async def get_all_applicants_by_corporate_user_service(
    current_user_id: int,
) -> List[ApplicantResponse]:
    corporate_user: CorporateUser = await CorporateUser.get_or_none(
        user_id=current_user_id
    )
    if not corporate_user:
        logger.warning(
            f"[APPLICANT-SERVICE] 요청자 BaseUser ID: {current_user_id}에 대해 CorporateUser 정보를 찾을 수 없습니다."
        )
        raise PermissionDeniedException()

    applicants = await repo_get_applicants_by_corporate_user(corporate_user.id)
    if not applicants:
        logger.warning(
            f"[APPLICANT-SERVICE] CorporateUser ID {corporate_user.id}에 등록된 공고에 지원한 지원자가 없습니다."
        )
        raise NotificationNotFoundException()
    return [format_applicant_response(app) for app in applicants]


async def get_applicants_by_seeker_user_service(user_id=int) -> List[ApplicantResponse]:
    applicants = await get_applicants_by_seeker_user(user_id)
    return [format_applicant_response(app) for app in applicants]


async def get_applicant_detail_service(
    user_id: int, applicant_id: int
) -> ApplicantResponse:
    applicant = await get_applicant_by_id(applicant_id, user_id)
    if not applicant:
        logger.warning(
            f"[APPLICANT-SERVICE] 지원내역ID {applicant_id}를 BaseUser ID {user_id}에 대해 찾을 수 없습니다."
        )
        raise NotificationNotFoundException()
    return format_applicant_response(applicant)
