import os

import pytest
from dotenv import load_dotenv
from tortoise import Tortoise


@pytest.fixture(scope="session")
def event_loop():
    """pytest-asyncio에서 사용할 이벤트 루프를 생성합니다."""
    import asyncio

    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module", autouse=True)
async def setup_test_db(event_loop):
    """테스트 데이터베이스를 설정합니다."""
    await Tortoise.init(
        db_url="sqlite://:memory:",
        modules={
            "models": [
                "app.domain.chatbot.model",
                "app.domain.success_review.models",
                "app.domain.free_board.models",
                "app.domain.resume.models",
                "app.domain.comment.models",
                "app.domain.job_posting.models",
                "app.domain.user.user_models",
            ]
        },
    )
    # 스키마 생성
    await Tortoise.generate_schemas()

    yield

    # 테스트 후 연결 종료
    await Tortoise.close_connections()


load_dotenv(dotenv_path=".env.test")  # 또는 .env

# SECRET_KEY 기본값 보장 (환경 변수 없을 때)
os.environ.setdefault("SECRET_KEY", "test_secret_key_123")
