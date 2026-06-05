from fastapi import UploadFile, HTTPException, status
from app.domain.entities.user import UserEntity
from app.infrastructure.repositories.user_repository import UserRepository
from app.infrastructure.storage.s3_service import s3_service

ALLOWED_TYPES = {"image/jpeg", "image/png", "application/pdf"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


class UploadPortfolio:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def execute(self, current_user: UserEntity, files: list[UploadFile]) -> list[str]:
        urls = []

        for file in files:
            if file.content_type not in ALLOWED_TYPES:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"{file.filename}: only JPG, PNG, PDF are allowed",
                )

            file_bytes = await file.read()

            if len(file_bytes) > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"{file.filename}: file size must not exceed 5MB",
                )

            url = s3_service.upload_file(
                file_bytes=file_bytes,
                filename=file.filename,
                content_type=file.content_type,
            )
            urls.append(url)

        existing = current_user.portfolio_urls or []
        all_urls = existing + urls
        await self.user_repo.update_portfolio(current_user.id, all_urls)
        return all_urls