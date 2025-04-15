from enum import Enum

from tortoise import fields, models


class BaseUser(models.Model):
    GENDER_CHOICES = [("male", "남자"), ("female", "여자")]

    class UserType(str, Enum):
        SEEKER = "seeker"
        BUSINESS = "business"

    class Status(str, Enum):
        ACTIVE = "active"
        SUSPEND = "suspend"
        DELETE = "delete"
        PENDING = "pending"  # 메일 인증 미 완료시 상태 추가

    USER_TYPE_CHOICES = [
        (UserType.SEEKER.value, "구직자"),
        (UserType.BUSINESS.value, "기업"),
    ]

    STATUS_CHOICES = [
        (Status.PENDING.value, "pending"),
        (Status.ACTIVE.value, "active"),
        (Status.SUSPEND.value, "suspend"),
        (Status.DELETE.value, "delete"),
    ]

    id = fields.IntField(pk=True)
    password = fields.CharField(
        max_length=80,
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
    status = fields.CharField(
        max_length=20,
        null=True,
        choices=STATUS_CHOICES,
        default=Status.PENDING.value,
    )
    email_verified = fields.BooleanField(default=False)
    is_superuser = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)
    deleted_at = fields.DatetimeField(null=True)
    gender = fields.CharField(max_length=10, choices=GENDER_CHOICES)
    leave_reason = fields.TextField(null=True)

    class Meta:
        table = "base_users"


class UserBan(models.Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.BaseUser", related_name="bans")
    reason = fields.TextField(null=True)
    banned_at = fields.DatetimeField(auto_now_add=True)
    banned_until = fields.DatetimeField(null=True)
    banned_by = fields.ForeignKeyField("models.BaseUser", related_name="bans_given")
    email_sent = fields.BooleanField(default=False)

    class Meta:
        table = "user_bans"


class CorporateUser(models.Model):
    GENDER_CHOICES = [("male", "남자"), ("female", "여자")]

    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.BaseUser", related_name="corporate_profiles")
    company_name = fields.CharField(max_length=255, null=False)
    business_start_date = fields.DatetimeField(null=False)
    business_number = fields.CharField(max_length=20, null=False, unique=True)
    company_description = fields.TextField(null=True)
    manager_name = fields.CharField(max_length=100, null=False)
    manager_phone_number = fields.CharField(max_length=20, null=False)
    manager_email = fields.CharField(max_length=255, null=True, unique=True)
    gender = fields.CharField(max_length=10, choices=GENDER_CHOICES)
    profile_url = fields.CharField(max_length=255, null=True)

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
    user = fields.ForeignKeyField("models.BaseUser", related_name="seeker_profiles")
    name = fields.CharField(max_length=20, null=False)
    phone_number = fields.CharField(max_length=20, null=False)
    birth = fields.DateField(null=True)
    interests = fields.CharField(max_length=100, null=True)
    interests_posting = fields.CharField(max_length=255, null=True)
    purposes = fields.CharField(max_length=100, null=True)
    sources = fields.CharField(max_length=60, null=True)
    applied_posting = fields.CharField(max_length=60, null=True)
    applied_posting_count = fields.IntField(null=False, default=0)
    is_social = fields.BooleanField(default=False)
    status = fields.CharField(
        max_length=20,
        null=False,
        choices=STATUS_CHOICES,
        default=Status.SEEKING.value,
    )
    profile_url = fields.CharField(max_length=255, null=True)

    class Meta:
        table = "seeker_users"
