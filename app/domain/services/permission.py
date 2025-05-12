import logging

from app.domain.job_posting.models import Applicants
from app.exceptions.auth_exceptions import PermissionDeniedException

logger = logging.getLogger(__name__)


async def check_author(obj, current_user):
    """작성자인지 검증"""
    # 관리자는 통과
    if "admin" in current_user.user_type:
        return

    # 작성자는 통과
    if obj.user_id == current_user.id:
        return

    # 제출된 이력서의 경우: 지원자인 경우 통과
    is_applicant = await Applicants.filter(
        resume_id=obj.id, user_id=current_user.id
    ).exists()
    if is_applicant:
        return

    logger.warning(f"[AUTH] 권한이 없습니다. user_id={current_user.id}")
    raise PermissionDeniedException()
