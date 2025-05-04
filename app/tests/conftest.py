import os

import pytest
from tortoise import Tortoise


@pytest.fixture(scope="session")
def event_loop():
    """pytest-asyncio에서 사용할 이벤트 루프를 생성합니다."""
    import asyncio

    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


DB_NAME = "test_senior"
DB_USER = "postgres"
DB_PASSWORD = "1q2w3e4r"
DB_HOST = "localhost"
DB_PORT = "5432"


@pytest.fixture(scope="module", autouse=True)
async def setup_test_db(event_loop):
    """테스트 데이터베이스를 설정합니다."""
    # 먼저 기본 데이터베이스에 연결하여 테스트 데이터베이스를 생성/삭제할 수 있게 함
    await Tortoise.init(
        db_url=f"postgres://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/postgres",
        modules={"models": []},  # 빈 모듈 목록이라도 제공
    )

    # 기존 테스트 데이터베이스 삭제 (있는 경우)
    conn = Tortoise.get_connection("default")
    try:
        await conn.execute_script(f"DROP DATABASE IF EXISTS {DB_NAME}")
    except Exception as e:
        pass

    # 테스트 데이터베이스 생성
    try:
        await conn.execute_script(f"CREATE DATABASE {DB_NAME}")
    except Exception as e:
        pass

    await Tortoise.close_connections()

    # 테스트 데이터베이스에 연결
    await Tortoise.init(
        db_url=f"postgres://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
        modules={
            "models": [
                "app.domain.chatbot.model",
                "app.domain.success_review.models",
                "app.domain.free_board.models",
                "app.domain.resume.models",
                "app.domain.comment.models",
                "app.domain.job_posting.models",
                "app.domain.user.models",
            ]
        },
    )

    await Tortoise.generate_schemas()
    yield
    await Tortoise.close_connections()


# SECRET_KEY 기본값 보장 (환경 변수 없을 때)
os.environ.setdefault("SECRET_KEY", "test_secret_key_123")
