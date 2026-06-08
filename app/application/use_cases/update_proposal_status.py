import uuid
from app.application.dto.proposal import ProposalResponse, AcceptProposalResponse
from app.application.interfaces.proposal_repository import IProposalRepository
from app.application.interfaces.job_repository import IJobRepository
from app.application.interfaces.user_repository import IUserRepository
from app.domain.entities.contract import ContractEntity
from app.domain.entities.user import UserEntity
from app.infrastructure.database.models.proposal import ProposalStatus
from app.infrastructure.database.models.user import UserRole
from app.infrastructure.database.models.notification import NotificationType
from app.infrastructure.repositories.contract_repository import ContractRepository
from app.domain.exceptions import ForbiddenError, NotFoundError, ValidationError


class UpdateProposalStatus:

    def __init__(
        self,
        proposal_repo: IProposalRepository,
        job_repo: IJobRepository,
        contract_repo: ContractRepository,
        user_repo: IUserRepository,
        db=None,
    ):
        self.proposal_repo = proposal_repo
        self.job_repo = job_repo
        self.contract_repo = contract_repo
        self.user_repo = user_repo
        self.db = db

    async def execute(
        self,
        proposal_id: uuid.UUID,
        new_status: ProposalStatus,
        current_user: UserEntity,
    ) -> ProposalResponse | AcceptProposalResponse:
        if current_user.role != UserRole.CLIENT:
            raise ForbiddenError("Only clients can accept or reject proposals")

        proposal = await self.proposal_repo.get_by_id(proposal_id)
        if not proposal:
            raise NotFoundError("Proposal not found")

        if proposal.status != ProposalStatus.PENDING:
            raise ValidationError("Proposal is no longer pending")

        job = await self.job_repo.get_by_id(proposal.job_id)
        if not job:
            raise NotFoundError("Job not found")

        if job.client_id != current_user.id:
            raise ForbiddenError("You do not own this job")

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

            freelancer = await self.user_repo.get_by_id(proposal.freelancer_id)
            if freelancer:
                from app.infrastructure.tasks.notifications import send_contract_notification
                from app.infrastructure.websocket.manager import manager
                try:
                    send_contract_notification.delay(
                        job_title=job.title,
                        freelancer_email=freelancer.email,
                        client_name=current_user.full_name,
                    )
                except Exception:
                    pass
                    
                await manager.send_to_user(
                    str(proposal.freelancer_id),
                    event="proposal_accepted",
                    data={
                        "job_id": str(proposal.job_id),
                        "job_title": job.title,
                        "contract_id": str(contract.id),
                        "client_name": current_user.full_name,
                    },
                )

                if self.db:
                    from app.infrastructure.notifications.notification_service import NotificationService
                    await NotificationService(self.db).notify(
                        user_id=freelancer.id,
                        type=NotificationType.PROPOSAL_ACCEPTED,
                        title="Your proposal was accepted!",
                        message=f"{current_user.full_name} accepted your proposal for '{job.title}'",
                        related_id=contract.id,
                    )

            return AcceptProposalResponse(
                proposal=ProposalResponse.model_validate(updated),
                contract_id=contract.id,
            )

        return ProposalResponse.model_validate(updated)
