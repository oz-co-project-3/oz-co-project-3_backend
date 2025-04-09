from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.freeboard_schemas import (FreeBoardCreateUpdate,
                                           FreeBoardResponse)

router = APIRouter(prefix="api/free-board/", tags=["FreeBoard"])


@router.post(
    "/",
    response_model=FreeBoardResponse,
    status_code=status.HTTP_201_CREATED,
    summary="자유게시판 글 생성",
    description="""
    - `400` `code`:`required_field` 필수 필드 누락\n
    - `401` `code`:`auth_required` 인증이 필요합니다.\n
    - `401` `code`:`invalid_token` 유효하지 않은 토큰입니다.\n
    """,
)
async def create_free_board(
    data: FreeBoardCreateUpdate,
    user: User,
):
    board = await create_free_board(data, user)
    return board
