import uuid
import boto3
from botocore.exceptions import ClientError
from app.core.config import settings
from app.core.logging import logger


class S3Service:
    def __init__(self):
        self.client = boto3.client(
            "s3",
            endpoint_url=settings.S3_ENDPOINT_URL,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
        )
        self.bucket = settings.S3_BUCKET
        self._ensure_bucket()

    def _ensure_bucket(self):
        """Создаёт bucket если не существует."""
        try:
            self.client.head_bucket(Bucket=self.bucket)
        except ClientError:
            self.client.create_bucket(Bucket=self.bucket)
            # Делаем bucket публичным для чтения
            self.client.put_bucket_policy(
                Bucket=self.bucket,
                Policy=f'''{{
                    "Version": "2012-10-17",
                    "Statement": [{{
                        "Effect": "Allow",
                        "Principal": {{"AWS": ["*"]}},
                        "Action": ["s3:GetObject"],
                        "Resource": ["arn:aws:s3:::{self.bucket}/*"]
                    }}]
                }}''',
            )
            logger.info(f"S3 bucket '{self.bucket}' created")

    def upload_file(self, file_bytes: bytes, filename: str, content_type: str) -> str:
        """Загружает файл и возвращает публичный URL."""
        key = f"{uuid.uuid4()}_{filename}"
        self.client.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=file_bytes,
            ContentType=content_type,
        )
        url = f"{settings.S3_ENDPOINT_URL}/{self.bucket}/{key}"
        logger.info(f"Uploaded file: {key}")
        return url

    def delete_file(self, url: str):
        """Удаляет файл по URL."""
        try:
            key = url.split(f"{self.bucket}/")[-1]
            self.client.delete_object(Bucket=self.bucket, Key=key)
            logger.info(f"Deleted file: {key}")
        except ClientError as e:
            logger.error(f"Failed to delete file: {e}")


s3_service = S3Service()