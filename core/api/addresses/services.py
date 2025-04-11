from core.api.addresses.schemas import AddressCreateSchema, AddressSchema, AddressUpdateSchema
from core.api.services import CRUDService
from core.database.models import Address


class AddressesCRUDService(CRUDService):
    model = Address
    schema_class = AddressSchema
    create_schema_class = AddressCreateSchema
    update_schema_class = AddressUpdateSchema

    user_field = "user_id"

    admin_or_owner_to_edit = True
    save_user_id_before_create = True
    list_binded_to_user = True
