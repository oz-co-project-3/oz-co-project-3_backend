from app.domain.services.permission import check_author
from app.domain.services.verification import check_existing
from app.domain.success_review.models import SuccessReview
from app.exceptions.success_review_exceptions import SuccessReviewNotFoundException


async def create_success_review_by_id(success_review, current_user):
    return await SuccessReview.create(**success_review.dict(), user=current_user)


async def get_all_success_reviews(current_user):
    return await SuccessReview.all().select_related("user")


async def get_success_review_by_id(id, current_user):
    review = await SuccessReview.filter(pk=id).select_related("user").first()
    check_existing(review, SuccessReviewNotFoundException)
    return review


async def patch_success_review_by_id(id, success_review, current_user):
    review = await SuccessReview.filter(pk=id).select_related("user").first()
    check_existing(review, SuccessReviewNotFoundException)
    await check_author(review, current_user)

    review.title = success_review.title
    review.content = success_review.content
    review.job_title = success_review.job_title
    review.company_name = success_review.company_name
    review.employment_type = success_review.employment_type

    await review.save()

    return review


async def delete_success_review_by_id(id, current_user):
    review = await SuccessReview.filter(pk=id).select_related("user").first()
    check_existing(review, SuccessReviewNotFoundException)
    await check_author(review, current_user)

    await review.delete()
