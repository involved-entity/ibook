from core.api.books.schemas import BookCreateSchema, BookSchema, BookUpdateSchema
from core.api.books.services import BooksCRUDService
from core.api.routers import CRUDRouter, CRUDRouterConfig
from core.api.users.dependencies import check_user_role
from core.database.models.user import UserRole

config = CRUDRouterConfig(
    "/books",
    ["Books API"],
    BookCreateSchema,
    BookUpdateSchema,
    BookSchema,
    BooksCRUDService(),
    {
        "list": check_user_role(UserRole.CUSTOMER, UserRole.SELLER),
        "retrieve": check_user_role(UserRole.CUSTOMER, UserRole.SELLER),
        "create": check_user_role(UserRole.SELLER),
        "update": check_user_role(UserRole.SELLER),
        "delete": check_user_role(UserRole.SELLER),
    },
)

crud_router = CRUDRouter(config)
router = crud_router.router
