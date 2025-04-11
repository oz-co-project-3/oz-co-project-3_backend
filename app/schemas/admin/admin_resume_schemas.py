from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr


class StatusEnum(str, Enum):
    Writing = "작성중"
    Seeking = "구직중"
    Closed = "완료"


class UserSchema(BaseModel):
    id: int

    class Config:
        from_attributes = True


class ResumeResponseSchema(BaseModel):
    id: int
    user: UserSchema
    title: str
    visibility: bool
    name: str
    phone_number: str
    email: EmailStr
    image_profile: Optional[str] = None
    interests: str
    desired_area: str
    education: str
    school_name: str
    graduation_status: str
    introduce: str
    status: StatusEnum
    document_url: Optional[str] = None

    class Config:
        from_attributes = True
