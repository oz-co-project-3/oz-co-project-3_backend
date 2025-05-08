from app.exceptions.base_exceptions import CustomException


class UnknownUserTypeException(CustomException):
    def __init__(self):
        super().__init__(
            status_code=500, code="unknown_user_type", error="알 수 없는 사용자 유형입니다."
        )


class ServerErrorException(CustomException):
    def __init__(self):
        super().__init__(
            status_code=500, code="SERVER_ERROR", error="서버 내부 오류가 발생했습니다."
        )


class ExternalApiErrorException(CustomException):
    def __init__(self):
        super().__init__(
            status_code=500, error="국세청 API 요청 실패", code="external_api_error"
        )
