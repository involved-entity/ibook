from fastapi_users.authentication import AuthenticationBackend

from core.api.authentication.strategy import get_database_strategy
from core.api.authentication.transport import bearer_transport

auth_backend = AuthenticationBackend(
    name="token",
    transport=bearer_transport,
    get_strategy=get_database_strategy,
)
