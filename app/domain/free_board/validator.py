from app.utils.exception import CustomException


def author_board(board, user):
    """작성자인지 확인하는 함수"""

    if board.user != user and not user.is_superuser:
        raise CustomException(
            error="작성자가 아닙니다.", code="permission_denied", status_code=403
        )
