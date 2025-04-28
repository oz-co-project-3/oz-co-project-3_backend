from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator

from app.domain.job_posting.job_posting_models import (
    EmploymentEnum,
    MethodEnum,
    StatusEnum,
)


class JobPostingCreateUpdate(BaseModel):
    title: str
    company: str
    location: str
    employment_type: EmploymentEnum
    employ_method: MethodEnum
    work_time: str
    position: str
    history: Optional[str] = None
    recruitment_count: int
    education: str
    deadline: str
    salary: str
    summary: Optional[str] = None
    description: str
    status: StatusEnum

    # 벨리데이터 추가
    @field_validator(
        "title",
        "location",
        "employment_type",
        "employ_method",
        "work_time",
        "position",
        "education",
        "deadline",
        "description",
    )
    def validate_required_fields(cls, value, field):
        if not value:
            raise ValueError(f"{field.name}값은 필수입니다.")
        return value

    # configdict 적용
    model_config = ConfigDict(from_attributes=True)


class JobPostingResponse(BaseModel):
    id: int
    title: str
    location: str
    employment_type: EmploymentEnum
    employ_method: MethodEnum
    position: str
    history: Optional[str] = None
    recruitment_count: int
    education: str
    deadline: str
    salary: str
    summary: Optional[str] = None
    description: str
    status: StatusEnum
    view_count: int
    report: int

    model_config = ConfigDict(from_attributes=True)


class JobPostingSummaryResponse(BaseModel):
    id: int
    title: str
    status: StatusEnum
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
