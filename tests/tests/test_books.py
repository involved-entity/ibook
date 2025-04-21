from typing import Any, Optional

import pytest

from core.api.books.schemas import BookCreateSchema, BookUpdateSchema
from core.database.models import Book
from core.database.models.user import UserRole
from tests.base.crud import CRUDTest


class TestBookCRUD(CRUDTest):
    endpoint = "/api/books/"
    create_schema = BookCreateSchema
    update_schema = BookUpdateSchema
    model = Book

    permissions_map = {
        "create": (UserRole.SELLER.value,),
        "retrieve": (UserRole.SELLER.value, UserRole.CUSTOMER.value),
        "update": (UserRole.SELLER.value,),
        "delete": (UserRole.SELLER.value,),
        "list": (UserRole.SELLER.value, UserRole.CUSTOMER.value),
    }

    keys_to_check_after_create = ["title", "author", "price"]

    def get_create_data(self, before_create_hook_return: Optional[Any] = None):
        return {"title": "Margin", "author": "Me", "price": 199.99, "categories": ["Bestsellers"]}

    @pytest.fixture
    def sample_update_data(self):
        return {"price": 99.99}
