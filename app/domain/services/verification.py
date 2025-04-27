from app.exceptions.auth_exceptions import PermissionDeniedException


def check_superuser(current_user):
    if not current_user.is_superuser:
        raise PermissionDeniedException()


def check_existing(obj, exception_class):
    if not obj:
        raise exception_class()
