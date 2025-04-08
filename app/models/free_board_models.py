from tortoise import fields

from app.utils.model import TimestampMixin


class FreeBoard(TimestampMixin):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField(
        "user.User", related_name="free_boards", on_delete=fields.CASCADE
    )
    title = fields.CharField(max_length=50)
    content = fields.TextField(default="")
    image_url = fields.CharField(max_length=255, null=True)
    view_count = fields.IntField(default=0)

    class Meta:
        table = "free_board"
        ordering = ["-created_at"]
