import uuid
from app.application.interfaces.payment_repository import IPaymentRepository
from app.application.interfaces.contract_repository import IContractRepository
from app.domain.entities.user import UserEntity
from app.domain.exceptions import NotFoundError, ForbiddenError, ConflictError
from app.infrastructure.payment.stripe_service import stripe_service


class CreatePayment:
    def __init__(self, payment_repo: IPaymentRepository, contract_repo: IContractRepository):
        self.payment_repo = payment_repo
        self.contract_repo = contract_repo

    async def execute(
        self,
        contract_id: uuid.UUID,
        current_user: UserEntity,
        freelancer_id: uuid.UUID,
    ) -> dict:
        contract = await self.contract_repo.get_by_id(contract_id)
        if not contract:
            raise NotFoundError("Contract not found")
        if contract.client_id != current_user.id:
            raise ForbiddenError("Only the client can create payment")

        existing = await self.payment_repo.get_by_contract_id(contract_id)
        if existing:
            raise ConflictError("Payment already exists for this contract")

        amount = float(contract.agreed_rate)

        intent = stripe_service.create_payment_intent(
            amount=amount,
            metadata={"contract_id": str(contract_id)},
        )

        payment = await self.payment_repo.create(
            contract_id=contract_id,
            client_id=current_user.id,
            freelancer_id=freelancer_id,
            amount=amount,
            platform_fee_percent=10.0,
        )

        await self.payment_repo.update_status(
            payment_id=payment.id,
            status="escrowed",
            stripe_payment_intent_id=intent["payment_intent_id"],
        )

        return {
            "payment_id": str(payment.id),
            "client_secret": intent["client_secret"],
            "amount": amount,
            "platform_fee": payment.platform_fee,
            "freelancer_amount": payment.freelancer_amount,
        }
