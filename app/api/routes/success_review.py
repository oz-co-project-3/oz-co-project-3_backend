from fastapi import APIRouter

from app.models.user_models import BaseUser
from app.schemas.success_review_schemas import (
    SuccessReviewCreateUpdateSchema,
    SuccessReviewResponseSchema,
)
from app.services.success_review_services import create_success_review_by_id

success_review_router = APIRouter(prefix="/api/success-review", tags=["success-review"])


async def fake_current_user():
    user = await BaseUser.get(pk=1)
    return user


@success_review_router.post(
    "/",
    response_model=SuccessReviewResponseSchema,
    summary="자유게시판 글 생성",
    description="""
    - `400` `code`:`required_field` 필수 필드 누락\n
    - `401` `code`:`auth_required` 인증이 필요합니다.\n
    - `401` `code`:`invalid_token` 유효하지 않은 토큰입니다.\n
    """,
)
async def create_success_review(
    success_review: SuccessReviewCreateUpdateSchema,
    current_user: BaseUser = fake_current_user(),
):
    return await create_success_review_by_id(success_review, current_user)
