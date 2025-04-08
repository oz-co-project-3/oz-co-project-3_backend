from tortoise import fields

from app.utils.model import TimestampMixin


class Comment(TimestampMixin):
    id = fields.IntField(pk=True)
    success_review = fields.ForeignKeyField(
        "success_review_models.SuccessReview",
        related_name="comments",
        on_delete=fields.CASCADE,
        null=True,
    )
    free_board = fields.ForeignKeyField(
        "free_board_models.FreeBoard",
        related_name="comments",
        on_delete=fields.CASCADE,
        null=True,
    )
    content = fields.TextField()

    class Meta:
        ordering = ["-created_at"]
        table = "comment"
