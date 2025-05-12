import copy

import pytest
from httpx import ASGITransport, AsyncClient
from passlib.handlers.bcrypt import bcrypt

from app.domain.resume.models import Resume
from app.domain.user.models import BaseUser, SeekerUser


@pytest.fixture(scope="module")
async def client(apply_redis_patch):
    from app.main import app

    transport = ASGITransport(app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture(scope="module")
async def access_token(client):
    hashed_pw = bcrypt.hash("!Test1234")
    user = await BaseUser.create(
        email="test@test.com",
        password=hashed_pw,
        user_type="normal,admin",
        signinMethod="email",
        status="active",
        email_verified=True,
        gender="male",
    )
    seeker = await SeekerUser.create(
        user=user,
        name="테스트유저",
        phone_number="01012341235",
        birth="1990-01-01",
        interest="프론트엔드",
        purpose="취업",
        sources="지인추천",
    )

    login_data = {"email": "test@test.com", "password": "!Test1234"}
    response = await client.post("/api/user/login/", json=login_data)

    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.mark.asyncio
async def test_create_resume(client, access_token):
    test_resume = {
        "title": "테스트 이력서",
        "visibility": True,
        "name": "홍길동",
        "phone_number": "010-1234-5678",
        "email": "hong@example.com",
        "desired_area": "서울",
        "introduce": "테스트 이력서 소개입니다.",
        "status": "작성중",
        "work_experiences": [
            {"company": "테스트회사", "period": "2020-2021", "position": "개발자"}
        ],
    }
    headers = {"Authorization": f"Bearer {access_token}"}

    response = await client.post("/api/resume/", json=test_resume, headers=headers)
    assert response.status_code == 201
    assert await Resume.all().count() == 1
    assert test_resume["title"] == "테스트 이력서"
    await client.post("/api/resume/", json=test_resume, headers=headers)

    test_resume2 = copy.deepcopy(test_resume)
    test_resume2["title"] = "테스트 이력서2"
    second_response = await client.post(
        "/api/resume/", json=test_resume2, headers=headers
    )
    assert second_response.status_code == 201
    resume_count = await Resume.all().count()
    assert resume_count == 2


@pytest.mark.asyncio
async def test_get_all_resume(client, access_token):
    header = {"Authorization": f"Bearer {access_token}"}
    response = await client.get("/api/resume/", headers=header)

    assert response.status_code == 200
    json_data = response.json()
    assert len(json_data["data"]) == 2


@pytest.mark.asyncio
async def test_get_resume(client, access_token):
    header = {"Authorization": f"Bearer {access_token}"}
    resume_id = 1
    response = await client.get(f"/api/resume/{resume_id}/", headers=header)

    assert response.status_code == 200
    assert response.json()["title"] == "테스트 이력서"


@pytest.mark.asyncio
async def test_update_resume(client, access_token):
    header = {"Authorization": f"Bearer {access_token}"}
    resume_id = 1
    update_data = {
        "title": "updated_title",
        "visibility": True,
        "name": "홍길동",
        "phone_number": "010-1234-5678",
        "email": "hong@example.com",
        "desired_area": "서울",
        "introduce": "테스트 이력서 소개입니다.",
        "status": "구직중",
    }
    response = await client.patch(
        f"/api/resume/{resume_id}/", json=update_data, headers=header
    )
    assert response.status_code == 200
    assert response.json()["title"] == "updated_title"


@pytest.mark.asyncio
async def test_delete_resume(client, access_token):
    header = {"Authorization": f"Bearer {access_token}"}
    resume_id = 1
    response = await client.delete(f"/api/resume/{resume_id}/", headers=header)
    assert response.status_code == 200
    assert await Resume.all().count() == 1
