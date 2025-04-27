from app.exceptions.base_exceptions import CustomException


class InvalidCodeException(CustomException):
    def __init__(self):
        super().__init__(
            status_code=400, code="invalid_code", error="잘못된 code이거나 만료된 code입니다."
        )


class KakaoApiErrorException(CustomException):
    def __init__(self):
        super().__init__(status_code=500, code="kakao_api_error", error="카카오 서버 응답 실패")


class KakaoEmailRequiredException(CustomException):
    def __init__(self):
        super().__init__(
            status_code=400, code="kakao_email_required", error="카카오 계정에 이메일이 없습니다."
        )


class NaverEmailRequiredException(CustomException):
    def __init__(self):
        super().__init__(
            status_code=400, code="naver_email_required", error="네이버 계정에 이메일이 없습니다."
        )
