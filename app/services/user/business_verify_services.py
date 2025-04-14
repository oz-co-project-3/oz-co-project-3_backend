import os

import httpx
from dotenv import load_dotenv

from app.utils.exception import CustomException

BIZINFO_API_KEY = os.getenv("BIZINFO_API_KEY")


async def verify_business_number(business_number: str):
    url = f"https://api.odcloud.kr/api/nts-businessman/v1/status?serviceKey={BIZINFO_API_KEY}"
    headers = {"Content-Type": "application/json"}
    body = {"b_no": [business_number]}

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(url, headers=headers, json=body)

    if response.status_code != 200:
        raise CustomException(
            status_code=500, error="국세청 API 요청 실패", code="external_api_error"
        )

    data = response.json().get("data", [])

    if not data:
        raise CustomException(
            status_code=400,
            error="국세청에 등록되지 않은 사업자등록번호입니다.",
            code="invalid_business_number",
        )

    item = data[0]

    return {
        "business_number": item.get("b_no"),
        "company_name": item.get("biz_nm") or "상호명 미확인",
        "business_status": item.get("b_stt"),
        "is_valid": item.get("b_stt") == "계속사업자",
    }
