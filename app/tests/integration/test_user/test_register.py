import uuid
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient
from passlib.hash import bcrypt

from app.core.redis import get_redis
from app.domain.user.models import BaseUser, Gender, SeekerUser


@pytest.fixture(scope="module")
async def client(apply_redis_patch):
    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture(scope="module", autouse=True)
def apply_redis_patch():
    mock = AsyncMock()

    # email_verified 키에 대해선 항상 True 반환
    def get_side_effect(key):
        if key.startswith("email_verified:"):
            return "true"
        return None

    mock.get.side_effect = get_side_effect
    mock.set.return_value = True
    mock.delete.return_value = True

    with patch("app.core.redis.get_redis", return_value=mock):
        yield


@pytest.fixture(scope="module")
async def activated_user(client):
    email = f"test_{uuid.uuid4().hex[:6]}@test.com"
    hashed_pw = bcrypt.hash("Test1234!")
    user = await BaseUser.create(
        email=email,
        password=hashed_pw,  # bcrypt 해시된 값
        email_verified=True,
        status="active",
        user_type="normal",
        signinMethod="email",
        gender=Gender.MALE,
    )
    await SeekerUser.create(
        user=user,
        name="김이준",
        phone_number="010-1234-5678",
        birth="1994-05-16",
        interests="IT,Gaming",
        purposes="취업,자기계발",
        sources="지인추천,검색",
        status="seeking",
        profile_url=None,
    )

    return user


@pytest.fixture(scope="module")
async def access_user_token(client, activated_user):
    # 실제 암호는 평문으로 테스트 (위와 bcrypt 해시 일치해야 함)
    await client.post(
        "/api/user/login/",
        json={"email": activated_user.email, "password": "Test1234!"},
    )
    return client.cookies.get("access_token")


@pytest.mark.asyncio
async def test_register_user_success(client):
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


@pytest.mark.asyncio
async def test_register_user_duplicate_email(client):
    email = "duplicate_test@example.com"
    user_data = {
        "name": "김중복",
        "email": email,
        "password": "Test1234!",
        "password_check": "Test1234!",
        "phone_number": "010-1234-5678",
        "birth": "1990-01-01",
        "interests": "AI",
        "purposes": "취업",
        "sources": "검색",
        "status": "seeking",
        "gender": "male",
        "signinMethod": "email",
    }

    # 첫 번째 가입 시도 (정상)
    response1 = await client.post("/api/user/register/", json=user_data)
    assert response1.status_code == 201

    # 두 번째 가입 시도 (중복 이메일)
    response2 = await client.post("/api/user/register/", json=user_data)
    assert response2.status_code in (400, 409)

    response_json = response2.json()
    assert "duplicate" in response_json["message"]["code"]  # 예: duplicate_email


@pytest.mark.asyncio
async def test_login_success(client):
    await client.post(
        "/api/user/register/",
        json={
            "name": "김이준",
            "email": "login_test@example.com",
            "password": "Test1234!",
            "password_check": "Test1234!",
            "phone_number": "010-1234-5678",
            "birth": "1994-05-16",
            "gender": "male",
            "interests": "IT,Gaming",
            "purposes": "취업,자기계발",
            "sources": "지인추천,검색",
            "status": "seeking",
            "signinMethod": "email",
        },
    )
    user = await BaseUser.get(email="login_test@example.com")
    user.email_verified = True
    user.status = "active"
    await user.save()

    response = await client.post(
        "/api/user/login/",
        json={
            "email": "login_test@example.com",
            "password": "Test1234!",
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["email"] == "login_test@example.com"
    assert data["name"] == "김이준"
    assert data["user_type"] == "normal"
    assert isinstance(data["user_id"], int)
    assert "access_token" in data


@pytest.mark.asyncio
async def test_register_without_email_verification(client):
    email = "not_verified@example.com"

    user_data = {
        "name": "인증안됨",
        "email": email,
        "password": "Test1234!",
        "password_check": "Test1234!",
        "phone_number": "010-0000-0000",
        "birth": "1999-09-09",
        "interests": "IT",
        "purposes": "취업",
        "sources": "SNS",
        "status": "seeking",
        "gender": "male",
        "signinMethod": "email",
    }

    mock_redis = AsyncMock()
    mock_redis.get.return_value = None
    mock_redis.set.return_value = True

    with patch(
        "app.domain.user.services.user_register_services.get_redis",
        return_value=mock_redis,
    ):
        response = await client.post("/api/user/register/", json=user_data)

    assert response.status_code == 403
    response_json = response.json()
    assert response_json["message"]["code"] == "unverified_or_inactive_account"


@pytest.mark.asyncio
async def test_register_with_verified_email(client):
    email = "verified_test@example.com"

    user_data = {
        "name": "이메일인증됨",
        "email": email,
        "password": "Test1234!",
        "password_check": "Test1234!",
        "phone_number": "010-1111-2222",
        "birth": "1990-10-10",
        "interests": "백엔드",
        "purposes": "취업",
        "sources": "검색",
        "status": "seeking",
        "gender": "male",
        "signinMethod": "email",
    }

    # Redis mock 설정 (인증 완료 상태)
    mock_redis = AsyncMock()
    mock_redis.get.return_value = "true"
    mock_redis.set.return_value = True

    # 정확한 경로로 patch 해야 제대로 작동
    with patch(
        "app.domain.user.services.user_register_services.get_redis",
        return_value=mock_redis,
    ):
        response = await client.post("/api/user/register/", json=user_data)

    assert response.status_code == 201
    res_json = response.json()
    assert res_json["base"]["email"] == email
    assert res_json["seeker"]["name"] == "이메일인증됨"


@pytest.mark.asyncio
async def test_upgrade_to_corporate_user(client, access_user_token, activated_user):
    headers = {"Authorization": f"Bearer {access_user_token}"}
    user = activated_user

    upgrade_payload = {
        "business_number": "1248100998",
        "company_name": "테스트회사",
        "manager_name": "김이사",
        "manager_phone_number": "010-9999-0000",
        "manager_email": "ceo@example.com",
        "profile_url": "http://cdn.example.com/logo.png",
        "business_start_date": "2022-01-01",
    }
    response = await client.post(
        "/api/user/upgrade-to-business/",
        headers=headers,
        json=upgrade_payload,
    )

    response_json = response.json()

    assert response.status_code == 200
    assert "access_token" in response_json
    assert response_json["user_type"] == "business,normal"
    assert response_json["email"] == user.email


@pytest.mark.asyncio
async def test_logout_user_success(client, access_user_token):
    headers = {"Authorization": f"Bearer {access_user_token}"}

    response = await client.post("/api/user/logout/", headers=headers)

    assert response.status_code == 200
    assert response.json()["message"] == "로그아웃이 완료되었습니다."

    # redis = get_redis()
    # is_blacklisted = await redis.get(f"blacklist:{access_user_token}")
    # assert is_blacklisted.decode() == "true"
