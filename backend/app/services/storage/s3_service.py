from io import BytesIO
from datetime import datetime

import boto3
from botocore.client import Config

from app.config.aws_settings import get_aws_settings
from .base_storage import BaseStorage

class S3StorageService(BaseStorage):
    def __init__(self):
        aws_settings = get_aws_settings()
        self.client = boto3.client(
            "s3",
            region_name=aws_settings.aws_region,
            aws_access_key_id=aws_settings.aws_access_key_id.get_secret_value(),
            aws_secret_access_key=aws_settings.aws_secret_access_key.get_secret_value(),
            config=Config(signature_version="s3v4"),
        )
        self.bucket = aws_settings.s3_bucket_name
        self.s3_presigned_url_expiry = aws_settings.s3_presigned_url_expiry

    def upload_file(self, file_bytes: bytes, file_name: str) -> str:
        self.client.put_object(Bucket=self.bucket, Key=file_name, Body=BytesIO(file_bytes))
        return f"{self.bucket}/{file_name}"

    def generate_presigned_url(self, filename: str, user_id: str | None = None):
        """
        Generate a presigned URL for uploading to S3.

        Returns (url, object_name) to match the MinIO service interface.
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        if "." in filename:
            name, extension = filename.rsplit(".", 1)
            new_filename = f"{name}_{timestamp}.{extension}"
        else:
            new_filename = f"{filename}_{timestamp}"

        if user_id:
            object_name = f"{user_id}/{new_filename}"
        else:
            object_name = new_filename

        url = self.client.generate_presigned_url(
            ClientMethod="put_object",
            Params={"Bucket": self.bucket, "Key": object_name},
            ExpiresIn=self.s3_presigned_url_expiry,
        )

        return url, object_name

    def generate_download_url(self, filename: str):
        """Generate a presigned URL for downloading a file from S3."""
        url = self.client.generate_presigned_url(
            ClientMethod="get_object",
            Params={"Bucket": self.bucket, "Key": filename},
            ExpiresIn=self.s3_presigned_url_expiry,
        )
        return url

    def get_object(self, object_name: str, bucket_name: str | None = None):
        """Get object from S3. Returns a StreamingBody similar to MinIO's get_object."""
        bucket_name = bucket_name or self.bucket
        response = self.client.get_object(Bucket=bucket_name, Key=object_name)
        return response["Body"]


def get_s3_service():
    return S3StorageService()


