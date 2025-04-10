from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field, model_validator

from app.utils.exception import CustomException


class UserResponseSchema(BaseModel):
    id: int
    email: EmailStr
    user_type: str
    is_active: bool
    status: str
    email_verified: bool
    is_superuser: bool
    created_at: datetime
    deleted_at: Optional[datetime] = None
    is_banned: bool
    gender: str

    class Config:
        from_attributes = True


class SeekerUserResponseSchema(BaseModel):
    id: int
    name: str
    phone_number: str
    age: int
    interests: List[str]
    purposes: List[str]
    sources: List[str]
    applied_posting: Optional[List[int]] = None
    applied_posting_count: int
    is_social: bool
    status: str

    class Config:
        from_attributes = True


class CorpUserResponseSchema(BaseModel):
    id: int
    company_name: str
    business_start_date: datetime
    business_number: str
    company_description: str
    manager_name: str
    manager_phone_number: str
    manager_email: str
    gender: str

    class Config:
        from_attributes = True


class UserUnionResponseSchema(BaseModel):
    base: UserResponseSchema
    seeker: Optional[SeekerUserResponseSchema] = None
    corp: Optional[CorpUserResponseSchema] = None


class UserUpdateSchema(BaseModel):
    is_active: bool

    @model_validator(mode="after")
    def check_field(self):
        if self.is_active is None:
            raise CustomException(
                code="required_field", status_code=400, error="필수 필드 누락"
            )
        return self
