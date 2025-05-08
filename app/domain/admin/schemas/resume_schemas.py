from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


class StatusEnum(str, Enum):
    Writing = "작성중"
    Seeking = "구직중"
    Closed = "완료"


class UserSchema(BaseModel):
    id: int

    class Config:
        from_attributes = True


class WorkExpResponseDTO(BaseModel):
    id: int
    company: str
    period: str
    position: str

    class Config:
        from_attributes = True


class ResumeResponseDTO(BaseModel):
    id: int
    user: UserSchema
    title: str
    visibility: bool
    name: str
    phone_number: str
    email: str
    image_url: Optional[str] = None
    interests: str
    desired_area: str
    education: str
    school_name: str
    graduation_status: str
    introduce: str
    status: StatusEnum
    document_url: Optional[str] = None
    work_experiences: List[WorkExpResponseDTO] = Field(default_factory=list)

    class Config:
        from_attributes = True
