from app.exceptions.base_exceptions import CustomException


class SuccessReviewNotFoundException(CustomException):
    def __init__(self):
        super().__init__(
            status_code=404, code="success_review_not_found", error="존재하지 않는 성공 후기입니다."
        )
