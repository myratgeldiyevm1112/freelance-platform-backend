import uuid
from app.application.dto.proposal import SubmitProposalRequest, ProposalResponse
from app.application.interfaces.proposal_repository import IProposalRepository
from app.application.interfaces.job_repository import IJobRepository
from app.application.interfaces.user_repository import IUserRepository
from app.domain.entities.proposal import ProposalEntity
from app.domain.entities.user import UserEntity
from app.infrastructure.database.models.job import JobStatus
from app.infrastructure.database.models.user import UserRole
from app.domain.exceptions import ForbiddenError, NotFoundError, ValidationError, ConflictError


class SubmitProposal:

    def __init__(
        self,
        proposal_repo: IProposalRepository,
        job_repo: IJobRepository,
        user_repo: IUserRepository,
    ):
        self.proposal_repo = proposal_repo
        self.job_repo = job_repo
        self.user_repo = user_repo

    async def execute(
        self, job_id: uuid.UUID, data: SubmitProposalRequest, current_user: UserEntity
    ) -> ProposalResponse:
        if current_user.role != UserRole.FREELANCER:
            raise ForbiddenError("Only freelancers can submit proposals")

        job = await self.job_repo.get_by_id(job_id)
        if not job:
            raise NotFoundError("Job not found")

        if job.status != JobStatus.OPEN:
            raise ValidationError("Job is not open for proposals")

        existing = await self.proposal_repo.get_by_freelancer_and_job(
            current_user.id, job_id
        )
        if existing:
            raise ConflictError("You already submitted a proposal for this job")

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

        client = await self.user_repo.get_by_id(job.client_id)
        if client:
            from app.infrastructure.tasks.notifications import send_proposal_notification
            send_proposal_notification.delay(
                job_title=job.title,
                client_email=client.email,
                freelancer_name=current_user.full_name,
            )

        return ProposalResponse.model_validate(created)