from enum import Enum

from tortoise import fields, models


class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"


class UserStatus(str, Enum):
    ACTIVE = "active"
    SUSPEND = "suspend"
    DELETE = "delete"
    PENDING = "pending"  # 메일 인증 미 완료시 상태 추가


class SeekerStatus(str, Enum):
    SEEKING = "seeking"
    EMPLOYED = "employed"
    NOT_SEEKING = "not_seeking"


class BaseUser(models.Model):
    id = fields.IntField(pk=True)
    password = fields.CharField(max_length=80, null=False)
    email = fields.CharField(max_length=50, unique=True)
    user_type = fields.CharField(max_length=20, null=False)
    signinMethod = fields.CharField(max_length=20, null=False)
    status = fields.CharEnumField(UserStatus, max_length=20, default=UserStatus.PENDING)
    email_verified = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)
    deleted_at = fields.DatetimeField(null=True)
    gender = fields.CharEnumField(Gender, max_length=10)
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
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.BaseUser", related_name="corporate_profiles")
    company_name = fields.CharField(max_length=255, null=False)
    business_start_date = fields.DatetimeField(null=False)
    business_number = fields.CharField(max_length=20, null=False, unique=True)
    company_description = fields.TextField(null=True)
    manager_name = fields.CharField(max_length=100, null=False)
    manager_phone_number = fields.CharField(max_length=20, null=False)
    manager_email = fields.CharField(max_length=255, null=True, unique=True)
    gender = fields.CharEnumField(Gender, max_length=10)
    profile_url = fields.CharField(max_length=255, null=True)

    class Meta:
        table = "corporate_users"


class SeekerUser(models.Model):
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
    status = fields.CharEnumField(
        SeekerStatus, max_length=20, default=SeekerStatus.SEEKING
    )
    profile_url = fields.CharField(max_length=255, null=True)

    class Meta:
        table = "seeker_users"
