from enum import Enum

from app.domain.job_posting.models import JobPosting
from app.domain.job_posting.public_services import ExternalAPIService


class EmploymentEnum(Enum):
    General = "일반"
    Temporary = "임시"
    Internship = "인턴"


class StatusEnum(Enum):
    Open = "모집중"
    Closed = "마감"
    OnHold = "보류"


def map_employment_type(job_type: str) -> EmploymentEnum:
    # 외부 데이터(job_type)를 EmploymentEnum으로 매핑
    mapping = {
        "일자리유형1": EmploymentEnum.General,
        "일자리유형2": EmploymentEnum.Temporary,
        "일자리유형3": EmploymentEnum.Internship,
    }
    return mapping.get(job_type, EmploymentEnum.General)  # 기본값 설정


def map_status(status: str) -> StatusEnum:
    # 외부 데이터(status)를 StatusEnum으로 매핑
    mapping = {
        "모집중": StatusEnum.Open,
        "마감": StatusEnum.Closed,
        "보류": StatusEnum.OnHold,
    }
    return mapping.get(status, StatusEnum.Open)  # 기본값 설정


async def save_job_postings():
    # 외부 API 호출
    api_service = ExternalAPIService(
        base_url="https://openapi.gg.go.kr", api_key="your_api_key_here"
    )
    response = await api_service.get_data(endpoint="/Oldpsnslfjobbiz")

    for item in response["data"]:
        # 외부 데이터를 모델 형식에 맞게 변환
        job_posting_data = {
            "company": item["ENTRPS_NM"],
            "title": f"{item['JOB_TYPE']} - {item['ENTRPS_NM']}",
            "location": item["SIGUN_NM"],
            "employment_type": map_employment_type(item["JOB_TYPE"]),  # Enum 변환 적용
            "deadline": f"{item['BEGIN_DE']} ~ {item['END_DE']}",
            "salary": item["WAGE_INFO"],
            "recruitment_count": int(item["RECRUT_PSNNUM"]),
            "description": item.get("MESSAGE", "상세 설명 없음"),
            "status": map_status(item["STATE_DIV_NM"]),  # Enum 변환 적용
        }

        # Tortoise ORM을 사용해 DB 저장
        await JobPosting.create(**job_posting_data)
