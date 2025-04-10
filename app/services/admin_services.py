from app.models.user_models import BaseUser
from app.schemas.admin_schmeas import UserResponseSchema


async def get_user_all(current_user: UserResponseSchema):
    if current_user.is_superuser:
        users = await BaseUser.all().select_related(
            "corporate_profiles", "seeker_profiles"
        )
