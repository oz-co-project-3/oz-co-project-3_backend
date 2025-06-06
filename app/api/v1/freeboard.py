import logging
from typing import List

from fastapi import APIRouter, Depends, Path, status

from app.core.token import get_current_user
from app.domain.free_board.schemas import FreeBoardCreateUpdate, FreeBoardResponseDTO
from app.domain.free_board.services import (
    create_free_board_by_id_service,
    delete_free_board_by_id_service,
    get_all_free_board_service,
    get_free_board_by_id_service,
    patch_free_board_by_id_service,
)
from app.domain.user.models import BaseUser

logger = logging.getLogger(__name__)

free_board_router = APIRouter(prefix="/api/free-board", tags=["FreeBoard"])


@free_board_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=FreeBoardResponseDTO,
    summary="자유게시판 글 생성",
    description=(
        """
`400` `code`:`required_field` 필수 필드 누락\n
`401` `code`:`auth_required` 인증이 필요합니다.\n
`401` `code`:`invalid_token` 유효하지 않은 토큰입니다.\n
`422` : Unprocessable Entity
"""
    ),
)
async def create_free_board(
    free_board: FreeBoardCreateUpdate,
    current_user: BaseUser = Depends(get_current_user),
):
    logger.info(f"[API] 자유게시판 글 생성 요청: user_id={current_user.id}")
    return await create_free_board_by_id_service(free_board, current_user)


@free_board_router.get(
    "/",
    response_model=List[FreeBoardResponseDTO],
    status_code=status.HTTP_200_OK,
    summary="자유게시판 전체 조회",
    description="""
`401` `code`:`auth_required` 인증이 필요합니다.\n
`401` `code`:`invalid_token` 유효하지 않은 토큰입니다.\n
    """,
)
async def get_list_free_board(current_user: BaseUser = Depends(get_current_user)):
    logger.info(f"[API] 자유게시판 전체 조회 요청: user_id={current_user.id}")
    return await get_all_free_board_service()


@free_board_router.get(
    "/{id}/",
    response_model=FreeBoardResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="자유게시판 상세 조회",
    description="""
`401` `code`:`auth_required` 인증이 필요합니다.\n
`401` `code`:`invalid_token` 유효하지 않은 토큰입니다.\n
`404` `code`:`free_board_not_found` 존재하지 않는 자유게시판 입니다..\n
`422` : Unprocessable Entity
    """,
)
async def get_detail_free_board(
    current_user: BaseUser = Depends(get_current_user),
    id: int = Path(
        ..., gt=0, le=2147483647, description="free_board ID (1 ~ 2147483647)"
    ),
):
    logger.info(f"[API] 자유게시판 상세 조회 요청: user_id={current_user.id}, board_id={id}")
    return await get_free_board_by_id_service(id)


@free_board_router.patch(
    "/{id}/",
    response_model=FreeBoardResponseDTO,
    summary="자유게시판 수정",
    status_code=status.HTTP_200_OK,
    description="""
`401` `code`:`auth_required` 인증이 필요합니다.\n
`401` `code`:`invalid_token` 유효하지 않은 토큰입니다.\n
`403` `code`:`permission_denied` 권한이 없습니다, 작성자가 아닙니다.\n
`404` `code`:`free_board_not_found` 존재하지 않는 자유게시판 입니다..\n
`422` : Unprocessable Entity
""",
)
async def patch_free_board(
    free_board: FreeBoardCreateUpdate,
    current_user: BaseUser = Depends(get_current_user),
    id: int = Path(
        ..., gt=0, le=2147483647, description="free_board ID (1 ~ 2147483647)"
    ),
):
    logger.info(f"[API] 자유게시판 수정 요청: user_id={current_user.id}, board_id={id}")
    return await patch_free_board_by_id_service(id, free_board, current_user)


@free_board_router.delete(
    "/{id}/",
    status_code=status.HTTP_200_OK,
    summary="자유게시판 삭제",
    description="""
`401` `code`:`auth_required` 인증이 필요합니다.\n
`401` `code`:`invalid_token` 유효하지 않은 토큰입니다.\n
`403` `code`:`permission_denied` 권한이 없습니다, 작성자가 아닙니다.\n
`404` `code`:`free_board_not_found` 존재하지 않는 자유게시판 입니다..\n
`422` : Unprocessable Entity
""",
)
async def delete_free_board(
    current_user: BaseUser = Depends(get_current_user),
    id: int = Path(
        ..., gt=0, le=2147483647, description="free_board ID (1 ~ 2147483647)"
    ),
):
    logger.info(f"[API] 자유게시판 삭제 요청: user_id={current_user.id}, board_id={id}")
    await delete_free_board_by_id_service(id, current_user)
    return {"message": "삭제가 완료되었습니다."}
