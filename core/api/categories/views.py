from core.api.categories.schemas import CategoryCreateSchema, CategorySchema, CategoryUpdateSchema
from core.api.categories.services import CategoriesCRUDService
from core.api.routers import CRUDRouter, CRUDRouterConfig
from core.api.users.dependencies import check_user_role
from core.database.models.user import UserRole

config = CRUDRouterConfig(
    "/categories",
    ["Categories API"],
    CategoryCreateSchema,
    CategoryUpdateSchema,
    CategorySchema,
    CategoriesCRUDService(),
    {
        "list": check_user_role(UserRole.CUSTOMER, UserRole.SELLER),
        "create": check_user_role(),
        "delete": check_user_role(),
    },
    excluded_opts=["retrieve", "update"],
)

crud_router = CRUDRouter(config)
router = crud_router.router
