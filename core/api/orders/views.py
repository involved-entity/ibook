from core.api.orders.schemas import OrderCreateSchema, OrderSchema, OrderUpdateSchema
from core.api.orders.services import OrdersCRUDService
from core.api.routers import CRUDRouter, CRUDRouterConfig
from core.api.users.dependencies import check_user_role
from core.database.models.user import UserRole

config = CRUDRouterConfig(
    "/orders",
    ["Orders API"],
    OrderCreateSchema,
    OrderUpdateSchema,
    OrderSchema,
    OrdersCRUDService(),
    {
        "list": check_user_role(UserRole.CUSTOMER),
        "retrieve": check_user_role(UserRole.CUSTOMER),
        "create": check_user_role(UserRole.CUSTOMER),
        "update": check_user_role(UserRole.CUSTOMER),
        "delete": check_user_role(UserRole.CUSTOMER),
    },
)

crud_router = CRUDRouter(config)
router = crud_router.router
