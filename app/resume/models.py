from enum import Enum

from tortoise import fields
from tortoise.models import Model


class StatusEnum(str, Enum):
    Writing = "작성중"
    Seeking = "구직중"
    Closed = "완료"


class Resume(Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("users.models", related_name="writer")
    title = fields.CharField(max_length=255)
    visibility = fields.BooleanField(default=True)
    name = fields.CharField(max_length=255)
    phone_number = fields.CharField(max_length=255)
    email = fields.CharField(max_length=255)
    image_profile = fields.CharField(max_length=255, null=True, blank=True)
    interests = fields.JSONField(default=[])
    desired_area = fields.CharField(max_length=255)
    work_exp = fields.ForeignKeyField("work.exp.models", related_name="experience")
    education = fields.CharField(max_length=255, null=True, blank=True)
    school_name = fields.CharField(max_length=255, null=True, blank=True)
    graduation_status = fields.CharField(max_length=255, null=True, blank=True)
    introduce = fields.TextField()
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    status = fields.CharEnumField(StatusEnum, default=StatusEnum.Writing)
    document_url = fields.CharField(max_length=255, null=True, blank=True)
