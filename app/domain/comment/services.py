from typing import Any

from app.domain.comment.models import Comment
from app.domain.comment.repository import (
    create_comment_by_id,
    delete_comment_by_id,
    get_comment_query,
    get_comments_query,
    patch_comment_by_id,
)
from app.domain.comment.schemas import CommentCreateUpdateSchema
from app.domain.user.user_models import BaseUser
from app.utils.auth import check_author
from app.utils.exception import check_existing


async def create_comment_by_id_service(
    comment_data: Any,
    id: int,
    current_user: Any,
):
    return await create_comment_by_id(comment_data, id, current_user)


async def get_all_comments_service(
    id: int,
):
    return await get_comments_query(id)


async def patch_comment_by_id_service(
    comment_data: CommentCreateUpdateSchema,
    id: int,
    current_user: BaseUser,
):
    comment = await get_comment_query(id)
    check_existing(comment, "해당 댓글을 찾을 수 없습니다.", "comment_not_found")
    await check_author(comment, current_user)
    comment = await patch_comment_by_id(comment, comment_data)

    return comment


async def delete_comment_by_id_service(
    id: int,
    current_user: BaseUser,
):
    comment = await get_comment_query(id)
    check_existing(comment, "해당 댓글을 찾을 수 없습니다.", "comment_not_found")

    await delete_comment_by_id(comment)
