from datetime import date, datetime
from typing import List, Optional, Union

from pydantic import BaseModel, EmailStr, Field

from app.domain.user.models import Gender, SeekerStatus, SignInEnum, UserTypeEnum


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
    signinMethod: SignInEnum


class UserRegisterResponseData(BaseModel):
    id: int
    email: EmailStr
    name: str
    user_type: UserTypeEnum
    email_verified: bool
    created_at: datetime


class UserRegisterResponseDTO(BaseModel):
    success: bool
    data: UserRegisterResponseData


class BusinessUpgradeRequest(BaseModel):
    business_number: str
    company_name: str
    manager_name: str
    manager_phone_number: str
    business_start_date: date


class BusinessUpgradeData(BaseModel):
    access_token: str
    refresh_token: str
    user_id: int
    user_type: str
    email: str


class BusinessUpgradeResponseDTO(BaseModel):
    success: bool
    data: BusinessUpgradeData


# 구직자 프로필 조회 응답용
class SeekerProfileResponse(BaseModel):
    id: int
    email: EmailStr
    user_type: UserTypeEnum
    signin_method: Optional[str] = None
    name: str
    phone_number: str
    birth: Optional[date]
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
    user_type: UserTypeEnum
    signin_method: Optional[str] = None
    company_name: str
    business_number: str
    business_start_date: datetime
    company_description: Optional[str]
    manager_name: str
    manager_phone_number: str
    manager_email: Optional[str] = None
    email_verified: bool
    created_at: datetime
    profile_url: Optional[str] = None


# 공통 Wrapper
class UserProfileResponseDTO(BaseModel):
    success: bool
    data: Union["SeekerProfileResponse", "CorporateProfileResponse"]


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
    signin_method: Optional[str] = None
    birth: date
    interests: List[str]
    status: SeekerStatus
    profile_url: Optional[str] = None


class CorporateProfileUpdateResponse(BaseModel):
    id: int
    company_name: str
    email: EmailStr
    company_description: Optional[str]
    manager_name: str
    manager_phone_number: str
    manager_email: Optional[str] = None
    profile_url: Optional[str] = None


class UserProfileUpdateResponseDTO(BaseModel):
    success: bool
    data: Union["SeekerProfileUpdateResponse", "CorporateProfileUpdateResponse"]


class UserDeleteRequest(BaseModel):
    password: str
    is_active: bool
    reason: Optional[str] = None


class UserDeleteData(BaseModel):
    user_id: int
    email: str
    reason: Optional[str] = None
    deleted_at: datetime


class UserDeleteResponseDTO(BaseModel):
    success: bool
    data: UserDeleteData


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponseData(BaseModel):
    access_token: str
    refresh_token: str
    user_id: str
    user_type: List[UserTypeEnum]
    email: str
    name: Optional[str] = "소셜 유저"


class LoginResponseDTO(BaseModel):
    success: bool
    data: LoginResponseData


class LogoutResponseDTO(BaseModel):
    success: bool


class VerifyPasswordRequest(BaseModel):
    password: str


class MessageResponse(BaseModel):
    message: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class RefreshTokenResponseDTO(BaseModel):
    success: bool
    access_token: str


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
