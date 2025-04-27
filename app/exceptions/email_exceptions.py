from app.exceptions.base_exceptions import CustomException


class EmailAlreadyVerifiedException(CustomException):
    def __init__(self):
        super().__init__(
            status_code=400, code="already_verified", error="이미 인증된 계정입니다."
        )


class InvalidVerificationCodeException(CustomException):
    def __init__(self):
        super().__init__(
            status_code=400, code="invalid_verification_code", error="유효하지 않은 인증 코드입니다."
        )


class EmailNotFoundException(CustomException):
    def __init__(self):
        super().__init__(
            status_code=404, code="user_not_found", error="가입된 이메일을 찾을 수 없습니다."
        )


class DuplicateEmailException(CustomException):
    def __init__(self):
        super().__init__(status_code=400, code="duplicate_email", error="중복된 이메일입니다.")
