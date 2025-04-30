from app.domain.user.models import BaseUser


def split_user_types(user_type_str: str) -> list[str]:
    return [t.strip() for t in user_type_str.split(",") if t.strip()]


def is_business_user(user: BaseUser) -> bool:
    return "business" in split_user_types(user.user_type)


def is_seeker_user(user: BaseUser) -> bool:
    return "normal" in split_user_types(user.user_type)


def is_admin_user(user: BaseUser) -> bool:
    return "admin" in split_user_types(user.user_type)
