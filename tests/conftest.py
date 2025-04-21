import typing

import pytest
from httpx import AsyncClient

from core.config import settings
from core.database.models.user import UserRole
from tests.factories.user import UserFactory


@pytest.fixture(scope="session")
def user_factory() -> typing.Type[UserFactory]:
    return UserFactory


async def client_factory(
    client: AsyncClient, user_factory: typing.Type[UserFactory], role: UserRole = UserRole.CUSTOMER
):
    register_data = user_factory.stub(password=settings.test_user_password, first_name="G", role=role)
    register_data = {
        "email": register_data.email,
        "password": register_data.password,
        "first_name": register_data.first_name,
        "phone": register_data.phone,
        "role": register_data.role.value,
    }

    await client.post("/api/auth/register", json=register_data)

    login_data = {"username": register_data["email"], "password": settings.test_user_password}
    response = await client.post(settings.login_url, data=login_data)
    token = response.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"
    return client


@pytest.fixture
async def customer(user_factory: typing.Type[UserFactory]):
    async with AsyncClient(base_url=settings.test_base_app_url) as client:
        yield await client_factory(client, user_factory)


@pytest.fixture
async def seller(user_factory: typing.Type[UserFactory]):
    async with AsyncClient(base_url=settings.test_base_app_url) as client:
        yield await client_factory(client, user_factory, role=UserRole.SELLER)
