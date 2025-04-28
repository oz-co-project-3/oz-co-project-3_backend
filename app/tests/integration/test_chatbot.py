from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient
from passlib.handlers.bcrypt import bcrypt

from app.domain.chatbot.model import ChatBot
from app.domain.user.user_models import BaseUser, CorporateUser, SeekerUser
from app.main import app


@pytest.fixture(scope="module")
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture(scope="module")
async def access_token(client):
    mock_set = AsyncMock(return_value=True)
    mock_get = AsyncMock(return_value=None)

    with (
        patch("app.core.redis.redis.set", mock_set),
        patch("app.core.redis.redis.get", mock_get),
    ):
        hashed_pw = bcrypt.hash("!!Test1234")  # 서비스에서 쓰는 방식 확인 필수!
        user = await BaseUser.create(
            email="test@test.com",
            password=hashed_pw,
            user_type="seeker",
            status="active",
            email_verified=True,
            is_superuser=True,
            gender="male",
        )
        await SeekerUser.create(
            user=user,
            name="테스트유저",
            phone_number="01012345678",
            birth="1990-01-01",
            interests="프론트엔드",
            purposes="취업",
            sources="지인 추천",
        )
        user2 = await BaseUser.create(
            email="test2@test.com",
            password=hashed_pw,
            user_type="business",
            status="active",
            email_verified=True,
            is_superuser=False,
            gender="male",
        )
        await CorporateUser.create(
            user=user2,
            company_name="테스트 주식회사",
            business_start_date="2010-01-01",
            business_number="123-45-67890",
            company_description="테스트 기업 설명입니다.",
            manager_name="홍길동",
            manager_phone_number="01012345678",
            manager_email="manager@test.com",
            gender="male",
        )

        login_data = {"email": "test@test.com", "password": "!!Test1234"}
        response = await client.post("/api/user/login/", json=login_data)
        access_token = [response.json()["data"]["access_token"]]

        login_data = {"email": "test2@test.com", "password": "!!Test1234"}
        response = await client.post("/api/user/login/", json=login_data)
        access_token.append(response.json()["data"]["access_token"])

        return access_token


@pytest.mark.asyncio
async def test_admin_create_chatbot(client, access_token):
    headers = {"Authorization": f"Bearer {access_token[0]}"}
    data = {
        "step": "3",
        "is_terminate": False,
        "selection_path": "기업/회원가입",
        "options": "선택1,선택2",
        "answer": "답변",
    }
    response = await client.post("/api/admin/chatbot/", json=data, headers=headers)

    assert response.status_code == 201
    assert response.json()["step"] == 3
    assert response.json()["is_terminate"] == False
    assert response.json()["selection_path"] == "기업/회원가입"
    assert response.json()["options"] == "선택1,선택2"
    assert response.json()["answer"] == "답변"

    await client.post("/api/admin/chatbot/", json=data, headers=headers)
    await client.post("/api/admin/chatbot/", json=data, headers=headers)

    assert await ChatBot.all().count() == 3

    headers = {"Authorization": f"Bearer {access_token[1]}"}
    response = await client.post("/api/admin/chatbot/", json=data, headers=headers)

    assert response.status_code == 403
    assert response.json()["message"]["code"] == "permission_denied"


@pytest.mark.asyncio
async def test_admin_get_chatbot(client, access_token):
    headers = {"Authorization": f"Bearer {access_token[0]}"}
    response = await client.get("/api/admin/chatbot/", headers=headers)

    assert response.status_code == 200
    assert len(response.json()) == 3


@pytest.mark.asyncio
async def test_admin_update_chatbot(client, access_token):
    headers = {"Authorization": f"Bearer {access_token[0]}"}
    data = {
        "step": "3",
        "is_terminate": False,
        "selection_path": "기업/회원가입",
        "answer": "답변 수정",
    }
    id = 1
    response = await client.patch(
        f"/api/admin/chatbot/{id}/", json=data, headers=headers
    )

    assert response.status_code == 200
    assert response.json()["answer"] == "답변 수정"


@pytest.mark.asyncio
async def test_delete_chatbot(client, access_token):
    headers = {"Authorization": f"Bearer {access_token[0]}"}
    id = 1
    response = await client.delete(f"/api/admin/chatbot/{id}/", headers=headers)

    assert response.status_code == 200
    assert await ChatBot.all().count() == 2
