from starlette import status

from app.models.job_posting_models import JobPosting
from app.utils.exception import CustomException


def existing_posting(post):
    if not post:
        raise CustomException(
            error="해당 공고를 찾을 수 없습니다.",
            code="job_posting_not_found",
            status_code=404,
        )


async def get_all_job_posting():
    return await JobPosting.all()


async def get_job_posting_by_id(id: int):
    post = await JobPosting.filter(pk=id).first()
    existing_posting(post)
    return post
