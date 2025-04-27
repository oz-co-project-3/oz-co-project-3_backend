import asyncio
import os
import random
import smtplib
from email.mime.text import MIMEText

from dotenv import load_dotenv
from pydantic import BaseModel, EmailStr

from app.core.redis import redis
from app.domain.user.user_models import BaseUser
from app.domain.user.user_schema import ResendEmailRequest
from app.exceptions.email_exceptions import (
    EmailAlreadyVerifiedException,
    InvalidVerificationCodeException,
)
from app.exceptions.user_exceptions import UserNotFoundException

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

    # 기본 본문
    content = (
        f"{purpose}에 사용할 인증코드는 다음과 같습니다:\n\n"
        f"📌 인증코드: {code}\n\n"
        f"※ 인증코드는 10분간 유효합니다.\n"
    )

    # 아이디 찾기 또는 비밀번호 찾기일 경우 링크 포함
    if purpose in ["아이디 찾기", "비밀번호 찾기"]:
        verify_link = (
            f"https://your-frontend.com/verify-code?email={email}&purpose={purpose}"
        )
        content += f"\n👇 아래 링크를 눌러 인증코드를 입력해주세요:\n{verify_link}"

    await asyncio.to_thread(send_email, email, subject, content)
    return code


class EmailVerifyRequest(BaseModel):
    email: EmailStr
    verification_code: str


async def verify_email_code(request: EmailVerifyRequest):
    saved_code = await redis.get(f"email_verify:{request.email}")
    if not saved_code or saved_code != request.verification_code:
        raise InvalidVerificationCodeException()

    user = await BaseUser.get_or_none(email=request.email)
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


async def resend_verification_email(request: ResendEmailRequest):
    user = await BaseUser.get_or_none(email=request.email)
    if not user:
        raise UserNotFoundException()
    if user.email_verified:
        raise EmailAlreadyVerifiedException()

    await send_email_code(email=user.email, purpose="이메일 재인증")
    return {"message": "인증코드가 재전송되었습니다.", "data": {"email": user.email}}
