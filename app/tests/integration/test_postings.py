import pytest
from httpx import ASGITransport, AsyncClient
from passlib.handlers.bcrypt import bcrypt

from app.domain.job_posting.models import Applicants, JobPosting
from app.domain.resume.models import Resume
from app.domain.user.models import BaseUser, CorporateUser, SeekerUser


@pytest.fixture(scope="module")
async def client(apply_redis_patch):
    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture(scope="module")
async def access_token(client):
    hashed_pw = bcrypt.hash("!!Test1234")
    user = await BaseUser.create(
        email="test@test.com",
        password=hashed_pw,
        signinMethod="email",
        user_type="normal,business",
        status="active",
        email_verified=True,
        gender="male",
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

    login_data = {"email": "test@test.com", "password": "!!Test1234"}
    response = await client.post("/api/user/login/", json=login_data)
    access_token = response.json()["access_token"]

    return access_token


@pytest.mark.asyncio
async def test_get_list_postings(client: AsyncClient, access_token: str):
    headers = {"Authorization": f"Bearer {access_token}"}
    response = await client.get("/api/postings/", headers=headers)

    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert len(response.json()["data"]) == 1


@pytest.mark.asyncio
async def test_get_list_postings_with_keyword(client: AsyncClient, access_token: str):
    headers = {"Authorization": f"Bearer {access_token}"}
    response = await client.get("/api/postings/?search_keyword=백엔드", headers=headers)
    assert response.status_code == 200
    assert any("백엔드" in item["title"] for item in response.json()["data"])


@pytest.mark.asyncio
async def test_get_list_postings_with_employment_type(
    client: AsyncClient, access_token: str
):
    headers = {"Authorization": f"Bearer {access_token}"}
    response = await client.get("/api/postings/?employment_type=공공,일반", headers=headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_list_postings_with_career(client: AsyncClient, access_token: str):
    headers = {"Authorization": f"Bearer {access_token}"}
    response = await client.get("/api/postings/?career=신입,경력직", headers=headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_list_postings_with_employ_method(
    client: AsyncClient, access_token: str
):
    headers = {"Authorization": f"Bearer {access_token}"}
    response = await client.get("/api/postings/?employ_method=정규직,계약직", headers=headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_list_postings_with_invalid_employment_type(
    client: AsyncClient, access_token: str
):
    headers = {"Authorization": f"Bearer {access_token}"}
    response = await client.get("/api/postings/?employment_type=비정규", headers=headers)
    assert response.status_code == 400
    assert response.json()["message"]["code"] == "invalid_employment_type"


@pytest.mark.asyncio
async def test_get_list_postings_with_limit_over_100(
    client: AsyncClient, access_token: str
):
    headers = {"Authorization": f"Bearer {access_token}"}
    response = await client.get("/api/postings/?limit=101", headers=headers)
    assert response.status_code == 400
    assert response.json()["message"]["code"] == "invalid_limit"


@pytest.mark.asyncio
async def test_get_posting(client: AsyncClient, access_token: str):
    headers = {"Authorization": f"Bearer {access_token}"}
    response = await client.get("/api/postings/1/", headers=headers)

    assert response.status_code == 200
    assert response.json()["title"] == "백엔드 개발자"


@pytest.mark.asyncio
async def test_create_posting_applicant(client: AsyncClient, access_token: str):
    headers = {"Authorization": f"Bearer {access_token}"}
    applicant = {"resume": 1, "status": "지원 중"}
    response = await client.post(
        "/api/postings/1/applicant/", headers=headers, json=applicant
    )

    assert response.status_code == 201
    assert await Applicants.all().count() == 2


@pytest.mark.asyncio
async def test_patch_posting_applicant(client: AsyncClient, access_token: str):
    headers = {"Authorization": f"Bearer {access_token}"}
    patch_applicant = {"resume": 1, "status": "지원 취소"}
    response = await client.patch(
        "/api/postings/1/applicant/1/", headers=headers, json=patch_applicant
    )
    print("RESPONSE JSON", response.json())
    assert response.status_code == 200
