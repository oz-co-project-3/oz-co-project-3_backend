import logging

from app.exceptions.auth_exceptions import PermissionDeniedException

logger = logging.getLogger(__name__)


def check_superuser(current_user):
    if "admin" not in current_user.user_type:
        logger.warning(f"[AUTH] 권한 없음: 관리자 아님 (user_id={current_user.id})")
        raise PermissionDeniedException()


def check_existing(obj, exception_class):
    if not obj:
        logger.warning(f"[CHECK] 존재하지 않음: raise {exception_class.__name__}")
        raise exception_class()
