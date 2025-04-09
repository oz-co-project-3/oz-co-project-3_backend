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
        table = "base_users"


class UserBan(models.Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("app.models.BaseUser", related_name="bans")
    reason = fields.TextField(null=True)
    banned_at = fields.DatetimeField(auto_now_add=True)
    banned_until = fields.DatetimeField(null=True)
    banned_by = fields.ForeignKeyField("app.models.BaseUser", related_name="bans_given")
    email_sent = fields.BooleanField(default=False)

    class Meta:
        table = "user_bans"


class CorporateUser(models.Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField(
        "app.models.BaseUser", related_name="corporate_profiles"
    )
    company_name = fields.CharField(max_length=255, null=False)
    business_start_date = fields.DatetimeField(null=False)
    business_number = fields.CharField(max_length=20, null=False, unique=True)
    company_description = fields.TextField(null=True)
    manager_name = fields.CharField(max_length=100, null=False)
    manager_phone_number = fields.CharField(max_length=20, null=False)
    manager_email = fields.CharField(max_length=255, null=True, unique=True)

    class Meta:
        table = "corporate_users"


class SeekerUser(models.Model):
    class Status(str, Enum):
        SEEKING = "seeking"
        EMPLOYED = "employed"
        NOT_SEEKING = "not_seeking"

    STATUS_CHOICES = [
        (Status.SEEKING.value, "seeking"),
        (Status.EMPLOYED.value, "employed"),
        (Status.NOT_SEEKING.value, "not_seeking"),
    ]

    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("app.models.BaseUser", related_name="seeker_profiles")
    name = fields.CharField(max_length=20, null=False)
    phone_number = fields.CharField(max_length=20, null=False)
    age = fields.IntField(null=False)
    interests = fields.JSONField(null=False)
    purposes = fields.JSONField(null=False)
    sources = fields.JSONField(null=True)
    applied_posting = fields.JSONField(null=True)
    applied_posting_count = fields.IntField(null=False, default=0)
    is_social = fields.BooleanField(default=False)
    status = fields.CharField(
        max_length=20,
        null=False,
        choices=STATUS_CHOICES,
        default=Status.SEEKING.value,
    )
    interested_companies = fields.ManyToManyField(
        "app.models.CorporateUser",
        related_name="interested_seekers",
        through="interested_companies_seeker",
    )

    class Meta:
        table = "seeker_users"
