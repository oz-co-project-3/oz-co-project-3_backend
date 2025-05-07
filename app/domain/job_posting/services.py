import logging
from typing import List

from app.domain.job_posting.models import JobPosting
from app.domain.job_posting.repository import JobPostingRepository
from app.domain.job_posting.schema import JobPostingCreateUpdate, JobPostingResponse
from app.domain.resume.repository import ResumeRepository
from app.domain.services.verification import check_existing
from app.domain.user.models import BaseUser, CorporateUser
from app.exceptions.auth_exceptions import PermissionDeniedException
from app.exceptions.job_posting_exceptions import (
    NotificationNotFoundException,
    SameTitleExistException,
)
from app.exceptions.user_exceptions import UserNotFoundException

logger = logging.getLogger(__name__)


class JobPostingService:
    @staticmethod
    async def validate_user_permissions(
        corporate_user: CorporateUser, job_posting: JobPosting = None
    ):
        if job_posting.user_id != corporate_user.id:
            logger.warning(
                f"[JOBPOSTING-SERVICE] 권한 없음: job_posting.user_id ({job_posting.user_id}) != corporate_user.user_id ({corporate_user.id})"
            )
            raise PermissionDeniedException()
        logger.info("[JOBPOSTING-SERVICE] validate_user_permissions 통과됨.")

    @staticmethod
    def format_job_posting_response(job_posting: JobPosting) -> JobPostingResponse:
        return JobPostingResponse.from_orm(job_posting)

    @staticmethod
    async def create_job_posting(
        current_user: BaseUser, data: JobPostingCreateUpdate
    ) -> JobPostingResponse:
        corporate_user = await JobPostingRepository.get_corporate_user_by_base_user(
            current_user
        )
        check_existing(corporate_user, UserNotFoundException)
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
        job_posting = await JobPostingRepository.get_job_posting_by_id(job_posting_id)
        if not job_posting:
            logger.warning(
                f"[JOBPOSTING-SERVICE] patch_job_posting 실패: JobPosting id {job_posting_id} not found."
            )
            raise NotificationNotFoundException()
        await JobPostingService.validate_user_permissions(corporate_user, job_posting)
        updated_fields = updated_data.model_dump(exclude_unset=True)
        if "title" in updated_fields:
            await JobPostingService._check_title_duplication(
                updated_fields["title"], exclude_id=job_posting.id
            )
        updated_job_posting = await JobPostingRepository.update_job_posting(
            job_posting, updated_fields
        )
        return JobPostingService.format_job_posting_response(updated_job_posting)

    @staticmethod
    async def _check_title_duplication(title: str, exclude_id: int = None):
        query = JobPosting.filter(title=title)
        if exclude_id:
            query = query.exclude(id=exclude_id)
        existing_posting = await query.first()
        if existing_posting:
            logger.warning(
                f"[JOBPOSTING-SERVICE] 제목 중복 발견: 기존 공고 id={existing_posting.id}"
            )
            raise SameTitleExistException()
        logger.info("[JOBPOSTING-SERVICE] 제목 중복 없음")

    @staticmethod
    async def get_job_postings_by_company_user(
        user: CorporateUser,
    ) -> List[JobPostingResponse]:
        job_postings = await JobPostingRepository.get_job_postings_by_user(user)
        return [JobPostingResponse.from_orm(posting) for posting in job_postings]

    @staticmethod
    async def get_specific_job_posting(
        corporate_user: CorporateUser, job_posting_id: int
    ) -> JobPosting:
        job_posting = await JobPostingRepository.get_job_posting_by_company_and_id(
            user_id=corporate_user.id, job_posting_id=job_posting_id
        )
        if not job_posting:
            logger.warning(
                f"[JOBPOSTING-SERVICE] get_specific_job_posting 실패: JobPosting id {job_posting_id} not found for corporate_user id={corporate_user.id}"
            )
            raise NotificationNotFoundException()
        return job_posting

    @staticmethod
    async def delete_job_posting(
        corporate_user: CorporateUser, job_posting_id: int
    ) -> dict:
        job_posting = await JobPostingRepository.get_job_posting_by_id(job_posting_id)
        if not job_posting:
            logger.warning(
                f"[JOBPOSTING-SERVICE] delete_job_posting 실패: JobPosting id {job_posting_id} not found."
            )
            raise NotificationNotFoundException()
        await JobPostingService.validate_user_permissions(corporate_user, job_posting)
        await JobPostingRepository.delete_job_posting(job_posting)
        return {"message": "구인 공고 삭제가 완료되었습니다.", "data": job_posting_id}

    @staticmethod
    async def toggle_bookmark(current_user: BaseUser, id: int):
        job_posting = await JobPostingRepository.get_job_posting_by_id(id)
        if not job_posting:
            logger.warning(
                f"[JOBPOSTING-SERVICE] toggle_job_posting_bookmark 실패: JobPosting id {id} not found."
            )
            raise NotificationNotFoundException()
        seeker_user = await ResumeRepository.get_seeker_user(current_user)
        return await JobPostingRepository.toggle_job_posting_bookmark(
            seeker_user, job_posting
        )
