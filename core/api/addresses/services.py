from core.api.addresses.schemas import AddressSchema, AddressSchemaCreate
from core.api.services import CRUDService
from core.database.models import Address


class AddressesCRUDService(CRUDService):
    model = Address
    schema_class = AddressSchema
    create_schema_class = AddressSchemaCreate

    user_field = "user_id"

    admin_or_owner_to_edit = True
    save_user_id_before_create = True
    binded_to_user = True
