from typing import Optional

from tortoise.query_utils import Prefetch

from app.domain.job_posting.models import JobPosting, RejectPosting, StatusEnum


async def get_all_job_postings_query(
    search_type: str,
    search_keyword: str,
    status: Optional[StatusEnum] = None,
):
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

    return await queryset


async def get_job_posting_by_id_query(id: int) -> Optional[JobPosting]:
    return (
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


async def patch_job_posting_by_id(posting, patch_job_posting):
    posting.status = patch_job_posting.status
    await posting.save()

    return posting


async def delete_job_posting_by_id(posting):
    await posting.delete()


async def create_reject_posting_by_id(reject_posting, job_posting, user):
    return await RejectPosting.create(
        **reject_posting.dict(), job_posting=job_posting, user=user
    )
