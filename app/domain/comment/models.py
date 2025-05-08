from tortoise import fields

from app.utils.model import TimestampMixin


class Comment(TimestampMixin):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField(
        "models.BaseUser", related_name="comments", on_delete=fields.CASCADE
    )
    success_review = fields.ForeignKeyField(
        "models.SuccessReview",
        related_name="comments",
        on_delete=fields.CASCADE,
        null=True,
    )
    free_board = fields.ForeignKeyField(
        "models.FreeBoard",
        related_name="comments",
        on_delete=fields.CASCADE,
        null=True,
    )
    content = fields.TextField()

    class Meta:
        ordering = ["-created_at"]
        table = "comments"
