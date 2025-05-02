from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator

from app.domain.job_posting.models import EmploymentEnum, MethodEnum, StatusEnum


class ApplicantEnum(str, Enum):
    Applied = "지원 중"
    Cancelled = "지원 취소"


class JobPostingCreateUpdate(BaseModel):
    title: str = Field(..., max_length=100, description="길이 제한 100자")
    company: str = Field(..., max_length=50, description="길이 제한 50자")
    location: str = Field(..., max_length=150, description="길이 제한 150자")
    employment_type: EmploymentEnum
    employ_method: MethodEnum
    work_time: str = Field(..., max_length=30, description="길이 제한 30자")
    position: str = Field(..., max_length=50, description="길이 제한 50자")
    history: Optional[str] = None
    recruitment_count: int = Field(..., ge=0, description="양수만 입력 가능")
    education: str = Field(..., max_length=20, description="길이 제한 20자")
    deadline: str = Field(..., max_length=20, description="길이 제한 20자")
    salary: str = Field(..., max_length=20, description="길이 제한 20자")
    summary: Optional[str] = None
    description: str
    status: StatusEnum

    # 필수 필드 검증
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
    def validate_required_fields(cls, value: str):
        if not value.strip():
            raise ValueError("필수 입력 항목입니다.")
        return value

    @field_validator("deadline", mode="before")
    def validate_deadline(value: str) -> str:
        try:
            parsed_date = datetime.strptime(value, "%Y-%m-%d").date()
            return parsed_date.strftime("%Y-%m-%d")
        except ValueError:
            raise ValueError("마감일은 YYYY-MM-DD 형식으로 입력해야 합니다.")

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

    @field_serializer("deadline")
    def serialize_deadline(self, value: str, _info) -> str:
        return datetime.strptime(value, "%Y-%m-%d").strftime("%Y-%m-%d")


class JobPostingSummaryResponse(BaseModel):
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
    created_at: datetime
    view_count: int
    report: int

    model_config = ConfigDict(from_attributes=True)
