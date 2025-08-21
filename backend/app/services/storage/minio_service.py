from minio import Minio
from io import BytesIO
from datetime import timedelta
from app.config.settings import MinIOSettings
from .base_storage import BaseStorage

settings = MinIOSettings()


class MinioStorageService(BaseStorage):
    def __init__(self):
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY.get_secret_value(),
            secret_key=settings.MINIO_SECRET_KEY.get_secret_value(),
            secure=False
        )
        self.bucket = settings.MINIO_BUCKET_NAME
        if not self.client.bucket_exists(self.bucket):
            self.client.make_bucket(self.bucket)
        self.minio_presigned_url_expiry = settings.MINIO_PRESIGNED_URL_EXPIRY

        # set the bucket policy
        self.client.set_bucket_policy(
            self.bucket,
            """
            {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": "*",
                        "Action": "s3:GetObject",
                        "Resource": "arn:aws:s3:::uploads/*"
                    }
                ]
            }
            """
        )

    def upload_file(self, file_bytes: bytes, file_name: str) -> str:
        self.client.put_object(
            self.bucket, file_name, BytesIO(file_bytes), length=len(file_bytes)
        )
        return f"{self.bucket}/{file_name}"

    def generate_presigned_url(self, filename: str):
        url = self.client.presigned_put_object(
            self.bucket,
            filename,
            expires=timedelta(seconds=self.minio_presigned_url_expiry)
        )
        return url

    def generate_download_url(self, filename: str):
        """Generate a presigned URL for downloading a file"""
        url = self.client.presigned_get_object(
            self.bucket,
            filename,
            expires=timedelta(seconds=self.minio_presigned_url_expiry)
        )
        return url


def get_minio_service():
    return MinioStorageService()
