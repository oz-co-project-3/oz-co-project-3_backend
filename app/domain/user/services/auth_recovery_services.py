import logging

from passlib.hash import bcrypt

from app.core.redis import redis
from app.domain.services.email_detail import send_email_code
from app.domain.user.repository import (
    get_corporate_by_manager_name_and_phone,
    get_corporate_profile_by_info,
    get_seeker_by_name_and_phone,
    get_seeker_profile_by_info,
    get_user_by_email,
)
from app.domain.user.schema import (
    EmailCheckResponseDTO,
    EmailVerificationResponseDTO,
    FindEmailResponseDTO,
    FindPasswordResponseDTO,
    ResendEmailRequest,
    ResendEmailResponseDTO,
    ResetPasswordResponseDTO,
)
from app.exceptions.auth_exceptions import PasswordMismatchException
from app.exceptions.email_exceptions import (
    EmailAlreadyVerifiedException,
    InvalidVerificationCodeException,
)
from app.exceptions.user_exceptions import (
    PasswordInvalidException,
    PasswordPreviouslyUsedException,
    UserNotFoundException,
)

logger = logging.getLogger(__name__)


# 이메일 마스킹 = 유틸로 안 넣고 리커버리 서비스 안에서 처리 (구조 변경 가능)
def mask_email(email: str) -> str:
    """
    이메일 마스킹 예시: abcde@naver.com → ab***@naver.com
    """
    username, domain = email.split("@")
    if len(username) <= 2:
        masked = username[0] + "*"
    else:
        masked = username[:2] + "*" * (len(username) - 2)
    return f"{masked}@{domain}"


# 아이디 찾기
async def find_email(name: str, phone_number: str) -> FindEmailResponseDTO:
    # 구직자에서 먼저 검색
    seeker = await get_seeker_by_name_and_phone(name, phone_number)
    if seeker:
        email = seeker.user.email
    else:
        # 없으면 기업회원에서 검색
        corp = await get_corporate_by_manager_name_and_phone(name, phone_number)
        if corp:
            email = corp.user.email
        else:
            logger.warning(f"[CHECK] 유저를 찾을 수 없음 {name},{phone_number}")
            raise UserNotFoundException()
    # 이메일 마스킹 추가 = 04/29 중간점검 이후
    masked_email = mask_email(email)

    return FindEmailResponseDTO(email=masked_email)


# 비밀번호 찾기
async def find_password(
    name: str, phone_number: str, email: str
) -> FindPasswordResponseDTO:
    # 해당 이메일로 BaseUser 조회
    user = await get_user_by_email(email=email)
    if not user:
        logger.warning(f"[CHECK] 일반 유저를 찾을 수 없음 {name},{phone_number},{email}")
        raise UserNotFoundException()

    # (여기까지 통과하면) 비밀번호 재설정 이메일 발송
    await send_email_code(email, "비밀번호 찾기")

    return FindPasswordResponseDTO(success=True)


# 새로운 비밀번호 생성 함수
async def reset_password(
    email: str, new_password: str, new_password_check: str
) -> ResetPasswordResponseDTO:
    if new_password != new_password_check:
        logger.warning(f"[CHECK] 패스워드가 일치하지 않음:{new_password},{new_password_check}")
        raise PasswordMismatchException()

    if len(new_password) < 8 or not any(
        char in "!@#$%^&*()_+{}:<>?" for char in new_password
    ):
        logger.warning(f"[CHECK] 패스워드 부적합 :{new_password}")
        raise PasswordInvalidException()

    user = await get_user_by_email(email)
    if not user:
        logger.warning(f"[CHECK] 유저를 찾을 수 없음:{email}")
        raise UserNotFoundException()

    if bcrypt.verify(new_password, user.password):
        logger.warning(f"[CHECK] 이전과 동일한 비밀번호 사용:{new_password}")
        raise PasswordPreviouslyUsedException()

    user.password = bcrypt.hash(new_password)
    await user.save()

    return ResetPasswordResponseDTO(success=True)


# 이메일 인증 완료 처리
async def complete_email_verification(
    email: str, verification_code: str
) -> EmailVerificationResponseDTO:
    saved_code = await redis.get(f"email_verify:{email}")

    if not saved_code or str(saved_code) != str(verification_code):
        raise InvalidVerificationCodeException()

    user = await get_user_by_email(email=email)
    if not user:
        raise UserNotFoundException()

    user.email_verified = True
    user.status = "active"
    await user.save()

    return EmailVerificationResponseDTO(email=user.email, email_verified=True)


# 이메일 재인증 요청
async def resend_verification_email_service(
    request: ResendEmailRequest,
) -> ResendEmailResponseDTO:
    user = await get_user_by_email(email=request.email)
    if not user:
        raise UserNotFoundException()

    if user.email_verified:
        raise EmailAlreadyVerifiedException()

    await send_email_code(email=user.email, purpose="이메일 재인증")

    return ResendEmailResponseDTO(success=True, email=user.email)


# 이메일 중복 검사 함수
async def check_email_duplicate(email: str) -> EmailCheckResponseDTO:
    existing_user = await get_user_by_email(email=email)
    if existing_user:
        return EmailCheckResponseDTO(success=True, is_available=False)
    return EmailCheckResponseDTO(success=True, is_available=True)
