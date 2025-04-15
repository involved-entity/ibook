import stripe
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from core.api.payments.schemas import PaymentCreateSchema, PaymentSchema
from core.config import settings
from core.database.models import Payment
from core.database.models.payment import PaymentStatus

stripe.api_key = settings.stripe_secret_key


async def create_payment_intent(amount: int, currency: str = "usd") -> dict:
    try:
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency=currency,
            automatic_payment_methods={"enabled": True, "allow_redirects": "never"},
        )
        return {"client_secret": intent.client_secret, "payment_intent_id": intent.id}
    except stripe.error.StripeError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)


async def create_payment(payment_data: PaymentCreateSchema, intent_data: dict, session: AsyncSession) -> None:
    db_payment = Payment(
        order_id=payment_data.order_id,
        transaction_id=intent_data["payment_intent_id"],
        amount=payment_data.amount,
        currency=payment_data.currency,
    )

    session.add(db_payment)
    await session.commit()


async def get_payment(payment_id: int, session: AsyncSession) -> PaymentSchema:
    result = await session.execute(select(Payment).where(Payment.id == payment_id))
    payment = result.scalars().first()
    if payment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")

    return PaymentSchema.model_validate(payment).model_dump()


async def handle_stripe_webhook(payload: bytes, sig_header: str, session: AsyncSession):
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, settings.stripe_webhook_key)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid signature")

    if event["type"] == "payment_intent.succeeded":
        payment = await session.scalar(
            select(Payment)
            .options(joinedload(Payment.order))
            .where(Payment.transaction_id == event["data"]["object"]["id"])
        )

        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Payment with transaction_id {event['data']['object']['id']} not found",
            )

        payment.status = PaymentStatus.PAID
        session.add(payment)
        await session.commit()

    return {"status": "success"}
