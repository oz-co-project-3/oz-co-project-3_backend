import os
import uuid

import boto3
from fastapi import UploadFile

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION,
)


async def upload_file_to_s3(file: UploadFile) -> str:
    """S3에 파일 업로드하고 퍼블릭 URL 반환"""
    file_extension = file.filename.split(".")[-1]
    key = f"images/{uuid.uuid4()}.{file_extension}"

    s3_client.upload_fileobj(
        file.file,
        S3_BUCKET_NAME,
        key,
        ExtraArgs={"ContentType": file.content_type},
    )

    url = f"https://{S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{key}"

    return url
