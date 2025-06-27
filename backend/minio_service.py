import os
from minio import Minio 
from datetime import timedelta

# ------------------ MinIO Setup ------------------- 
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")

# Default credentials and bucket name
MINIO_USERNAME = os.getenv("MINIO_USERNAME", "admin")
MINIO_PASSWORD = os.getenv("MINIO_PASSWORD", "password")
MINIO_BUCKET_NAME = os.getenv("MINIO_BUCKET_NAME", "uploads") 

# Initialize MinIO client
minio_client = Minio(
    MINIO_ENDPOINT,
    access_key = MINIO_USERNAME,
    secret_key = MINIO_PASSWORD,
    secure = False 
)

# add s3 policy to allow public access
minio_client.set_bucket_policy(
    MINIO_BUCKET_NAME,
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

# ------------------ MinIO Service Functions -------------------
# Generate a presigned URL for uploading files to MinIO
def generate_presigned_url(filename: str, expiry_seconds: int = 3600):
    if not minio_client.bucket_exists(MINIO_BUCKET_NAME):
        minio_client.make_bucket(MINIO_BUCKET_NAME)

    url = minio_client.presigned_put_object(
        MINIO_BUCKET_NAME, 
        filename, 
        expires = timedelta(seconds = expiry_seconds)
    )
    return url 