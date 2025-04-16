from enum import Enum

from tortoise import fields
from tortoise.models import Model

from app.utils.model import TimestampMixin


class EmploymentEnum(str, Enum):  # 공공, 일반 고용 형태 표시
    Public = "공공"
    General = "일반"


class StatusEnum(str, Enum):  # 공고 상태 표시
    Open = "모집중"
    Closing_soon = "마감 임박"
    Closed = "모집 종료"
    Blinded = "블라인드"
    Pending = "대기중"
    Rejected = "반려됨"


class MethodEnum(str, Enum):
    Permanent = "정규직"
    PartTime = "계약직"
    Temporary = "일용직"
    Freelancer = "프리랜서"
    Dispatch = "파견직"


class JobPosting(TimestampMixin, Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField(
        "models.CorporateUser", related_name="job_postings", on_delete=fields.CASCADE
    )
    company = fields.CharField(max_length=50)
    title = fields.CharField(max_length=100, unique=True)
    location = fields.CharField(max_length=150)
    employment_type = fields.CharEnumField(
        EmploymentEnum, default=EmploymentEnum.General, max_length=10
    )
    employ_method = fields.CharEnumField(MethodEnum, default=MethodEnum.Permanent)
    work_time = fields.CharField(max_length=30)
    position = fields.CharField(max_length=50)
    history = fields.TextField(null=True)
    recruitment_count = fields.IntField(default=0)
    education = fields.CharField(max_length=20)
    deadline = fields.CharField(max_length=20)
    salary = fields.CharField(max_length=20)
    summary = fields.TextField(null=True)
    description = fields.TextField()
    status = fields.CharEnumField(StatusEnum, default=StatusEnum.Open)
    view_count = fields.IntField(default=0)
    report = fields.IntField(default=0)

    class Meta:
        table = "job_postings"
        ordering = ["-created_at"]


class RejectPosting(Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField(
        "models.BaseUser", related_name="reject_by_admin", null=True
    )
    job_posting = fields.ForeignKeyField(
        "models.JobPosting", related_name="reject_postings", on_delete=fields.CASCADE
    )
    content = fields.TextField()

    class Meta:
        table = "reject_postings"


class Region(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=50, unique=True)

    class Meta:
        table = "regions"


class Applicants(TimestampMixin, Model):
    class ApplicantEnum(str, Enum):
        Applied = "지원 중"
        Cancelled = "지원 취소"

    id = fields.IntField(pk=True)
    job_posting = fields.ForeignKeyField("models.JobPosting", related_name="applicants")
    resume = fields.ForeignKeyField("models.Resume", related_name="applicants_resume")
    user = fields.ForeignKeyField(
        "models.BaseUser", related_name="applied_user", on_delete=fields.CASCADE
    )
    status = fields.CharEnumField(ApplicantEnum, default=ApplicantEnum.Applied)
    memo = fields.TextField(null=True)

    class Meta:
        table = "applicants"
        ordering = ["-created_at"]
