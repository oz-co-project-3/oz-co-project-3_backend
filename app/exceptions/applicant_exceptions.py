from app.exceptions.base_exceptions import CustomException


class ApplicantNotFoundException(CustomException):
    def __init__(self):
        super().__init__(
            status_code=404, code="applicant_not_found", error="지원자를 찾을 수 없습니다."
        )
