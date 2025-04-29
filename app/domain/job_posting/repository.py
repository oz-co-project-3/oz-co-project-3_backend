from app.domain.job_posting.models import JobPosting
from app.domain.user.models import CorporateUser
from app.exceptions.free_board_exceptions import CompanyNotFoundException
from app.exceptions.job_posting_exceptions import NotificationNotFoundException


class JobPostingRepository:
    @staticmethod
    async def get_job_posting_by_id(job_posting_id: int) -> JobPosting:
        job_posting = await JobPosting.get_or_none(id=job_posting_id)
        if not job_posting:
            raise NotificationNotFoundException()
        return job_posting

    @staticmethod
    async def get_job_postings_by_user(
        corporate_user: CorporateUser,
    ) -> list[JobPosting]:
        return await JobPosting.filter(user=corporate_user).all()

    @staticmethod
    async def get_job_posting_by_company_and_id(
        user_id: int, job_posting_id: int
    ) -> JobPosting:
        job_posting = await JobPosting.get_or_none(user_id=user_id, id=job_posting_id)
        if not job_posting:
            raise NotificationNotFoundException()
        return job_posting

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
