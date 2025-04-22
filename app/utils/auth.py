from app.utils.exception import CustomException


async def check_author(obj, current_user):
    """작성자인지 검증"""
    if obj.user_id != current_user.id and not current_user.is_superuser:
        raise CustomException(
            error="해당 작업을 수행할 권한이 없습니다.",
            code="permission_denied",
            status_code=403,
        )
