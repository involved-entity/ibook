import random
import string

import factory
from factory.alchemy import SQLAlchemyModelFactory
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.models import User


def random_string(length: int = 8) -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


def random_phone() -> str:
    return f"+79{''.join(random.choices(string.digits, k=9))}"


class UserFactory(SQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session = AsyncSession
        sqlalchemy_session_persistence = "commit"

    email = factory.LazyAttribute(lambda _: f"user_{random_string()}@example.com")
    phone = factory.LazyAttribute(lambda _: random_phone())
    role = "CUSTOMER"
