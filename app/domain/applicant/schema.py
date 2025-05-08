from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator, root_validator


class ApplicantEnum(str, Enum):
    Applied = "지원 중"
    Cancelled = "지원 취소"


class ApplicantCreateUpdate(BaseModel):
    job_posting_id: int
    resume_id: int
    memo: Optional[str] = None

    @field_validator("job_posting_id", "resume_id")
    def must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("job_posting_id와 resume_id는 0보다 커야 합니다.")
        return v


class ApplicantUpdate(BaseModel):
    status: Optional[ApplicantEnum] = None
    memo: Optional[str] = None


class ApplicantResponse(BaseModel):
    id: int
    job_posting_id: int
    resume_id: int
    user_id: int
    status: ApplicantEnum
    memo: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    title: str
    company: str
    position: str
    deadline: str

    model_config = ConfigDict(from_attributes=True)
