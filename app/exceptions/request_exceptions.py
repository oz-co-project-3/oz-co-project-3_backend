from app.exceptions.base_exceptions import CustomException


class RequiredFieldException(CustomException):
    def __init__(self):
        super().__init__(
            status_code=400, code="required_field", error="필수 필드가 누락되었습니다."
        )
