# from unittest.mock import AsyncMock, patch
#
# import pytest
# from httpx import ASGITransport, AsyncClient
# from passlib.hash import bcrypt
#
# from app.domain.user.models import BaseUser, SeekerUser
#
#
# @pytest.fixture(scope="module")
# async def client():
#     from app.main import app
#
#     transport = ASGITransport(app=app)
#     async with AsyncClient(transport=transport, base_url="http://test") as ac:
#         yield ac
#
#
# @pytest.fixture
# async def access_token(client):
#     hashed_pw = bcrypt.hash("1234!1234!")
#
#     user = await BaseUser.create(
#         email="profile_test@example.com",
#         password=hashed_pw,
#         user_type="seeker",
#         status="active",
#         email_verified=True,
#         gender="male",
#         signin_method="email",
#     )
#     await SeekerUser.create(
#         user=user,
#         name="프로필유저",
#         phone_number="01000001111",
#         birth="1990-01-01",
#         interests="테스트",
#         purposes="취업",
#         sources="유튜브",
#     )
#
#     with patch(
#         "app.domain.user.services.auth_services.redis.set", new_callable=AsyncMock
#     ):
#         response = await client.post(
#             "/api/user/login/",
#             json={"email": "profile_test@example.com", "password": "1234!1234!"},
#         )
#
#     return response.json()["data"]["access_token"]
#
#
# @pytest.mark.asyncio
# async def test_get_profile_success(client, access_token):
#     headers = {"Authorization": f"Bearer {access_token}"}
#     response = await client.get("/api/user/profile/", headers=headers)
#
#     assert response.status_code == 200
#     data = response.json()["data"]
#     assert data["email"] == "profile_test@example.com"
#     assert data["name"] == "프로필유저"
