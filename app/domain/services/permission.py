from app.exceptions.auth_exceptions import PermissionDeniedException


async def check_author(obj, current_user):
    """작성자인지 검증"""
    if obj.user_id != current_user.id and not current_user.is_superuser:
        raise PermissionDeniedException()
