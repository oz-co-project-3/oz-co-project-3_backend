from tortoise import fields, models


class BaseUser(models.Model):
    # 구직자 / 기업회원
    TYPE_SEEKER = "seeker"
    TYPE_BUSINESS = "business"

    # 활성화 상태
    STATUS_ACTIVE = "active"
    STATUS_SUSPEND = "suspend"
    STATUS_DELETE = "delete"

    USER_TYPE_CHOICES = [
        (TYPE_SEEKER, "구직자"),
        (TYPE_BUSINESS, "기업"),
    ]

    STATUS_CHOICES = [
        (STATUS_ACTIVE, "active"),
        (STATUS_SUSPEND, "suspend"),
        (STATUS_DELETE, "delete"),
    ]

    id = fields.IntField(pk=True)
    password = fields.CharField(
        max_length=20,
        null=False,
        description="비밀번호는 최소 8자 이상이며 특수 문자를 포함",
    )
    email = fields.CharField(max_length=50, unique=True)
    user_type = fields.CharField(
        max_length=20,
        null=False,
        choices=USER_TYPE_CHOICES,
        default=TYPE_SEEKER,
    )
    is_active = fields.BooleanField(default=True)
    status = fields.CharField(
        max_length=20,
        null=True,
        choices=STATUS_CHOICES,
        default=STATUS_ACTIVE,
    )
    email_verified = fields.BooleanField(default=False)
    is_superuser = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)
    deleted_at = fields.DatetimeField(null=True)
    is_banned = fields.BooleanField(default=False)

    class Meta:
        table = "BASE_USER"


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
