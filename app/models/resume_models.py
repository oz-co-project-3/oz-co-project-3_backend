from enum import Enum

from tortoise import fields
from tortoise.models import Model


class StatusEnum(str, Enum):
    Writing = "작성중"
    Seeking = "구직중"
    Closed = "완료"


class Resume(Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField(
        Users.models, related_name="resumes", on_delete=fields.CASCADE
    )
    title = fields.CharField(max_length=255)
    visibility = fields.BooleanField(default=True)
    name = fields.CharField(max_length=255)
    phone_number = fields.CharField(max_length=255)
    email = fields.CharField(max_length=255)
    image_profile = fields.CharField(max_length=255, null=True)
    interests = fields.JSONField(default=[])
    desired_area = fields.CharField(max_length=255)
    education = fields.CharField(max_length=255, null=True)
    school_name = fields.CharField(max_length=255, null=True)
    graduation_status = fields.CharField(max_length=255, null=True)
    introduce = fields.TextField()
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    status = fields.CharEnumField(StatusEnum, default=StatusEnum.Writing)
    document_url = fields.CharField(max_length=255, null=True)


class WorkExp(Model):
    id = fields.IntField(pk=True)
    resume = fields.ForeignKeyField(
        Resume.model, related_name="work_experiences", on_delete=fields.CASCADE
    )
    company = fields.CharField(max_length=255)
    period = fields.CharField(max_length=255)
    position = fields.CharField(max_length=255)
