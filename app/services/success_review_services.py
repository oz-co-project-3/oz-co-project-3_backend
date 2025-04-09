from app.models.success_review_models import SuccessReview


async def create_success_review_by_id(success_review, current_user):
    return await SuccessReview.create(**success_review.dict(), user=current_user)
