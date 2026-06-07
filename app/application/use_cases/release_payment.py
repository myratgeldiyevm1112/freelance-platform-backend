import uuid
from app.application.interfaces.payment_repository import IPaymentRepository
from app.domain.entities.payment import PaymentEntity
from app.domain.entities.user import UserEntity
from app.domain.exceptions import NotFoundError, ForbiddenError, ValidationError


class ReleasePayment:
    def __init__(self, payment_repo: IPaymentRepository):
        self.payment_repo = payment_repo

    async def execute(self, contract_id: uuid.UUID, current_user: UserEntity) -> PaymentEntity:
        payment = await self.payment_repo.get_by_contract_id(contract_id)
        if not payment:
            raise NotFoundError("Payment not found")
        if payment.client_id != current_user.id:
            raise ForbiddenError("Only the client can release payment")
        if payment.status != "escrowed":
            raise ValidationError("Payment is not in escrowed state")

        # В тестовом режиме пропускаем transfer
        updated = await self.payment_repo.update_status(
            payment_id=payment.id,
            status="released",
        )
        return updated
