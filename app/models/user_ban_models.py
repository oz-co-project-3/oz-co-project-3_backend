from tortoise import models, fields

class UserBan(models.Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("app.models.BaseUser", related_name="bans")
    reason = fields.TextField(null=True)
    banned_at = fields.DatetimeField(auto_now_add=True)
    banned_until = fields.DatetimeField(null=True)
    banned_by = fields.ForeignKeyField("app.models.BaseUser", related_name="bans_given")
    email_sent = fields.BooleanField(default=False)

    class Meta:
        table = "USER_BAN"