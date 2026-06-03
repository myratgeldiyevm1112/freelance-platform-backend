import uuid
from app.application.dto.proposal import ProposalResponse
from app.application.interfaces.proposal_repository import IProposalRepository
from app.domain.entities.user import UserEntity
from app.infrastructure.database.models.user import UserRole
from app.domain.exceptions import ForbiddenError


class GetProposals:

    def __init__(self, proposal_repo: IProposalRepository):
        self.proposal_repo = proposal_repo

    async def execute_by_job(
        self, job_id: uuid.UUID, current_user: UserEntity
    ) -> list[ProposalResponse]:
        if current_user.role != UserRole.CLIENT:
            raise ForbiddenError("Only clients can view proposals")

        proposals = await self.proposal_repo.get_by_job_id(job_id)
        return [ProposalResponse.model_validate(p) for p in proposals]
