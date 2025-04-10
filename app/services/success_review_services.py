from app.models.success_review_models import SuccessReview
from app.utils.exception import CustomException


def existing_review(review):
    """존재하는 게시판인지 확인"""
    if not review:
        raise CustomException(
            error="해당 게시글을 찾을 수 없습니다.",
            code="success_review_not_found",
            status_code=404,
        )


def author_board(review, user):
    """작성자인지 확인하는 함수"""
    if review.user != user:
        raise CustomException(
            error="작성자가 아닙니다.", code="permission_denied", status_code=403
        )


async def create_success_review_by_id(success_review, current_user):
    return await SuccessReview.create(**success_review.dict(), user=current_user)


async def get_all_success_reviews(current_user):
    return await SuccessReview.all().select_related("user")


async def get_success_review_by_id(id, current_user):
    review = await SuccessReview.filter(pk=id).select_related("user").first()
    existing_review(review)
    return review


async def patch_success_review_by_id(id, success_review, current_user):
    review = await SuccessReview.filter(pk=id).select_related("user").first()
    existing_review(review)
    author_board(review, current_user)

    review.title = success_review.title
    review.content = success_review.content
    review.job_title = success_review.job_title
    review.company_name = success_review.company_name
    review.employment_type = success_review.employment_type

    await review.save()

    return review


async def delete_success_review_by_id(id, current_user):
    review = await SuccessReview.filter(pk=id).select_related("user").first()
    existing_review(review)
    author_board(review, current_user)

    await review.delete()
