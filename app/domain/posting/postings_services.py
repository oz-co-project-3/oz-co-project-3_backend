from tortoise.expressions import Q

from app.domain.job_posting.job_posting_models import Applicants, JobPosting
from app.domain.posting.postings_schemas import ApplicantCreateUpdateSchema
from app.domain.resume.resume_models import Resume
from app.domain.user.user_models import BaseUser
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

    # 검색 키워드 처리 (제목 + 회사명)
    if search_keyword:
        query = query.filter(
            Q(title__icontains=search_keyword)
            | Q(company__icontains=search_keyword)
            | Q(summary__icontains=search_keyword)
            | Q(position__icontains=search_keyword)
            | Q(location__icontains=search_keyword)
        )

    # 필터 조건 처리
    if filter_type and filter_keyword:
        if filter_type == "location":
            query = query.filter(location__icontains=filter_keyword)
        elif filter_type == "view_count":
            try:
                count = int(filter_keyword)
                query = query.filter(view_count__gte=count)
            except ValueError:
                raise CustomException(
                    code="invalid_view_count",
                    error="view_count는 숫자여야 합니다.",
                    status_code=400,
                )
        elif filter_type == "employment_type":
            if filter_keyword not in ["공공", "일반"]:
                raise CustomException(
                    code="invalid_employment_type",
                    error="employment_type은 '공공' 또는 '일반'이어야 합니다.",
                    status_code=400,
                )
            query = query.filter(employment_type=filter_keyword)
        else:
            raise CustomException(
                code="invalid_filter_type", error="유효하지 않은 필터 타입입니다.", status_code=400
            )

    total = await query.count()
    start = offset * limit
    results = await query.offset(start).limit(limit).select_related("services")

    return {"total": total, "offset": offset, "limit": limit, "data": results}


async def get_posting_by_id(id: int):
    posting = await JobPosting.filter(pk=id).select_related("services").first()
    existing_posting(posting)
    return posting


async def create_posting_applicant_by_id(
    id: int, current_user: BaseUser, applicant: ApplicantCreateUpdateSchema
):
    posting = await JobPosting.filter(pk=id).select_related("services").first()
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
        "services": created_applicant.user_id,
        "status": created_applicant.status,
        "memo": created_applicant.memo,
    }


async def patch_posting_applicant_by_id(
    id: int,
    current_user: BaseUser,
    patch_applicant: ApplicantCreateUpdateSchema,
    applicant_id: int,
):
    posting = await JobPosting.filter(pk=id).select_related("services").first()
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
        "services": applicant.user_id,
        "status": applicant.status,
        "memo": applicant.memo,
    }
