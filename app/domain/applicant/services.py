from typing import List

from app.domain.applicant.repository import ApplicantRepository
from app.domain.applicant.schema import (
    ApplicantCreateUpdate,
    ApplicantResponse,
    ApplicantUpdate,
)
from app.domain.job_posting.models import StatusEnum
from app.domain.job_posting.repository import JobPostingRepository
from app.domain.job_posting.services import JobPostingService
from app.domain.user.user_models import BaseUser, CorporateUser
from app.exceptions.auth_exceptions import PermissionDeniedException
from app.exceptions.job_posting_exceptions import NotificationNotFoundException


class ApplicantService:
    @staticmethod
    async def _format_applicant_response(applicant) -> ApplicantResponse:
        """지원자 응답 데이터 포맷팅"""
        return ApplicantResponse(
            id=applicant.id,
            job_posting_id=applicant.job_posting_id,
            resume_id=applicant.resume_id,
            user_id=applicant.user_id,
            status=applicant.status,
            memo=applicant.memo,
            created_at=applicant.created_at,
            updated_at=applicant.updated_at,
            job_title=applicant.job_posting.title,
            company_name=applicant.job_posting.company,
            position=applicant.job_posting.position,
            deadline=applicant.job_posting.deadline,
        )

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

        return [ApplicantService._format_applicant_response(app) for app in applicants]

    @staticmethod
    async def get_all_applicants_by_corporate_user(
        current_user: BaseUser,
    ) -> List[ApplicantResponse]:
        """기업 사용자용: 모든 공고에 대한 지원자 조회"""
        applicants = await ApplicantRepository.get_applicants_by_corporate_user(
            current_user
        )

        if not applicants:
            raise NotificationNotFoundException()

        return [ApplicantService._format_applicant_response(app) for app in applicants]

    @staticmethod
    async def get_applicants_by_seeker_user(user: BaseUser) -> List[ApplicantResponse]:
        """구직자가 지원한 모든 공고 조회"""
        try:
            print(f"조회 시작 - user.id: {user.id}, user type: {type(user)}")

            applicants = await ApplicantRepository.get_applicants_by_seeker_user(user)

            print(f"조회된 applicants 개수: {len(applicants)}")

            # 데이터가 없는 경우 빈 리스트 반환 (예외 대신)
            if not applicants:
                return []

            # 응답 데이터 변환
            result = []
            for app in applicants:
                try:
                    formatted = ApplicantService._format_applicant_response(app)
                    result.append(formatted)
                except Exception as format_err:
                    print(f"응답 포맷 변환 중 오류: {format_err}")

            return result

        except Exception as e:
            print(f"전체 조회 과정에서 오류 발생: {str(e)}")
            raise

    @staticmethod
    async def get_applicant_detail(
        user: BaseUser, applicant_id: int
    ) -> ApplicantResponse:
        """구직자용: 특정 지원 내역 상세 조회"""
        applicant = await ApplicantRepository.get_applicant_by_id(applicant_id, user)

        if not applicant:
            raise NotificationNotFoundException

        return ApplicantService._format_applicant_response(applicant)

    @staticmethod
    async def apply_for_job(
        user: BaseUser, data: ApplicantCreateUpdate
    ) -> ApplicantResponse:
        """구직자용: 공고에 지원하기"""
        job_posting = await JobPostingRepository.get_job_posting_by_id(
            data.job_posting_id
        )

        if job_posting.status not in [StatusEnum.Open, StatusEnum.Closing_soon]:
            raise PermissionDeniedException

        applicant = await ApplicantRepository.create_applicant(
            user=user.id,
            data={
                "job_posting_id": data.job_posting_id,
                "resume_id": data.resume_id,
                "memo": data.memo,
            },
        )

        return ApplicantService._format_applicant_response(applicant)

    @staticmethod
    async def update_application(
        user: BaseUser, applicant_id: int, data: ApplicantUpdate
    ) -> ApplicantResponse:
        """구직자용: 지원 내역 수정"""
        applicant = await ApplicantRepository.get_applicant_by_id(applicant_id, user)

        if not applicant:
            raise NotificationNotFoundException

        updated_data = {k: v for k, v in data.dict().items() if v is not None}
        updated_applicant = await ApplicantRepository.update_applicant(
            applicant, updated_data
        )

        return ApplicantService._format_applicant_response(updated_applicant)
