import uuid
from abc import ABC, abstractmethod
from app.domain.entities.payment import PaymentEntity


class IPaymentRepository(ABC):

    @abstractmethod
    async def create(
        self,
        contract_id: uuid.UUID,
        client_id: uuid.UUID,
        freelancer_id: uuid.UUID,
        amount: float,
        platform_fee_percent: float,
    ) -> PaymentEntity:
        pass

    @abstractmethod
    async def get_by_contract_id(self, contract_id: uuid.UUID) -> PaymentEntity | None:
        pass

    @abstractmethod
    async def update_status(
        self,
        payment_id: uuid.UUID,
        status: str,
        stripe_payment_intent_id: str | None = None,
        stripe_transfer_id: str | None = None,
    ) -> PaymentEntity:
        pass
