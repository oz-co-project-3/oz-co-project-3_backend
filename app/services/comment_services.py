from app.models.comment_models import Comment
from app.models.user_models import BaseUser
from app.schemas.commnet_schemas import CommentCreateUpdateSchema
from app.utils.exception import CustomException


def existing_comment(comment):
    """존재하는 게시판인지 확인"""
    if not comment:
        raise CustomException(
            error="해당 댓글을 찾을 수 없습니다.",
            code="comment_not_found",
            status_code=404,
        )


def author_comment(comment, user):
    """작성자인지 확인하는 함수"""
    if comment.user != user and not user.is_superuser:
        raise CustomException(
            error="작성자가 아닙니다.", code="permission_denied", status_code=403
        )


async def create_comment_by_id(
    comment_data: CommentCreateUpdateSchema,
    id: int,
    current_user: BaseUser,
):
    return await Comment.create(
        **comment_data.dict(), free_board_id=id, user=current_user
    )


async def get_all_comments(
    id: int,
):
    return await Comment.filter(free_board_id=id).all()


async def patch_comment_by_id(
    comment_data: CommentCreateUpdateSchema,
    id: int,
    current_user: BaseUser,
):
    comment = await Comment.filter(id=id).first()
    existing_comment(comment)
    author_comment(comment, current_user)
    comment.content = comment_data.content

    await comment.save()

    return comment


async def delete_comment_by_id(
    id: int,
    current_user: BaseUser,
):
    comment = await Comment.filter(id=id).first()
    existing_comment(comment)
    author_comment(comment, current_user)

    await comment.delete()
