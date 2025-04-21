from typing import List

from fastapi import APIRouter, Depends, status

from app.core.token import get_current_user
from app.domain.free_board.freeboard_schemas import (
    FreeBoardCreateUpdate,
    FreeBoardResponse,
)
from app.domain.free_board.freeboard_services import (
    create_free_board_by_id,
    delete_free_board_by_id,
    get_all_free_board,
    get_free_board_by_id,
    patch_free_board_by_id,
)
from app.domain.user.user_models import BaseUser

free_board_router = APIRouter(prefix="/api/free-board", tags=["FreeBoard"])


@free_board_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="자유게시판 글 생성",
    description=(
        """
    - `400` `code`:`required_field` 필수 필드 누락\n
    - `401` `code`:`auth_required` 인증이 필요합니다.\n
    - `401` `code`:`invalid_token` 유효하지 않은 토큰입니다.\n
    """
    ),
)
async def create_free_board(
    free_board: FreeBoardCreateUpdate,
    current_user: BaseUser = Depends(get_current_user),
):
    return await create_free_board_by_id(free_board, current_user)


@free_board_router.get(
    "/",
    response_model=List[FreeBoardResponse],
    status_code=status.HTTP_200_OK,
    summary="자유게시판 전체 조회",
    description="""
    - `401` `code`:`auth_required` 인증이 필요합니다.\n
    - `401` `code`:`invalid_token` 유효하지 않은 토큰입니다.\n
    """,
)
async def get_list_free_board(current_user: BaseUser = Depends(get_current_user)):
    return await get_all_free_board()


@free_board_router.get(
    "/{id}/",
    response_model=FreeBoardResponse,
    status_code=status.HTTP_200_OK,
    summary="자유게시판 상세 조회",
    description="""
    - `401` `code`:`auth_required` 인증이 필요합니다.\n
    - `401` `code`:`invalid_token` 유효하지 않은 토큰입니다.\n
    - `404` `code`:`free_board_not_found` 존재하지 않는 자유게시판 입니다..\n
    """,
)
async def get_detail_free_board(
    id: int, current_user: BaseUser = Depends(get_current_user)
):
    return await get_free_board_by_id(id)


@free_board_router.patch(
    "/{id}/",
    response_model=FreeBoardResponse,
    summary="자유게시판 수정",
    status_code=status.HTTP_200_OK,
    description="""
- `401` `code`:`auth_required` 인증이 필요합니다.\n
- `401` `code`:`invalid_token` 유효하지 않은 토큰입니다.\n
- `403` `code`:`permission_denied` 권한이 없습니다, 작성자가 아닙니다.\n
- `404` `code`:`free_board_not_found` 존재하지 않는 자유게시판 입니다..\n
""",
)
async def patch_free_board(
    id: int,
    free_board: FreeBoardCreateUpdate,
    current_user: BaseUser = Depends(get_current_user),
):
    return await patch_free_board_by_id(id, free_board, current_user)


@free_board_router.delete(
    "/{id}/",
    status_code=status.HTTP_200_OK,
    summary="자유게시판 삭제",
    description="""
- `401` `code`:`auth_required` 인증이 필요합니다.\n
- `401` `code`:`invalid_token` 유효하지 않은 토큰입니다.\n
- `403` `code`:`permission_denied` 권한이 없습니다, 작성자가 아닙니다.\n
- `404` `code`:`free_board_not_found` 존재하지 않는 자유게시판 입니다..\n
""",
)
async def delete_free_board(
    id: int,
    current_user: BaseUser = Depends(get_current_user),
):
    await delete_free_board_by_id(id, current_user)
    return {"message": "삭제가 완료되었습니다."}
