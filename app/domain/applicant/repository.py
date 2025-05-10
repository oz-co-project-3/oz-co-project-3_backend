from typing import List, Optional

from app.domain.job_posting.models import Applicants, JobPosting


async def get_applicants_by_job_posting(job_posting_id: int) -> List[Applicants]:
    """특정 공고에 지원한 모든 지원자 조회 - 조회 결과가 없으면 빈 리스트 반환"""
    return (
        await Applicants.filter(job_posting_id=job_posting_id)
        .prefetch_related("resume", "user")
        .all()
    )


async def repo_get_applicants_by_corporate_user(
    corporate_user_id: int,
) -> List[Applicants]:
    """기업 사용자가 올린 모든 공고에 대한 지원자 조회 - 공고가 없으면 빈 리스트 반환"""
    if not await JobPosting.filter(user_id=corporate_user_id).exists():
        return []  # 예외 대신 빈 리스트 반환
    job_posting_ids = await JobPosting.filter(user_id=corporate_user_id).values_list(
        "id", flat=True
    )
    return (
        await Applicants.filter(job_posting_id__in=job_posting_ids)
        .prefetch_related("resume", "user", "job_posting")
        .all()
    )


async def get_applicants_by_seeker_user(user_id: int) -> List[Applicants]:
    """사용자가 지원한 모든 지원서를 조회 - 조회 결과가 없으면 빈 리스트 반환"""
    return (
        await Applicants.filter(user_id=user_id).prefetch_related("job_posting").all()
    )


async def get_applicant_by_id(applicant_id: int, user_id: int) -> Optional[Applicants]:
    """특정 지원 내역 조회 - 조회 결과가 없으면 None 반환"""
    # get_or_none() 대신 filter().first()를 사용하여 prefetch_related를 정상적으로 수행하도록 수정합니다.
    return (
        await Applicants.filter(id=applicant_id, user_id=user_id)
        .prefetch_related("job_posting")
        .first()
    )
