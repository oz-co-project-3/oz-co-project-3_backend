from datetime import datetime
from typing import List

from pydantic import BaseModel, EmailStr


class UserResponseSchema(BaseModel):
    id: int
    email: EmailStr
    user_type: str
    is_active: bool
    status: str
    email_verified: bool
    is_superuser: bool
    created_at: datetime
    deleted_at: datetime
    is_banned: bool
    gender: str

    class Config:
        from_attributes = True


class SeekerUserResponseSchema(BaseModel):
    id: int
    user: UserResponseSchema
    name: str
    phone_number: str
    age: int
    interests: List[str]
    purposes: List[str]
    sources: List[str]
    applied_posting = List[str]
    applied_posting_count: int
    is_social: bool
    status: str
    interested_companies = List[str]

    class Config:
        from_attributes = True


class CorpUserResponseSchema(BaseModel):
    id: int
    user: UserResponseSchema
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
