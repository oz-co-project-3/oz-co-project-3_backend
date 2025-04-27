from app.exceptions.base_exceptions import CustomException


class JobPostingNotFoundException(CustomException):
    def __init__(self):
        super().__init__(
            status_code=404, code="job_posting_not_found", error="공고를 찾을 수 없습니다."
        )


class NotificationNotFoundException(CustomException):
    def __init__(self):
        super().__init__(
            status_code=404, code="notification_not_found", error="등록된 공고를 찾을 수 없습니다."
        )
