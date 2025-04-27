from app.exceptions.base_exceptions import CustomException


class AuthRequiredException(CustomException):
    def __init__(self):
        super().__init__(status_code=401, code="auth_required", error="인증이 필요합니다.")


class InvalidTokenException(CustomException):
    def __init__(self):
        super().__init__(status_code=401, code="invalid_token", error="유효하지 않은 토큰입니다.")


class PermissionDeniedException(CustomException):
    def __init__(self):
        super().__init__(status_code=403, code="permission_denied", error="권한이 없습니다.")


class InvalidPasswordException(CustomException):
    def __init__(self):
        super().__init__(
            status_code=400,
            code="invalid_password",
            error="비밀번호는 8자 이상, 특수문자를 포함해야 합니다.",
        )


class PasswordMismatchException(CustomException):
    def __init__(self):
        super().__init__(
            status_code=400, code="password_mismatch", error="비밀번호와 확인이 일치하지 않습니다."
        )


class InvalidCredentialsException(CustomException):
    def __init__(self):
        super().__init__(
            status_code=400, code="invalid_credentials", error="이메일 또는 비밀번호가 일치하지 않습니다."
        )


class ExpiredTokenException(CustomException):
    def __init__(self):
        super().__init__(status_code=401, code="expired_token", error="토큰이 만료되었습니다.")


class InvalidRefreshTokenException(CustomException):
    def __init__(self):
        super().__init__(
            status_code=401, code="invalid_refresh_token", error="유효하지 않은 리프레시 토큰입니다."
        )


class ExpiredRefreshTokenException(CustomException):
    def __init__(self):
        super().__init__(
            status_code=401, code="expired_refresh_token", error="만료된 리프레시 토큰입니다."
        )
