import uuid
from app.application.interfaces.payment_repository import IPaymentRepository
from app.domain.entities.payment import PaymentEntity
from app.domain.entities.user import UserEntity
from app.domain.exceptions import NotFoundError, ForbiddenError, ValidationError
from app.infrastructure.payment.stripe_service import stripe_service


class RefundPayment:
    def __init__(self, payment_repo: IPaymentRepository):
        self.payment_repo = payment_repo

    async def execute(self, contract_id: uuid.UUID, current_user: UserEntity) -> PaymentEntity:
        payment = await self.payment_repo.get_by_contract_id(contract_id)
        if not payment:
            raise NotFoundError("Payment not found")
        if payment.client_id != current_user.id:
            raise ForbiddenError("Only the client can refund payment")
        if payment.status != "escrowed":
            raise ValidationError("Only escrowed payments can be refunded")

        if payment.stripe_payment_intent_id:
            stripe_service.refund_payment_intent(payment.stripe_payment_intent_id)

        updated = await self.payment_repo.update_status(
            payment_id=payment.id,
            status="refunded",
        )
        return updated
