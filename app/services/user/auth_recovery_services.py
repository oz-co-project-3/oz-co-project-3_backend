from passlib.hash import bcrypt

from app.models.user_models import BaseUser, CorporateUser, SeekerUser
from app.services.user.email_services import send_email_code
from app.utils.exception import CustomException


# 아이디 찾기
async def find_email(name: str, phone_number: str):
    # 구직자에서 먼저 검색
    seeker = await SeekerUser.get_or_none(
        name=name, phone_number=phone_number
    ).prefetch_related("user")
    if seeker:
        email = seeker.user.email
    else:
        # 2. 없으면 기업회원에서 검색
        corp = await CorporateUser.get_or_none(
            manager_name=name, manager_phone_number=phone_number
        ).prefetch_related("user")
        if corp:
            email = corp.user.email
        else:
            raise CustomException(404, "일치하는 사용자 정보가 없습니다.", "user_not_found")

    # 이메일 마스킹 처리 x = 프론트에서 진행한다고 함
    return {"message": "아이디 찾기 성공", "data": {"email": email}}


async def find_password(name: str, phone_number: str, email: str):
    # seeker_profiles, corporate_profiles는 실제 related_name
    user_qs = BaseUser.filter(email=email).prefetch_related(
        "seeker_profiles", "corporate_profiles"
    )
    user = await user_qs.first()

    if not user:
        raise CustomException(404, "일치하는 사용자 정보가 없습니다.", "user_not_found")

    if user.user_type == "seeker":
        seeker = await user.seeker_profiles.all().first()  # 리스트 중 첫 번째
        if not seeker or seeker.name != name or seeker.phone_number != phone_number:
            raise CustomException(404, "일치하는 사용자 정보가 없습니다.", "user_not_found")

    elif user.user_type == "business":
        corp = await user.corporate_profiles.all().first()  # 리스트 중 첫 번째
        if (
            not corp
            or corp.manager_name != name
            or corp.manager_phone_number != phone_number
        ):
            raise CustomException(404, "일치하는 사용자 정보가 없습니다.", "user_not_found")

    else:
        raise CustomException(500, "알 수 없는 사용자 유형입니다.", "unknown_user_type")

    # 이메일로 재설정 링크 전송
    await send_email_code(email=email, purpose="비밀번호 찾기")

    return {"message": "비밀번호 재설정 링크가 이메일로 발송되었습니다", "data": {"email": email}}


# 새로운 비밀번호 생성 함수
async def reset_password(email: str, new_password: str, new_password_check: str):
    if new_password != new_password_check:
        raise CustomException(
            status_code=400, error="새 비밀번호와 확인이 일치하지 않습니다.", code="password_mismatch"
        )

    if len(new_password) < 8 or not any(
        char in "!@#$%^&*()_+{}:<>?" for char in new_password
    ):
        raise CustomException(
            status_code=400,
            error="비밀번호는 8자 이상이며 특수 문자를 포함해야 합니다.",
            code="invalid_password",
        )

    user = await BaseUser.get_or_none(email=email)
    if not user:
        raise CustomException(
            status_code=404, error="유저를 찾을 수 없습니다.", code="user_not_found"
        )

    if bcrypt.verify(new_password, user.password):
        raise CustomException(
            status_code=400,
            error="이전에 사용했던 비밀번호는 사용할 수 없습니다.",
            code="password_previously_used",
        )

    user.password = bcrypt.hash(new_password)
    await user.save()

    return {"message": "비밀번호가 성공적으로 변경되었습니다."}
