from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient
from passlib.handlers.bcrypt import bcrypt

from app.domain.admin.schemas.admin_job_posting_schemas import EmploymentEnum
from app.domain.job_posting.job_posting_models import (
    JobPosting,
    MethodEnum,
    RejectPosting,
    StatusEnum,
)
from app.domain.resume.resume_models import Resume, WorkExp
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
        seeker = await SeekerUser.create(
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
        corp_user = await CorporateUser.create(
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

        resume = await Resume.create(
            user=seeker,
            title="테스트 이력서",
            visibility=True,
            name="테스터",
            phone_number="01012345678",
            email="resume@test.com",
            interests="백엔드 개발",
            desired_area="서울",
            education="대졸",
            school_name="테스트대학교",
            graduation_status="졸업",
            introduce="이력서 소개글입니다.",
        )
        await WorkExp.create(
            resume=resume,
            company="테스트 회사",
            period="2020-2022",
            position="백엔드 개발자",
        )
        await Resume.create(
            user=seeker,
            title="테스트 이력서2",
            visibility=True,
            name="테스터2",
            phone_number="01012345678",
            email="resume@test.com",
            interests="백엔드 개발",
            desired_area="서울",
            education="대졸",
            school_name="테스트대학교",
            graduation_status="졸업",
            introduce="이력서 소개글입니다.",
        )
        job_posting = await JobPosting.create(
            user=corp_user,
            company="테스트 주식회사",
            title="백엔드 개발자 채용",
            location="서울 강남구",
            employment_type=EmploymentEnum.General,
            employ_method=MethodEnum.Permanent,  # ✅ 이 필드도 누락 시 에러날 수 있음
            work_time="09:00~18:00",  # ✅ 추가!
            position="백엔드 개발자",
            history="경력 3년 이상",
            recruitment_count=2,
            education="대졸",
            deadline="2025-05-01",
            salary="4000",
            summary="백엔드 개발 채용 요약",
            description="백엔드 개발 관련 상세 업무 내용",
            status=StatusEnum.Pending,
        )

        await RejectPosting.create(
            job_posting=job_posting,
            user=user,
            content="기업 정보가 부족합니다.",
        )

        await JobPosting.create(
            user=corp_user,
            company="테스트 주식회사2",
            title="백엔드 개발자 채2용",
            location="서울 강남구",
            employment_type=EmploymentEnum.General,
            employ_method=MethodEnum.Permanent,  # ✅ 이 필드도 누락 시 에러날 수 있음
            work_time="09:00~18:00",  # ✅ 추가!
            position="백엔드 개발자",
            history="경력 3년 이상",
            recruitment_count=2,
            education="대졸",
            deadline="2025-05-01",
            salary="4000",
            summary="백엔드 개발 채용 요약",
            description="백엔드 2개발 관련 상세 업무 내용",
            status=StatusEnum.Pending,
        )

        login_data = {"email": "test@test.com", "password": "!!Test1234"}
        response = await client.post("/api/user/login/", json=login_data)
        access_token = [response.json()["data"]["access_token"]]

        login_data = {"email": "test2@test.com", "password": "!!Test1234"}
        response = await client.post("/api/user/login/", json=login_data)
        access_token.append(response.json()["data"]["access_token"])

        return access_token


@pytest.mark.asyncio
async def test_admin_get_list_user(client, access_token):
    headers = {"Authorization": f"Bearer {access_token[0]}"}
    response = await client.get("/api/admin/user/", headers=headers)

    assert response.status_code == 200
    assert await BaseUser.all().count() == 2

    headers = {"Authorization": f"Bearer {access_token[1]}"}
    response = await client.get("/api/admin/user/", headers=headers)
    assert response.status_code == 403
    assert response.json()["message"]["code"] == "permission_denied"


@pytest.mark.asyncio
async def test_admin_get_user_by_id(client, access_token):
    id = 1
    headers = {"Authorization": f"Bearer {access_token[0]}"}
    response = await client.get(f"/api/admin/user/{id}/", headers=headers)
    assert response.status_code == 200

    headers = {"Authorization": f"Bearer {access_token[1]}"}
    response = await client.get(f"/api/admin/user/{id}/", headers=headers)
    assert response.status_code == 403
    assert response.json()["message"]["code"] == "permission_denied"


@pytest.mark.asyncio
async def test_admin_patch_user_by_id(client, access_token):
    id = 1
    headers = {"Authorization": f"Bearer {access_token[0]}"}
    data = {"status": "suspend"}
    response = await client.patch(f"/api/admin/user/{id}/", json=data, headers=headers)

    assert response.status_code == 200
    assert response.json()["status"] == "suspend"


@pytest.mark.asyncio
async def test_admin_get_all_resumes(client, access_token):
    headers = {"Authorization": f"Bearer {access_token[0]}"}
    response = await client.get("/api/admin/resume/", headers=headers)
    assert response.status_code == 200
    assert await Resume.all().count() == 2

    headers = {"Authorization": f"Bearer {access_token[1]}"}
    response = await client.get("/api/admin/resume/", headers=headers)
    assert response.status_code == 403
    assert response.json()["message"]["code"] == "permission_denied"


@pytest.mark.asyncio
async def test_admin_get_resume_by_id(client, access_token):
    id = 1
    headers = {"Authorization": f"Bearer {access_token[0]}"}
    response = await client.get(f"/api/admin/resume/{id}/", headers=headers)

    assert response.status_code == 200
    assert response.json()["title"] == "테스트 이력서"

    headers = {"Authorization": f"Bearer {access_token[1]}"}
    response = await client.get(f"/api/admin/resume/{id}/", headers=headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_admin_delete_resume_by_id(client, access_token):
    id = 1
    headers = {"Authorization": f"Bearer {access_token[0]}"}
    response = await client.delete(f"/api/admin/resume/{id}/", headers=headers)
    assert response.status_code == 200
    assert await Resume.all().count() == 1

    id = 2
    headers = {"Authorization": f"Bearer {access_token[1]}"}
    response = await client.delete(f"/api/admin/resume/{id}/", headers=headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_admin_get_all_job_postings(client, access_token):
    headers = {"Authorization": f"Bearer {access_token[0]}"}
    response = await client.get("/api/admin/job-posting/", headers=headers)
    assert response.status_code == 200
    assert await JobPosting.all().count() == 2

    headers = {"Authorization": f"Bearer {access_token[1]}"}
    response = await client.get("/api/admin/job-posting/", headers=headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_admin_get_job_posting_by_id(client, access_token):
    id = 1
    headers = {"Authorization": f"Bearer {access_token[0]}"}
    response = await client.get(f"/api/admin/job-posting/{id}/", headers=headers)

    assert response.status_code == 200
    assert response.json()["company"] == "테스트 주식회사"

    headers = {"Authorization": f"Bearer {access_token[1]}"}
    response = await client.get(f"/api/admin/job-posting/{id}/", headers=headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_admin_patch_job_posting_by_id(client, access_token):
    id = 1
    data = {"status": "반려됨"}
    headers = {"Authorization": f"Bearer {access_token[0]}"}
    response = await client.patch(
        f"/api/admin/job-posting/{id}/", json=data, headers=headers
    )

    assert response.status_code == 200
    assert response.json()["status"] == "반려됨"

    headers = {"Authorization": f"Bearer {access_token[1]}"}
    response = await client.get(f"/api/admin/job-posting/{id}/", headers=headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_create_reject_posting(client, access_token):
    # given
    job_posting_id = 1
    data = {"content": "이력서 내용이 너무 부족합니다."}
    headers = {"Authorization": f"Bearer {access_token[0]}"}

    # when
    response = await client.post(
        f"/api/admin/job-posting/{job_posting_id}/reject-posting/",
        json=data,
        headers=headers,
    )

    # then
    assert response.status_code == 200
    res_json = response.json()
    assert "id" in res_json
    assert res_json["content"] == data["content"]
    assert "user" in res_json
    assert "job_posting" in res_json
