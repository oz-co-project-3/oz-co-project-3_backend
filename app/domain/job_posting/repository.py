import logging
from typing import List, Optional

from app.domain.job_posting.models import JobPosting
from app.domain.user.models import BaseUser, CorporateUser
from app.exceptions.auth_exceptions import PermissionDeniedException
from app.exceptions.job_posting_exceptions import NotCorpUserException


class JobPostingRepository:
    @staticmethod
    async def get_corporate_user_by_base_user(user: BaseUser) -> CorporateUser:
        if "business" not in user.user_type:
            raise NotCorpUserException()
        corporate_user = await CorporateUser.get_or_none(user=user)
        return corporate_user

    @staticmethod
    async def get_job_posting_by_id(job_posting_id: int) -> Optional[JobPosting]:
        return await JobPosting.get_or_none(id=job_posting_id)

    @staticmethod
    async def get_job_postings_by_user(
        corporate_user: CorporateUser,
    ) -> List[JobPosting]:
        # 특정 CorporateUser가 올린 모든 공고 조회 (없으면 빈 리스트 반환)
        return await JobPosting.filter(user=corporate_user).all()

    @staticmethod
    async def get_job_posting_by_company_and_id(
        user_id: int, job_posting_id: int
    ) -> Optional[JobPosting]:
        # 회사(user_id)와 공고 id 조건으로 조회 (없으면 None 반환)
        return await JobPosting.get_or_none(user_id=user_id, id=job_posting_id)

    @staticmethod
    async def create_job_posting(
        corporate_user: CorporateUser, data: dict
    ) -> JobPosting:
        # JobPosting 생성
        job_posting = JobPosting(user=corporate_user, **data)
        await job_posting.save()
        return job_posting

    @staticmethod
    async def update_job_posting(
        job_posting: JobPosting, updated_data: dict
    ) -> JobPosting:
        # 업데이트할 필드를 순회하며 값을 변경
        for field, value in updated_data.items():
            setattr(job_posting, field, value)
        await job_posting.save()
        return job_posting

    @staticmethod
    async def delete_job_posting(job_posting: JobPosting) -> None:
        # JobPosting 삭제
        await job_posting.delete()
