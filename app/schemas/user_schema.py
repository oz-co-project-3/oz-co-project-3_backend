from datetime import date, datetime
from typing import List

from pydantic import BaseModel, EmailStr, Field


class UserRegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(min_length=8)
    password_check: str
    phone_number: str
    age: int
    interests: List[str]
    purposes: List[str]
    sources: List[str]
    status: str  # "seeking", "employed", "not_seeking"
    gender: str


class UserRegisterResponseData(BaseModel):
    id: int
    email: EmailStr
    name: str
    user_type: str
    email_verified: bool
    created_at: datetime


class UserRegisterResponse(BaseModel):
    message: str
    data: UserRegisterResponseData


class CompanyRegisterRequest(BaseModel):
    email: EmailStr
    password: str
    password_check: str
    company_name: str
    business_number: str
    business_start_date: datetime
    company_description: str
    manager_name: str
    manager_phone_number: str
    manager_email: EmailStr
    gender: str


class CompanyRegisterResponseData(BaseModel):
    id: int
    email: EmailStr
    company_name: str
    manager_name: str
    user_type: str
    email_verified: bool
    created_at: datetime


class CompanyRegisterResponse(BaseModel):
    message: str
    data: CompanyRegisterResponseData
