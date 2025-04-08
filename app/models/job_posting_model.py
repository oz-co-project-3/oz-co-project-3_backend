from enum import Enum

from tortoise import fields
from tortoise.models import Model

from app.utils.model import TimestampMixin


class JobPosting(TimestampMixin, Model):
    class EmploymentEnum(str, Enum):  # 공공, 일반 고용 형태 표시
        Public = "공공"
        General = "일반"

    class StatusEnum(str, Enum):  # 공고 상태 표시
        Open = "모집중"
        Closing_soon = "마감 임박"
        Closed = "모집 종료"
        Blinded = "블라인드"

    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField(
        "user_model.User", related_name="job_postings", on_delete="CASCADE"
    )
    title = fields.CharField(max_length=100, unique=True)
    location = fields.CharField(max_length=150)
    employment_type = fields.CharEnumField(
        EmploymentEnum, default=EmploymentEnum.General
    )
    position = fields.CharField(max_length=50)
    history = fields.TextField(null=True)
    recruitment_count = fields.IntField()
    education = fields.CharField(max_length=20)
    deadline = fields.CharField(max_length=20)
    salary = fields.IntField()
    summary = fields.TextField(null=True)
    description = fields.TextField()
    status = fields.CharEnumField(StatusEnum, default=StatusEnum.Open)
    view_count = fields.IntField(default=0)
    report = fields.IntField(default=0)

    class Meta:
        table = "job_postings"
        ordering = ["-created_at"]


class RejectPosting(TimestampMixin, Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField(
        "user_model.User", related_name="reject_postings", null=True
    )
    job_posting = fields.ForeignKeyField("JobPosting", related_name="reject_by_admins")
    content = fields.TextField()

    class Meta:
        table = "reject_postings"
        ordering = ["-created_at"]
