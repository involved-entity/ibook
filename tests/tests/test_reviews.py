from typing import Any, Optional

import pytest
from httpx import AsyncClient

from core.api.reviews.schemas import ReviewCreateSchema, ReviewUpdateSchema
from core.database.models import Review
from core.database.models.user import UserRole
from tests.base.crud import CRUDTest


class TestReviewCRUD(CRUDTest):
    endpoint = "/api/reviews/"
    create_schema = ReviewCreateSchema
    update_schema = ReviewUpdateSchema
    model = Review

    permissions_map = {
        "create": (UserRole.CUSTOMER.value,),
        "retrieve": (UserRole.CUSTOMER.value, UserRole.SELLER.value),
        "update": (UserRole.CUSTOMER.value,),
        "delete": (UserRole.CUSTOMER.value,),
    }

    keys_to_check_after_create = ["rating", "text"]

    def get_create_data(self, before_create_hook_return: Optional[Any] = None):
        return {"book_id": before_create_hook_return["book_id"], "rating": 4, "text": "good"}

    @pytest.fixture
    def sample_update_data(self):
        return {"rating": 5, "text": "Very good!"}

    async def before_create_entity(self, seller: AsyncClient, customer: AsyncClient):
        create_response = await seller.post(
            "/api/books/", json={"title": "Margin", "author": "Me", "price": 199.99, "categories": ["Bestsellers"]}
        )
        return {"book_id": create_response.json()["id"]}
