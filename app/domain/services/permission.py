import logging

from app.exceptions.auth_exceptions import PermissionDeniedException

logger = logging.getLogger(__name__)


async def check_author(obj, current_user):
    """작성자인지 검증"""
    if obj.user_id != current_user.id and not current_user.is_superuser:
        logger.warning(f"[AUTH] 권한이 없습니다. user_id={current_user.id}")
        raise PermissionDeniedException()
