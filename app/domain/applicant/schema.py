from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ApplicantEnum(str, Enum):
    Applied = "지원 중"
    Cancelled = "지원 취소"


class ApplicantCreateUpdate(BaseModel):
    job_posting_id: int
    resume_id: int
    memo: Optional[str] = None


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
    job_title: str
    company_name: str
    position: str
    deadline: str

    model_config = ConfigDict(from_attributes=True)
