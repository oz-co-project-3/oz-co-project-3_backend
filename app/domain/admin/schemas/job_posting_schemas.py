from enum import Enum
from typing import List

from pydantic import BaseModel, Field, model_validator


class UserSchema(BaseModel):
    id: int

    class Config:
        from_attributes = True


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


class RejectPostingSchema(BaseModel):
    id: int
    user: UserSchema
    content: str

    class Config:
        from_attributes = True


class JobPostingResponseDTO(BaseModel):
    id: int
    user: UserSchema
    title: str
    company: str
    location: str
    employment_type: EmploymentEnum
    position: str
    history: str
    recruitment_count: int
    education: str
    deadline: str
    salary: str
    summary: str
    description: str
    status: StatusEnum
    view_count: int
    report: int
    reject_postings: List[RejectPostingSchema] = Field(default_factory=list)

    class Config:
        from_attributes = True


class JobPostingUpdateSchema(BaseModel):
    status: StatusEnum

    class Config:
        from_attributes = True


class RejectPostingCreateSchema(BaseModel):
    content: str = Field(
        ..., min_length=1, max_length=1000, description="거절 사유 내용 (1~1000자)"
    )

    class Config:
        from_attributes = True


class RejectPostingResponseDTO(BaseModel):
    id: int
    user: UserSchema
    job_posting: JobPostingResponseDTO
    content: str
