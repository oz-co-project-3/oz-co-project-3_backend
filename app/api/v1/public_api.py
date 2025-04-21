import os

from fastapi import APIRouter, Depends

from app.domain.job_posting.job_posting_models import JobPosting
from app.domain.job_posting.jobposting_schemas import JobPostingResponse
from app.domain.job_posting.public_collection import save_job_postings
from app.domain.job_posting.public_services import ExternalAPIService
from app.utils.exception import CustomException

base_url = os.getenv("BASE_URL")
api_key = os.getenv("API_KEY")

# API 서비스 초기화
public_router = APIRouter(
    prefix="/api/public",
    tags=["public_api"],  # 스웨거 표시 태그
)


def get_api_service() -> ExternalAPIService:
    base_url = os.getenv("BASE_URL")
    api_key = os.getenv("API_KEY")
    return ExternalAPIService(base_url=base_url, api_key=api_key)


# 외부 데이터 가져오기 및 저장
@public_router.post("/")
async def update_job_postings(
    api_service: ExternalAPIService = Depends(get_api_service),
):
    try:
        await save_job_postings()  # 데이터 저장 로직 호출
        return {"message": "Job postings updated successfully"}
    except Exception as e:
        raise CustomException(
            error="등록에 실패하였습니다.", code="update_failure", status_code=500
        )


# 데이터 조회 엔드포인트
@public_router.get("/postings/", response_model=list[JobPostingResponse])
async def get_job_postings(skip: int = 0, limit: int = 10):
    try:
        job_postings = await JobPosting.all().offset(skip).limit(limit)
        return [
            JobPostingResponse(**job_posting).model_dump()
            for job_posting in job_postings
        ]
    except Exception as e:
        raise CustomException(
            error="불러오기에 실패했습니다", code="fetch_failure", status_code=500
        )
