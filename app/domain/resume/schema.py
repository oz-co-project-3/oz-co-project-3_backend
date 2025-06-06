from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class StatusEnum(str, Enum):
    Writing = "작성중"
    Seeking = "구직중"
    Closed = "완료"


# 경력 생성 및 수정
class WorkExpRequestSchema(BaseModel):
    company: str
    period: str
    position: str


# 이력서 생성 및 수정
class ResumeRequestSchema(BaseModel):
    user: Optional[int] = None
    title: str = Field(..., max_length=100, description="길이 제한 100자")
    visibility: bool
    name: str = Field(..., max_length=20, description="길이 제한 20자")
    phone_number: str = Field(..., max_length=50, description="길이 제한 50자")
    email: str = Field(..., max_length=100, description="길이 제한 100자")
    image_url: Optional[str] = None
    interests: Optional[str] = None
    desired_area: str = Field(..., max_length=20, description="길이 제한 20자")
    education: Optional[str] = None
    school_name: Optional[str] = None
    graduation_status: Optional[str] = None
    introduce: str = Field(..., max_length=500, description="길이 제한 500자")
    status: StatusEnum
    document_url: Optional[str] = None
    work_experiences: Optional[List[WorkExpRequestSchema]] = None  # 경력 사항 추가

    model_config = ConfigDict(from_attributes=True)


# 경력 조회
class WorkExpResponseSchema(BaseModel):
    id: int
    resume_id: int
    company: str
    period: str
    position: str

    model_config = ConfigDict(from_attributes=True)


class UserSchema(BaseModel):
    id: int

    model_config = ConfigDict(from_attributes=True)


# 이력서 조회
class ResumeResponseSchema(BaseModel):
    id: int
    user: UserSchema
    title: str
    visibility: bool
    name: str
    phone_number: str
    email: str
    image_url: Optional[str] = None
    interests: Optional[str] = None
    desired_area: str
    education: Optional[str] = None
    school_name: Optional[str] = None
    graduation_status: Optional[str] = None
    introduce: str
    status: StatusEnum
    document_url: Optional[str] = None
    work_experiences: Optional[List[WorkExpResponseSchema]] = None  # 경력 사항 추가
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaginatedResumeResponse(BaseModel):
    total: int
    offset: int
    limit: int
    data: List[ResumeResponseSchema]
