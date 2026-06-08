import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock, patch
from botocore.exceptions import ClientError

from app.infrastructure.email.sender import send_email
from app.infrastructure.storage.s3_service import S3Service


# ─── Email Sender ────────────────────────────────────────────────────────────

class TestSendEmail:

    @pytest.mark.asyncio
    async def test_send_email_success(self):
        with patch("app.infrastructure.email.sender.aiosmtplib.send", new_callable=AsyncMock) as mock_send:
            await send_email("test@example.com", "Hello", "Body text")
            mock_send.assert_called_once()
            call_kwargs = mock_send.call_args
            assert call_kwargs is not None

    @pytest.mark.asyncio
    async def test_send_email_uses_correct_recipient(self):
        with patch("app.infrastructure.email.sender.aiosmtplib.send", new_callable=AsyncMock) as mock_send:
            await send_email("recipient@example.com", "Subject", "Body")
            msg = mock_send.call_args[0][0]
            assert msg["To"] == "recipient@example.com"
            assert msg["Subject"] == "Subject"

    @pytest.mark.asyncio
    async def test_send_email_handles_smtp_error_gracefully(self):
        """Ошибка SMTP не должна пробрасываться — просто логируется."""
        with patch("app.infrastructure.email.sender.aiosmtplib.send", new_callable=AsyncMock) as mock_send:
            mock_send.side_effect = Exception("SMTP connection refused")
            # не должно бросать исключение
            await send_email("test@example.com", "Subject", "Body")

    @pytest.mark.asyncio
    async def test_send_email_logs_success(self):
        with patch("app.infrastructure.email.sender.aiosmtplib.send", new_callable=AsyncMock):
            with patch("app.infrastructure.email.sender.logger") as mock_logger:
                await send_email("log@example.com", "Test", "Body")
                mock_logger.info.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_email_logs_error_on_failure(self):
        with patch("app.infrastructure.email.sender.aiosmtplib.send", new_callable=AsyncMock) as mock_send:
            mock_send.side_effect = Exception("Connection failed")
            with patch("app.infrastructure.email.sender.logger") as mock_logger:
                await send_email("fail@example.com", "Test", "Body")
                mock_logger.error.assert_called_once()


# ─── S3Service ───────────────────────────────────────────────────────────────

class TestS3Service:

    def _make_service(self):
        with patch("app.infrastructure.storage.s3_service.boto3.client") as mock_boto:
            mock_boto.return_value = MagicMock()
            svc = S3Service()
            svc._client = MagicMock()  # подменяем сразу
            return svc

    def test_client_lazy_init(self):
        """Клиент создаётся только при первом обращении."""
        with patch("app.infrastructure.storage.s3_service.boto3.client") as mock_boto:
            mock_boto.return_value = MagicMock()
            svc = S3Service()
            assert svc._client is None
            _ = svc.client
            mock_boto.assert_called_once()

    def test_client_cached(self):
        """Повторный вызов client не создаёт новый boto3 client."""
        with patch("app.infrastructure.storage.s3_service.boto3.client") as mock_boto:
            mock_boto.return_value = MagicMock()
            svc = S3Service()
            c1 = svc.client
            c2 = svc.client
            assert c1 is c2
            mock_boto.assert_called_once()

    def test_ensure_bucket_bucket_exists(self):
        """Если bucket уже существует — create_bucket не вызывается."""
        svc = self._make_service()
        svc.client.head_bucket.return_value = {}  # не бросает

        svc._ensure_bucket()

        svc.client.head_bucket.assert_called_once_with(Bucket=svc.bucket)
        svc.client.create_bucket.assert_not_called()

    def test_ensure_bucket_creates_if_not_exists(self):
        """Если bucket не существует — создаётся и устанавливается policy."""
        svc = self._make_service()
        error = ClientError({"Error": {"Code": "404", "Message": "Not Found"}}, "HeadBucket")
        svc.client.head_bucket.side_effect = error

        svc._ensure_bucket()

        svc.client.create_bucket.assert_called_once_with(Bucket=svc.bucket)
        svc.client.put_bucket_policy.assert_called_once()

    def test_upload_file_returns_url(self):
        svc = self._make_service()
        svc.client.head_bucket.return_value = {}

        with patch("app.infrastructure.storage.s3_service.uuid.uuid4", return_value=uuid.UUID("12345678-1234-5678-1234-567812345678")):
            url = svc.upload_file(b"file_content", "test.jpg", "image/jpeg")

        assert svc.bucket in url
        assert "test.jpg" in url
        svc.client.put_object.assert_called_once()

    def test_upload_file_calls_put_object_with_correct_args(self):
        svc = self._make_service()
        svc.client.head_bucket.return_value = {}

        svc.upload_file(b"data", "photo.png", "image/png")

        call_kwargs = svc.client.put_object.call_args[1]
        assert call_kwargs["Bucket"] == svc.bucket
        assert call_kwargs["Body"] == b"data"
        assert call_kwargs["ContentType"] == "image/png"
        assert "photo.png" in call_kwargs["Key"]

    def test_delete_file_success(self):
        svc = self._make_service()
        url = f"http://localhost:9000/{svc.bucket}/abc123_file.pdf"

        svc.delete_file(url)

        svc.client.delete_object.assert_called_once_with(
            Bucket=svc.bucket, Key="abc123_file.pdf"
        )

    def test_delete_file_logs_error_on_failure(self):
        svc = self._make_service()
        error = ClientError({"Error": {"Code": "NoSuchKey", "Message": "Not found"}}, "DeleteObject")
        svc.client.delete_object.side_effect = error

        with patch("app.infrastructure.storage.s3_service.logger") as mock_logger:
            svc.delete_file(f"http://localhost:9000/{svc.bucket}/missing.jpg")
            mock_logger.error.assert_called_once()

    def test_upload_file_logs_success(self):
        svc = self._make_service()
        svc.client.head_bucket.return_value = {}

        with patch("app.infrastructure.storage.s3_service.logger") as mock_logger:
            svc.upload_file(b"data", "file.jpg", "image/jpeg")
            mock_logger.info.assert_called()
