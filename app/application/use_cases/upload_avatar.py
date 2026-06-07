from fastapi import UploadFile
from app.domain.entities.user import UserEntity
from app.infrastructure.repositories.user_repository import UserRepository
from app.infrastructure.storage.s3_service import s3_service
from app.domain.exceptions import ValidationError

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

class UploadAvatar:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def execute(self, current_user: UserEntity, file: UploadFile) -> str:
        if file.content_type not in ALLOWED_IMAGE_TYPES:
            raise ValidationError("Only JPG and PNG images are allowed")
        file_bytes = await file.read()
        if len(file_bytes) > MAX_FILE_SIZE:
            raise ValidationError("File size must not exceed 5MB")
        url = s3_service.upload_file(
            file_bytes=file_bytes,
            filename=file.filename,
            content_type=file.content_type,
        )
        await self.user_repo.update_avatar(current_user.id, url)
        return url