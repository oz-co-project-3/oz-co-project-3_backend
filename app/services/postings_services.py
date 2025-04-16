from tortoise.expressions import Q

from app.models.job_posting_models import Applicants, JobPosting
from app.models.resume_models import Resume
from app.models.user_models import BaseUser
from app.schemas.postings_schemas import ApplicantCreateUpdateSchema
from app.utils.exception import CustomException


def existing_applicant(applicant):
    """존재하는 게시판인지 확인"""
    if not applicant:
        raise CustomException(
            error="지원자를 찾을 수 없습니다.",
            code="applicant_not_found",
            status_code=404,
        )


def existing_posting(posting):
    """존재하는 게시판인지 확인"""
    if not posting:
        raise CustomException(
            error="공고를 찾을 수 없습니다.",
            code="posting_not_found",
            status_code=404,
        )


def author_applicant(applicant, user):
    """작성자인지 확인하는 함수"""
    if applicant.user != user and not user.is_superuser:
        raise CustomException(
            error="작성자가 아닙니다.", code="permission_denied", status_code=403
        )


async def get_all_postings(
    search_keyword: str,
    filter_type: str,
    filter_keyword: str,
    offset: int = 0,
    limit: int = 10,
):
    query = JobPosting.all()

    if search_keyword:
        query = query.filter(
            Q(title__icontains=search_keyword) | Q(company__icontains=search_keyword)
        ).select_related()

    if filter_type and filter_keyword:
        query = query.filter(**{filter_type: filter_keyword}).select_related("user")

    total = await query.count()
    results = await query.offset(offset).limit(limit).select_related("user")

    return {"total": total, "offset": offset, "limit": limit, "data": results}


async def get_posting_by_id(id: int):
    posting = await JobPosting.filter(pk=id).select_related("user").first()
    existing_posting(posting)
    return posting


async def create_posting_applicant_by_id(
    id: int, current_user: BaseUser, applicant: ApplicantCreateUpdateSchema
):
    posting = await JobPosting.filter(pk=id).select_related("user").first()
    existing_posting(posting)
    resume_obj = await Resume.get_or_none(id=applicant.resume)
    if not resume_obj:
        raise CustomException(
            status_code=404, error="이력서를 찾을 수 없습니다.", code="resume_not_found"
        )

    created_applicant = await Applicants.create(
        resume=resume_obj,
        status=applicant.status,
        memo=applicant.memo,
        job_posting=posting,
        user=current_user,
    )

    return {
        "id": created_applicant.id,
        "job_posting": created_applicant.job_posting_id,
        "resume": created_applicant.resume_id,
        "user": created_applicant.user_id,
        "status": created_applicant.status,
        "memo": created_applicant.memo,
    }


async def patch_posting_applicant_by_id(
    id: int,
    current_user: BaseUser,
    patch_applicant: ApplicantCreateUpdateSchema,
    applicant_id: int,
):
    posting = await JobPosting.filter(pk=id).select_related("user").first()
    existing_posting(posting)

    applicant = await Applicants.filter(id=applicant_id).first()
    if not applicant:
        raise CustomException(
            status_code=404, error="지원 내역이 없습니다.", code="applicant_not_found"
        )

    resume_obj = await Resume.get_or_none(id=patch_applicant.resume)
    if not resume_obj:
        raise CustomException(
            status_code=404, error="이력서를 찾지 못했습니다.", code="resume_not_found"
        )

    applicant.resume = resume_obj
    applicant.status = patch_applicant.status
    applicant.memo = patch_applicant.memo

    await applicant.save()

    return {
        "id": applicant.id,
        "job_posting": applicant.job_posting_id,
        "resume": applicant.resume_id,
        "user": applicant.user_id,
        "status": applicant.status,
        "memo": applicant.memo,
    }
