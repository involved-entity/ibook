from typing import Any, Dict, List, Type

import pytest
from fastapi import status
from httpx import AsyncClient

from core.api.routers import UserDependenciesMethodsType
from core.api.services import C, M, U
from core.database.models.user import UserRole


class CRUDTest:
    model: Type[M]
    endpoint: str
    create_schema: Type[C]
    update_schema: Type[U]

    permissions_map: Dict[UserDependenciesMethodsType, tuple]

    @pytest.fixture
    def keys_to_check_after_create(self) -> List[str]:
        raise NotImplementedError

    @pytest.fixture
    def sample_create_data(self) -> Dict[str, Any]:
        raise NotImplementedError

    @pytest.fixture
    def sample_update_data(self) -> Dict[str, Any]:
        raise NotImplementedError

    def get_client(
        self, endpoint_type: UserDependenciesMethodsType, seller: AsyncClient, customer: AsyncClient
    ) -> AsyncClient:
        return seller if UserRole.SELLER.value in self.permissions_map[endpoint_type] else customer

    @pytest.mark.asyncio
    async def test_create_item(
        self,
        seller: AsyncClient,
        customer: AsyncClient,
        sample_create_data: Dict[str, Any],
        keys_to_check_after_create: List[str],
    ):
        if "create" not in self.permissions_map:
            return

        client = self.get_client("create", seller, customer)
        response = await client.post(self.endpoint, json=sample_create_data)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        for key in keys_to_check_after_create:
            assert data[key] == sample_create_data[key]
        return data

    @pytest.mark.asyncio
    async def test_read_item(
        self,
        seller: AsyncClient,
        customer: AsyncClient,
        sample_create_data: Dict[str, Any],
        keys_to_check_after_create: List[str],
    ):
        if "retrieve" not in self.permissions_map:
            return

        create_response = await self.get_client("create", seller, customer).post(self.endpoint, json=sample_create_data)
        item_id = create_response.json()["id"]

        response = await self.get_client("retrieve", seller, customer).get(f"{self.endpoint}{item_id}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == item_id
        for key in keys_to_check_after_create:
            assert data[key] == sample_create_data[key]

    @pytest.mark.asyncio
    async def test_update_item(
        self,
        seller: AsyncClient,
        customer: AsyncClient,
        sample_create_data: Dict[str, Any],
        sample_update_data: Dict[str, Any],
    ):
        if "update" not in self.permissions_map:
            return

        create_response = await self.get_client("create", seller, customer).post(self.endpoint, json=sample_create_data)
        item_id = create_response.json()["id"]

        response = await self.get_client("update", seller, customer).patch(
            f"{self.endpoint}{item_id}", json=sample_update_data
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == item_id
        for key, value in sample_update_data.items():
            assert data[key] == value

    @pytest.mark.asyncio
    async def test_delete_item(self, seller: AsyncClient, customer: AsyncClient, sample_create_data: Dict[str, Any]):
        if "remove" not in self.permissions_map:
            return

        create_response = await self.get_client("create", seller, customer).post(self.endpoint, json=sample_create_data)
        item_id = create_response.json()["id"]

        response = await self.get_client("delete", seller, customer).delete(f"{self.endpoint}{item_id}")
        assert response.status_code == status.HTTP_204_NO_CONTENT

        response = await self.get_client("retrieve", seller, customer).get(f"{self.endpoint}{item_id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_list_items(self, seller: AsyncClient, customer: AsyncClient, sample_create_data: Dict[str, Any]):
        if "list" not in self.permissions_map:
            return

        initial_response = await self.get_client("list", seller, customer).get(self.endpoint)
        initial_count = len(initial_response.json().get("items", []))

        for _ in range(3):
            await self.get_client("create", seller, customer).post(self.endpoint, json=sample_create_data)

        response = await self.get_client("list", seller, customer).get(self.endpoint)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, dict)
        assert len(data["items"]) == initial_count + 3
