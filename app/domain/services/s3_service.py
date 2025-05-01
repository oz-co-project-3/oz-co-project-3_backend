import logging

from fastapi import APIRouter, File, UploadFile

from app.exceptions.base_exceptions import CustomException
from app.utils.s3_upload import upload_file_to_s3

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

image_upload_router = APIRouter()

logger = logging.getLogger(__name__)


@image_upload_router.post("/api/upload-image/")
async def upload_image(file: UploadFile = File(...)):
    logger.info("[API] S3에 이미지 업로드 요청")
    file_extension = file.filename.split(".")[-1].lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        logger.warning(f"[CHECK] 지원하지 않는 파일 형식입니다 {file_extension}")
        raise CustomException(
            status_code=400, code="not_allowed", error="허용되지 않는 파일 양식입니다"
        )

    url = await upload_file_to_s3(file)
    return {"image_url": url}
