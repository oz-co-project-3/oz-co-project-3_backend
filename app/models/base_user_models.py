from enum import Enum

from tortoise import fields, models


class BaseUser(models.Model):
    class UserType(str, Enum):
        SEEKER = "seeker"
        BUSINESS = "business"

    class Status(str, Enum):
        ACTIVE = "active"
        SUSPEND = "suspend"
        DELETE = "delete"

    USER_TYPE_CHOICES = [
        (UserType.SEEKER.value, "구직자"),
        (UserType.BUSINESS.value, "기업"),
    ]

    STATUS_CHOICES = [
        (Status.ACTIVE.value, "active"),
        (Status.SUSPEND.value, "suspend"),
        (Status.DELETE.value, "delete"),
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
        default=UserType.SEEKER.value,
    )
    is_active = fields.BooleanField(default=True)
    status = fields.CharField(
        max_length=20,
        null=True,
        choices=STATUS_CHOICES,
        default=Status.ACTIVE.value,
    )
    email_verified = fields.BooleanField(default=False)
    is_superuser = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)
    deleted_at = fields.DatetimeField(null=True)
    is_banned = fields.BooleanField(default=False)

    class Meta:
        table = "BASE_USER"
