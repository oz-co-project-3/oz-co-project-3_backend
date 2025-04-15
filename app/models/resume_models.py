from enum import Enum

from tortoise import fields
from tortoise.models import Model

from app.utils.model import TimestampMixin


class StatusEnum(str, Enum):
    Writing = "작성중"
    Seeking = "구직중"
    Closed = "완료"


class Resume(TimestampMixin):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField(
        "models.SeekerUser", related_name="resumes", on_delete=fields.CASCADE
    )
    title = fields.CharField(max_length=100)
    visibility = fields.BooleanField(default=True)
    name = fields.CharField(max_length=30)
    phone_number = fields.CharField(max_length=40)
    email = fields.CharField(max_length=50)
    image_profile = fields.CharField(max_length=255, null=True)
    interests = fields.CharField(max_length=100, null=True)
    desired_area = fields.CharField(max_length=50)
    education = fields.CharField(max_length=10, null=True)
    school_name = fields.CharField(max_length=20, null=True)
    graduation_status = fields.CharField(max_length=20, null=True)
    introduce = fields.TextField(default="")
    status = fields.CharEnumField(StatusEnum, default=StatusEnum.Writing)
    document_url = fields.CharField(max_length=255, null=True)

    class Meta:
        table = "resumes"
        ordering = ["-created_at"]


class WorkExp(Model):
    id = fields.IntField(pk=True)
    resume = fields.ForeignKeyField(
        "models.Resume",
        related_name="work_experiences",
        on_delete=fields.CASCADE,
    )
    company = fields.CharField(max_length=30)
    period = fields.CharField(max_length=20)
    position = fields.CharField(max_length=20)

    class Meta:
        table = "work_experiences"
