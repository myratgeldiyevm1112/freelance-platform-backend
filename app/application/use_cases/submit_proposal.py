import uuid
from app.application.dto.proposal import SubmitProposalRequest, ProposalResponse
from app.application.interfaces.proposal_repository import IProposalRepository
from app.application.interfaces.job_repository import IJobRepository
from app.domain.entities.proposal import ProposalEntity
from app.domain.entities.user import UserEntity
from app.infrastructure.database.models.job import JobStatus
from app.infrastructure.database.models.user import UserRole


class SubmitProposal:

    def __init__(
        self,
        proposal_repo: IProposalRepository,
        job_repo: IJobRepository,
    ):
        self.proposal_repo = proposal_repo
        self.job_repo = job_repo

    async def execute(
        self, job_id: uuid.UUID, data: SubmitProposalRequest, current_user: UserEntity
    ) -> ProposalResponse:
        if current_user.role != UserRole.FREELANCER:
            raise ValueError("Only freelancers can submit proposals")

        job = await self.job_repo.get_by_id(job_id)
        if not job:
            raise ValueError("Job not found")

        if job.status != JobStatus.OPEN:
            raise ValueError("Job is not open for proposals")

        existing = await self.proposal_repo.get_by_freelancer_and_job(
            current_user.id, job_id
        )
        if existing:
            raise ValueError("You already submitted a proposal for this job")

        entity = ProposalEntity(
            id=uuid.uuid4(),
            job_id=job_id,
            freelancer_id=current_user.id,
            cover_letter=data.cover_letter,
            proposed_rate=data.proposed_rate,
            status=None,
            created_at=None,
        )

        created = await self.proposal_repo.create(entity)
        return ProposalResponse.model_validate(created)
