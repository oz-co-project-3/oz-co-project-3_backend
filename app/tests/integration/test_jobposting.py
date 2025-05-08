import copy

import pytest
from httpx import ASGITransport, AsyncClient
from passlib.handlers.bcrypt import bcrypt

from app.domain.job_posting.models import JobPosting
from app.domain.user.models import BaseUser, CorporateUser, SeekerUser


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
        user_type="normal,business",
        signinMethod="email",
        status="active",
        email_verified=True,
        gender="male",
    )

    corp_user = await CorporateUser.create(
        user=user,
        company_name="테스트 주식회사",
        business_start_date="2010-01-01",
        business_number="123-45-67890",
        company_description="테스트 기업 설명입니다.",
        manager_name="홍길동",
        manager_phone_number="01012345678",
        manager_email="manager@test.com",
    )
    seeker_user = await SeekerUser.create(
        user=user,
        name="테스트유저",
        phone_number="01012345678",
        birth="1990-01-01",
        interests="프론트엔드",
        purposes="취업",
        sources="지인 추천",
    )

    login_data = {"email": "test@test.com", "password": "!Test1234"}
    response = await client.post("/api/user/login/", json=login_data)

    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.mark.asyncio
async def test_job_posting(client, access_token):
    test_jobposting = {
        "company": "테스트 주식회사",
        "title": "개발자 모집 공고",
        "location": "서울",
        "employment_type": "일반",
        "career": "경력직",
        "employ_method": "정규직",
        "work_time": "9시간",
        "position": "사원",
        "history": "test",
        "recruitment_count": 0,
        "education": "대졸",
        "salary": "면접 후 결정",
        "deadline": "2025-04-30",
        "summary": "test",
        "description": "test",
        "status": "모집중",
    }
    headers = {"Authorization": f"Bearer {access_token}"}
    response = await client.post(
        "/api/job_posting/", json=test_jobposting, headers=headers
    )
    assert response.status_code == 201
    assert await JobPosting.all().count() == 1
    assert test_jobposting["title"] == "개발자 모집 공고"
    await client.post(
        "/api/job_posting/", json=test_jobposting, headers=headers
    )  # 중복된 제목으로 실패됨

    test_jobposting2 = copy.deepcopy(test_jobposting)
    test_jobposting2["title"] = "개발자 모집 공고 2"
    second_response = await client.post(
        "/api/job_posting/", json=test_jobposting2, headers=headers
    )
    assert second_response.status_code == 201
    assert await JobPosting.all().count() == 2


@pytest.mark.asyncio
async def test_job_posting_get(client, access_token):
    header = {"Authorization": f"Bearer {access_token}"}
    response = await client.get("api/job_posting/", headers=header)

    assert response.status_code == 200
    assert len(response.json()) == 2  # 중복 제목으로 인해 실패 1, 제목 변경으로 성공 1 총 2개임


@pytest.mark.asyncio
async def test_job_posting_detail(client, access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    id = 1
    response = await client.get(f"api/job_posting/{id}/", headers=headers)
    assert response.status_code == 200
    assert response.json()["title"] == "개발자 모집 공고"


@pytest.mark.asyncio
async def test_job_posting_update(client, access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    id = 1
    update_data = {
        "company": "테스트 주식회사",
        "title": "개발자 모집 공고",
        "location": "서울",
        "employment_type": "일반",
        "career": "경력직",
        "employ_method": "계약직",
        "work_time": "10시에서 7시",
        "position": "사원",
        "history": "test",
        "recruitment_count": 0,
        "education": "대졸",
        "salary": "면접 후 결정",
        "deadline": "2025-04-30",
        "summary": "test",
        "description": "test",
        "status": "모집중",
    }
    response = await client.patch(
        f"api/job_posting/{id}/", json=update_data, headers=headers
    )
    assert response.status_code == 200
    assert response.json()["title"] == "개발자 모집 공고"
    assert response.json()["employ_method"] == "계약직"


@pytest.mark.asyncio
async def test_job_posting_delete(client, access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    id = 1
    response = await client.delete(f"api/job_posting/{id}/", headers=headers)


@pytest.mark.asyncio
async def test_job_posting_bookmark(client, access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    id = 3
    url = f"/api/job_posting/{id}/bookmark/"

    # 초기상태로 설정
    init_response = await client.post(url, headers=headers)
    init_message = init_response.json().get("message")
    # 이미 북마크 등록되어 있을 경우 한번 더 실행해서 해제 상태로 만듬
    if init_message == "북마크가 추가되었습니다.":
        await client.post(url, headers=headers)
    # 북마크가 추가되지 않은 상태를 가정하고 테스트 진행

    # 추가되어야함
    response = await client.post(url, headers=headers)
    assert response.status_code == 200
    json_data = response.json()
    first_message = json_data.get("message")

    assert first_message == "북마크가 추가되었습니다."

    # 해제되어야함
    response2 = await client.post(url, headers=headers)
    assert response2.status_code == 200
    second_message = response2.json().get("message")

    assert second_message == "북마크가 해제되었습니다."
