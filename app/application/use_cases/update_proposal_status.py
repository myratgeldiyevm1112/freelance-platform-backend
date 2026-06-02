import uuid
from app.application.dto.proposal import ProposalResponse
from app.application.interfaces.proposal_repository import IProposalRepository
from app.application.interfaces.job_repository import IJobRepository
from app.domain.entities.user import UserEntity
from app.infrastructure.database.models.proposal import ProposalStatus
from app.infrastructure.database.models.user import UserRole


class UpdateProposalStatus:

    def __init__(
        self,
        proposal_repo: IProposalRepository,
        job_repo: IJobRepository,
    ):
        self.proposal_repo = proposal_repo
        self.job_repo = job_repo

    async def execute(
        self,
        proposal_id: uuid.UUID,
        new_status: ProposalStatus,
        current_user: UserEntity,
    ) -> ProposalResponse:
        if current_user.role != UserRole.CLIENT:
            raise ValueError("Only clients can accept or reject proposals")

        proposal = await self.proposal_repo.get_by_id(proposal_id)
        if not proposal:
            raise ValueError("Proposal not found")

        if proposal.status != ProposalStatus.PENDING:
            raise ValueError("Proposal is no longer pending")

        job = await self.job_repo.get_by_id(proposal.job_id)
        if not job:
            raise ValueError("Job not found")

        if job.client_id != current_user.id:
            raise ValueError("You do not own this job")

        updated = await self.proposal_repo.update_status(proposal_id, new_status)
        return ProposalResponse.model_validate(updated)
