import logging

from app.domain.job_posting.models import Applicants
from app.exceptions.auth_exceptions import PermissionDeniedException

logger = logging.getLogger(__name__)


async def check_author(obj, current_user):
    """작성자인지 검증"""
    if obj.user_id != current_user.id and "admin" not in current_user.user_type:
        logger.warning(f"[AUTH] 권한이 없습니다. user_id={current_user.id}")
        raise PermissionDeniedException()


async def check_permission(resume, current_user_id: int, seeker_user):
    # 공고들 중에서 이 이력서를 쓴 지원자 데이터 조회
    applicant = (
        await Applicants.filter(resume=resume)
        .prefetch_related("job_posting__user")
        .first()
    )

    if resume.user_id == seeker_user.id:
        return

    if applicant:
        job_posting = applicant.job_posting
        corp_user = job_posting.user  # CorporateUser
        if corp_user.user_id == current_user_id:
            return
    raise PermissionDeniedException()
