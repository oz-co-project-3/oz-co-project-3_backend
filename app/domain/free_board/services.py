from typing import Any, List

from app.domain.free_board.repository import (
    create_free_board_by_id,
    delete_free_board_by_id,
    get_free_board_query,
    get_free_boards_query,
    patch_free_board_by_id,
)
from app.domain.free_board.schemas import FreeBoardResponseDTO
from app.domain.services.permission import check_author
from app.domain.services.verification import check_existing


async def create_free_board_by_id_service(
    free_board: Any, current_user
) -> FreeBoardResponseDTO:
    return await create_free_board_by_id(free_board, current_user)


async def get_all_free_board_service() -> List[FreeBoardResponseDTO]:
    """전체조회"""
    return await get_free_boards_query()


async def get_free_board_by_id_service(id: int) -> FreeBoardResponseDTO:
    """상세조회"""
    board = await get_free_board_query(id)
    check_existing(board, "해당 게시글을 찾을 수 없습니다.", "free_board_not_found")
    return board


async def patch_free_board_by_id_service(
    id: int, free_board: Any, current_user: Any
) -> FreeBoardResponseDTO:
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
