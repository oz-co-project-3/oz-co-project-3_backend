from tortoise import fields

from app.utils.model import TimestampMixin


class ChatBot(TimestampMixin):
    id = fields.IntField(primary_key=True)
    step = fields.IntField()
    is_terminate = fields.BooleanField(default=False)
    selection_path = fields.CharField(max_length=50, default=None)
    options = fields.CharField(max_length=50, default=None, null=True)
    answer = fields.CharField(max_length=150, default=None, null=True)

    class Meta:
        table = "chatbot"
