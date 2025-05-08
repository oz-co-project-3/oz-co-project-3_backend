from typing import List

from fastapi import APIRouter, Depends, status

from app.core.token import get_current_user
from app.domain.success_review.schemas import (
    SuccessReviewCreateUpdateSchema,
    SuccessReviewResponseSchema,
)
from app.domain.success_review.services import (
    create_success_review_by_id,
    delete_success_review_by_id,
    get_all_success_reviews,
    get_success_review_by_id,
    patch_success_review_by_id,
)
from app.domain.user.models import SeekerUser

success_review_router = APIRouter(prefix="/api/success-review", tags=["success-review"])


@success_review_router.post(
    "/",
    response_model=SuccessReviewResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="자유게시판 글 생성",
    description="""
`400` `code`:`required_field` 필수 필드 누락\n
`401` `code`:`auth_required` 인증이 필요합니다.\n
`401` `code`:`invalid_token` 유효하지 않은 토큰입니다.\n
    """,
)
async def create_success_review(
    success_review: SuccessReviewCreateUpdateSchema,
    current_user: SeekerUser = Depends(get_current_user),
):
    return await create_success_review_by_id(success_review, current_user)


@success_review_router.get(
    "/",
    response_model=List[SuccessReviewResponseSchema],
    summary="자유게시판 글 전체 조회",
    status_code=status.HTTP_200_OK,
    description="""
`401` `code`:`auth_required` 인증이 필요합니다.\n
`401` `code`:`invalid_token` 유효하지 않은 토큰입니다.\n
    """,
)
async def get_list_success_reviews(
    current_user: SeekerUser = Depends(get_current_user),
):
    return await get_all_success_reviews(current_user)


@success_review_router.get(
    "/{id}/",
    response_model=SuccessReviewResponseSchema,
    summary="자유게시판 글 상세 조회",
    status_code=status.HTTP_200_OK,
    description="""
`401` `code`:`auth_required` 인증이 필요합니다.\n
`401` `code`:`invalid_token` 유효하지 않은 토큰입니다.\n
`404` `code`:`success_review_not_found` 존재하지 않는 성공 후기 입니다.\n
    """,
)
async def get_success_review(
    id: int,
    current_user: SeekerUser = Depends(get_current_user),
):
    return await get_success_review_by_id(id, current_user)


@success_review_router.patch(
    "/{id}/",
    response_model=SuccessReviewResponseSchema,
    summary="자유게시판 글 수정",
    status_code=status.HTTP_200_OK,
    description="""
`401` `code`:`auth_required` 인증이 필요합니다.\n
`401` `code`:`invalid_token` 유효하지 않은 토큰입니다.\n
`403` `code`:`permission_denied` 권한이 없습니다, 작성자가 아닙니다.\n
`404` `code`:`success_review_not_found` 존재하지 않는 성공 후기 입니다.\n
    """,
)
async def patch_success_review(
    id: int,
    success_review: SuccessReviewCreateUpdateSchema,
    current_user: SeekerUser = Depends(get_current_user),
):
    return await patch_success_review_by_id(id, success_review, current_user)


@success_review_router.delete(
    "/{id}/",
    summary="자유게시판 글 삭제",
    status_code=status.HTTP_200_OK,
    description="""
`401` `code`:`auth_required` 인증이 필요합니다.\n
`401` `code`:`invalid_token` 유효하지 않은 토큰입니다.\n
`403` `code`:`permission_denied` 권한이 없습니다, 작성자가 아닙니다.\n
`404` `code`:`success_review_not_found` 존재하지 않는 성공 후기 입니다.\n
    """,
)
async def delete_success_review(
    id: int,
    current_user: SeekerUser = Depends(get_current_user),
):
    await delete_success_review_by_id(id, current_user)
    return {"message": "삭제가 완료되었습니다."}
