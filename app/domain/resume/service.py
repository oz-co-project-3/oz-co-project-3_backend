from typing import Any

from app.domain.resume.repository import ResumeRepository, WorkExpRepository
from app.domain.resume.schema import ResumeResponseSchema, WorkExpResponseSchema
from app.utils.exception import CustomException, check_existing, check_superuser


class ResumeService:
    @staticmethod
    async def create_resume_service(data: dict):
        # 이력서 생성
        work_experiences = data.pop("work_experiences", [])
        resume = await ResumeRepository.create_resume(data)

        # 경력 사항 생성
        for work_exp in work_experiences:
            work_exp["resume_id"] = resume.id
            await WorkExpRepository.create_work_experience(work_exp)

        return ResumeResponseSchema.model_validate(resume)

    @staticmethod
    async def get_resume_by_id_service(resume_id: int, current_user: Any):
        # 이력서 조회
        resume = await ResumeRepository.get_resume_by_id(resume_id)
        check_existing(resume, error_message="이력서를 찾을 수 없습니다.", code="resume_not_found")
        if not resume or not getattr(resume, "user", None):
            raise CustomException(
                error="올바르지 않은 접근입니다.",
                code="invalid_resume",
                status_code=400,
            )
        if resume.user != current_user.id:
            check_superuser(current_user)

        # 경력 사항 조회 및 매핑
        work_experiences = await WorkExpRepository.get_work_experiences_by_resume_id(
            resume_id
        )
        work_experience_schemas = [
            WorkExpResponseSchema.model_validate(work_exp)
            for work_exp in work_experiences
        ]

        resume_data = ResumeResponseSchema.model_validate(resume)
        resume_data.work_experiences = work_experience_schemas
        return resume_data

    @staticmethod
    async def update_resume_service(resume_id: int, data: dict, current_user: Any):
        resume = await ResumeRepository.get_resume_by_id(resume_id)
        check_existing(resume, error_message="이력서를 찾을 수 없습니다.", code="resume_not_found")
        if resume.user != current_user.id:
            check_superuser(current_user)

        # 업데이트
        work_experiences = data.pop("work_experiences", [])
        updated_resume = await ResumeRepository.update_resume(resume_id, data)

        # 기존 경력 사항 처리
        existing_work_exps = await WorkExpRepository.get_work_experiences_by_resume_id(
            resume_id
        )
        existing_work_exp_ids = {work_exp.id for work_exp in existing_work_exps}

        new_work_exp_ids = {
            work_exp.get("id") for work_exp in work_experiences if work_exp.get("id")
        }

        # 삭제된 경력
        for work_exp in existing_work_exps:
            if work_exp.id not in new_work_exp_ids:
                await WorkExpRepository.delete_work_experience(work_exp.id)

        # 추가 또는 업데이트된 경력
        for work_exp in work_experiences:
            if work_exp.get("id") in existing_work_exp_ids:
                # 수정
                await WorkExpRepository.update_work_experience(work_exp["id"], work_exp)
            else:
                # 추가
                work_exp["resume_id"] = resume_id
                await WorkExpRepository.create_work_experience(work_exp)

        return ResumeResponseSchema.model_validate(updated_resume)

    @staticmethod
    async def get_all_resume_service(
        current_user: Any, offset: int = 0, limit: int = 10
    ):
        # 사용자 이력서 조회
        resumes = await ResumeRepository.get_resumes_by_user_id(
            user_id=current_user.id, offset=offset, limit=limit
        )
        total_count = await ResumeRepository.get_total_resume_count_by_user_id(
            current_user.id
        )

        # 응답 데이터 구성
        return {
            "total": total_count,
            "offset": offset,
            "limit": limit,
            "data": [ResumeResponseSchema.model_validate(resume) for resume in resumes],
        }

    @staticmethod
    async def delete_resume_service(resume_id: int, current_user: Any):
        # 이력서 조회
        resume = await ResumeRepository.get_resume_by_id(resume_id)
        check_existing(resume, error_message="이력서를 찾을 수 없습니다.", code="resume_not_found")

        # 사용자 권한 확인
        if resume.user != current_user.id:
            check_superuser(current_user)

        # 관련된 경력 사항 삭제
        await WorkExpRepository.delete_work_experiences_by_resume_id(resume_id)

        # 이력서 삭제
        if not await ResumeRepository.delete_resume(resume_id):
            raise CustomException(
                error="이력서 삭제에 실패했습니다.",
                code="resume_delete_failed",
                status_code=500,
            )

        return {"message": "이력서가 성공적으로 삭제되었습니다."}
