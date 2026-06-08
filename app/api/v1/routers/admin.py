import uuid
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_admin_user
from app.api.dependencies.db import get_db
from app.application.dto.auth import UserResponse
from app.application.use_cases.admin_users import GetAllUsers, BanUser, UnbanUser
from app.application.use_cases.admin_jobs import GetAllJobs, DeleteJob
from app.application.use_cases.admin_stats import GetPlatformStats
from app.application.dto.job import JobResponse
from app.domain.entities.user import UserEntity

router = APIRouter(prefix="/admin", tags=["Admin"])


# ═══════════════════════════════════════════
# Users
# ═══════════════════════════════════════════

@router.get("/users", response_model=list[UserResponse])
async def get_all_users(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: UserEntity = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    use_case = GetAllUsers(db)
    return await use_case.execute(limit=limit, offset=offset)


@router.patch("/users/{user_id}/ban", response_model=UserResponse)
async def ban_user(
    user_id: uuid.UUID,
    current_user: UserEntity = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    use_case = BanUser(db)
    return await use_case.execute(user_id)


@router.patch("/users/{user_id}/unban", response_model=UserResponse)
async def unban_user(
    user_id: uuid.UUID,
    current_user: UserEntity = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    use_case = UnbanUser(db)
    return await use_case.execute(user_id)


# ═══════════════════════════════════════════
# Jobs
# ═══════════════════════════════════════════

@router.get("/jobs", response_model=list[JobResponse])
async def get_all_jobs(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: UserEntity = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    use_case = GetAllJobs(db)
    return await use_case.execute(limit=limit, offset=offset)


@router.delete("/jobs/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(
    job_id: uuid.UUID,
    current_user: UserEntity = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    use_case = DeleteJob(db)
    await use_case.execute(job_id)


# ═══════════════════════════════════════════
# Stats
# ═══════════════════════════════════════════

@router.get("/stats")
async def get_platform_stats(
    current_user: UserEntity = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    use_case = GetPlatformStats(db)
    return await use_case.execute()
