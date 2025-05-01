from typing import List

from app.domain.job_posting.models import JobPosting
from app.domain.user.user_models import CorporateUser
from app.exceptions.job_posting_exceptions import NotificationNotFoundException


class JobPostingRepository:
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
    async def get_job_posting_by_id(job_posting_id: int) -> JobPosting:
        return await JobPostingRepository._get_or_raise(JobPosting, id=job_posting_id)

    @staticmethod
    async def get_job_postings_by_user(
        corporate_user: CorporateUser,
    ) -> List[JobPosting]:
        return await JobPosting.filter(user=corporate_user).all()

    @staticmethod
    async def get_job_posting_by_company_and_id(
        user_id: int, job_posting_id: int
    ) -> JobPosting:
        return await JobPostingRepository._get_or_raise(
            JobPosting, user_id=user_id, id=job_posting_id
        )

    @staticmethod
    async def create_job_posting(
        corporate_user: CorporateUser, data: dict
    ) -> JobPosting:
        job_posting = JobPosting(user=corporate_user, **data)
        await job_posting.save()
        return job_posting

    @staticmethod
    async def update_job_posting(
        job_posting: JobPosting, updated_data: dict
    ) -> JobPosting:
        for field, value in updated_data.items():
            setattr(job_posting, field, value)
        await job_posting.save()
        return job_posting

    @staticmethod
    async def delete_job_posting(job_posting: JobPosting) -> None:
        await job_posting.delete()
