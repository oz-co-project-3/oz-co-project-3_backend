import logging
from typing import List

from fastapi import APIRouter, Depends, status

from app.core.token import get_current_user
from app.domain.applicant.schema import ApplicantResponse, ApplicantUpdate
from app.domain.applicant.services import ApplicantService
from app.domain.user.user_models import BaseUser, CorporateUser, SeekerUser

applicant_router = APIRouter(prefix="/api/applicants", tags=["applicants"])

logger = logging.getLogger(__name__)


# 기업 특정 공고의 모든 지원자 조회
@applicant_router.get(
    "/corporate/{job_posting_id}/",
    response_model=List[ApplicantResponse],
    status_code=status.HTTP_200_OK,
    summary="특정 공고의 모든 지원자 조회",
    description="""
기업 사용자가 특정 공고에 지원한 모든 지원자 목록을 조회합니다.
- `200 OK`: 정상 응답
- `401 Unauthorized`: 인증이 필요합니다 (`invalid_token`)
- `403 Forbidden`: 권한이 없습니다 (`permission_denied`)
- `404 Not Found`: 해당 공고 또는 지원자가 없습니다 (`job_posting_not_found`, `applicants_not_found`)
    """,
)
async def get_applicants_by_job_posting(
    job_posting_id: int, current_user: BaseUser = Depends(get_current_user)
):
    logger.info(
        f"[API] 기업 특정 공고 지원자 조회 요청 : job_posting_id={job_posting_id}, BaseUser id={current_user.id}"
    )
    result = await ApplicantService.get_applicants_by_job_posting(
        current_user, job_posting_id
    )
    logger.info(
        f"[API] 기업 특정 공고 지원자 조회 완료 : job_posting_id={job_posting_id}, 응답 지원자 수={len(result)}"
    )
    return result


# 기업 모든 공고의 전체 지원자 조회
@applicant_router.get(
    "/corporate/",
    response_model=List[ApplicantResponse],
    status_code=status.HTTP_200_OK,
    summary="모든 공고의 지원자 조회",
    description="""
기업 사용자가 등록한 모든 공고에 지원한 지원자 목록을 조회합니다.
- `200 OK`: 정상 응답
- `401 Unauthorized`: 인증이 필요합니다 (`invalid_token`)
- `403 Forbidden`: 권한이 없습니다 (`permission_denied`)
    """,
)
async def get_all_applicants_by_corporate_user(
    current_user: CorporateUser = Depends(get_current_user),
):
    logger.info(f"[API] 기업 전체 공고 지원자 조회 요청 : BaseUser id={current_user.id}")
    result = await ApplicantService.get_all_applicants_by_corporate_user(current_user)
    logger.info(f"[API] 기업 전체 공고 지원자 조회 완료 : 응답 지원자 수={len(result)}")
    return result


# 구직자 지원한 모든 공고 조회
@applicant_router.get("/seeker/", response_model=List[ApplicantResponse])
async def get_seeker_applications(current_user: BaseUser = Depends(get_current_user)):
    logger.info(f"[API] 구직자 지원 내역 전체 조회 요청 : BaseUser id={current_user.id}")
    applications = await ApplicantService.get_applicants_by_seeker_user(current_user)
    logger.info(f"[API] 구직자 지원 내역 전체 조회 완료 : 응답 건수={len(applications)}")
    return applications


# 구직자 특정 지원 내역 상세 조회
@applicant_router.get(
    "/seeker/{applicant_id}/",
    response_model=ApplicantResponse,
    status_code=status.HTTP_200_OK,
    summary="특정 지원 내역 조회",
    description="""
구직자가 특정 지원 내역을 상세 조회합니다.
- `200 OK`: 정상 응답
- `401 Unauthorized`: 인증이 필요합니다 (`invalid_token`)
- `404 Not Found`: 지원 내역을 찾을 수 없습니다 (`application_not_found`)
    """,
)
async def get_applicant_detail(
    applicant_id: int, current_user: BaseUser = Depends(get_current_user)
):
    logger.info(
        f"[API] 구직자 특정 지원 내역 조회 요청 : applicant_id={applicant_id}, BaseUser id={current_user.id}"
    )
    result = await ApplicantService.get_applicant_detail(current_user, applicant_id)
    logger.info(f"[API] 구직자 특정 지원 내역 조회 완료 : applicant_id={applicant_id}")
    return result
