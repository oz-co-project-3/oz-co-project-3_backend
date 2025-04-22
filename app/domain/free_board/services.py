from typing import Any

from app.domain.free_board.repository import (
    create_free_board_by_id,
    delete_free_board_by_id,
    get_free_board_query,
    get_free_boards_query,
    patch_free_board_by_id,
)
from app.utils.auth import check_author
from app.utils.exception import check_existing


async def create_free_board_by_id_service(free_board: Any, current_user):
    return await create_free_board_by_id(free_board, current_user)


async def get_all_free_board_service():
    """전체조회"""
    return await get_free_boards_query()


async def get_free_board_by_id_service(id: int):
    """상세조회"""
    board = await get_free_board_query(id)
    check_existing(board, "해당 게시글을 찾을 수 없습니다.", "free_board_not_found")
    return board


async def patch_free_board_by_id_service(id: int, free_board: Any, current_user: Any):
    """업데이트"""
    board = await get_free_board_query(id)
    check_existing(board, "해당 게시글을 찾을 수 없습니다.", "free_board_not_found")
    await check_author(board, current_user)
    board = await patch_free_board_by_id(board, free_board)

    return board


async def delete_free_board_by_id_service(id: int, current_user):
    """삭제"""
    board = await get_free_board_query(id)
    check_existing(board, "해당 게시글을 찾을 수 없습니다.", "free_board_not_found")
    await check_author(board, current_user)
    await delete_free_board_by_id(board)
