from typing import Any

from app.domain.free_board.models import FreeBoard


async def create_free_board_by_id(free_board: Any, current_user):
    return await FreeBoard.create(**free_board.model_dump(), user=current_user)


async def get_free_boards_query():
    return await FreeBoard.all().select_related("user")


async def get_free_board_query(id: int):
    return await FreeBoard.filter(pk=id).select_related("user").first()


async def patch_free_board_by_id(board, patch_free_board):
    board.title = patch_free_board.title
    board.content = patch_free_board.content

    if patch_free_board.image_url is not None:
        board.image_url = patch_free_board.image_url

    await board.save()

    return board


async def delete_free_board_by_id(board):
    await board.delete()
