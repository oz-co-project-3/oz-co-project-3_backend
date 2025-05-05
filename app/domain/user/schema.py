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
    name: str = Field(..., max_length=20, description="이름, 길이제한 20자")
    email: EmailStr = Field(..., max_length=50, description="이메일, 길이제한 50자")
    password: str = Field(min_length=8, description="비밀번호 최소 8자 이상")
    password_check: str = Field(min_length=8, description="비밀번호 최소 8자 이상")
    phone_number: str = Field(max_length=15, description="번호 길이제한 15자")
    birth: date = Field(..., description="생년월일")
    interests: str = Field(..., max_length=100, description="관심사, 최대 100자")
    purposes: str = Field(..., max_length=100, description="가입 목적, 최대 100자")
    sources: str = Field(..., max_length=100, description="가입 경로, 최대 100자")
    status: SeekerStatus = Field(..., description="구직 상태 (예: seeking, not_seeking)")
    gender: Optional[str] = Field(None, max_length=10, description="성별 (선택)")
    signinMethod: str = Field(..., description="가입 방식")

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
    business_number: str = Field(..., max_length=20, description="사업자등록번호, 길이제한 20자")
    company_name: str = Field(..., max_length=255, description="회사명, 최대 255자")
    manager_name: str = Field(..., max_length=100, description="담당자 이름, 최대 100자")
    manager_phone_number: str = Field(
        ..., max_length=20, description="담당자 전화번호, 최대 20자"
    )
    business_start_date: date = Field(..., description="사업 시작일자")

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
    name: Optional[str] = Field(None, max_length=20, description="이름 (선택), 최대 20자")
    phone_number: Optional[str] = Field(
        None, max_length=20, description="전화번호 (선택), 최대 20자"
    )
    birth: Optional[date] = Field(None, description="생년월일 (선택)")
    interests: Optional[List[str]] = Field(
        None, description="관심사 리스트 (선택), 각 항목 최대 100자"
    )
    purposes: Optional[List[str]] = Field(
        None, description="가입 목적 리스트 (선택), 각 항목 최대 100자"
    )
    sources: Optional[List[str]] = Field(
        None, description="가입 경로 리스트 (선택), 각 항목 최대 60자"
    )
    status: Optional[SeekerStatus] = Field(None, description="구직 상태 (선택)")
    profile_url: Optional[str] = Field(
        None, max_length=255, description="프로필 이미지 URL (선택), 최대 255자"
    )

    class Config:
        from_attributes = True


class CorporateProfileUpdateRequest(BaseModel):
    company_name: Optional[str] = Field(
        None, max_length=255, description="회사명 (선택), 최대 255자"
    )
    company_description: Optional[str] = Field(None, description="회사 소개 (선택)")
    manager_name: Optional[str] = Field(
        None, max_length=100, description="담당자 이름 (선택), 최대 100자"
    )
    manager_phone_number: Optional[str] = Field(
        None, max_length=20, description="담당자 전화번호 (선택), 최대 20자"
    )
    manager_email: Optional[EmailStr] = Field(
        None, max_length=255, description="담당자 이메일 (선택), 최대 255자"
    )
    profile_url: Optional[str] = Field(
        None, max_length=255, description="프로필 이미지 URL (선택), 최대 255자"
    )

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
    password: str = Field(..., description="비밀번호")
    is_active: bool
    reason: Optional[str] = Field(None, description="탈퇴 사유 (선택)")


class UserDeleteDTO(BaseModel):
    user_id: int
    email: str
    reason: Optional[str] = None
    deleted_at: datetime


class LoginRequest(BaseModel):
    email: EmailStr = Field(..., description="이메일")
    password: str = Field(..., description="패스워드")


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
    name: str = Field(..., description="이름")
    phone_number: str = Field(..., description="전화번호")


class FindEmailResponseDTO(BaseModel):
    email: str


class FindPasswordRequest(BaseModel):
    name: str = Field(..., description="이름")
    phone_number: str = Field(..., description="전화번호")
    email: str = Field(..., description="이메일")


class FindPasswordResponseDTO(BaseModel):
    success: bool


class ResetPasswordRequest(BaseModel):
    email: EmailStr = Field(..., description="이메일")
    new_password: str = Field(..., description="새로운 비밀번호")
    new_password_check: str = Field(..., description="새로운 비밀번호")


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
    email: EmailStr = Field(..., description="이메일")


class EmailCheckResponseDTO(BaseModel):
    success: bool
    is_available: bool


class BookMarkResponseDTO(BaseModel):
    job_posting_id: int


class BookMarkPostingDTO(BaseModel):
    id: int = Field(..., description="공고 ID")
    title: str = Field(..., max_length=255, description="공고 제목")
    company: str = Field(..., max_length=100, description="회사명")
    location: str = Field(..., max_length=100, description="근무 위치")
    image_url: Optional[str] = Field(None, max_length=255, description="이미지 URL (선택)")
    employ_method: str = Field(..., max_length=50, description="고용 형태 (예: 정규직, 계약직 등)")

    class Config:
        from_attributes = True
