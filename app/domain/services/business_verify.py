import os

import httpx

from app.exceptions.server_exceptions import ExternalApiErrorException
from app.exceptions.user_exceptions import InvalidBusinessNumberException

BIZINFO_API_KEY = os.getenv("BIZINFO_API_KEY")


async def verify_business_number(business_number: str):
    url = f"https://api.odcloud.kr/api/nts-businessman/v1/status?serviceKey={BIZINFO_API_KEY}"
    headers = {"Content-Type": "application/json"}
    body = {"b_no": [business_number]}

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(url, headers=headers, json=body)

    if response.status_code != 200:
        raise ExternalApiErrorException()

    data = response.json().get("data", [])

    if not data:
        raise InvalidBusinessNumberException()

    item = data[0]

    return {
        "business_number": item.get("b_no"),
        "company_name": item.get("biz_nm") or "상호명 미확인",
        "business_status": item.get("b_stt"),
        "is_valid": item.get("b_stt") == "계속사업자",
    }
