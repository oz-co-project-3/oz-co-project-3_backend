from app.domain.user.repository import create_base_user
from app.exceptions.base_exceptions import CustomException


class UserNotFoundException(CustomException):
    def __init__(self):
        super().__init__(status_code=404, code="user_not_found", error="유저를 찾을 수 없습니다.")


class InvalidPhoneException(CustomException):
    def __init__(self):
        super().__init__(
            status_code=400, code="invalid_phone", error="올바른 전화번호 형식을 입력해주세요."
        )


class PasswordInvalidException(CustomException):
    def __init__(self):
        super().__init__(
            status_code=400,
            code="invalid_password",
            error="비밀번호는 8자 이상이며 특수 문자를 포함해야 합니다.",
        )


class PasswordPreviouslyUsedException(CustomException):
    def __init__(self):
        super().__init__(
            status_code=400,
            code="password_previously_used",
            error="이전에 사용했던 비밀번호는 사용할 수 없습니다.",
        )


class UnverifiedOrInactiveAccountException(CustomException):
    def __init__(self):
        super().__init__(
            status_code=403,
            code="unverified_or_inactive_account",
            error="이메일 인증이 완료되지 않았거나 계정이 활성화되지 않았습니다.",
        )


class InvalidBusinessNumberException(CustomException):
    def __init__(self):
        super().__init__(
            status_code=400,
            code="invalid_business_number",
            error="국세청에 등록되지 않은 사업자등록번호입니다.",
        )


class AlreadyBusinessUserException(CustomException):
    def __init__(self):
        super().__init__(
            status_code=400,
            code="already_business_user",
            error="이미 기업회원으로 등록된 사용자입니다.",
        )
