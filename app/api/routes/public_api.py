import os

from fastapi import APIRouter

from app.models.job_posting_models import JobPosting
from app.schemas.jobposting_schemas import JobPostingResponse
from app.services.public_collection import save_job_postings
from app.services.public_services import ExternalAPIService
from app.utils.exception import CustomException

router = APIRouter()

base_url = os.getenv.get("BASE_URL")
api_key = os.getenv.get("API_KEY")

# API 서비스 초기화
api_service = ExternalAPIService(
    base_url=base_url,
    api_key=api_key,
)


# 외부 데이터 가져오기 및 저장
@router.post("/update-job-postings")
async def update_job_postings():
    try:
        await save_job_postings()  # 데이터 저장 로직 호출
        return {"message": "Job postings updated successfully"}
    except Exception as e:
        raise CustomException(
            error="등록에 실패하였습니다.", code="update_failure", status_code=500
        )


@router.get("/job-postings", response_model=list[JobPostingResponse])
async def get_job_postings():
    try:
        job_postings = await JobPosting.all()
        return [
            JobPostingResponse(**job_posting).dict() for job_posting in job_postings
        ]
    except Exception as e:
        raise CustomException(
            error="불러오기에 실패했습니다", code="fetch_failure", status_code=500
        )
