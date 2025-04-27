from app.exceptions.base_exceptions import CustomException


class CommentNotFoundException(CustomException):
    def __init__(self):
        super().__init__(
            status_code=404, code="comment_not_found", error="존재하지 않는 댓글입니다."
        )
