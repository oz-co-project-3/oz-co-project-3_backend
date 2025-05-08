import copy

import pytest
from httpx import ASGITransport, AsyncClient
from passlib.handlers.bcrypt import bcrypt

from app.domain.job_posting.models import Applicants, JobPosting
from app.domain.resume.models import Resume
from app.domain.user.models import BaseUser, CorporateUser, SeekerUser


@pytest.fixture(scope="module")
async def client(apply_redis_patch):
    from app.main import app

    transport = ASGITransport(app)
    async with AsyncClient(
        transport=transport, base_url="http://test", follow_redirects=True
    ) as client:
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

    posting = await JobPosting.create(
        user=corp_user,
        title="백엔드 개발자",
        company="테스트컴퍼니",
        location="서울",
        employment_type="일반",
        position="백엔드",
        career="경력직",
        education="학사",
        employ_method="정규직",
        work_time="time",
        deadline="2020-01-01",
        salary="급여",
        description="설명",
        view_count=100,
        summary="test",
        history="test",
    )
    resume = await Resume.create(
        user=seeker_user,
        title="이력서",
        name="TEST",
        phone_number="01012345678",
        email="test@email.com",
        desired_area="서울",
        status="구직중",
    )
    await Applicants.create(
        job_posting=posting, resume=resume, user=user, status="지원 중"
    )

    login_data = {"email": "test@test.com", "password": "!Test1234"}
    response = await client.post("/api/user/login/", json=login_data)

    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.mark.asyncio
async def test_applicant_corp(client, access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    job_posting_id = 1
    response = await client.get(
        f"/api/applicants/corporate/{job_posting_id}/", headers=headers
    )
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

    assert "id" in data[0]
    assert isinstance(data[0]["id"], int)


@pytest.mark.asyncio
async def test_applicant_all_corp(client, access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    response = await client.get("/api/applicants/corporate/", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 1


@pytest.mark.asyncio
async def test_applicant_all_seeker(client, access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    response = await client.get("/api/applicants/seeker/", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 1


@pytest.mark.asyncio
async def test_applicant_seeker(client, access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    id = 1
    response = await client.get(f"/api/applicants/seeker/{id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "id" in data
    assert isinstance(data["id"], int)

    assert "job_title" in data, "응답 데이터에 'job_title' 키가 존재하지 않습니다."
    assert isinstance(data["job_title"], str), "'job_title'은 문자열이어야 합니다."
