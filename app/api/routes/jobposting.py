from fastapi import APIRouter, Depends, HTTPException

from app.schemas.jobposting_schemas import JobPostingCreateUpdate, JobPostingResponse
from app.services.jobposting_services import JobPostingService
from app.utils.exception import CustomException

router = APIRouter(
    prefix="/job_posting",
    tags=["job_posting"],  # 스웨거 표시 태그
)


@router.post("/{company_id}/", response_model=JobPostingResponse, status_code=201)
async def create_job_posting(
    data: JobPostingCreateUpdate,  # 요청 데이터 검증
    user: dict = Depends(get_current_user),  # 인증된 사용자 정보
):
    try:
        return await JobPostingService.create_job_posting(user, data)
    except CustomException as e:
        raise HTTPException(status_code=e.status_code, detail=e.error)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
