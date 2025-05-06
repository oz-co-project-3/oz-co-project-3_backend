import os
from pathlib import Path

from pydantic_settings import BaseSettings

ENV = os.getenv("ENV", "dev")

ENV_PATH = Path(__file__).resolve().parent.parent / f".envs/.{ENV}.env"


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
        env_file = ENV_PATH
        extra = "ignore"


settings = Settings()
