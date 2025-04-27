from app.exceptions.base_exceptions import CustomException


class ResumeNotFoundException(CustomException):
    def __init__(self):
        super().__init__(
            status_code=404, code="resume_not_found", error="존재하지 않는 이력서입니다."
        )


class ResumeDeleteFailedException(CustomException):
    def __init__(self):
        super().__init__(
            status_code=500, code="resume_delete_failed", error="이력서 삭제에 실패했습니다."
        )
