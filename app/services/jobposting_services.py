from app.models.job_posting_models import JobPosting
from app.models.user_models import BaseUser, CorporateUser
from app.schemas.jobposting_schemas import JobPostingCreateUpdate, JobPostingResponse
from app.utils.exception import CustomException


class JobPostingService:
    @staticmethod
    async def create_job_posting(
        user: BaseUser, data: JobPostingCreateUpdate
    ) -> JobPosting:
        # 인증 검사
        if not user:
            raise CustomException(
                error="로그인이 필요합니다.", code="invalid_token", status_code=401
            )
        # 권한 검사
        if user.UserType != "business":
            raise CustomException(
                error="해당 작업을 수행할 권한이 없습니다.", code="permission_denied", status_code=403
            )
        # JobPosting 생성
        job_posting = JobPosting(user_id=user.id, **data.dict())
        await job_posting.save()

        # 딕셔너리 형태로 반환
        return {
            "message": "구인 공고가 등록되었습니다.",
            "data": {
                "id": job_posting.id,
                "title": job_posting.title,
                "status": job_posting.status.value,
            },
        }

    @staticmethod
    async def patch_job_posting(
        user: CorporateUser,
        job_posting: JobPosting,
        updated_data: JobPostingCreateUpdate,
    ) -> dict:
        # JobPosting 존재 여부 확인
        if not job_posting:
            raise CustomException(
                error="공고를 찾을 수 없습니다.", code="notification_not_found", status_code=404
            )

        # 인증 검사
        if not user:
            raise CustomException(
                error="로그인이 필요합니다.", code="invalid_token", status_code=401
            )

        # 권한 검사: 작성자인지 확인
        if job_posting.user_id != user.id:
            raise CustomException(
                error="해당 작업을 수행할 권한이 없습니다.", code="permission_denied", status_code=403
            )

        # JobPosting 업데이트 로직
        for field, value in updated_data.dict(exclude_unset=True).items():
            setattr(job_posting, field, value)
        await job_posting.save()

        return {
            "message": "구인 공고가 성공적으로 수정되었습니다.",
            "data": {
                "id": job_posting.id,
                "title": job_posting.title,
                "status": job_posting.status.value,
            },
        }
