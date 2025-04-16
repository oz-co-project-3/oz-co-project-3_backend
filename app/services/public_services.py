import httpx

from app.utils.exception import CustomException


class ExternalAPIService:
    def __init__(self, base_url: str, api_key: str = None):
        self.base_url = base_url
        self.api_key = api_key
        self.headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
        if not self.api_key:
            raise ValueError("API 키가 필요합니다.")

    async def get_data(self, endpoint: str, params: dict = None):
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.base_url}/{endpoint}", params=params, headers=self.headers
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            raise CustomException(
                error=f"외부 API 오류: {str(e)}", code="API_Error", status_code=500
            )
