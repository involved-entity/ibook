from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from core.api.payments.schemas import PaymentCreateSchema, PaymentSchema
from core.api.payments.services import create_payment, create_payment_intent, get_payment, handle_stripe_webhook
from core.database import get_session

router = APIRouter(prefix="/stripe", tags=["Stripe API"])


@router.post("/create-payment")
async def stripe_create_payment_intent(payment_data: PaymentCreateSchema, session: AsyncSession = Depends(get_session)):
    amount_cents = int(payment_data.amount * 100)
    intent_data = await create_payment_intent(amount_cents, payment_data.currency)
    await create_payment(payment_data, intent_data, session)

    return {"client_secret": intent_data["client_secret"]}


@router.post("/stripe-webhook")
async def stripe_webhook(request: Request, session: AsyncSession = Depends(get_session)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    return await handle_stripe_webhook(payload, sig_header, session)


@router.get("/payments/{payment_id}", response_model=PaymentSchema)
async def read_payment(payment_id: int, session: AsyncSession = Depends(get_session)):
    payment = await get_payment(payment_id, session)
    return payment
