from typing import Optional

from tortoise.expressions import Q

from app.domain.job_posting.job_posting_models import Applicants, JobPosting
from app.domain.resume.resume_models import Resume


async def get_postings_query(
    search_keyword: Optional[str] = "",
    location: Optional[str] = "",
    employment_type: Optional[str] = "",
    position: Optional[str] = "",
    career: Optional[str] = "",
    education: Optional[str] = "",
    view_count: Optional[int] = 0,
):
    query = JobPosting.all().select_related("user")

    # 🔍 검색 키워드 (제목, 회사, 요약, 포지션, 위치)
    if search_keyword:
        query = query.filter(
            Q(title__icontains=search_keyword)
            | Q(company__icontains=search_keyword)
            | Q(summary__icontains=search_keyword)
            | Q(position__icontains=search_keyword)
            | Q(location__icontains=search_keyword)
        )

    if location:
        query = query.filter(location__icontains=location)

    if employment_type:
        types = [t.strip() for t in employment_type.split(",")]
        allowed = ["공공", "일반"]
        query = query.filter(employment_type__in=[t for t in types if t in allowed])

    if position:
        keywords = [k.strip() for k in position.split(",")]
        q = Q()
        for k in keywords:
            q |= Q(position__icontains=k)
        query = query.filter(q)

    if career:
        options = ["신입", "경력직", "경력무관"]
        query = query.filter(
            career__in=[k.strip() for k in career.split(",") if k.strip() in options]
        )

    if education:
        allowed = [
            "학력무관",
            "고등학교 졸업",
            "대학교 졸업(2,3년제)",
            "대학교 졸업(4년제)",
            "대학원 석사 졸업",
            "대학원 박사 졸업",
        ]
        query = query.filter(
            education__in=[
                e.strip() for e in education.split(",") if e.strip() in allowed
            ]
        )

    if view_count and view_count > 0:
        query = query.filter(view_count__gte=view_count)

    return query


async def get_posting_query(id):
    return await JobPosting.filter(pk=id).select_related("user").first()


async def get_resume_query(resume_id):
    return await Resume.filter(id=resume_id).select_related("user").first()


async def get_applicant_query(id):
    return await Applicants.filter(pk=id).select_related("user").first()


async def get_resume_id_by_applicant_id(applicant_id: int):
    applicant = await Applicants.filter(id=applicant_id).only("resume_id").first()
    return applicant.resume_id if applicant else None


async def create_posting_applicant(applicant, current_user, resume, posting):
    applicant = await Applicants.create(
        resume=resume,
        status=applicant.status,
        memo=applicant.memo,
        job_posting=posting,
        user=current_user,
    )
    return {
        "id": applicant.id,
        "job_posting_id": applicant.job_posting_id,
        "resume_id": applicant.resume_id,
        "user_id": applicant.user_id,
        "status": applicant.status,
        "memo": applicant.memo,
    }


async def patch_posting_applicant_by_id(applicant, resume, patch_applicant):
    applicant.resume = resume
    applicant.status = patch_applicant.status
    applicant.memo = patch_applicant.memo

    await applicant.save()

    return {
        "id": applicant.id,
        "job_posting_id": applicant.job_posting_id,
        "resume_id": applicant.resume_id,
        "user_id": applicant.user_id,
        "status": applicant.status,
        "memo": applicant.memo,
    }
