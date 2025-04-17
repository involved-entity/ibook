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

    @pytest.fixture
    def keys_to_check_after_create(self):
        return ["title", "author", "price"]

    @pytest.fixture
    def sample_create_data(self):
        return {"title": "Margin", "author": "Me", "price": 199.99, "categories": ["Bestsellers"]}

    @pytest.fixture
    def sample_update_data(self):
        return {"price": 99.99}
