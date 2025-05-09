from core.api.reviews.schemas import ReviewCreateSchema, ReviewSchema, ReviewUpdateSchema
from core.api.reviews.services import ReviewsCRUDService
from core.api.routers import CRUDRouter, CRUDRouterConfig
from core.api.users.dependencies import check_user_role
from core.database.models.user import UserRole

config = CRUDRouterConfig(
    "/reviews",
    ["Reviews API"],
    ReviewCreateSchema,
    ReviewUpdateSchema,
    ReviewSchema,
    ReviewsCRUDService(),
    {
        "retrieve": check_user_role(UserRole.CUSTOMER, UserRole.SELLER),
        "create": check_user_role(UserRole.CUSTOMER),
        "update": check_user_role(UserRole.CUSTOMER),
        "delete": check_user_role(UserRole.CUSTOMER),
    },
    excluded_opts=["list"],
)

crud_router = CRUDRouter(config)
router = crud_router.router
