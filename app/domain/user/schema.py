from datetime import date, datetime
from typing import List, Optional, Union

from pydantic import BaseModel, EmailStr, Field

from app.domain.user.models import (
    Gender,
    SeekerStatus,
    SignInEnum,
    UserStatus,
    UserTypeEnum,
)


class UserRegisterRequest(BaseModel):
    name: str
    email: EmailStr = Field(..., max_length=50, description="이메일, 길이제한 50자")
    password: str = Field(min_length=8)
    password_check: str
    phone_number: str
    birth: date
    interests: str
    purposes: str
    sources: str
    status: SeekerStatus
    gender: Optional[str] = None
    signinMethod: SignInEnum

    class Config:
        from_attributes = True


class UserRegisterResponseDTO(BaseModel):
    id: int
    email: EmailStr
    name: str
    user_type: UserTypeEnum
    email_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserResponseDTO(BaseModel):
    id: int
    email: EmailStr
    user_type: str
    signinMethod: str
    status: UserStatus
    email_verified: bool
    gender: Gender
    leave_reason: Optional[str] = None
    created_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class BusinessUpgradeRequest(BaseModel):
    business_number: str
    company_name: str
    manager_name: str
    manager_phone_number: str
    business_start_date: date

    class Config:
        from_attributes = True


class BusinessUpgradeDTO(BaseModel):
    access_token: str
    refresh_token: str
    user_id: int
    user_type: str
    email: str

    class Config:
        from_attributes = True


# 구직자 프로필 조회 응답용
class SeekerProfileResponse(BaseModel):
    id: int
    name: str
    phone_number: str
    birth: Optional[date]
    interests: str
    purposes: str
    sources: str
    status: SeekerStatus
    applied_posting: Optional[List[int]] = None
    applied_posting_count: int
    profile_url: Optional[str] = None

    class Config:
        from_attributes = True


# 기업 회원용
class CorporateProfileResponse(BaseModel):
    id: int
    company_name: str
    business_number: str
    business_start_date: datetime
    company_description: Optional[str]
    manager_name: str
    manager_phone_number: str
    manager_email: Optional[str] = None
    profile_url: Optional[str] = None

    class Config:
        from_attributes = True


class UserUnionResponseDTO(BaseModel):
    base: UserResponseDTO
    seeker: Optional[SeekerProfileResponse] = None
    corp: Optional[CorporateProfileResponse] = None

    class Config:
        from_attributes = True


class SeekerProfileUpdateRequest(BaseModel):
    name: Optional[str] = None
    phone_number: Optional[str] = None
    birth: Optional[date] = None
    interests: Optional[List[str]] = None
    purposes: Optional[List[str]] = None
    sources: Optional[List[str]] = None
    status: Optional[SeekerStatus] = None
    profile_url: Optional[str] = None

    class Config:
        from_attributes = True


class CorporateProfileUpdateRequest(BaseModel):
    company_name: Optional[str] = None
    company_description: Optional[str] = None
    manager_name: Optional[str] = None
    manager_phone_number: Optional[str] = None
    manager_email: Optional[EmailStr] = None
    profile_url: Optional[str] = None

    class Config:
        from_attributes = True


class SeekerProfileUpdateResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone_number: str
    signin_method: Optional[str] = None
    birth: date
    interests: List[str]
    status: SeekerStatus
    profile_url: Optional[str] = None

    class Config:
        from_attributes = True


class CorporateProfileUpdateResponse(BaseModel):
    id: int
    company_name: str
    email: EmailStr
    company_description: Optional[str]
    manager_name: str
    manager_phone_number: str
    manager_email: Optional[str] = None
    profile_url: Optional[str] = None

    class Config:
        from_attributes = True


class UserDeleteRequest(BaseModel):
    password: str
    is_active: bool
    reason: Optional[str] = None


class UserDeleteDTO(BaseModel):
    user_id: int
    email: str
    reason: Optional[str] = None
    deleted_at: datetime


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponseDTO(BaseModel):
    user_id: int
    user_type: str
    email: str
    name: Optional[str] = "소셜 유저"
    access_token: str

    class Config:
        from_attributes = True


class LogoutResponseDTO(BaseModel):
    success: bool


class VerifyPasswordRequest(BaseModel):
    password: str


class MessageResponse(BaseModel):
    message: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class RefreshTokenResponseDTO(BaseModel):
    access_token: str

    class Config:
        from_attributes = True


class ResendEmailRequest(BaseModel):
    email: EmailStr


class BusinessVerifyRequest(BaseModel):
    business_number: str


class BusinessVerifyResponse(BaseModel):
    business_number: str
    company_name: Optional[str]
    business_status: str
    is_valid: bool


"""
DTO 적용 스키마 🔽
"""


class FindEmailRequest(BaseModel):
    name: str
    phone_number: str


class FindEmailResponseDTO(BaseModel):
    email: str


class FindPasswordRequest(BaseModel):
    name: str
    phone_number: str
    email: str


class FindPasswordResponseDTO(BaseModel):
    success: bool


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    new_password: str
    new_password_check: str


class ResetPasswordResponseDTO(BaseModel):
    success: bool


class SocialCallbackRequest(BaseModel):
    code: str
    state: Optional[str] = None


class EmailVerificationResponseDTO(BaseModel):
    email: str
    email_verified: bool


class ResendEmailResponseDTO(BaseModel):
    success: bool
    email: str


# 이메일 중복검사 체크스키마
class EmailCheckRequest(BaseModel):
    email: EmailStr


class EmailCheckResponseDTO(BaseModel):
    success: bool
    is_available: bool


class BookMarkResponseDTO(BaseModel):
    job_posting_id: int


class BookMarkPostingDTO(BaseModel):
    id: int
    title: str
    company: str
    location: str
    image_url: Optional[str] = None
    employ_method: str

    class Config:
        from_attributes = True
