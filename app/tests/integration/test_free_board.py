from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient
from passlib.handlers.bcrypt import bcrypt

from app.domain.free_board.models import FreeBoard
from app.domain.user.models import BaseUser, SeekerUser
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
            is_active=True,
            status="active",
            email_verified=True,
            is_superuser=False,
            gender="male",
        )
        await SeekerUser.create(
            user=user,
            name="테스트유저",
            phone_number="01012345678",
            birth="1990-01-01",
        )

        login_data = {"email": "test@test.com", "password": "!!Test1234"}
        response = await client.post("/api/user/login/", json=login_data)

        assert response.status_code == 200
        return response.json()["data"]["access_token"]


@pytest.mark.asyncio
async def test_create_free_board(client, access_token):
    free_board = {
        "title": "test_title",
        "content": "test_content",
    }
    headers = {"Authorization": f"Bearer {access_token}"}

    response = await client.post("/api/free-board/", json=free_board, headers=headers)
    assert response.status_code == 201
    assert await FreeBoard.all().count() == 1
    assert free_board["title"] == "test_title"
    await client.post("/api/free-board/", json=free_board, headers=headers)
    await client.post("/api/free-board/", json=free_board, headers=headers)


@pytest.mark.asyncio
async def test_get_all_free_boards(client, access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    response = await client.get("/api/free-board/", headers=headers)

    assert response.status_code == 200
    assert len(response.json()) == 3


@pytest.mark.asyncio
async def test_get_free_board(client, access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    id = 1
    response = await client.get(f"/api/free-board/{id}/", headers=headers)

    assert response.status_code == 200
    assert response.json()["title"] == "test_title"
    assert response.json()["content"] == "test_content"


@pytest.mark.asyncio
async def test_patch_free_board(client, access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    id = 1
    update_data = {"title": "update_title", "content": "update_content"}
    response = await client.patch(
        f"/api/free-board/{id}/", json=update_data, headers=headers
    )
    assert response.status_code == 200
    assert response.json()["title"] == "update_title"


@pytest.mark.asyncio
async def test_delete_free_board(client, access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    id = 1
    response = await client.delete(f"/api/free-board/{id}/", headers=headers)
    assert response.status_code == 200
    assert await FreeBoard.all().count() == 2
