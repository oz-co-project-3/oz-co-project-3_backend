from fastapi import APIRouter, File, UploadFile

from app.domain.services.verification import CustomException
from app.utils.s3_upload import upload_file_to_s3

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

image_upload_router = APIRouter()


@image_upload_router.post("/api/upload-image/")
async def upload_image(file: UploadFile = File(...)):
    file_extension = file.filename.split(".")[-1].lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        raise CustomException(
            status_code=400, code="not_allowed", error="허용되지 않는 파일 양식입니다"
        )

    url = await upload_file_to_s3(file)
    return {"image_url": url}
