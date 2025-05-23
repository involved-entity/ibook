from typing import Any, Optional

import pytest

from core.api.addresses.schemas import AddressCreateSchema, AddressUpdateSchema
from core.database.models import Address
from core.database.models.user import UserRole
from tests.base.crud import CRUDTest


class TestAddressCRUD(CRUDTest):
    endpoint = "/api/addresses/"
    create_schema = AddressCreateSchema
    update_schema = AddressUpdateSchema
    model = Address

    permissions_map = {
        "create": (UserRole.CUSTOMER.value,),
        "retrieve": (UserRole.CUSTOMER.value,),
        "update": (UserRole.CUSTOMER.value,),
        "delete": (UserRole.CUSTOMER.value,),
        "list": (UserRole.CUSTOMER.value,),
    }

    keys_to_check_after_create = ["city", "street", "house", "postal_code", "is_primary"]

    def get_create_data(self, before_create_hook_return: Optional[Any] = None):
        return {"city": "Tokyo", "street": "Shibuya?", "house": "683B", "postal_code": "456753", "is_primary": True}

    @pytest.fixture
    def sample_update_data(self):
        return {"street": "Shibuya", "house": "683A", "is_primary": False}
