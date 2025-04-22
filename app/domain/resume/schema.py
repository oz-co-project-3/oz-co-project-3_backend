from enum import Enum
from typing import Optional

from pydantic import BaseModel


class StatusEnum(str, Enum):
    Writing = "작성중"
    Seeking = "구직중"
    Closed = "완료"


# 생성 및 수정 - 이력서
class ResumeRequestSchema(BaseModel):
    user_id: int
    title: str
    visibility: bool
    name: str
    phone_number: str
    email: str
    image_profile: Optional[str] = None
    interests: Optional[str] = None
    desired_area: str
    education: Optional[str] = None
    school_name: Optional[str] = None
    graduation_status: Optional[str] = None
    introduce: str
    status: StatusEnum
    document_url: Optional[str] = None


# 경력 생성 및 수정
class WorkExpRequestSchema(BaseModel):
    resume_id: int
    company: str
    period: str
    position: str


# 이력서 조회
class ResumeResponseSchema(BaseModel):
    id: int
    user_id: int
    title: str
    visibility: bool
    name: str
    phone_number: str
    email: str
    image_profile: Optional[str] = None
    interests: Optional[str] = None
    desired_area: str
    education: Optional[str] = None
    school_name: Optional[str] = None
    graduation_status: Optional[str] = None
    introduce: str
    status: StatusEnum
    document_url: Optional[str] = None
    created_at: str
    updated_at: str


# 경력 조회
class WorkExpResponseSchema(BaseModel):
    id: int
    resume_id: int
    company: str
    period: str
    position: str
