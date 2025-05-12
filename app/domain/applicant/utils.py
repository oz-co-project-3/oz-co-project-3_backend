from app.domain.applicant.schema import ApplicantResponse
from app.domain.job_posting.models import JobPosting
from app.domain.resume.models import Resume


async def format_applicant_response(applicant) -> ApplicantResponse:
    """지원자 응답 데이터 포맷팅"""
    job_posting = (
        applicant.job_posting if isinstance(applicant.job_posting, JobPosting) else None
    )
    resume = await Resume.filter(id=applicant.resume_id).first()
    resume_data = {
        "id": resume.id if resume else None,
        "title": resume.title if resume else "",
        "name": resume.name if resume else "",
        "email": resume.email if resume else "",
    }

    return ApplicantResponse(
        id=applicant.id,
        job_posting_id=applicant.job_posting_id,
        resume=resume_data,
        user_id=applicant.user_id,
        status=applicant.status,
        memo=applicant.memo,
        created_at=applicant.created_at,
        updated_at=applicant.updated_at,
        title=job_posting.title if job_posting else "",
        company=job_posting.company if job_posting else "",
        position=job_posting.position if job_posting else "",
        deadline=job_posting.deadline if job_posting else "",
        location=job_posting.location if job_posting else "",
        image_url=job_posting.image_url if job_posting else "",
    )
