from datetime import datetime, timedelta

import jwt
from passlib.hash import bcrypt

from app.models.user_models import BaseUser, CorporateUser, SeekerUser
from app.schemas.user_schema import LoginRequest, LoginResponse, LoginResponseData
from app.utils.exception import CustomException

ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 1
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"


# JWT 생성
def create_token(data: dict, expires_delta: timedelta) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")


# 비밀번호 검증
async def authenticate_user(email: str, password: str) -> BaseUser:
    user = await BaseUser.get_or_none(email=email)
    if not user or not bcrypt.verify(password, user.password):
        raise CustomException(
            status_code=401, error="이메일 또는 비밀번호가 일치하지 않습니다.", code="invalid_credentials"
        )
    return user


# 로그인
async def login_user(request: LoginRequest) -> LoginResponse:
    user = await authenticate_user(request.email, request.password)

    access_token = create_token(
        {"sub": str(user.id)}, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    refresh_token = create_token(
        {"sub": str(user.id)}, timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )

    # 이름 정보 가져오기 (구직자/기업 구분)
    if user.user_type == "seeker":
        profile = await SeekerUser.get(user=user)
        name = profile.name
    elif user.user_type == "business":
        profile = await CorporateUser.get(user=user)
        name = profile.company_name
    else:
        raise CustomException(
            status_code=500, error="알 수 없는 사용자 유형입니다.", code="unknown_user_type"
        )

    return LoginResponse(
        message="로그인 성공",
        data=LoginResponseData(
            access_token=access_token,
            refresh_token=refresh_token,
            user_id=user.id,
            user_type=user.user_type,
            email=user.email,
            name=name,
        ),
    )
