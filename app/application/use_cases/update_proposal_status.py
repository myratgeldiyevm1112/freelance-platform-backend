import uuid
from app.application.dto.proposal import ProposalResponse, AcceptProposalResponse
from app.application.interfaces.proposal_repository import IProposalRepository
from app.application.interfaces.job_repository import IJobRepository
from app.domain.entities.contract import ContractEntity
from app.domain.entities.user import UserEntity
from app.infrastructure.database.models.proposal import ProposalStatus
from app.infrastructure.database.models.user import UserRole
from app.infrastructure.repositories.contract_repository import ContractRepository


class UpdateProposalStatus:

    def __init__(
        self,
        proposal_repo: IProposalRepository,
        job_repo: IJobRepository,
        contract_repo: ContractRepository,
    ):
        self.proposal_repo = proposal_repo
        self.job_repo = job_repo
        self.contract_repo = contract_repo

    async def execute(
        self,
        proposal_id: uuid.UUID,
        new_status: ProposalStatus,
        current_user: UserEntity,
    ) -> ProposalResponse | AcceptProposalResponse:
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

        if new_status == ProposalStatus.ACCEPTED:
            contract = await self.contract_repo.create(
                ContractEntity(
                    id=uuid.uuid4(),
                    job_id=proposal.job_id,
                    proposal_id=proposal_id,
                    client_id=job.client_id,
                    freelancer_id=proposal.freelancer_id,
                    agreed_rate=proposal.proposed_rate,
                    status=None,
                    created_at=None,
                )
            )
            return AcceptProposalResponse(
                proposal=ProposalResponse.model_validate(updated),
                contract_id=contract.id,
            )

        return ProposalResponse.model_validate(updated)