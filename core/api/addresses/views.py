from core.api.addresses.schemas import AddressCreateSchema, AddressSchema, AddressUpdateSchema
from core.api.addresses.services import AddressesCRUDService
from core.api.routers import CRUDRouter, CRUDRouterConfig
from core.api.users.dependencies import check_user_role
from core.database.models.user import UserRole

config = CRUDRouterConfig(
    "/addresses",
    ["Addresses API"],
    AddressCreateSchema,
    AddressUpdateSchema,
    AddressSchema,
    AddressesCRUDService(),
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
