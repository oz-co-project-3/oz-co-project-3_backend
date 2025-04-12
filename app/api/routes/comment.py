from fastapi import APIRouter, Depends, status

from app.core.token import get_current_user
from app.models.user_models import BaseUser
from app.schemas.commnet_schemas import CommentCreateUpdateSchema
from app.services.comment_services import (
    create_comment_by_id,
    delete_comment_by_id,
    get_all_comments,
    patch_comment_by_id,
)

comment_router = APIRouter(prefix="/api/free-board/{id}/comment", tags=["FreeBoard"])


@comment_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="자유게시판 댓글 생성",
    description=(
        """
    - `400` `code`:`required_field` 필수 필드 누락\n
    - `401` `code`:`auth_required` 인증이 필요합니다.\n
    - `401` `code`:`invalid_token` 유효하지 않은 토큰입니다.\n
    """
    ),
)
async def create_comment(
    id: int,
    comment: CommentCreateUpdateSchema,
    current_user: BaseUser = Depends(get_current_user),
):
    return await create_comment_by_id(
        id=id, comment_data=comment, current_user=current_user
    )


@comment_router.get(
    "/",
    status_code=status.HTTP_200_OK,
    summary="자유게시판 조회",
    description=(
        """
    - `401` `code`:`auth_required` 인증이 필요합니다.\n
    - `401` `code`:`invalid_token` 유효하지 않은 토큰입니다.\n
    """
    ),
)
async def get_list_comments(
    id: int, current_user: BaseUser = Depends(get_current_user)
):
    return await get_all_comments(id=id)


@comment_router.patch(
    "/{comment_id}/",
    summary="자유게시판 댓글 수정",
    status_code=status.HTTP_200_OK,
    description="""
- `401` `code`:`auth_required` 인증이 필요합니다.\n
- `401` `code`:`invalid_token` 유효하지 않은 토큰입니다.\n
- `403` `code`:`permission_denied` 권한이 없습니다, 작성자가 아닙니다.\n
- `404` `code`:`comment_not_found` 존재하지 않는 자유게시판 입니다..\n
""",
)
async def patch_comment(
    comment_data: CommentCreateUpdateSchema,
    comment_id: int,
    current_user: BaseUser = Depends(get_current_user),
):
    return await patch_comment_by_id(comment_data, comment_id, current_user)


@comment_router.delete(
    "/{comment_id}/",
    status_code=status.HTTP_200_OK,
    summary="자유게시판 댓글 삭제",
    description="""
- `401` `code`:`auth_required` 인증이 필요합니다.\n
- `401` `code`:`invalid_token` 유효하지 않은 토큰입니다.\n
- `403` `code`:`permission_denied` 권한이 없습니다, 작성자가 아닙니다.\n
- `404` `code`:`comment_not_found` 존재하지 않는 자유게시판 입니다..\n
""",
)
async def delete_comment(
    comment_id: int, current_user: BaseUser = Depends(get_current_user)
):
    await delete_comment_by_id(comment_id, current_user)
    return {"message": "댓글이 삭제되었습니다."}
