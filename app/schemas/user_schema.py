from datetime import date, datetime
from typing import List, Optional, Union

from pydantic import BaseModel, EmailStr, Field

from app.models.user_models import Gender, SeekerStatus, UserType


class UserRegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(min_length=8)
    password_check: str
    phone_number: str
    birth: date
    interests: List[str]
    purposes: List[str]
    sources: List[str]
    status: SeekerStatus
    gender: Gender


class UserRegisterResponseData(BaseModel):
    id: int
    email: EmailStr
    name: str
    user_type: UserType
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
    gender: Gender


class CompanyRegisterResponseData(BaseModel):
    id: int
    email: EmailStr
    company_name: str
    manager_name: str
    user_type: UserType
    email_verified: bool
    created_at: datetime


class CompanyRegisterResponse(BaseModel):
    message: str
    data: CompanyRegisterResponseData


# 구직자 프로필 조회 응답용
class SeekerProfileResponse(BaseModel):
    id: int
    email: EmailStr
    user_type: UserType
    name: str
    phone_number: str
    birth: date
    interests: List[str]
    purposes: List[str]
    sources: List[str]
    status: SeekerStatus
    is_social: bool
    email_verified: bool
    applied_posting: List[int] = []
    applied_posting_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    profile_url: Optional[str] = None


# 기업 회원용
class CorporateProfileResponse(BaseModel):
    id: int
    email: EmailStr
    user_type: UserType
    company_name: str
    business_number: str
    business_start_date: datetime
    company_description: Optional[str]
    manager_name: str
    manager_phone_number: str
    manager_email: str
    email_verified: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    profile_url: Optional[str] = None


# 공통 Wrapper
class UserProfileResponse(BaseModel):
    data: Union[SeekerProfileResponse, CorporateProfileResponse]


class SeekerProfileUpdateRequest(BaseModel):
    name: Optional[str] = None
    phone_number: Optional[str] = None
    birth: Optional[date] = None
    interests: Optional[List[str]] = None
    purposes: Optional[List[str]] = None
    sources: Optional[List[str]] = None
    status: Optional[SeekerStatus] = None
    profile_url: Optional[str] = None


class CorporateProfileUpdateRequest(BaseModel):
    company_name: Optional[str] = None
    company_description: Optional[str] = None
    manager_name: Optional[str] = None
    manager_phone_number: Optional[str] = None
    manager_email: Optional[EmailStr] = None
    profile_url: Optional[str] = None


class SeekerProfileUpdateResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone_number: str
    birth: date
    interests: List[str]
    status: SeekerStatus
    updated_at: Optional[datetime]
    profile_url: Optional[str] = None


class CorporateProfileUpdateResponse(BaseModel):
    id: int
    company_name: str
    email: EmailStr
    company_description: Optional[str]
    manager_name: str
    manager_phone_number: str
    manager_email: str
    updated_at: Optional[datetime]
    profile_url: Optional[str] = None


class UserProfileUpdateResponse(BaseModel):
    message: str
    data: Union[SeekerProfileUpdateResponse, CorporateProfileUpdateResponse]


class UserDeleteRequest(BaseModel):
    password: str
    is_active: bool
    reason: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponseData(BaseModel):
    access_token: str
    refresh_token: str
    user_id: int
    user_type: UserType
    email: str
    name: str


class LoginResponse(BaseModel):
    message: str
    data: LoginResponseData


class VerifyPasswordRequest(BaseModel):
    password: str


class MessageResponse(BaseModel):
    message: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class RefreshTokenResponseData(BaseModel):
    access_token: str


class RefreshTokenResponse(BaseModel):
    message: str
    data: RefreshTokenResponseData


class ResendEmailRequest(BaseModel):
    email: EmailStr


class BusinessVerifyRequest(BaseModel):
    business_number: str


class BusinessVerifyResponse(BaseModel):
    business_number: str
    company_name: Optional[str]
    business_status: str
    is_valid: bool


class FindEmailRequest(BaseModel):
    name: str
    phone_number: str


class FindEmailResponseData(BaseModel):
    email: str


# 메일 찾을 시 DICT로 간단하게 가능하지만
# DICT구조 사용시 SWAGGER에서 안보이거나 깨진다고함
class FindEmailResponse(BaseModel):
    message: str
    data: FindEmailResponseData


class FindPasswordRequest(BaseModel):
    name: str
    phone_number: str
    email: str


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    new_password: str
    new_password_check: str
