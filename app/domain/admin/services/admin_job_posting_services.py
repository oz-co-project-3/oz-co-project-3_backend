from fastapi import status
from tortoise.query_utils import Prefetch

from app.domain.admin.schemas.admin_job_posting_schemas import (
    JobPostingUpdateSchema,
    RejectPostingCreateSchema,
    StatusEnum,
)
from app.domain.job_posting.job_posting_models import JobPosting, RejectPosting
from app.domain.services.verification import CustomException, check_superuser
from app.domain.user.user_models import BaseUser


def check_job_posting(job_posting: JobPosting):
    if not job_posting:
        raise CustomException(
            status_code=status.HTTP_404_NOT_FOUND,
            code="job_posting_not_found",
            error="해당 이력서를 찾지 못했습니다.",
        )


async def get_all_job_postings(
    current_user: BaseUser,
    search_type: str,
    search_keyword: str,
    status: StatusEnum,
):
    check_superuser(current_user)

    queryset = (
        JobPosting.all()
        .select_related("user")
        .prefetch_related(
            Prefetch(
                "reject_postings",
                queryset=RejectPosting.all().select_related("user"),
            )
        )
    )

    if search_type == "company":
        queryset = queryset.filter(company__icontains=search_keyword)
    elif search_type == "employment_type":
        queryset = queryset.filter(employment_type__icontains=search_keyword)

    if status:
        queryset = queryset.filter(status=status)

    job_postings = await queryset

    return job_postings


async def get_job_posting_by_id(
    id: int,
    current_user: BaseUser,
):
    check_superuser(current_user)

    posting = (
        await JobPosting.filter(pk=id)
        .select_related("user")
        .prefetch_related(
            Prefetch(
                "reject_postings",
                queryset=RejectPosting.all().select_related("user"),
            )
        )
        .first()
    )

    check_job_posting(posting)

    return posting


async def patch_job_posting_by_id(
    id: int,
    patch_job_posting: JobPostingUpdateSchema,
    current_user: BaseUser,
):
    check_superuser(current_user)
    job_posting = await get_job_posting_by_id(id, current_user)

    job_posting.status = patch_job_posting.status
    await job_posting.save()

    return job_posting


async def delete_job_posting_by_id(
    id: int,
    current_user: BaseUser,
):
    check_superuser(current_user)
    job_posting = await get_job_posting_by_id(id, current_user)
    await job_posting.delete()


async def create_reject_posting_by_id(
    id: int, current_user: BaseUser, reject_posting: RejectPostingCreateSchema
):
    check_superuser(current_user)
    job_posting = await get_job_posting_by_id(id, current_user)
    reject_posting = await RejectPosting.create(
        **reject_posting.dict(), job_posting=job_posting, user=current_user
    )

    await reject_posting.save()
    return reject_posting
