import os
from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings

ENV = os.getenv("ENV", "dev")
TESTING = os.getenv("TESTING", "false").lower() == "true"


def get_env_path():
    base_path = Path(__file__).resolve().parent.parent.parent / ".envs"
    if TESTING:
        return base_path / ".test.env"
    return base_path / f".{ENV}.env"


class Settings(BaseSettings):
    # DB 설정
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str

    # 네이버 SMTP
    SMTP_USER: str
    SMTP_PASSWORD: str
    SMTP_SERVER: str
    SMTP_PORT: str

    # JWT
    SECRET_KEY: str

    # Redis 설정
    REDIS_HOST: str
    REDIS_PORT: str

    # 공공 포털 - 사업자 등록증 확인 API
    BIZINFO_API_KEY: str

    # AWS
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str
    S3_BUCKET_NAME: str

    # DOMAIN & SCHEME(DEV)
    URL_SCHEME: str
    DOMAIN: str

    # 카카오 로그인
    KAKAO_CLIENT_ID: str
    KAKAO_REDIRECT_URI: str
    KAKAO_CLIENT_SECRET: str

    # 네이버 로그인
    NAVER_CLIENT_ID: str
    NAVER_CLIENT_SECRET: str
    NAVER_REDIRECT_URI: str
    NAVER_STATE: str

    class Config:
        env_file = get_env_path()
        extra = "ignore"


# 테스트용 더미 설정 클래스
class TestSettings(BaseSettings):
    # DB 설정
    POSTGRES_DB: str = "test_senior"
    POSTGRES_USER: str = "test_user"
    POSTGRES_PASSWORD: str = "test_password"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: str = "5432"

    # 네이버 SMTP
    SMTP_USER: str = "test_smtp_user"
    SMTP_PASSWORD: str = "test_smtp_password"
    SMTP_SERVER: str = "test.smtp.server"
    SMTP_PORT: str = "587"

    # JWT
    SECRET_KEY: str = "test_secret_key_123"

    # Redis 설정
    REDIS_HOST: str = "localhost"
    REDIS_PORT: str = "6379"

    # 공공 포털 - 사업자 등록증 확인 API
    BIZINFO_API_KEY: str = "test_bizinfo_api_key"

    # AWS
    AWS_ACCESS_KEY_ID: str = "test_aws_access_key"
    AWS_SECRET_ACCESS_KEY: str = "test_aws_secret_key"
    AWS_REGION: str = "ap-northeast-2"
    S3_BUCKET_NAME: str = "test-bucket"

    # DOMAIN & SCHEME(DEV)
    URL_SCHEME: str = "http"
    DOMAIN: str = "localhost:8000"

    # 카카오 로그인
    KAKAO_CLIENT_ID: str = "test_kakao_client_id"
    KAKAO_REDIRECT_URI: str = "http://localhost:8000/callback"
    KAKAO_CLIENT_SECRET: str = "test_kakao_client_secret"

    # 네이버 로그인
    NAVER_CLIENT_ID: str = "test_naver_client_id"
    NAVER_CLIENT_SECRET: str = "test_naver_client_secret"
    NAVER_REDIRECT_URI: str = "http://localhost:8000/callback"
    NAVER_STATE: str = "test_state"

    class Config:
        env_file = None  # 환경 파일 사용하지 않음
        extra = "ignore"


@lru_cache()
def get_settings():
    """설정을 가져오는 함수"""
    if TESTING:
        return TestSettings()
    return Settings()


# 기본 설정 인스턴스 생성
settings = get_settings()
