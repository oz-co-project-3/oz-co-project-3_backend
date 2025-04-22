from fastapi import HTTPException, status


class CustomException(HTTPException):
    def __init__(self, *, error: str, code: str, status_code: int = 400):
        super().__init__(status_code=status_code)
        self.error = error
        self.code = code


def check_superuser(current_user):
    if not current_user.is_superuser:
        raise CustomException(
            status_code=status.HTTP_403_FORBIDDEN,
            error="접근 권한이 없습니다",
            code="permission_denied",
        )


def check_existing(obj, error_message: str, code: str):
    if not obj:
        raise CustomException(
            error=error_message,
            code=code,
            status_code=404,
        )
