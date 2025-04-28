from passlib.hash import bcrypt

from app.core.redis import redis
from app.domain.services.email_detail import send_email_code
from app.domain.user.repository import (
    get_corporate_by_manager_name_and_phone,
    get_seeker_by_name_and_phone,
    get_user_by_email,
    get_user_with_profiles_by_email,
)
from app.domain.user.schema import ResendEmailRequest
from app.exceptions.auth_exceptions import PasswordMismatchException
from app.exceptions.email_exceptions import (
    EmailAlreadyVerifiedException,
    InvalidVerificationCodeException,
)
from app.exceptions.server_exceptions import UnknownUserTypeException
from app.exceptions.user_exceptions import (
    PasswordInvalidException,
    PasswordPreviouslyUsedException,
    UserNotFoundException,
)


# 아이디 찾기
async def find_email(name: str, phone_number: str):
    # 구직자에서 먼저 검색
    seeker = await get_seeker_by_name_and_phone(name, phone_number)
    if seeker:
        email = seeker.user.email
    else:
        # 2. 없으면 기업회원에서 검색
        corp = await get_corporate_by_manager_name_and_phone(name, phone_number)
        if corp:
            email = corp.user.email
        else:
            raise UserNotFoundException()

    # 이메일 마스킹 처리 x = 프론트에서 진행한다고 함
    return {"message": "아이디 찾기 성공", "data": {"email": email}}


async def find_password(name: str, phone_number: str, email: str):
    user = await get_user_with_profiles_by_email(email)

    if not user:
        raise UserNotFoundException()

    if user.user_type == "seeker":
        seeker = await user.seeker_profiles.all().first()  # 리스트 중 첫 번째
        if not seeker or seeker.name != name or seeker.phone_number != phone_number:
            raise UserNotFoundException()

    elif user.user_type == "business":
        corp = await user.corporate_profiles.all().first()  # 리스트 중 첫 번째
        if (
            not corp
            or corp.manager_name != name
            or corp.manager_phone_number != phone_number
        ):
            raise UserNotFoundException()

    else:
        raise UnknownUserTypeException()

    # 이메일로 재설정 링크 전송
    await send_email_code(email=email, purpose="비밀번호 찾기")

    return {"message": "비밀번호 재설정 링크가 이메일로 발송되었습니다", "data": {"email": email}}


# 새로운 비밀번호 생성 함수
async def reset_password(email: str, new_password: str, new_password_check: str):
    if new_password != new_password_check:
        raise PasswordMismatchException()

    if len(new_password) < 8 or not any(
        char in "!@#$%^&*()_+{}:<>?" for char in new_password
    ):
        raise PasswordInvalidException()

    user = await get_user_by_email(email)
    if not user:
        raise UserNotFoundException()

    if bcrypt.verify(new_password, user.password):
        raise PasswordPreviouslyUsedException()

    user.password = bcrypt.hash(new_password)
    await user.save()

    return {"message": "비밀번호가 성공적으로 변경되었습니다."}


# 이메일 인증완료 / 재인증 요청


# 이메일 인증 완료 처리
async def complete_email_verification(email: str, verification_code: str):
    saved_code = await redis.get(f"email_verify:{email}")

    if not saved_code or saved_code != verification_code:
        raise InvalidVerificationCodeException()

    user = await get_user_by_email(email=email)
    if not user:
        raise UserNotFoundException()

    user.email_verified = True
    user.status = "active"
    await user.save()

    return {
        "message": "이메일 인증이 완료되었습니다.",
        "data": {
            "email": user.email,
            "email_verified": user.email_verified,
        },
    }


# 이메일 재인증 요청
async def resend_verification_email_service(request: ResendEmailRequest):
    user = await get_user_by_email(email=request.email)
    if not user:
        raise UserNotFoundException()

    if user.email_verified:
        raise EmailAlreadyVerifiedException()

    await send_email_code(email=user.email, purpose="이메일 재인증")

    return {"message": "인증코드가 재전송되었습니다.", "data": {"email": user.email}}
