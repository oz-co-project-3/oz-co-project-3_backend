from app.domain.free_board.free_board_models import FreeBoard
from app.domain.free_board.freeboard_schemas import FreeBoardCreateUpdate
from app.domain.user.user_models import BaseUser
from app.utils.exception import CustomException


def existing_board(board):
    """존재하는 게시판인지 확인"""
    if not board:
        raise CustomException(
            error="해당 게시글을 찾을 수 없습니다.",
            code="free_board_not_found",
            status_code=404,
        )


def author_board(board, user):
    """작성자인지 확인하는 함수"""
    if board.user != user and not user.is_superuser:
        raise CustomException(
            error="작성자가 아닙니다.", code="permission_denied", status_code=403
        )


async def create_free_board_by_id(
    free_board: FreeBoardCreateUpdate, current_user: BaseUser
):
    return await FreeBoard.create(**free_board.model_dump(), user=current_user)


async def get_all_free_board():
    """전체조회"""
    return await FreeBoard.all().select_related("services")


async def get_free_board_by_id(id: int):
    """상세조회"""
    board = await FreeBoard.filter(pk=id).select_related("services").first()
    existing_board(board)
    return board


async def patch_free_board_by_id(
    id: int, free_board: FreeBoardCreateUpdate, current_user: BaseUser
):
    """업데이트"""
    board = await FreeBoard.filter(pk=id).select_related("services").first()
    existing_board(board)
    author_board(board, current_user)
    board.title = free_board.title
    board.content = free_board.content
    if free_board.image_url is not None:
        board.image_url = free_board.image_url

    await board.save()

    return board


async def delete_free_board_by_id(id: int, current_user: BaseUser):
    """삭제"""
    board = await FreeBoard.filter(pk=id).select_related("services").first()
    existing_board(board)
    author_board(board, current_user)
    await board.delete()
