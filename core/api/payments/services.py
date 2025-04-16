import typing

import stripe
from fastapi import HTTPException, status
from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from core.api.payments.schemas import PaymentCreateResponseSchema, PaymentCreateSchema, PaymentSchema
from core.api.services import C, CRUDService, M, S
from core.config import settings
from core.database.models import Order, OrderItem, Payment, User
from core.database.models.order import OrderStatus
from core.database.models.payment import PaymentStatus
from core.database.models.user import UserRole

stripe.api_key = settings.stripe_secret_key


class IntentData(typing.NamedTuple):
    client_secret: str
    payment_intent_id: str


class PaymentsCRUDService(CRUDService):
    model = Payment
    schema_class = PaymentSchema
    create_schema_class = PaymentCreateSchema
    update_schema_class = PaymentSchema

    create_entity_error = HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unknown stripe error")

    def get_entities_default_query(self, query: typing.Optional[dict] = None) -> Select:
        return select(self.model).options(joinedload(self.model.order)).order_by(self.model.id.desc())

    def check_permissions_to_retrieve_entity(self, entity: M, user: User) -> M:
        if user.role != UserRole.ADMIN and entity.order.user_id != user.id:
            raise self.permission_denied_error

        return entity

    async def before_entity_create(
        self, entity: M, create_entity: C, user: User, session: AsyncSession
    ) -> tuple[M, IntentData]:
        await self._check_perms_to_create_payment(create_entity.order_id, user, session)
        intent_data = await self._create_payment_intent(int(create_entity.amount * 100), create_entity.currency)
        entity.transaction_id = intent_data.payment_intent_id

        return entity, intent_data

    async def create_entity(self, create_entity_data: C, session: AsyncSession, user: User) -> S:
        entity = self.model(**create_entity_data.model_dump())
        entity, intent_data = await self.before_entity_create(entity, create_entity_data, user, session)
        session.add(entity)
        await session.commit()

        return PaymentCreateResponseSchema(client_secret=intent_data.client_secret).model_dump()

    async def _check_perms_to_create_payment(self, order_id: int, user: User, session: AsyncSession) -> None:
        order = await session.get(Order, order_id, options=(selectinload(Order.items),))

        if user.role != UserRole.ADMIN and order.user_id != user.id:
            raise self.permission_denied_error

        if not (order.status == OrderStatus.CREATED and len(order.items)):  # noqa
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order is not ready to accept payments")

    async def _create_payment_intent(self, amount: int, currency: str = "usd") -> IntentData:  # noqa
        try:
            intent = stripe.PaymentIntent.create(
                amount=amount,
                currency=currency,
                automatic_payment_methods={"enabled": True, "allow_redirects": "never"},
            )
            return IntentData(client_secret=intent.client_secret, payment_intent_id=intent.id)
        except stripe.error.StripeError:
            raise self.create_entity_error


def _construct_event(payload: bytes, sig_header: str) -> dict[str, typing.Any]:
    try:
        return stripe.Webhook.construct_event(payload, sig_header, settings.stripe_webhook_key)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid signature")


async def _get_and_validate_payment_by_transaction_id(transaction_id: int, session: AsyncSession) -> Payment:
    payment = await session.scalar(
        select(Payment).options(joinedload(Payment.order)).where(Payment.transaction_id == transaction_id)
    )

    if payment:
        return payment

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Payment with transaction_id {transaction_id} not found",
    )


async def _handle_payment_success_for_order(order_id: int, session: AsyncSession) -> None:
    stmt = select(
        Order,
        func.coalesce(
            select(func.sum(Payment.amount))
            .where(Payment.order_id == Order.id)
            .where(Payment.status == PaymentStatus.PAID)
            .scalar_subquery(),
            0,
        ).label("total_paid"),
        func.coalesce(
            select(func.sum(OrderItem.quantity * OrderItem.price))
            .where(OrderItem.order_id == Order.id)
            .scalar_subquery(),
            0,
        ).label("total_books_cost"),
    ).where(Order.id == order_id)

    result = await session.execute(stmt)
    row = result.mappings().first()

    order, total_amount, total_price = row["Order"], row["total_paid"], row["total_books_cost"]

    if total_amount >= total_price:
        order.status = OrderStatus.PAID
        # notification to admins here mb?
        session.add(order)
        await session.commit()


async def handle_stripe_webhook(payload: bytes, sig_header: str, session: AsyncSession):
    event = _construct_event(payload, sig_header)

    if event["type"] == "payment_intent.succeeded":
        payment = await _get_and_validate_payment_by_transaction_id(event["data"]["object"]["id"], session)

        payment.status = PaymentStatus.PAID
        session.add(payment)
        await session.commit()
        await _handle_payment_success_for_order(payment.order.id, session)

    return {"status": "success"}
