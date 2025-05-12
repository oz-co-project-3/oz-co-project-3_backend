from typing import Any, Optional

from tortoise.expressions import Q

from app.domain.job_posting.models import ApplicantEnum, Applicants, JobPosting
from app.domain.posting.schemas import (
    JobPostingResponseDTO,
    PaginatedJobPostingsResponseDTO,
)
from app.domain.resume.models import Resume
from app.domain.user.models import SeekerUser


async def get_postings_query(
    search_keyword: Optional[str] = "",
    location: Optional[str] = "",
    employment_type: Optional[str] = "",
    position: Optional[str] = "",
    career: Optional[str] = "",
    education: Optional[str] = "",
    view_count: Optional[int] = 0,
    employ_method: Optional[str] = "",
    current_user: Optional[Any] = None,
    offset: Optional[int] = 0,
    limit: Optional[int] = 100,
):
    bookmarked_ids = []
    if current_user:
        seeker = await SeekerUser.get_or_none(user=current_user).prefetch_related(
            "interests_posting"
        )
        if seeker:
            bookmarked_ids = await seeker.interests_posting.all().values_list(
                "id", flat=True
            )
    query = (
        JobPosting.filter(status__in=["모집중", "마감 임박", "모집 종료"])
        .select_related("user")
        .all()
    )

    # 검색 키워드 (제목, 회사, 요약, 포지션, 위치, 고용 형태)
    if search_keyword:
        query = query.filter(
            Q(title__icontains=search_keyword)
            | Q(company__icontains=search_keyword)
            | Q(summary__icontains=search_keyword)
            | Q(position__icontains=search_keyword)
            | Q(location__icontains=search_keyword)
        )

    if location:
        locations = [l.strip() for l in location.split(",") if l.strip()]
        q = Q()
        for loc in locations:
            q |= Q(location__icontains=loc)
        query = query.filter(q)

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

    if employ_method:
        methods = [m.strip() for m in employ_method.split(",")]
        allowed_methods = ["정규직", "계약직", "일용직", "프리랜서", "파견직"]
        query = query.filter(
            employ_method__in=[m for m in methods if m in allowed_methods]
        )

    total = await query.count()
    start = offset * limit
    postings = await query.offset(start).limit(limit)
    result = []
    for post in postings:
        dto = JobPostingResponseDTO.from_orm(post)
        dto.is_bookmarked = post.id in bookmarked_ids
        result.append(dto.model_dump())

    return PaginatedJobPostingsResponseDTO(
        total=total,
        offset=offset,
        limit=limit,
        data=result,
    )


async def get_posting_query(id):
    posting = await JobPosting.filter(pk=id).select_related("user").first()

    if posting:
        posting.view_count += 1
        await posting.save()

    return posting


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
    return applicant


async def patch_posting_applicant_by_id(applicant, resume, patch_applicant):
    applicant.resume = resume
    applicant.status = patch_applicant.status
    applicant.memo = patch_applicant.memo

    if patch_applicant.status == ApplicantEnum.Cancelled:
        await applicant.delete()
        return {"message": "지원이 취소되었습니다"}

    await applicant.save()

    applicant = (
        await Applicants.filter(id=applicant.id)
        .select_related("job_posting", "resume", "user")
        .first()
    )

    return applicant
