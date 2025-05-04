# from unittest.mock import AsyncMock, patch
#
# import pytest
# from httpx import ASGITransport, AsyncClient
#
# from app.main import app
#
# transport = ASGITransport(app=app)
#
#
# # 모든 테스트에서 Redis mock이 전역으로 작동 + 메일 mock 추가
# @pytest.fixture(scope="module")
# async def client():
#     with (
#         patch("app.core.redis.redis.get", new_callable=AsyncMock) as mock_get,
#         patch("app.core.redis.redis.set", new_callable=AsyncMock) as mock_set,
#         patch("app.core.redis.redis.delete", new_callable=AsyncMock) as mock_delete,
#         patch("app.domain.user.services.email_services.send_email", return_value=None),
#     ):
#         mock_get.return_value = "123456"
#         mock_set.return_value = True
#         mock_delete.return_value = True
#
#         async with AsyncClient(transport=transport, base_url="http://test") as client:
#             yield client
#
#
# @pytest.mark.asyncio
# async def test_user_register_success(client):
#     response = await client.post(
#         "/api/user/register/",
#         json={
#             "name": "등록유저",
#             "email": "register_test@example.com",
#             "password": "1234!1234!",
#             "password_check": "1234!1234!",
#             "phone_number": "01012345678",
#             "birth": "1995-05-16",
#             "interests": ["개발", "AI"],
#             "purposes": ["취업"],
#             "sources": ["유튜브"],
#             "status": "seeking",
#             "gender": "male",
#         },
#     )
#
#     assert response.status_code == 201
#
#
# @pytest.mark.asyncio
# async def test_user_register_email_duplicate(client):
#     # 첫 등록
#     await client.post(
#         "/api/user/register/",
#         json={
#             "name": "중복유저",
#             "email": "duplicate_test@example.com",
#             "password": "1234!1234!",
#             "password_check": "1234!1234!",
#             "phone_number": "01012345678",
#             "birth": "1995-05-16",
#             "interests": ["AI"],
#             "purposes": ["테스트"],
#             "sources": ["지인"],
#             "status": "seeking",
#             "gender": "male",
#         },
#     )
#
#     # 중복 등록 시도
#     response = await client.post(
#         "/api/user/register/",
#         json={
#             "name": "중복유저",
#             "email": "duplicate_test@example.com",
#             "password": "1234!1234!",
#             "password_check": "1234!1234!",
#             "phone_number": "01012345678",
#             "birth": "1995-05-16",
#             "interests": ["AI"],
#             "purposes": ["테스트"],
#             "sources": ["지인"],
#             "status": "seeking",
#             "gender": "male",
#         },
#     )
#
#     assert response.status_code == 400
#     assert response.json()["message"]["code"] == "duplicate_email"
#
#
# @pytest.mark.asyncio
# async def test_user_register_password_mismatch(client):
#     response = await client.post(
#         "/api/user/register/",
#         json={
#             "name": "비번불일치",
#             "email": "pw_mismatch_test@example.com",
#             "password": "1234!1234!",
#             "password_check": "wrongpassword",
#             "phone_number": "01099998888",
#             "birth": "1993-03-03",
#             "interests": ["테스트"],
#             "purposes": ["검증"],
#             "sources": ["블로그"],
#             "status": "seeking",
#             "gender": "male",
#         },
#     )
#
#     assert response.status_code == 400
#     assert response.json()["message"]["code"] == "password_mismatch"
#
#
# @pytest.mark.asyncio
# async def test_company_register_success(client):
#     response = await client.post(
#         "/api/user/register-company/",
#         json={
#             "email": "bizuser@example.com",
#             "password": "1234!1234!",
#             "password_check": "1234!1234!",
#             "company_name": "테스트회사",
#             "business_number": "123-45-67890",
#             "business_start_date": "2020-01-01T00:00:00",
#             "company_description": "AI 서비스 기업",
#             "manager_name": "김매니저",
#             "manager_phone_number": "01098765432",
#             "manager_email": "manager@example.com",
#             "gender": "female",
#         },
#     )
#
#     assert response.status_code == 201
#     assert response.json()["data"]["email"] == "bizuser@example.com"
