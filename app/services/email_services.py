import asyncio
import os
import random
import smtplib
from email.mime.text import MIMEText

from dotenv import load_dotenv
from pydantic import BaseModel, EmailStr

from app.core.redis import redis
from app.models.user_models import BaseUser
from app.schemas.user_schema import ResendEmailRequest
from app.utils.exception import CustomException

load_dotenv()

SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.naver.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 465))


# 동기 함수로 변경
def send_email(to_email: str, subject: str, content: str):
    msg = MIMEText(content, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = f"<{SMTP_USER}>"
    msg["To"] = to_email

    try:
        server = smtplib.SMTP_SSL(SMTP_SERVER, 465)  # SSL 연결
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(SMTP_USER, to_email, msg.as_string())
        server.quit()
    except Exception as e:
        print(f"이메일 전송 실패: {e}")
        raise


async def generate_email_code(email: str) -> str:
    code = str(random.randint(100000, 999999))
    await redis.set(f"email_verify:{email}", code, ex=600)  # 10분 유효
    return code


async def send_email_code(email: str, purpose: str) -> str:
    code = await generate_email_code(email)
    subject = f"[{purpose}] 인증코드 안내"
    content = f"{purpose}에 사용할 인증코드는 다음과 같습니다:\n\n인증코드: {code}\n\n10분 이내에 입력해주세요."

    # 핵심 수정: 동기 함수 비동기 실행
    await asyncio.to_thread(send_email, email, subject, content)
    return code


class EmailVerifyRequest(BaseModel):
    email: EmailStr
    verification_code: str


async def verify_email_code(request: EmailVerifyRequest):
    saved_code = await redis.get(f"email_verify:{request.email}")
    if not saved_code or saved_code != request.verification_code:
        raise CustomException(
            status_code=400,
            error="유효하지 않은 인증코드입니다.",
            code="invalid_verification_code",
        )

    user = await BaseUser.get_or_none(email=request.email)
    if not user:
        raise CustomException(
            status_code=404,
            error="유저를 찾을 수 없습니다.",
            code="user_not_found",
        )

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


async def resend_verification_email(request: ResendEmailRequest):
    user = await BaseUser.get_or_none(email=request.email)
    if not user:
        raise CustomException(
            status_code=404,
            error="가입된 이메일이 아닙니다.",
            code="user_not_found",
        )
    if user.email_verified:
        raise CustomException(
            status_code=400,
            error="이미 인증된 계정입니다.",
            code="already_verified",
        )

    await send_email_code(email=user.email, purpose="이메일 재인증")
    return {"message": "인증코드가 재전송되었습니다.", "data": {"email": user.email}}
