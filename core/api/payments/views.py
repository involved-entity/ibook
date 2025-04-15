from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from core.api.payments.schemas import PaymentCreateResponseSchema, PaymentCreateSchema, PaymentSchema
from core.api.payments.services import PaymentsCRUDService, handle_stripe_webhook
from core.api.routers import CRUDRouter, CRUDRouterConfig
from core.api.users.dependencies import check_user_role
from core.database import get_session
from core.database.models.user import UserRole

config = CRUDRouterConfig(
    "/stripe/payments",
    ["Stripe API"],
    PaymentCreateSchema,
    PaymentSchema,
    PaymentCreateResponseSchema,
    PaymentsCRUDService(),
    {
        "create": check_user_role(UserRole.CUSTOMER),
        "retrieve": check_user_role(UserRole.CUSTOMER),
    },
    excluded_opts=["list", "update", "delete"],
)

crud_router = CRUDRouter(config)
router = crud_router.router


@router.post("/stripe-webhook")
async def stripe_webhook(request: Request, session: AsyncSession = Depends(get_session)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    return await handle_stripe_webhook(payload, sig_header, session)
