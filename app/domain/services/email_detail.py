import asyncio
import os
import random
import smtplib
from email.mime.text import MIMEText

from dotenv import load_dotenv

from app.core.redis import redis

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

    URL_SCHEME = os.getenv("URL_SCHEME")
    DOMAIN = os.getenv("DOMAIN")

    # 아이디 찾기 또는 비밀번호 찾기일 경우 링크 포함
    if purpose in ["아이디 찾기", "비밀번호 찾기"]:
        verify_link = (
            f"{URL_SCHEME}://{DOMAIN}/reset-password/verify-code?email={email}"
        )
        content += f"\n👇 아래 링크를 눌러 인증코드를 입력해주세요:\n{verify_link}"

    await asyncio.to_thread(send_email, email, subject, content)
