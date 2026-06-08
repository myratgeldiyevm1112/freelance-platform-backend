import uuid
from app.application.interfaces.dispute_repository import IDisputeRepository
from app.application.interfaces.contract_repository import IContractRepository
from app.application.interfaces.payment_repository import IPaymentRepository
from app.domain.entities.dispute import DisputeEntity
from app.domain.entities.user import UserEntity
from app.domain.exceptions import NotFoundError, ForbiddenError, ValidationError
from app.infrastructure.database.models.dispute import DisputeStatus
from app.infrastructure.database.models.contract import ContractStatus
from app.infrastructure.database.models.user import UserRole


class ResolveDispute:
    def __init__(
        self,
        dispute_repo: IDisputeRepository,
        contract_repo: IContractRepository,
        payment_repo: IPaymentRepository,
    ):
        self.dispute_repo = dispute_repo
        self.contract_repo = contract_repo
        self.payment_repo = payment_repo

    async def execute(
        self,
        dispute_id: uuid.UUID,
        resolution: str,
        resolution_note: str | None,
        current_user: UserEntity,
    ) -> DisputeEntity:
        if not getattr(current_user, 'is_admin', False):
            raise ForbiddenError("Only admins can resolve disputes")

        dispute = await self.dispute_repo.get_by_id(dispute_id)
        if not dispute:
            raise NotFoundError("Dispute not found")

        if dispute.status != DisputeStatus.OPEN:
            raise ValidationError("Dispute is already resolved")

        if resolution == "refund":
            status = DisputeStatus.RESOLVED_REFUND
            contract_status = ContractStatus.CANCELLED
            payment_status = "refunded"
        elif resolution == "release":
            status = DisputeStatus.RESOLVED_RELEASE
            contract_status = ContractStatus.COMPLETED
            payment_status = "released"
        else:
            raise ValidationError("Resolution must be 'refund' or 'release'")

        await self.contract_repo.update_status(dispute.contract_id, contract_status)

        payment = await self.payment_repo.get_by_contract_id(dispute.contract_id)
        if payment:
            await self.payment_repo.update_status(payment.id, payment_status)

        return await self.dispute_repo.resolve(
            dispute_id=dispute_id,
            status=status,
            resolved_by=current_user.id,
            resolution_note=resolution_note,
        )


class GetDisputes:
    def __init__(self, dispute_repo: IDisputeRepository):
        self.dispute_repo = dispute_repo

    async def execute(self, limit: int = 20, offset: int = 0) -> list[DisputeEntity]:
        return await self.dispute_repo.get_all(limit=limit, offset=offset)
