from typing import Any, Dict, List, Optional, Type, TypeVar

import pytest
from fastapi import status
from httpx import AsyncClient, Response

from core.api.routers import UserDependenciesMethodsType
from core.api.services import C, M, U
from core.database.models.user import UserRole

I = TypeVar("I")


class CRUDTest:
    model: Type[M]
    create_schema: Type[C]
    update_schema: Type[U]
    endpoint: str

    permissions_map: Dict[UserDependenciesMethodsType, tuple]

    keys_to_check_after_create: List[str]

    @pytest.fixture
    def sample_update_data(self) -> Dict[str, Any]:
        raise NotImplementedError

    def get_create_data(self, initial_data: Optional[I] = None) -> Dict[str, Any]:
        raise NotImplementedError

    def get_client(
        self, endpoint_type: UserDependenciesMethodsType, seller: AsyncClient, customer: AsyncClient
    ) -> AsyncClient:
        return seller if UserRole.SELLER.value in self.permissions_map[endpoint_type] else customer

    def check_response_status(self, response: Response, status_required: int = status.HTTP_200_OK) -> Dict[str, Any]:  # noqa
        assert response.status_code == status_required
        return response.json()

    async def create_entity(self, seller: AsyncClient, customer: AsyncClient) -> tuple[Response, Dict[str, Any]]:
        client = self.get_client("create", seller, customer)
        res = await self.before_create_entity(seller, customer)
        sample_create_data = self.get_create_data(res)

        return await client.post(self.endpoint, json=sample_create_data), sample_create_data

    def check_keys_after_create(self, data: Dict[str, Any], sample_create_data: Dict[str, Any]) -> None:
        for key in self.keys_to_check_after_create:
            assert data[key] == sample_create_data[key]

    @pytest.mark.asyncio
    async def test_create_item(
        self,
        seller: AsyncClient,
        customer: AsyncClient,
    ):
        if "create" not in self.permissions_map:
            return

        response, sample_create_data = await self.create_entity(seller, customer)
        data = self.check_response_status(response, status.HTTP_201_CREATED)
        self.check_keys_after_create(data, sample_create_data)

    @pytest.mark.asyncio
    async def test_read_item(
        self,
        seller: AsyncClient,
        customer: AsyncClient,
    ):
        if "retrieve" not in self.permissions_map:
            return

        response, sample_create_data = await self.create_entity(seller, customer)
        client = self.get_client("retrieve", seller, customer)

        item_id = response.json()["id"]
        response = await client.get(f"{self.endpoint}{item_id}")
        data = self.check_response_status(response)
        assert data["id"] == item_id
        self.check_keys_after_create(data, sample_create_data)

    @pytest.mark.asyncio
    async def test_update_item(
        self,
        seller: AsyncClient,
        customer: AsyncClient,
        sample_update_data: Dict[str, Any],
    ):
        if "update" not in self.permissions_map:
            return

        response, _ = await self.create_entity(seller, customer)
        item_id = response.json()["id"]
        client = self.get_client("update", seller, customer)

        response = await client.patch(f"{self.endpoint}{item_id}", json=sample_update_data)
        data = self.check_response_status(response)
        assert data["id"] == item_id
        for key, value in sample_update_data.items():
            assert data[key] == value

    @pytest.mark.asyncio
    async def test_delete_item(self, seller: AsyncClient, customer: AsyncClient):
        if "remove" not in self.permissions_map:
            return

        response, _ = await self.create_entity(seller, customer)
        item_id = response.json()["id"]
        delete_client = self.get_client("delete", seller, customer)
        retrieve_client = self.get_client("retrieve", seller, customer)

        response = await delete_client.delete(f"{self.endpoint}{item_id}")
        assert response.status_code == status.HTTP_204_NO_CONTENT

        response = await retrieve_client.get(f"{self.endpoint}{item_id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_list_items(self, seller: AsyncClient, customer: AsyncClient):
        if "list" not in self.permissions_map:
            return

        client = self.get_client("list", seller, customer)

        initial_response = await client.get(self.endpoint)
        initial_count = len(initial_response.json().get("items", []))

        for _ in range(3):
            await self.create_entity(seller, customer)

        response = await client.get(self.endpoint)
        data = self.check_response_status(response)
        assert isinstance(data, dict)
        assert len(data["items"]) == initial_count + 3

    async def before_create_entity(self, seller: AsyncClient, customer: AsyncClient) -> I | None:
        pass
