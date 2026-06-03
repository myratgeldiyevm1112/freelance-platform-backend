# app/api/v1/routers/proposals.py
import uuid
from typing import Union
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies.auth import get_current_user
from app.api.dependencies.db import get_db
from app.application.dto.proposal import SubmitProposalRequest, ProposalResponse, UpdateProposalStatusRequest, AcceptProposalResponse
from app.application.use_cases.submit_proposal import SubmitProposal
from app.domain.entities.user import UserEntity
from app.infrastructure.repositories.job_repository import JobRepository
from app.infrastructure.repositories.proposal_repository import ProposalRepository
from app.application.use_cases.get_proposals import GetProposals
from app.application.use_cases.update_proposal_status import UpdateProposalStatus
from app.infrastructure.repositories.contract_repository import ContractRepository

router = APIRouter(prefix="/proposals", tags=["proposals"])

@router.post("/jobs/{job_id}/proposals", response_model=ProposalResponse, status_code=status.HTTP_201_CREATED)
async def submit_proposal(
    job_id: uuid.UUID,
    data: SubmitProposalRequest,
    current_user: UserEntity = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    use_case = SubmitProposal(ProposalRepository(db), JobRepository(db))
    return await use_case.execute(job_id, data, current_user)


@router.get("/jobs/{job_id}/proposals", response_model=list[ProposalResponse])
async def get_proposals(
    job_id: uuid.UUID,
    current_user: UserEntity = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    use_case = GetProposals(ProposalRepository(db))
    return await use_case.execute_by_job(job_id, current_user)


@router.patch("/{proposal_id}", response_model=Union[AcceptProposalResponse, ProposalResponse])
async def update_proposal_status(
    proposal_id: uuid.UUID,
    data: UpdateProposalStatusRequest,
    current_user: UserEntity = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    use_case = UpdateProposalStatus(
        ProposalRepository(db),
        JobRepository(db),
        ContractRepository(db),
    )
    return await use_case.execute(proposal_id, data.status, current_user)