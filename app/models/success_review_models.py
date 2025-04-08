from enum import Enum

from tortoise import fields

from app.utils.model import TimestampMixin


class EmploymnetType(str, Enum):
    REGULAR = "정규직"
    CONTRACT = "계약직"
    INTERN = "인턴"


class SuccessReview(TimestampMixin):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField(
        "user.User", related_name="success_reviews", on_delete=fields.CASCADE
    )
    title = fields.CharField(max_length=100)
    content = fields.TextField(default="")
    job_title = fields.CharField(max_length=50)
    company_name = fields.CharField(max_length=50)
    employment_type = fields.CharEnumField(
        EmploymnetType, default=EmploymnetType.REGULAR
    )
    view_count = fields.IntField(default=0)

    class Meta:
        table = "success_review"
        ordering = ["-created_at"]

    pass
