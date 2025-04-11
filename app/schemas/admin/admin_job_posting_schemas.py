from enum import Enum

from pydantic import BaseModel, Field


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


class JobPostingResponseSchema(BaseModel):
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
    salary: int
    summary: str
    description: str
    status: StatusEnum
    view_count: int
    report: int

    class Config:
        from_attributes = True


class JobPostingPatchSchema(BaseModel):
    status: StatusEnum

    class Config:
        from_attributes = True


class JobPostingUpdateSchema(BaseModel):
    status: StatusEnum

    class Config:
        from_attributes = True


class RejectPostingCreateSchema(BaseModel):
    content: str

    class Config:
        from_attributes = True


class RejectPostingResponseSchema(BaseModel):
    id: int
    user: UserSchema
    job_posting: JobPostingResponseSchema
    content: str
