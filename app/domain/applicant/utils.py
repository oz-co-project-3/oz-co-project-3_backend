from app.domain.applicant.schema import ApplicantResponse


def format_applicant_response(applicant) -> ApplicantResponse:
    """지원자 응답 데이터 포맷팅"""
    return ApplicantResponse(
        id=applicant.id,
        job_posting_id=applicant.job_posting_id,
        resume_id=applicant.resume_id,
        user_id=applicant.user_id,
        status=applicant.status,
        memo=applicant.memo,
        created_at=applicant.created_at,
        updated_at=applicant.updated_at,
        job_title=applicant.job_posting.title,
        company_name=applicant.job_posting.company,
        position=applicant.job_posting.position,
        deadline=applicant.job_posting.deadline,
    )
