from core.api.order_items.schemas import OrderItemsCreateSchema, OrderItemsSchema, OrderItemsUpdateSchema
from core.api.order_items.services import OrderItemsCRUDService
from core.api.routers import CRUDRouter, CRUDRouterConfig
from core.api.users.dependencies import check_user_role
from core.database.models.user import UserRole

config = CRUDRouterConfig(
    "/order-items",
    ["Order items API"],
    OrderItemsCreateSchema,
    OrderItemsUpdateSchema,
    OrderItemsSchema,
    OrderItemsCRUDService(),
    {
        "create": check_user_role(UserRole.CUSTOMER),
        "update": check_user_role(UserRole.CUSTOMER),
        "delete": check_user_role(UserRole.CUSTOMER),
    },
    excluded_opts=["retrieve", "list"],
)

crud_router = CRUDRouter(config)
router = crud_router.router
