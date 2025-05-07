from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient


@pytest.fixture(scope="module")
async def client():
    from app.main import app  # FastAPI 앱 가져오기

    transport = ASGITransport(app=app)

    with (
        patch("app.core.redis.redis.get", new_callable=AsyncMock) as mock_get,
        patch("app.core.redis.redis.set", new_callable=AsyncMock) as mock_set,
        patch("app.core.redis.redis.delete", new_callable=AsyncMock) as mock_delete,
        patch("app.domain.user.services.email_services.send_email", return_value=None),
    ):
        mock_get.return_value = "123456"
        mock_set.return_value = True
        mock_delete.return_value = True

        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac


@pytest.mark.asyncio
async def test_register_user_success():
    from app.main import app

    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/user/register/",
            json={
                "name": "김이준",
                "email": "test_register@example.com",
                "password": "Test1234!",
                "password_check": "Test1234!",
                "phone_number": "010-1234-5678",
                "birth": "1994-05-16",
                "interests": "IT,Gaming",
                "purposes": "취업,자기계발",
                "sources": "지인추천,검색",
                "status": "seeking",
                "gender": "male",
                "signinMethod": "email",
            },
        )

        # 응답 상태코드 확인
        assert response.status_code == 201

        # 응답 데이터 구조 확인
        json_data = response.json()

        assert json_data["base"]["email"] == "test_register@example.com"
        assert json_data["base"]["user_type"] == "normal"
        assert json_data["base"]["signinMethod"] == "email"
        assert json_data["seeker"]["name"] == "김이준"
        assert json_data["corp"] is None
