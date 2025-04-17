import os

from fastapi import APIRouter

from app.services.public_services import ExternalAPIService
from app.utils.exception import CustomException

router = APIRouter()

base_url = os.getenv.get("BASE_URL")
api_key = os.getenv.get("API_KEY")

# API 서비스 초기화
api_service = ExternalAPIService(
    base_url=base_url,
    api_key=api_key,
)


@router.get("/fetch-data")
async def fetch_data():
    try:
        endpoint = "/Oldpsnslfjobbiz"
        params = {"query": "example"}
        response = await api_service.get_data(endpoint=endpoint, params=params)
        return response
    except CustomException as e:
        return {
            "error": str(e),
        }
