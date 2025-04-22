from typing import Any

from app.domain.comment.models import Comment


async def create_comment_by_id(comment: Any, id, current_user):
    return await Comment.create(**comment.dict(), free_board_id=id, user=current_user)


async def get_comments_query(id):
    return await Comment.filter(free_board_id=id).all()


async def get_comment_query(id):
    return await Comment.filter(pk_id=id).select_related("user").first()


async def patch_comment_by_id(comment, patch_comment):
    comment.content = patch_comment.content
    await comment.save()
    return comment


async def delete_comment_by_id(comment):
    await comment.delete()
