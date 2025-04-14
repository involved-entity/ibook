from core.api.book_images.schemas import BookImageCreateSchema, BookImageSchema, BookImageUpdateSchema
from core.api.book_images.services import BookImagesCRUDService
from core.api.routers import CRUDRouter, CRUDRouterConfig
from core.api.users.dependencies import check_user_role
from core.database.models.user import UserRole

config = CRUDRouterConfig(
    "/book-images",
    ["Book images API"],
    BookImageCreateSchema,
    BookImageUpdateSchema,
    BookImageSchema,
    BookImagesCRUDService(),
    {
        "create": check_user_role(UserRole.SELLER),
        "delete": check_user_role(UserRole.SELLER),
    },
    excluded_opts=["list", "update"],
)

crud_router = CRUDRouter(config)
router = crud_router.router
