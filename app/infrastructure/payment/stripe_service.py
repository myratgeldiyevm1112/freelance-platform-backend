import stripe
from app.core.config import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeService:

    def create_payment_intent(self, amount: float, currency: str = "usd", metadata: dict = {}) -> dict:
        """Создать PaymentIntent — клиент платит картой."""
        intent = stripe.PaymentIntent.create(
            amount=int(amount * 100),  # Stripe принимает центы
            currency=currency,
            metadata=metadata,
            capture_method="automatic",
        )
        return {
            "payment_intent_id": intent.id,
            "client_secret": intent.client_secret,
            "status": intent.status,
        }

    def create_transfer(self, amount: float, stripe_account: str, metadata: dict = {}) -> dict:
        """Перевести деньги фрилансеру."""
        transfer = stripe.Transfer.create(
            amount=int(amount * 100),
            currency="usd",
            destination=stripe_account,
            metadata=metadata,
        )
        return {
            "transfer_id": transfer.id,
            "status": "completed",
        }

    def refund_payment_intent(self, payment_intent_id: str) -> dict:
        """Возврат денег клиенту."""
        refund = stripe.Refund.create(payment_intent=payment_intent_id)
        return {
            "refund_id": refund.id,
            "status": refund.status,
        }

    def construct_webhook_event(self, payload: bytes, sig_header: str) -> stripe.Event:
        """Верифицировать webhook от Stripe."""
        return stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )


stripe_service = StripeService()
