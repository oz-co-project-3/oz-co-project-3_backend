import pytest
from fastapi.testclient import TestClient
from tortoise.contrib.test import finalizer, initializer

from app.main import app
from app.models.job_posting_models import JobPosting
from app.models.user_models import BaseUser, CorporateUser
from app.services.jobposting_services import JobPostingService
from app.utils.exception import CustomException

client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def setup():
    # 테스트 시작 전 초기화
    initializer(
        [
            "app.models.job_posting_models",
            "app.models.resume_models",
            "app.models.user_models",
        ]
    )
    yield
    # 테스트 종료 후 정리
    finalizer()


@pytest.mark.asyncio
@pytest.fixture(scope="module", autouse=True)
async def pre_data():
    # 테스트용 유저 데이터 생성
    user = await BaseUser.create(
        email="test_user@example.com",
        password="TestPassword123!",
        user_type="business",
        is_active=True,
    )

    # 테스트용 회사 데이터 생성
    company = await CorporateUser.create(
        id=1,
        user=user,
        company_name="test_company",
        business_start_date="2023-01-01",
        business_number="1234567890",
        company_description="Test company description",
        manager_name="Test Manager",
        manager_phone_number="010-1234-5678",
        manager_email="manager@example.com",
    )
    yield company


def test_create_job_posting():
    # JobPosting 생성 테스트
    company_id = 1
    data = {
        "user_id": 1,
        "title": "테스트 공고",
        "location": "서울",
        "employment_type": "General",
        "employ_method": "permanent",
        "work_time": "9시에서 6시",
        "position": "사무원",
        "recruitment": 5,
        "education": "고등학교 졸업",
        "deadline": "2025-04-30",
        "salary": 100000,
        "description": "공고 상세 설명",
        "status": "Open",
    }
    response = client.post("/job_posting/1", json=data)
    print(response.json())
    assert response.status_code == 200
    assert response.json()["title"] == "테스트 채용 공고"
    assert response.json()["position"] == "사무원"


async def test_patch_job_posting_unauthorized_user():
    job_posting = await JobPosting.create(
        user_id=1, title="Test Job", status="Open"  # 작성자 ID
    )

    other_user = CorporateUser(id=2)  # 다른 사용자
    data = {"title": "Updated Title"}

    with pytest.raises(CustomException) as excinfo:
        await JobPostingService().patch_job_posting(other_user, job_posting, data)
    assert excinfo.value.status_code == 403
    assert excinfo.value.error == "해당 작업을 수행할 권한이 없습니다."
